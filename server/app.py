"""Persistent player accounts and public profiles; same-origin API and static site."""
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
AVATARS = ['♟️', '🎼', '🌈', '🦊', '🐸', '🦉', '🌲', '⚡']
COLORS = ['#37e6ff', '#c060ff', '#5fe3a0', '#e8c170', '#ff94bf']
PUBLIC = ('username', 'display_name', 'bio', 'avatar', 'accent', 'chess', 'music', 'lichess', 'chesscom', 'created_at')
FIELDS = {'display_name': 60, 'bio': 1200, 'chess': 200, 'music': 200, 'lichess': 30, 'chesscom': 30}


def password_hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def public(row):
    return {key: row[key] for key in PUBLIC}


class App(ThreadingHTTPServer):
    def __init__(self, address, db, origin=None):
        self.db = str(db)
        self.origin = origin
        self.limits = {}
        self.limit_lock = threading.Lock()
        Path(self.db).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, salt TEXT NOT NULL,
                display_name TEXT NOT NULL, bio TEXT NOT NULL DEFAULT '',
                avatar TEXT NOT NULL DEFAULT '♟️', accent TEXT NOT NULL DEFAULT '#37e6ff',
                chess TEXT NOT NULL DEFAULT '', music TEXT NOT NULL DEFAULT '',
                lichess TEXT NOT NULL DEFAULT '', chesscom TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')));
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES users(username),
                csrf TEXT NOT NULL, expires REAL NOT NULL);
            ''')
        os.chmod(self.db, 0o600)
        super().__init__(address, Handler)

    def connect(self):
        conn = sqlite3.connect(self.db, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def limited(self, ip):
        now = time.time()
        with self.limit_lock:
            self.limits = {key: values for key, values in self.limits.items() if values and values[-1] > now - 600}
            attempts = [v for v in self.limits.get(ip, []) if v > now - 600]
            self.limits[ip] = attempts
            if len(attempts) >= 20:
                return True
            attempts.append(now)
            return False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        super().end_headers()

    def reply(self, code, payload, cookie=None):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body)

    def session(self, conn):
        cookies = self.headers.get('Cookie', '').split(';')
        token = next((c.strip()[len('maestro_session='):] for c in cookies if c.strip().startswith('maestro_session=')), '')
        return conn.execute('SELECT * FROM sessions WHERE token_hash=? AND expires>?',
                            (hashlib.sha256(token.encode()).hexdigest(), time.time())).fetchone()

    def cookie(self, token, age=604800):
        secure = '; Secure' if self.server.origin and self.server.origin.startswith('https://') else ''
        return f'maestro_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={age}{secure}'

    def do_GET(self):
        path = urlsplit(self.path).path.rstrip('/')
        if path.startswith('/api/'):
            with self.server.connect() as conn:
                if path == '/api/me':
                    session = self.session(conn)
                    if not session:
                        return self.reply(200, {'user': None})
                    user = conn.execute('SELECT * FROM users WHERE username=?', (session['username'],)).fetchone()
                    return self.reply(200, {'user': public(user), 'csrf': session['csrf']})
                if path == '/api/profiles':
                    rows = conn.execute('SELECT * FROM users ORDER BY created_at DESC, username LIMIT 100').fetchall()
                    return self.reply(200, {'profiles': [public(row) for row in rows]})
                if path.startswith('/api/profiles/'):
                    user = conn.execute('SELECT * FROM users WHERE username=?', (unquote(path.split('/')[-1]).lower(),)).fetchone()
                    return self.reply(200, {'profile': public(user)}) if user else self.reply(404, {'error': 'Player not found.'})
            return self.reply(404, {'error': 'Unknown API route.'})
        target = Path(self.translate_path(self.path)).resolve()
        if not target.is_relative_to(ROOT) or any(part.startswith('.') for part in target.relative_to(ROOT).parts) or (target.is_relative_to(ROOT / 'server')):
            return self.send_error(404)
        return super().do_GET()

    def do_HEAD(self):
        # Apply the same file restrictions to HEAD requests.
        target = Path(self.translate_path(self.path)).resolve()
        if not target.is_relative_to(ROOT) or any(p.startswith('.') for p in target.relative_to(ROOT).parts) or target.is_relative_to(ROOT / 'server'):
            return self.send_error(404)
        return super().do_HEAD()

    def list_directory(self, path):
        return self.send_error(404)

    def do_POST(self):
        expected = self.server.origin or f'http://{self.headers.get("Host", "")}'
        if self.headers.get('Origin') != expected:
            return self.reply(403, {'error': 'Request origin rejected.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192 or self.headers.get_content_type() != 'application/json':
                return self.reply(400, {'error': 'Send a JSON object smaller than 8 KB.'})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self.reply(400, {'error': 'Invalid JSON request.'})
        path = urlsplit(self.path).path
        with self.server.connect() as conn:
            if path in ('/api/signup', '/api/login'):
                if self.server.limited(self.client_address[0]):
                    return self.reply(429, {'error': 'Too many attempts. Try again in ten minutes.'})
                username = data.get('username', '')
                password = data.get('password', '')
                if not isinstance(username, str) or not isinstance(password, str):
                    return self.reply(400, {'error': 'Username and password must be text.'})
                username = username.lower().strip()
                if not re.fullmatch(r'[a-z0-9_]{3,24}', username) or not 12 <= len(password) <= 128:
                    return self.reply(400, {'error': 'Use a username of 3–24 letters, numbers or underscores, and a password of 12–128 characters.'})
                if path == '/api/signup':
                    salt = secrets.token_hex(16)
                    try:
                        conn.execute('INSERT INTO users(username,password_hash,salt,display_name) VALUES (?,?,?,?)',
                                     (username, password_hash(password, salt), salt, username))
                    except sqlite3.IntegrityError:
                        return self.reply(409, {'error': 'That username is already taken.'})
                else:
                    user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                    candidate = password_hash(password, user['salt'] if user else '00' * 16)
                    if not user or not hmac.compare_digest(candidate, user['password_hash']):
                        return self.reply(401, {'error': 'Username or password is incorrect.'})
                # Replace any existing browser session when changing accounts.
                previous = self.session(conn)
                if previous:
                    conn.execute('DELETE FROM sessions WHERE token_hash=?', (previous['token_hash'],))
                conn.execute('DELETE FROM sessions WHERE expires<=?', (time.time(),))
                token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
                conn.execute('INSERT INTO sessions VALUES (?,?,?,?)',
                             (hashlib.sha256(token.encode()).hexdigest(), username, csrf, time.time() + 604800))
                user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                conn.commit()
                return self.reply(201 if path == '/api/signup' else 200, {'user': public(user), 'csrf': csrf}, self.cookie(token))
            session = self.session(conn)
            if not session:
                return self.reply(401, {'error': 'Log in first.'})
            if not hmac.compare_digest(self.headers.get('X-CSRF-Token', ''), session['csrf']):
                return self.reply(403, {'error': 'Session check failed. Reload and try again.'})
            if path == '/api/logout':
                conn.execute('DELETE FROM sessions WHERE token_hash=?', (session['token_hash'],))
                conn.commit()
                return self.reply(200, {'ok': True}, self.cookie('', 0))
            if path == '/api/profile':
                values = {}
                for key, maximum in FIELDS.items():
                    value = data.get(key, '')
                    if not isinstance(value, str) or len(value) > maximum:
                        return self.reply(400, {'error': f'{key} must be text of at most {maximum} characters.'})
                    values[key] = value.strip()
                if not values['display_name']:
                    return self.reply(400, {'error': 'Please add a display name.'})
                for key in ('lichess', 'chesscom'):
                    if values[key] and not re.fullmatch(r'[a-zA-Z0-9_-]{2,30}', values[key]):
                        return self.reply(400, {'error': 'Chess account names can contain letters, numbers, underscores and hyphens.'})
                avatar, accent = data.get('avatar'), data.get('accent')
                if avatar not in AVATARS or accent not in COLORS:
                    return self.reply(400, {'error': 'Choose one of the available avatars and colors.'})
                values.update(avatar=avatar, accent=accent)
                sql = ','.join(f'{key}=?' for key in values)
                conn.execute(f'UPDATE users SET {sql} WHERE username=?', (*values.values(), session['username']))
                conn.commit()
                user = conn.execute('SELECT * FROM users WHERE username=?', (session['username'],)).fetchone()
                return self.reply(200, {'user': public(user)})
            return self.reply(404, {'error': 'Unknown API route.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8788)
    parser.add_argument('--db', default=str(Path.home() / '.local/share/maestro/accounts.sqlite3'))
    parser.add_argument('--origin', help='Exact public origin, e.g. https://chess.example.org; enables Secure cookies')
    args = parser.parse_args()
    if args.origin and not re.fullmatch(r'https?://[^/]+', args.origin):
        parser.error('--origin must be an origin without a path or trailing slash')
    server = App((args.host, args.port), args.db, args.origin)
    print(f'Maestro: http://{args.host}:{args.port}', flush=True)
    server.serve_forever()
