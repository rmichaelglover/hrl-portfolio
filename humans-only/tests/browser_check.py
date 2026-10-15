"""Local browser integration check; all test accounts/posts use a disposable DB."""
import base64
import importlib.util
import json
import logging
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request
import websocket

spec=importlib.util.spec_from_file_location('humansonly',Path(__file__).resolve().parents[1]/'backend/server.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def main():
 logging.basicConfig(level=logging.INFO)
 with tempfile.TemporaryDirectory(prefix='humansonly-browser-') as temp:
  store=module.Store(Path(temp)/'forum.db')
  server=module.Server(('127.0.0.1',8788),module.Handler);server.store=store
  origin='http://127.0.0.1:'+str(server.server_port);server.allowed_origins={origin}
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  with urllib.request.urlopen(origin+'/') as response:
   assert response.status==200
   assert response.headers.get_content_type()=='text/html',response.headers
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  browser=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--no-first-run','--no-default-browser-check','--no-proxy-server',f'--remote-debugging-port={port}',f'--user-data-dir={temp}/chrome',origin+'/'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  ws=None
  try:
   for _ in range(100):
    try:
     with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as response:tabs=json.load(response)
     tabs=[tab for tab in tabs if tab.get('type')=='page' and tab.get('url','').startswith(origin)]
     if tabs:break
    except Exception:time.sleep(.1)
   else:raise AssertionError('Chrome did not start')
   ws=websocket.create_connection(tabs[0]['webSocketDebuggerUrl'],suppress_origin=True,timeout=10)
   counter=0
   events=[]
   def command(method,params=None):
    nonlocal counter
    counter+=1;ws.send(json.dumps({'id':counter,'method':method,'params':params or {}}))
    while True:
     reply=json.loads(ws.recv())
     if reply.get('method') in ('Runtime.exceptionThrown','Log.entryAdded'):events.append(reply)
     if reply.get('id')==counter:
      assert 'error' not in reply,reply
      return reply.get('result',{})
   def js(expression):
    r=command('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
    assert 'exceptionDetails' not in r,r
    return r.get('result',{}).get('value')
   def wait(expression):
    for _ in range(100):
     if js(expression):return
     time.sleep(.1)
    raise AssertionError('Timed out: '+expression+'\n'+str(js('({url:location.href,html:document.documentElement.outerHTML})'))+'\n'+str(events))
   command('Page.enable');command('Runtime.enable');command('Log.enable')
   wait("document.getElementById('connection')?.dataset.state==='online'")
   js("document.getElementById('account-button').click();document.getElementById('join-tab').click();document.getElementById('username').value='BrowserPerson';document.getElementById('password').value='a browser test passphrase';document.getElementById('age-group').value='18-20';document.getElementById('human').checked=true;document.getElementById('accept').checked=true;document.getElementById('auth-form').requestSubmit()")
   wait("document.getElementById('account-button').textContent==='@BrowserPerson'&&!document.getElementById('account').open")
   js("document.getElementById('message-body').value='<img src=x onerror=alert(1)> is plain text';document.getElementById('compose').requestSubmit()")
   wait("document.getElementById('messages').textContent.includes('<img src=x')")
   assert js("document.querySelectorAll('#messages img').length===0")
   js("document.getElementById('new-topic').click();document.getElementById('new-title').value='Browser integration topic';document.getElementById('new-body').value='Opening post from the browser test.';document.getElementById('topic-form').requestSubmit()")
   wait("document.getElementById('topic-title').textContent==='Browser integration topic'&&!document.getElementById('topic-dialog').open")
   wait("document.getElementById('messages').textContent.includes('Opening post')")
   command('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
   assert js('document.documentElement.scrollWidth<=innerWidth'),js('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
   command('Page.navigate',{'url':origin+'/'})
   wait("document.getElementById('connection')?.dataset.state==='online'")
   screenshot=command('Page.captureScreenshot',{'format':'png'})['data']
   Path('/tmp/humansonly-mobile.png').write_bytes(base64.b64decode(screenshot))
   command('Emulation.setDeviceMetricsOverride',{'width':1360,'height':1000,'deviceScaleFactor':1,'mobile':False})
   time.sleep(.2)
   Path('/tmp/humansonly-desktop.png').write_bytes(base64.b64decode(command('Page.captureScreenshot',{'format':'png'})['data']))
   command('Page.navigate',{'url':origin+'/game-chat.html'})
   wait("document.getElementById('game-widget')?.contentDocument?.getElementById('connection')?.dataset.state==='online'")
   js("(()=>{const d=document.getElementById('game-widget').contentDocument;d.getElementById('message-body').value='Shared game backend is working.';d.getElementById('compose').requestSubmit()})()")
   wait("document.getElementById('game-widget').contentDocument.getElementById('messages').textContent.includes('Shared game backend is working.')")
   assert store.handle('GET','/messages',{'room':['game-lobby']},{})['messages'][0]['body']=='Shared game backend is working.'
   print('PASS: real browser registration, sign-in, safe text rendering, topic creation, 390px layout, and in-game chat persistence. Screenshots: /tmp/humansonly-{mobile,desktop}.png')
  finally:
   if ws:ws.close()
   browser.terminate();browser.wait(timeout=10);server.shutdown();server.server_close();thread.join()

if __name__=='__main__':main()
