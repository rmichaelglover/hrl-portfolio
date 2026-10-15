"""Behavior tests use temporary databases and never post to the live community."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

spec=importlib.util.spec_from_file_location('humansonly',Path(__file__).resolve().parents[1]/'backend/server.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class ForumTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.now=1800000000
  self.store=module.Store(Path(self.temp.name)/'forum.db',lambda:self.now)
  self.alice=self.join('Alice','18-20');self.bob=self.join('Bob','under18');self.owner=self.join('Owner','22plus')
  with self.store.connect() as db:db.execute("UPDATE users SET role='owner' WHERE id=?",(self.owner['user']['id'],))

 def tearDown(self):self.temp.cleanup()
 def call(self,path,data=None,person=None,query=None):
  return self.store.handle('GET' if data is None else 'POST',path,query or {},data or {},(person or {}).get('token',''))
 def join(self,name,age):
  return self.call('/auth/register',{'username':name,'password':'a test passphrase with spaces','age_group':age,'accepted_rules':True,'human':True})
 def denied(self,status,path,data=None,person=None,query=None):
  with self.assertRaises(module.APIError) as ctx:self.call(path,data,person,query)
  self.assertEqual(ctx.exception.status,status)

 def test_age_gates_protect_bodies_topics_and_writes(self):
  topic=self.call('/topics',{'room':'adults','title':'Adult discussion','body':'Restricted content stays in its room.'},self.alice)
  self.denied(401,'/messages',query={'room':['adults']})
  self.denied(403,'/messages',person=self.bob,query={'room':['adults'],'topic':[topic['topic']]})
  self.denied(403,'/topics',person=self.bob,query={'room':['adults']})
  self.denied(403,'/messages',{'room':'adults','body':'Cannot send'},self.bob)
  self.denied(403,'/messages',person=self.owner,query={'room':['young-adults']})
  twentyone=self.join('Twentyone','21')
  for room in ('young-adults','adults','over21'):self.call('/messages',person=twentyone,query={'room':[room]})
  self.denied(404,'/messages',person=self.alice,query={'room':['commons'],'topic':[topic['topic']]})
  self.now+=module.MONTH+1
  # Session expires too: sign in again, then the older age declaration still fails.
  self.alice=self.call('/auth/login',{'username':'Alice','password':'a test passphrase with spaces'})
  self.denied(403,'/messages',person=self.alice,query={'room':['adults']})

 def test_timeout_is_global_nonstacking_and_expires(self):
  original=self.now
  action={'action':'timeout','user_id':self.alice['user']['id'],'reason':'Repeated targeted harassment.'}
  self.call('/moderation',action,self.owner)
  for room in ('commons','game-lobby','tiny-creek-chess'):
   self.denied(403,'/messages',{'room':room,'body':'A blocked post'},self.alice)
  self.denied(403,'/topics',{'room':'commons','title':'Blocked topic','body':'Also blocked'},self.alice)
  self.call('/messages',person=self.alice,query={'room':['commons']})
  self.call('/appeals',{'body':'Please review the circumstances.'},self.alice)
  self.now+=60;self.call('/moderation',action,self.owner)
  self.assertEqual(self.call('/me',person=self.alice)['user']['timeout_until'],original+module.WEEK)
  self.now=original+module.WEEK
  self.call('/messages',{'room':'game-lobby','body':'The timer ended; I can participate.'},self.alice)

 def test_reports_do_not_punish_and_hidden_text_is_withheld(self):
  sent=self.call('/messages',{'room':'commons','body':'A message for review.'},self.alice)
  self.call('/reports',{'message_id':sent['id'],'reason':'Please review this particular message.'},self.bob)
  self.assertEqual(self.call('/me',person=self.alice)['user']['timeout_until'],0)
  self.denied(403,'/moderation',person=self.bob)
  report=self.call('/moderation',person=self.owner)['reports'][0]
  self.assertEqual(report['body'],'A message for review.')
  self.call('/moderation',{'action':'hide','message_id':sent['id'],'reason':'Removed following a human review.'},self.owner)
  message=self.call('/messages',query={'room':['commons']})['messages'][0]
  self.assertEqual(message['body'],'[Removed by moderation]')

 def test_session_revocation_hashing_and_restart(self):
  with self.store.connect() as db:
   row=db.execute('SELECT password_hash FROM users WHERE username=\'Alice\'').fetchone()
   self.assertNotIn('a test passphrase',row[0])
   hashes=[r[0] for r in db.execute('SELECT token_hash FROM sessions')]
   self.assertNotIn(self.alice['token'],hashes)
  self.call('/messages',{'room':'commons','body':'Persists across service restarts.'},self.alice)
  self.store=module.Store(self.store.path,lambda:self.now)
  self.assertEqual(len(self.call('/messages',query={'room':['commons']})['messages']),1)
  self.call('/auth/logout',{},self.alice)
  self.denied(401,'/messages',{'room':'commons','body':'Not signed in.'},self.alice)

 def test_failed_auth_rate_limit_persists(self):
  for _ in range(57):
   self.denied(401,'/auth/login',{'username':'Nobody','password':'wrong'})
  self.denied(429,'/auth/login',{'username':'Nobody','password':'wrong'})

 def test_password_change_revokes_other_sessions(self):
  second=self.call('/auth/login',{'username':'Alice','password':'a test passphrase with spaces'})
  changed=self.call('/me/password',{'current':'a test passphrase with spaces','password':'the new long passphrase'},self.alice)
  self.assertIsNone(self.call('/me',person=second)['user'])
  self.assertEqual(self.call('/me',person=changed)['user']['username'],'Alice')

 def test_concurrent_sends_rate_limit_without_partial_writes(self):
  def send(i):
   try:self.call('/messages',{'room':'game-lobby','body':f'Message {i}'},self.alice);return True
   except module.APIError as e:self.assertEqual(e.status,429);return False
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
   results=list(pool.map(send,range(15)))
  self.assertEqual(sum(results),10)
  self.assertEqual(len(self.call('/messages',query={'room':['game-lobby']})['messages']),10)

 def test_http_origins_and_private_files(self):
  server=module.Server(('127.0.0.1',0),module.Handler);server.store=self.store;server.allowed_origins={'https://rmichaelglover.github.io'}
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_port)
  try:
   with urllib.request.urlopen(urllib.request.Request(base+'/api/v1/health',headers={'Origin':'https://rmichaelglover.github.io'})) as response:
    self.assertEqual(response.headers['Access-Control-Allow-Origin'],'https://rmichaelglover.github.io');self.assertTrue(json.load(response)['ok'])
   for path in ('/backend/server.py','/../backend/schema.sql','/forum.sqlite3'):
    with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(base+path)
    self.assertEqual(ctx.exception.code,404)
   with self.assertRaises(urllib.error.HTTPError) as ctx:
    urllib.request.urlopen(urllib.request.Request(base+'/api/v1/health',headers={'Origin':'https://evil.example'}))
   self.assertEqual(ctx.exception.code,403)
  finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
