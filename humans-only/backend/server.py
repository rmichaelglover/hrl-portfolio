#!/usr/bin/env python3
"""HumansOnly: shared SQLite forum/chat service. Python 3.10+, no dependencies."""
import argparse
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
WEEK = 7 * 24 * 60 * 60
MONTH = 30 * 24 * 60 * 60
AGE_GROUPS = ('under18', '18-20', '21', '22plus')
ROOMS = (
 {'id': 'commons', 'title': 'The Common Room', 'age': 'all', 'label': 'All ages', 'description': 'Introductions, questions, and ordinary human company.'},
 {'id': 'ideas', 'title': 'The Argument Clinic', 'age': 'all', 'label': 'All ages', 'description': 'Bring an argument. Leave other people their dignity.'},
 {'id': 'creative', 'title': 'Bread Upon the Water', 'age': 'all', 'label': 'All ages', 'description': 'Poems, drawings, music, and things you made.'},
 {'id': 'young-adults', 'title': 'The First Apartment', 'age': '18-21', 'label': 'Ages 18–21 inclusive', 'description': 'A room for adults aged eighteen through twenty-one.'},
 {'id': 'adults', 'title': 'After Hours', 'age': '18+', 'label': 'Ages 18+', 'description': 'Adult conversation. The same boundaries apply.'},
 {'id': 'over21', 'title': 'The Long Table', 'age': '21+', 'label': 'Ages 21+', 'description': 'A room for people twenty-one and older.'},
 {'id': 'game-lobby', 'title': 'Game Lobby', 'age': 'all', 'label': 'All ages', 'description': 'Shared chat for HRL games and players.'},
 {'id': 'tiny-creek-chess', 'title': 'Tiny Creek Chess', 'age': 'all', 'label': 'All ages', 'description': 'The riverside chess conversation.'},
 {'id': 'whimsy-chess', 'title': 'Whimsy Chess', 'age': 'all', 'label': 'All ages', 'description': 'Moves, puzzles, and postgame conversation.'},
)
ROOM_MAP = {r['id']: r for r in ROOMS}
HASH_SLOTS = threading.BoundedSemaphore(3)


class APIError(Exception):
 def __init__(self, status, message):
  self.status, self.message = status, message


def password_hash(password):
 if not isinstance(password, str) or not 12 <= len(password) <= 200:
  raise APIError(400, 'Use a passphrase of 12 to 200 characters.')
 salt = secrets.token_hex(16)
 with HASH_SLOTS:
  digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
 return 'scrypt$' + salt + '$' + digest


def password_matches(password, stored):
 if not isinstance(password, str) or len(password) > 200:
  return False
 _, salt, expected = stored.split('$')
 with HASH_SLOTS:
  actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
 return hmac.compare_digest(actual, expected)


def token_hash(token):
 return hashlib.sha256(token.encode()).hexdigest()


def clean_text(value, minimum=1, maximum=4000):
 if not isinstance(value, str):
  raise APIError(400, 'Text is required.')
 value = value.strip()
 if not minimum <= len(value) <= maximum:
  raise APIError(400, f'Use {minimum} to {maximum} characters.')
 if any(ord(c) < 32 and c not in '\n\t' for c in value):
  raise APIError(400, 'Control characters are not allowed.')
 return value


class Store:
 def __init__(self, path, clock=time.time):
  self.path, self.clock = str(path), clock
  Path(path).parent.mkdir(parents=True, exist_ok=True)
  with self.connect() as db:
   db.executescript((Path(__file__).parent / 'schema.sql').read_text())
  os.chmod(path, 0o600)

 def connect(self):
  db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
  db.row_factory = sqlite3.Row
  db.execute('PRAGMA foreign_keys=ON')
  return db

 def now(self):
  return int(self.clock())

 def rate(self, db, key, limit, window):
  now = self.now()
  row = db.execute('SELECT * FROM rates WHERE key=?', (key,)).fetchone()
  if not row or row['started'] + window <= now:
   db.execute('INSERT OR REPLACE INTO rates VALUES (?, ?, 1)', (key, now))
  elif row['count'] >= limit:
   raise APIError(429, 'Please slow down and try again later.')
  else:
   db.execute('UPDATE rates SET count=count+1 WHERE key=?', (key,))

 def user(self, db, token, required=True):
  u = db.execute('SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token_hash=? AND s.expires>?', (token_hash(token), self.now())).fetchone() if token else None
  if required and not u:
   raise APIError(401, 'Please sign in.')
  return dict(u) if u else None

 def public_user(self, user):
  return {k: user[k] for k in ('id', 'username', 'age_group', 'age_declared', 'role', 'timeout_until', 'timeout_reason', 'must_change_password')}

 def room(self, room_id, user):
  room = ROOM_MAP.get(room_id)
  if not room:
   raise APIError(404, 'Room not found.')
  if room['age'] != 'all':
   if not user:
    raise APIError(401, 'Sign in to enter an age-restricted room.')
   if self.now() - user['age_declared'] > MONTH:
    raise APIError(403, 'Please renew your age declaration in your account.')
   group = user['age_group']
   ok = room['age'] == '18+' and group != 'under18' or room['age'] == '21+' and group in ('21', '22plus') or room['age'] == '18-21' and group in ('18-20', '21')
   if not ok:
    raise APIError(403, 'This room is outside your declared age group.')
  return room

 def may_post(self, user):
  if user['must_change_password']:
   raise APIError(403, 'Change your setup password in your account first.')
  if user['timeout_until'] > self.now():
   raise APIError(403, 'You are in a seven-day reflection period until ' + time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(user['timeout_until'])) + '. Reading and appeals remain available.')

 def issue(self, db, uid):
  token = secrets.token_urlsafe(32)
  db.execute('DELETE FROM sessions WHERE expires<=?', (self.now(),))
  db.execute('INSERT INTO sessions VALUES (?, ?, ?)', (token_hash(token), uid, self.now()+MONTH))
  return token

 def handle(self, method, path, query, data, token='', remote='local'):
  db = self.connect()
  try:
   # Serialize decisions with their writes: moderation cannot race a send.
   if method != 'GET':
    db.execute('BEGIN IMMEDIATE')
   u = self.user(db, token, required=False)
   result = self.dispatch(db, method, path, query, data, token, u, remote)
   if method != 'GET':
    db.commit()
   return result
  except Exception:
   if db.in_transaction:
    db.rollback()
   raise
  finally:
   db.close()

 def dispatch(self, db, method, path, q, data, token, u, remote):
  now = self.now()
  if method == 'GET' and path == '/health':
   return {'ok': True, 'service': 'humansonly', 'api': 1, 'server_time': now}
  if method == 'GET' and path == '/rooms':
   rooms = []
   for r in ROOMS:
    try:
     self.room(r['id'], u); available = True
    except APIError:
     available = False
    rooms.append({**r, 'available': available})
   return {'rooms': rooms, 'server_time': now}
  if method == 'POST' and path in ('/auth/register', '/auth/login'):
   # Persist authentication throttles separately so failed passwords cannot roll them back.
   db.commit()
   db.execute('BEGIN IMMEDIATE')
   self.rate(db, 'auth:' + remote, 60, 600)
   if path.endswith('register'):
    self.rate(db, 'signup:' + remote, 12, 3600)
   db.commit(); db.execute('BEGIN IMMEDIATE')
   name = clean_text(data.get('username'), 3, 30)
   if not re.fullmatch(r'[A-Za-z0-9_\-]{3,30}', name):
    raise APIError(400, 'Names use 3–30 letters, numbers, underscores, or hyphens.')
   if path.endswith('register'):
    if data.get('website') or data.get('accepted_rules') is not True or data.get('human') is not True:
     raise APIError(400, 'Human participants must accept the community charter.')
    group = data.get('age_group')
    if group not in AGE_GROUPS:
     raise APIError(400, 'Choose your current age group.')
    uid = secrets.token_hex(16)
    hashed = password_hash(data.get('password'))
    try:
     db.execute('INSERT INTO users (id,username,password_hash,age_group,age_declared,created) VALUES (?,?,?,?,?,?)', (uid, name, hashed, group, now, now))
    except sqlite3.IntegrityError:
     raise APIError(409, 'That name is already in use.')
    user = dict(db.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone())
   else:
    row = db.execute('SELECT * FROM users WHERE username=? COLLATE NOCASE', (name,)).fetchone()
    # Run the same expensive operation for an unknown username.
    stored = row['password_hash'] if row else 'scrypt$'+'00'*16+'$'+'00'*64
    if not password_matches(data.get('password'), stored):
     raise APIError(401, 'Name or passphrase was not recognized.')
    user = dict(row)
   return {'token': self.issue(db, user['id']), 'user': self.public_user(user), 'server_time': now}
  if method == 'GET' and path == '/me':
   return {'user': self.public_user(u) if u else None, 'server_time': now}
  if method == 'GET' and path in ('/topics', '/messages'):
   rid = q.get('room', ['commons'])[0]
   self.room(rid, u)
   if path == '/topics':
    rows = db.execute('SELECT t.*,u.username,(SELECT COUNT(*) FROM messages m WHERE m.topic_id=t.id AND m.hidden=0) replies FROM topics t JOIN users u ON u.id=t.author_id WHERE t.room=? ORDER BY t.created DESC LIMIT 100', (rid,)).fetchall()
    return {'topics': [dict(r) for r in rows]}
   topic = q.get('topic', [''])[0]
   if topic:
    t = db.execute('SELECT * FROM topics WHERE id=? AND room=?', (topic, rid)).fetchone()
    if not t:
     raise APIError(404, 'Topic not found in this room.')
   after = q.get('after', ['0'])[0]
   if not after.isdigit() or len(after)>18:
    raise APIError(400, 'Invalid message cursor.')
   # Return only visible bodies. Hidden content never travels to ordinary clients.
   clause = 'm.topic_id=?' if topic else 'm.topic_id IS NULL'
   args = [rid] + ([topic] if topic else []) + [int(after)]
   order = 'ASC' if int(after) else 'DESC'
   rows = db.execute(f'SELECT m.id,m.room,m.topic_id,m.author_id,m.created,m.hidden,CASE WHEN m.hidden=1 THEN \'[Removed by moderation]\' ELSE m.body END body,u.username FROM messages m JOIN users u ON u.id=m.author_id WHERE m.room=? AND {clause} AND m.id>? ORDER BY m.id {order} LIMIT 100', args).fetchall()
   rows = sorted((dict(r) for r in rows), key=lambda r:r['id'])
   return {'messages': rows, 'server_time': now}
  if not u:
   raise APIError(401, 'Please sign in.')
  uid = u['id']
  if method == 'POST' and path == '/auth/logout':
   db.execute('DELETE FROM sessions WHERE token_hash=?', (token_hash(token),))
   return {'ok': True}
  if method == 'POST' and path == '/me/password':
   if not password_matches(data.get('current'), u['password_hash']):
    raise APIError(403, 'Current passphrase was not recognized.')
   db.execute('UPDATE users SET password_hash=?,must_change_password=0 WHERE id=?', (password_hash(data.get('password')), uid))
   db.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
   return {'token': self.issue(db, uid)}
  if method == 'POST' and path == '/me/age':
   group = data.get('age_group')
   if group not in AGE_GROUPS:
    raise APIError(400, 'Choose a current age group.')
   self.rate(db, 'age:' + uid, 3, MONTH)
   db.execute('UPDATE users SET age_group=?,age_declared=? WHERE id=?', (group, now, uid))
   return {'ok': True}
  if method == 'POST' and path in ('/topics', '/messages'):
   self.may_post(u)
   rid = data.get('room', 'commons'); self.room(rid, u)
   self.rate(db, 'send:' + uid, 10, 60)
   body = clean_text(data.get('body'))
   if path == '/topics':
    self.rate(db, 'topic:' + uid, 5, 3600)
    title = clean_text(data.get('title'), 3, 140)
    tid = secrets.token_hex(12)
    db.execute('INSERT INTO topics VALUES (?,?,?,?,?)', (tid, rid, title, uid, now))
   else:
    tid = data.get('topic') or None
    if tid and not db.execute('SELECT id FROM topics WHERE id=? AND room=?', (tid, rid)).fetchone():
     raise APIError(404, 'Topic not found in this room.')
   cursor = db.execute('INSERT INTO messages (room,topic_id,author_id,body,created) VALUES (?,?,?,?,?)', (rid, tid, uid, body, now))
   return {'ok': True, 'id': cursor.lastrowid, 'topic': tid}
  if method == 'POST' and path == '/reports':
   self.rate(db, 'report:' + uid, 15, 3600)
   mid = data.get('message_id')
   row = db.execute('SELECT * FROM messages WHERE id=?', (mid,)).fetchone()
   if not row:
    raise APIError(404, 'Message not found.')
   self.room(row['room'], u)
   reason = clean_text(data.get('reason'), 10, 1000)
   db.execute('INSERT OR IGNORE INTO reports (message_id,reporter_id,reason,created) VALUES (?,?,?,?)', (mid, uid, reason, now))
   return {'ok': True}
  if method == 'POST' and path == '/appeals':
   if u['timeout_until'] <= now:
    raise APIError(400, 'There is no active timeout to appeal.')
   self.rate(db, 'appeal:' + uid, 2, WEEK)
   db.execute('INSERT INTO appeals (user_id,body,created) VALUES (?,?,?)', (uid, clean_text(data.get('body'), 10, 2000), now))
   return {'ok': True}
  if method == 'GET' and path == '/moderation':
   self.require_mod(u)
   reports = db.execute('SELECT r.*,m.body,m.room,m.author_id,u.username FROM reports r JOIN messages m ON m.id=r.message_id JOIN users u ON u.id=m.author_id WHERE r.status=\'open\' ORDER BY r.created LIMIT 100').fetchall()
   appeals = db.execute('SELECT a.*,u.username FROM appeals a JOIN users u ON u.id=a.user_id WHERE a.status=\'open\' ORDER BY a.created LIMIT 100').fetchall()
   return {'reports': [dict(r) for r in reports], 'appeals': [dict(a) for a in appeals]}
  if method == 'POST' and path == '/moderation':
   self.require_mod(u)
   action = data.get('action')
   reason = clean_text(data.get('reason'), 10, 1000)
   target = None
   if action in ('timeout', 'release'):
    target = data.get('user_id')
    row = db.execute('SELECT * FROM users WHERE id=?', (target,)).fetchone()
    if not row:
     raise APIError(404, 'Person not found.')
    if row['role'] == 'owner' or target == uid:
     raise APIError(403, 'This action cannot target the owner or yourself.')
    if action == 'timeout':
     # Do not turn repeated reports into an indefinite ban by stacking timeouts.
     until = row['timeout_until'] if row['timeout_until'] > now else now+WEEK
     db.execute('UPDATE users SET timeout_until=?,timeout_reason=? WHERE id=?', (until, reason, target))
    else:
     db.execute('UPDATE users SET timeout_until=0,timeout_reason=\'\' WHERE id=?', (target,))
     db.execute('UPDATE appeals SET status=\'resolved\' WHERE user_id=?', (target,))
   elif action == 'hide':
    row = db.execute('SELECT * FROM messages WHERE id=?', (data.get('message_id'),)).fetchone()
    if not row:
     raise APIError(404, 'Message not found.')
    target = row['author_id']
    db.execute('UPDATE messages SET hidden=1 WHERE id=?', (row['id'],))
    if row['topic_id']:
     first = db.execute('SELECT MIN(id) FROM messages WHERE topic_id=?', (row['topic_id'],)).fetchone()[0]
     if first == row['id']:
      db.execute('UPDATE topics SET title=\'[Title removed by moderation]\' WHERE id=?', (row['topic_id'],))
    db.execute('UPDATE reports SET status=\'resolved\' WHERE message_id=?', (row['id'],))
   elif action == 'dismiss':
    db.execute('UPDATE reports SET status=\'resolved\' WHERE id=?', (data.get('report_id'),))
   else:
    raise APIError(400, 'Unknown moderation action.')
   db.execute('INSERT INTO audit (moderator_id,target_id,action,reason,created) VALUES (?,?,?,?,?)', (uid, target, action, reason, now))
   return {'ok': True}
  raise APIError(404, 'API route not found.')

 @staticmethod
 def require_mod(user):
  if user['role'] not in ('moderator', 'owner'):
   raise APIError(403, 'Moderator access is required.')
  if user['must_change_password']:
   raise APIError(403, 'Change your setup password first.')


class Handler(BaseHTTPRequestHandler):
 server_version = 'HumansOnly/1'
 sys_version = ''
 def log_message(self, fmt, *args):
  # Avoid logging visitor IP addresses, authorization tokens, or request text.
  logging.info('%s %s', self.command, urlsplit(self.path).path)

 def send_bytes(self, status, body, content_type='application/json; charset=utf-8'):
  self.send_response(status)
  self.send_header('Content-Type', content_type)
  self.send_header('Content-Length', str(len(body)))
  self.send_header('X-Content-Type-Options', 'nosniff')
  self.send_header('Referrer-Policy', 'no-referrer')
  self.send_header('Cache-Control', 'no-store' if self.path.startswith('/api/') else 'no-cache')
  origin = self.headers.get('Origin')
  if origin in self.server.allowed_origins:
   self.send_header('Access-Control-Allow-Origin', origin)
   self.send_header('Vary', 'Origin')
  self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https:; frame-ancestors 'self' https://rmichaelglover.github.io; base-uri 'none'; form-action 'self'")
  self.end_headers()
  self.wfile.write(body)

 def json_response(self, status, value):
  self.send_bytes(status, json.dumps(value).encode())

 def do_OPTIONS(self):
  origin = self.headers.get('Origin')
  if origin not in self.server.allowed_origins:
   self.json_response(403, {'error': 'Origin not allowed.'}); return
  self.send_response(204)
  self.send_header('Access-Control-Allow-Origin', origin)
  self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
  self.send_header('Access-Control-Max-Age', '600')
  self.send_header('Vary', 'Origin')
  self.end_headers()

 def do_GET(self):
  self.dispatch()

 def do_POST(self):
  self.dispatch()

 def dispatch(self):
  try:
   url = urlsplit(self.path)
   if url.path.startswith('/api/v1/'):
    origin = self.headers.get('Origin')
    if origin and origin not in self.server.allowed_origins:
     raise APIError(403, 'Origin not allowed.')
    data = {}
    if self.command == 'POST':
     if self.headers.get('Transfer-Encoding'):
      raise APIError(400, 'Chunked requests are not supported.')
     if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
      raise APIError(415, 'Send JSON.')
     try:
      size = int(self.headers.get('Content-Length', '0'))
      if not 0 < size <= 16000:
       raise APIError(413, 'Request is too large or empty.')
      data = json.loads(self.rfile.read(size))
      if not isinstance(data, dict):
       raise ValueError()
     except (ValueError, UnicodeDecodeError):
      raise APIError(400, 'Invalid JSON.')
    auth = self.headers.get('Authorization', '')
    token = auth[7:] if auth.startswith('Bearer ') and len(auth)<300 else ''
    remote = hashlib.sha256(self.client_address[0].encode()).hexdigest()[:24]
    result = self.server.store.handle(self.command, url.path[len('/api/v1'):], parse_qs(url.query), data, token, remote)
    self.json_response(200, result)
   elif self.command == 'GET':
    public = {'/': 'index.html', '/index.html': 'index.html', '/style.css': 'style.css', '/app.js': 'app.js', '/config.js': 'config.js', '/chat-client.js': 'chat-client.js', '/game-chat.html': 'game-chat.html', '/game-chat.js': 'game-chat.js', '/README.md': 'README.md', '/docs/api.md': 'docs/api.md', '/docs/serve.md': 'docs/serve.md'}
    name = public.get(url.path)
    if not name or not (ROOT/name).is_file():
     raise APIError(404, 'Not found.')
    mime = 'text/html' if name.endswith('.html') else 'text/css' if name.endswith('.css') else 'text/plain' if name.endswith('.md') else 'text/javascript'
    self.send_bytes(200, (ROOT/name).read_bytes(), mime+'; charset=utf-8')
   else:
    raise APIError(404, 'Not found.')
  except APIError as e:
   self.json_response(e.status, {'error': e.message})
  except (BrokenPipeError, ConnectionResetError):
   pass
  except Exception:
   logging.exception('Request failed')
   self.json_response(500, {'error': 'The server could not complete this request.'})


class Server(ThreadingHTTPServer):
 daemon_threads = True
 request_queue_size = 32
 slots = threading.BoundedSemaphore(48)
 def process_request(self, request, client_address):
  if not self.slots.acquire(blocking=False):
   try:
    request.sendall(b'HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nContent-Length: 0\r\n\r\n')
   finally:
    self.shutdown_request(request)
   return
  try:
   super().process_request(request, client_address)
  except Exception:
   self.slots.release()
   raise

 def process_request_thread(self, request, client_address):
  try:
   super().process_request_thread(request, client_address)
  finally:
   self.slots.release()

 def get_request(self):
  sock, address = super().get_request()
  sock.settimeout(15)
  return sock, address


def main():
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument('command', nargs='?', choices=['serve', 'owner', 'backup'], default='serve')
 parser.add_argument('--db', default=str(Path.home()/'.local/share/humansonly/forum.sqlite3'))
 parser.add_argument('--host', default='127.0.0.1')
 parser.add_argument('--port', type=int, default=8787)
 parser.add_argument('--origin', action='append', default=['https://rmichaelglover.github.io'])
 parser.add_argument('--username', default='CypherKeeper')
 parser.add_argument('--output')
 args = parser.parse_args()
 os.umask(0o077)
 store = Store(args.db)
 if args.command == 'owner':
  with store.connect() as db:
   db.execute('BEGIN IMMEDIATE')
   if db.execute('SELECT 1 FROM users WHERE role=\'owner\'').fetchone():
    parser.error('An owner already exists; no credentials were changed.')
   if not re.fullmatch(r'[A-Za-z0-9_\-]{3,30}', args.username):
    parser.error('Invalid owner name.')
   password = secrets.token_urlsafe(24)
   dest = Path(args.output or str(Path(args.db).parent/'owner-access.txt'))
   fd = os.open(dest, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
   with os.fdopen(fd,'w') as f:
    f.write(f'Name: {args.username}\nTemporary passphrase: {password}\nChange this passphrase in Account immediately after signing in.\n')
   db.execute('INSERT INTO users (id,username,password_hash,age_group,age_declared,role,created,must_change_password) VALUES (?,?,?,?,?,?,?,1)', (secrets.token_hex(16),args.username,password_hash(password),'under18',store.now(),'owner',store.now()))
   db.commit()
   print('Owner created. Credentials saved privately at '+str(dest))
 elif args.command == 'backup':
  if not args.output:
   parser.error('--output is required for a backup.')
  dest = Path(args.output)
  if dest.exists():
   parser.error('Backup destination already exists.')
  with store.connect() as db, sqlite3.connect(dest) as backup:
   db.backup(backup)
  os.chmod(dest, 0o600)
  print('Backup saved: '+str(dest))
 else:
  server = Server((args.host,args.port),Handler)
  server.store=store
  server.allowed_origins=set(args.origin+[f'http://localhost:{args.port}',f'http://127.0.0.1:{args.port}'])
  logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
  logging.info('Serving HumansOnly at http://%s:%s',args.host,args.port)
  server.serve_forever()


if __name__ == '__main__':
 main()
