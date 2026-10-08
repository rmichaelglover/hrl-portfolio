import subprocess,time,json,urllib.request,websocket,base64
p=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--remote-allow-origins=http://localhost:9247','--remote-debugging-port=9247','--user-data-dir=/tmp/hrl-lab-browser','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(50):
  try:pages=json.load(urllib.request.urlopen('http://localhost:9247/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(next(x for x in pages if x.get('type')=='page')['webSocketDebuggerUrl'],origin='http://localhost:9247');seq=0
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
 call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1100,'deviceScaleFactor':1,'mobile':False})
 call('Page.navigate',{'url':__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'http://127.0.0.1:8769/hrl-lab/'})
 for _ in range(70):
  if js("document.readyState==='complete' && document.querySelector('#strengthRows').children.length===5"):break
  time.sleep(.1)
 assert js("document.querySelector('#strengthRows').children.length") == 5
 js("paused=true;mnistState.S=mnistState.prior.map(r=>r.slice());initializeRun()")
 assert js('iteration') == 0
 assert js('score().tied') == 35
 js("document.querySelector('#mnistStep').click()")
 assert js('iteration') == 1
 assert js('trace.maxDelta>0')
 assert js("document.querySelector('#traceCaption').textContent.includes('0 → 1')")
 assert js('Math.abs(trace.after[1].reduce((a,b)=>a+b,0)-1)<1e-12')
 js("document.querySelector('#digitSelect').value='17';document.querySelector('#digitSelect').dispatchEvent(new Event('change'))")
 assert js('selectedSample') == 17
 assert js("document.querySelector('#inspectSummary').textContent.includes('Sample #18')")
 js("document.querySelector('#neighborList button').click()")
 assert js('selectedSample') != 17
 seeds=js('[...mnistSeeds]')
 js("document.querySelector('#mnistReset').click()")
 assert js('iteration') == 0 and js('[...mnistSeeds]') == seeds
 js('advance();advance()')
 assert js('history.length') == 3
 js("document.querySelector('#mnistNew').click()")
 assert js('history.length') == 1 and js('mnistSeeds.size') == 5
 for width in [320,390,720,820,821,1280]:
  call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1100,'deviceScaleFactor':1,'mobile':width<821})
  js('drawInspector()')
  assert js('document.documentElement.scrollWidth<=innerWidth'),width
  assert js('document.querySelector("#mnist").width>0'),width
  if width==1280:
   assert js("Math.abs(document.querySelectorAll('.digit-layout>section')[0].getBoundingClientRect().top-document.querySelectorAll('.digit-layout>section')[1].getBoundingClientRect().top)<1")
   js("selectedSample=1;for(let k=0;k<5;k++)advance();document.querySelector('#digit-lab').scrollIntoView()")
   data=call('Page.captureScreenshot',{'format':'png'})['data'];open('/tmp/hrl-lab-desktop.png','wb').write(base64.b64decode(data))
 js('while(!settled && iteration<MAX_STEPS)advance()')
 assert js('settled')
 assert js("document.querySelector('#fieldMetrics').textContent.includes('Numerically stable')")
 assert js("document.querySelector('#mnistStep').disabled")
 assert js('history.length===iteration+1')
 js("document.querySelector('#mnistReset').click();document.querySelector('#mnistPause').click()")
 start=js('iteration');time.sleep(.8);assert js('iteration')>start
 js("document.querySelector('#mnistPause').click()")
 start=js('iteration');time.sleep(.8);assert js('iteration')==start
 call('Emulation.setDeviceMetricsOverride',{'width':390,'height':1100,'deviceScaleFactor':1,'mobile':True})
 js("drawInspector();document.querySelector('#digit-lab').scrollIntoView()")
 data=call('Page.captureScreenshot',{'format':'png'})['data'];open('/tmp/hrl-lab-mobile.png','wb').write(base64.b64decode(data))
 print('PASS: browser controls, selection, neighbors, reset, baseline, convergence stop, pause/resume, side-by-side desktop and six responsive widths.')
 ws.close()
finally:p.terminate();p.wait(timeout=10)
