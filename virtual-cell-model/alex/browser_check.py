import subprocess,time,json,urllib.request,websocket,base64
from pathlib import Path
chrome=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=http://localhost:9258','--remote-debugging-port=9258','--user-data-dir=/tmp/alex-world-browser','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(70):
  try:pages=json.load(urllib.request.urlopen('http://localhost:9258/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(next(x for x in pages if x.get('type')=='page')['webSocketDebuggerUrl'],origin='http://localhost:9258');seq=0;errors=[]
 def call(method,params=None):
  global seq
  seq+=1;ws.send(json.dumps({'id':seq,'method':method,'params':params or {}}))
  while True:
   r=json.loads(ws.recv())
   if r.get('method')=='Runtime.exceptionThrown':errors.append(r)
   if r.get('id')==seq:
    if 'error' in r:raise RuntimeError(r['error'])
    return r.get('result',{})
 def js(s):
  r=call('Runtime.evaluate',{'expression':s,'returnByValue':True})
  if r.get('exceptionDetails'):raise RuntimeError(r['exceptionDetails'])
  return r['result'].get('value')
 call('Network.enable');call('Network.setCacheDisabled',{'cacheDisabled':True});call('Runtime.enable');call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1100,'deviceScaleFactor':1,'mobile':False})
 call('Page.navigate',{'url':(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'http://127.0.0.1:8788/virtual-cell-model/alex/')})
 for _ in range(70):
  if js("!!window.alexWorld && !!document.querySelector(\"#show-tracker\")"):break
  time.sleep(.1)
 assert js('!!window.alexWorld'),'World did not initialize'
 js("document.querySelector('#pause').click()")
 snapshot=js('JSON.stringify(alexWorld.getState())');js("document.querySelector('#show-tracker').click()");assert js('JSON.stringify(alexWorld.getState())')==snapshot
 before=js('alexWorld.getState().time');time.sleep(.25);assert js('alexWorld.getState().time')==before
 js('alexWorld.reset()')
 names=js('alexWorld.visibleNames()');js('alexWorld.turn(.4)');assert js('alexWorld.visibleNames()')!=names
 js('alexWorld.reset();alexWorld.act("eat");alexWorld.step(30)')
 assert js('alexWorld.getState().hunger')<.1
 assert js('alexWorld.free(alexWorld.getState().x,alexWorld.getState().z)')
 assert not js('alexWorld.walkTo(6.9,.85)'),'Furniture accepted as walk target'
 js('alexWorld.reset();alexWorld.act("lyrics");alexWorld.step(30)')
 assert js('alexWorld.getState().lyrics')>.1
 assert js('alexWorld.getState().guitar')==.85
 js('alexWorld.reset();alexWorld.act("papa");alexWorld.step(30)')
 assert js('alexWorld.getState().connection')==.4
 assert js('alexWorld.getState().journal.some(x=>x.text.includes("preferred quiet"))')
 js("document.querySelector('#household').value='social';document.querySelector('#household').dispatchEvent(new Event('change'));alexWorld.act('papa');alexWorld.step(30)")
 assert js('alexWorld.getState().connection')>.4
 js("document.querySelector('#sing').click()")
 assert js('alexWorld.getState().musicPermission')==False
 js("document.querySelector('#household').value='music';document.querySelector('#household').dispatchEvent(new Event('change'));document.querySelector('#sing').click();alexWorld.step(30)")
 assert js('alexWorld.getState().voice')>.3
 js("document.querySelector('#mantra').click()")
 assert js('alexWorld.getState().mantras')==1
 js('alexWorld.reset();alexWorld.walkTo(4,4.8);alexWorld.step(10)')
 assert abs(js('alexWorld.getState().x')-4)<.01
 js('alexWorld.reset();document.getElementById("room").focus();document.dispatchEvent(new KeyboardEvent("keydown",{key:"w"}));alexWorld.step(.4);document.dispatchEvent(new KeyboardEvent("keyup",{key:"w"}))')
 assert js('Math.hypot(alexWorld.getState().x-3.2,alexWorld.getState().z-4.9)')>.1
 js("alexWorld.reset();document.querySelector('#autonomy').click();alexWorld.step(90)")
 assert js('alexWorld.getState().journal.length')>=3
 assert js('alexWorld.getState().autonomy')
 assert js('alexWorld.free(alexWorld.getState().x,alexWorld.getState().z)')
 js('alexWorld.reset()')
 for width in [320,390,720,1000,1440]:
  call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1100,'deviceScaleFactor':1,'mobile':width<721});time.sleep(.2)
  assert js('document.documentElement.scrollWidth<=innerWidth'),f'Overflow at {width}'
  assert js('document.querySelector("#room").width>0')
  if width in [390,1440]:
   data=call('Page.captureScreenshot',{'format':'png'})['data'];Path(f'/tmp/alex-world-{width}.png').write_bytes(base64.b64decode(data))
 assert not errors,errors
 print('PASS: initialization, pause, visual field, route/collision, eating, independent practice, family replies, music permission, mantra, keyboard motion, autonomy, reset, five viewport widths and no runtime exceptions.')
 ws.close()
finally:
 chrome.terminate();chrome.wait(timeout=10)
