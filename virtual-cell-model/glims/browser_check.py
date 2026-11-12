import subprocess,time,json,urllib.request,websocket,base64
from pathlib import Path
chrome=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=http://localhost:9258','--remote-debugging-port=9258','--user-data-dir=/tmp/glims-browser','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
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
 call('Page.navigate',{'url':(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'http://127.0.0.1:8788/virtual-cell-model/glims/')})
 for _ in range(70):
  if js("!!window.alexWorld && !!document.querySelector(\"#show-tracker\")"):break
  time.sleep(.1)
 assert js('!!window.glimsWorld'),'Glims did not initialize'
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
 assert js('document.title.includes("Glims")')
 for _ in range(50):
  if js('glimsWorld.learningInfo().loaded===100'):break
  time.sleep(.1)
 assert js('glimsWorld.learningInfo().loaded')==100
 assert js('glimsWorld.learningInfo().lastLoss')<.04
 js('glimsWorld.reset();glimsWorld.act("nap");glimsWorld.step(30)')
 assert js('glimsWorld.getState().energy')>.9
 js('glimsWorld.reset();glimsWorld.act("work");glimsWorld.step(30)')
 assert js('glimsWorld.getState().wishes.learning')
 assert js('glimsWorld.learningInfo().step')==100
 js('glimsWorld.reset();glimsWorld.act("listen");glimsWorld.enqueueAction("lyrics");glimsWorld.enqueueAction("nap")')
 assert js('glimsWorld.getState().queue.length')==2
 js('glimsWorld.step(80)')
 assert js('glimsWorld.getState().queue.length')==0
 assert js('glimsWorld.getState().wishes.music')
 assert js('glimsWorld.getState().lyrics')>.1
 js('glimsWorld.reset();glimsWorld.act("cypher");glimsWorld.step(30)')
 assert js('glimsWorld.getState().connection')>.4
 assert js('glimsWorld.getState().residents.cypher.happiness')>.65
 js('glimsWorld.reset();glimsWorld.step(19);glimsWorld.act("rosy")')
 assert js('glimsWorld.getState().residents.rosy.occupied')
 assert js('glimsWorld.getState().action') is None
 js('glimsWorld.reset();document.querySelector("#mantra").click();glimsWorld.saveEvening();glimsWorld.reset();glimsWorld.loadEvening()')
 assert js('glimsWorld.getState().mantras')==1
 assert js('glimsWorld.getState().queue.length')==0
 js('localStorage.setItem("glover-machine-works-glims-evening-v1","{broken")')
 assert js('glimsWorld.loadEvening()')==False
 assert js('glimsWorld.getState().mantras')==1
 js('document.querySelector("#speed").click()');assert js('glimsWorld.getState().speed')==2
 js('document.querySelector("#speed").click()');assert js('glimsWorld.getState().speed')==4
 js('glimsWorld.reset();document.querySelector("#autonomy").click();glimsWorld.step(70)')
 assert js('Math.hypot(glimsWorld.getState().residents.cypher.x-4.8,glimsWorld.getState().residents.cypher.z-4.8)')>.1
 js('glimsWorld.reset();document.querySelector("#paint-together").click();glimsWorld.step(40)')
 assert js('glimsWorld.getState().wishes.creative'),'Painting did not complete'
 assert js('new Set(glimsWorld.getState().artworks.map(a=>a.author)).size')==5,'Family gallery lacks an artist'
 assert js('document.querySelector("#mama-pastime").textContent.includes("Painting")')
 js('document.querySelector("#read-together").click();glimsWorld.step(30)')
 assert js('glimsWorld.getState().booksRead')>=1
 assert js('document.querySelector("#mama-pastime").textContent.includes("book")')
 js('document.querySelector("#tv-toggle").click()');assert js('glimsWorld.getState().tvOn')
 js('glimsWorld.saveEvening();glimsWorld.reset();glimsWorld.loadEvening()')
 assert js('glimsWorld.getState().artworks.length')==5
 assert js('glimsWorld.getState().booksRead')>=1
 assert js('glimsWorld.getState().tvOn')
 js('glimsWorld.reset();glimsWorld.act("mama");glimsWorld.step(30)')
 assert js('glimsWorld.getState().journal.some(a=>a.text.includes("finish a page"))')
 js('glimsWorld.reset();glimsWorld.turn(Math.atan2(3.65-3.2,.85-4.9))')
 assert js('glimsWorld.visibleNames().includes("mama")'),'Mama missing from the visual field'
 js('glimsWorld.reset();glimsYard.enter()')
 assert js('glimsYard.getState().active')
 assert js('glimsYard.wildlife().length')==8
 assert js('document.querySelectorAll("[data-wildlife]").length')==8
 js('document.querySelector("[data-wildlife=skink]").click()')
 assert js('document.querySelector("#wildlife-note").textContent.includes("blue tail")')
 fish=js('glimsYard.wildlife().find(a=>a.id==="fish")')
 assert abs(fish['x']-(7.45+__import__('math').sin(fish['y']*1.25)*.38))<.62

 assert js('document.querySelector(".world-shell").hidden')
 assert not js('glimsYard.walkable(7.45+Math.sin(1.25)*.38,1)')
 assert js('glimsYard.walkable(7.1,3.7)')
 assert js('glimsYard.go("bridge")')
 js('glimsYard.step(30)')
 assert js('glimsYard.getState().people[0].x')>8.5,'Bridge crossing failed'
 assert js('glimsYard.getState().completed')
 js('glimsYard.go("paint");glimsYard.step(40)')
 assert js('glimsWorld.getState().wishes.creative')
 js('glimsYard.go("read");glimsYard.step(35)')
 assert js('glimsWorld.getState().booksRead')>=1
 js('if(!glimsYard.getState().night)document.querySelector("#yard-night").click();document.querySelector("#yard-save").click()')
 assert js('glimsYard.getState().night')
 js('glimsYard.leave();glimsYard.load();glimsYard.enter()')
 assert js('glimsYard.getState().night')
 js('document.querySelector("#yard-pause").click()')
 before=js('glimsYard.getState().time');js('glimsYard.step(5)');assert js('glimsYard.getState().time')==before
 js('document.querySelector("#yard-pause").click()')
 for width in [320,390,720,1000,1440]:
  call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1100,'deviceScaleFactor':1,'mobile':width<721});time.sleep(.2)
  assert js('document.documentElement.scrollWidth<=innerWidth'),f'Yard overflow at {width}'
  if width in [390,1440]:
   js('document.querySelector("#glackyard").scrollIntoView()');time.sleep(.1)
   data=call('Page.captureScreenshot',{'format':'png'})['data'];Path(f'/tmp/glims-glackyard-{width}.png').write_bytes(base64.b64decode(data))
 js('glimsYard.leave();glimsWorld.reset();document.querySelector("#paint-together").click();glimsWorld.step(40);document.querySelector("#tv-toggle").click()')
 for width in [320,390,720,1000,1440]:
  call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1100,'deviceScaleFactor':1,'mobile':width<721});time.sleep(.2)
  assert js('document.documentElement.scrollWidth<=innerWidth'),f'Overflow at {width}'
  assert js('document.querySelector("#room").width>0')
  if width in [390,1440]:
   data=call('Page.captureScreenshot',{'format':'png'})['data'];Path(f'/tmp/glims-world-{width}.png').write_bytes(base64.b64decode(data))
 js('glimsWorld.act("work");glimsWorld.step(30);document.querySelector(".learning-workbench").scrollIntoView()')
 data=call('Page.captureScreenshot',{'format':'png'})['data'];Path('/tmp/glims-workbench-1440.png').write_bytes(base64.b64decode(data))
 assert not errors,errors
 print('PASS: Glackyard bridge routing, glamping, shared art/reading progress, night, pause/save/load, outdoor responsive layouts; Glims households, queue, wishes, naps, NPC autonomy and replies, C++ trace replay, local save/load, speed, initialization, pause, visual field, route/collision, eating, independent practice, family replies, music permission, mantra, keyboard motion, autonomy, reset, five viewport widths and no runtime exceptions.')
 ws.close()
finally:
 chrome.terminate();chrome.wait(timeout=10)
