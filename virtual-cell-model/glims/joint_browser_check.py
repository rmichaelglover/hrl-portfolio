import subprocess,time,json,urllib.request,websocket,base64
from pathlib import Path
chrome=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=http://localhost:9278','--remote-debugging-port=9278','--user-data-dir=/tmp/glims-cpp-joint-check','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(70):
  try:pages=json.load(urllib.request.urlopen('http://localhost:9278/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(next(x for x in pages if x.get('type')=='page')['webSocketDebuggerUrl'],origin='http://localhost:9278');seq=0;errors=[]
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
 call('Runtime.enable');call('Network.enable');call('Network.setCacheDisabled',{'cacheDisabled':True})
 url=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'http://127.0.0.1:8788/virtual-cell-model/glims/'
 call('Page.navigate',{'url':url})
 for _ in range(100):
  if js('!!window.glimsWorld&&!!window.glimsYard&&GlimsMotion.loaded()'):break
  time.sleep(.1)
 assert js('GlimsMotion.loaded()'),'C++ kernel failed to load'
 assert js('GlimsMotion.status().profile.plies')==180
 js('glimsWorld.reset();glimsWorld.act("roses");glimsWorld.step(30)')
 assert js('GlimsMotion.status().rosePauses')>=1,'Indoor rose moment missing'
 js('glimsWorld.reset();glimsYard.enter();glimsYard.go("bridge")')
 result=js("""(()=>{let peopleMin=100,frogMin=100,moved=0;for(let turn=0;turn<700;turn++){const a=glimsYard.getState(),frogA=glimsYard.wildlife().find(p=>p.id==='frog');glimsYard.step(.05);const b=glimsYard.getState(),frogB=glimsYard.wildlife().find(p=>p.id==='frog');if(b.time===a.time)continue;for(let i=0;i<a.people.length;i++){const p=a.people[i],q=b.people[i],v={x:p.x,z:p.y},w={x:q.x,z:q.y};moved+=Math.hypot(v.x-w.x,v.z-w.z);frogMin=Math.min(frogMin,GlimsMotion.swept(v,w,{x:frogA.x,z:frogA.y},{x:frogB.x,z:frogB.y}));for(let j=0;j<i;j++)peopleMin=Math.min(peopleMin,GlimsMotion.swept(v,w,{x:a.people[j].x,z:a.people[j].y},{x:b.people[j].x,z:b.people[j].y}));}}return {peopleMin,frogMin,moved,people:glimsYard.getState().people.map(p=>({name:p.name,x:p.x,left:p.path.length})),completed:glimsYard.getState().completed};})()""")
 assert result['peopleMin']>=.43-1e-7,result
 assert result['frogMin']>=.4-1e-7,result
 assert result['completed'] and all(p['left']==0 for p in result['people']),result
 js('glimsYard.go("roses");glimsYard.step(50)')
 assert js('glimsYard.getState().completed'),'Garden rose gathering failed'
 assert js('glimsYard.getState().people.filter(p=>p.roseVisited).length')>=3
 assert js('GlimsMotion.status().engine.includes("C++")')
 print('Live C++ browser checks passed: 180-ply profile, indoor roses, all five bridge arrivals, 700 turns of swept person/frog clearance, and shared outdoor roses.')
 print(json.dumps(result))
 assert not errors,errors
finally:
 chrome.terminate();chrome.wait(timeout=10)
