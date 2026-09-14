import subprocess,time,json,urllib.request,websocket,base64
p=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=http://localhost:9238','--remote-debugging-port=9238','--user-data-dir=/tmp/capture-tutor-browser','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(50):
  try:pages=json.load(urllib.request.urlopen('http://localhost:9238/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(next(x for x in pages if x.get('type')=='page')['webSocketDebuggerUrl'],origin='http://localhost:9238');seq=0
 def call(method,params={}):
  global seq
  seq+=1;ws.send(json.dumps({'id':seq,'method':method,'params':params}))
  while True:
   r=json.loads(ws.recv())
   if r.get('id')==seq:return r.get('result',{})
 def js(s):
  r=call('Runtime.evaluate',{'expression':s,'returnByValue':True})
  if r.get('exceptionDetails'):raise Exception(r['exceptionDetails'])
  return r['result'].get('value')
 call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1200,'deviceScaleFactor':1,'mobile':False})
 call('Network.enable')
 call('Network.setCacheDisabled',{'cacheDisabled':True})
 call('Page.navigate',{'url':'http://127.0.0.1:8766/capture-tutor/'})
 for _ in range(50):
  if js("document.readyState==='complete' && !!document.querySelector('#board .square')"):break
  time.sleep(.1)
 assert js("document.querySelectorAll('#board .square').length") == 64
 for width in [320,390,720,721,850,1280]:
  call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<721})
  for lesson in range(6):
   for flip in [False,True]:
    for state in range(3):
     js(f'start(lessons[{lesson}]);flipped={str(flip).lower()};frame={state};drawBoard()')
     geometry=js("(()=>{const cells=[...document.querySelectorAll('#board .square')].map(e=>e.getBoundingClientRect());return {count:cells.length,error:Math.max(...cells.map(r=>Math.abs(r.width-r.height))),spread:Math.max(...cells.map(r=>r.height))-Math.min(...cells.map(r=>r.height)),overflow:document.documentElement.scrollWidth>innerWidth}})()")
     assert geometry['count']==64 and geometry['error']<1 and geometry['spread']<1 and not geometry['overflow'],(width,lesson,flip,state,geometry)
 assert js("[...document.querySelectorAll('#board .square')].find(e=>e.title.startsWith('a1 ')).classList.contains('dark')")
 assert js("![...document.querySelectorAll('#board .square')].find(e=>e.title.startsWith('h1 ')).classList.contains('dark')")
 print('PASS: square geometry across 216 viewport/lesson/orientation/replay combinations.')
 call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1200,'deviceScaleFactor':1,'mobile':False})

 js("records=[];save();start(lessons[0]);$('answers').children[1].click();$('answers').children[0].click();")
 assert js("phase==='feedback' && records.length===1 && records[0].decision && records[0].prediction")
 assert js("$('line').textContent.includes('Re1#')")
 js("$('back').click();$('back').click()")
 assert js('frame')==0
 js("$('next').click();$('hint').click();$('answers').children[1].click();$('answers').children[current.answer].click()")
 assert js('records[1].hinted')
 call('Page.reload')
 time.sleep(.5)
 assert js('records.length')==2
 js('start(lessons[4])')
 assert js("document.documentElement.scrollWidth<=innerWidth")
 data=call('Page.captureScreenshot',{'format':'png'})['data'];open('/tmp/capture-tutor-desktop.png','wb').write(base64.b64decode(data))
 call('Emulation.setDeviceMetricsOverride',{'width':390,'height':1000,'deviceScaleFactor':1,'mobile':True})
 time.sleep(.2)
 assert js('document.documentElement.scrollWidth<=innerWidth')
 js("$('answers').children[0].click();$('answers').children[2].click()")
 assert js("phase==='feedback' && records.find(r=>r.id===current.id).decision")
 data=call('Page.captureScreenshot',{'format':'png'})['data'];open('/tmp/capture-tutor-mobile.png','wb').write(base64.b64decode(data))
 print('PASS: real browser rendering, complete answer flow, mate replay, hint tracking, persistent reload, 390px layout, safe-capture feedback.')

 if '--share-card' in __import__('sys').argv:
  call('Emulation.setDeviceMetricsOverride',{'width':1200,'height':630,'deviceScaleFactor':1,'mobile':False})
  js("start(lessons[0]);window.scrollTo(0,0);const style=document.createElement('style');style.textContent='body{width:1200px;height:630px;max-width:none;padding:0;overflow:hidden}header{position:absolute;left:48px;top:55px;width:510px;margin:0}header h1{font-size:76px}header .intro{font-size:20px}main{position:absolute;right:38px;top:24px;width:540px}.layout{display:block}.lesson-panel,.panel,footer,.controls,#positionLabel,#line{display:none}.board-panel{padding:18px}.board-heading button{display:none}';document.head.append(style)")
  time.sleep(.2)
  data=call('Page.captureScreenshot',{'format':'png'})['data']
  from pathlib import Path
  (Path(__file__).resolve().parents[1]/'assets/social/capture-tutor--index.png').write_bytes(base64.b64decode(data))
 ws.close()
finally:p.terminate();p.wait(timeout=10)
