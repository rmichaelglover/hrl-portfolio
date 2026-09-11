"""Render 1200x630 Open Graph cards from live local views and existing artwork.
Requires Chrome and Python websocket-client; no image-generation service.
"""
from pathlib import Path
import base64,html,json,subprocess,time,urllib.request,sys
import websocket
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/social';SOURCE=OUT/'source';SOURCE.mkdir(exist_ok=True)
proc=subprocess.Popen(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--allow-file-access-from-files','--remote-allow-origins=http://localhost:9236','--remote-debugging-port=9236','--user-data-dir=/tmp/hrl-social-chrome','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 for _ in range(100):
  try:pages=json.load(urllib.request.urlopen('http://localhost:9236/json'));break
  except Exception:time.sleep(.1)
 ws=websocket.create_connection(next(page for page in pages if page.get('type')=='page')['webSocketDebuggerUrl'],origin='http://localhost:9236',timeout=30);seq=0
 def call(method,params=None):
  global seq
  seq+=1;ws.send(json.dumps({'id':seq,'method':method,'params':params or {}}))
  while True:
   msg=json.loads(ws.recv())
   if msg.get('id')==seq:
    if 'error' in msg:raise RuntimeError(msg['error'])
    return msg.get('result',{})
 def js(expr):
  r=call('Runtime.evaluate',{'expression':expr,'returnByValue':True,'awaitPromise':True})
  if 'exceptionDetails' in r:raise RuntimeError(r['exceptionDetails'])
  return r.get('result',{}).get('value')
 def navigate(rel):
  call('Page.navigate',{'url':(ROOT/rel).as_uri()})
  for _ in range(100):
   if js('location.href')==(ROOT/rel).as_uri() and js('document.readyState')=='complete':break
   time.sleep(.05)
  time.sleep(.15)
 def capture(path,clip=None):
  args={'format':'png','captureBeyondViewport':True}
  if clip:args['clip']=dict(clip,scale=1)
  path.write_bytes(base64.b64decode(call('Page.captureScreenshot',args)['data']))
 call('Emulation.setDeviceMetricsOverride',{'width':1200,'height':1000,'deviceScaleFactor':1,'mobile':False})
 navigate('hyperobject/index.html')
 js("$('hud').style.display='none';$('field').style.height='630px';$('view').value='mono';$('side').value=0;$('yaw').value=0;choose([0,2,4,5,7,9,11,12]);moving=false;visualTime=.002;drawField();")
 rect=js("(()=>{const r=$('field').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
 capture(SOURCE/'sound-field.png',rect)
 navigate('cellular-complexes/index.html');js("$('rule').value='cyclic';reset();for(let i=0;i<7;i++)advance();")
 rect=js("(()=>{const r=document.querySelector('.panels').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
 capture(SOURCE/'cellular-complexes.png',rect)
 navigate('projective-resolution/index.html')
 rect=js("(()=>{const r=document.querySelector('.views').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
 capture(SOURCE/'projective-resolution.png',rect)
 navigate('wave-worlds/index.html');js("setPaused(true);visualTime=.004;choose([0,2,4,5,7,9,11,12]);render();")
 rect=js("(()=>{const r=$('worlds').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
 capture(SOURCE/'wave-worlds.png',rect)
 manifest=json.loads((ROOT/'tools/social-manifest.json').read_text())
 call('Emulation.setDeviceMetricsOverride',{'width':1200,'height':630,'deviceScaleFactor':1,'mobile':False})
 rendered=0
 for index,item in enumerate(manifest):
  if len(sys.argv)>1 and item['key'] not in sys.argv[1:]:continue
  key=item['key'];title=html.escape(item['title']);desc=html.escape(item['description'])
  special=SOURCE/(key+'.png')
  art=special if special.exists() else ROOT/item['artwork'] if item['artwork'] else None
  if key=='portfolio':
   graphic='<div class="mosaic">'+''.join('<img src="'+(ROOT/'assets/thumbs'/name).as_uri()+'">' for name in ['sdss.png','brain.png','simplicial.png','world.png'])+'</div>'
  elif art:graphic='<img class="art" src="'+art.as_uri()+'">'
  else:graphic='''<svg viewBox="0 0 600 560"><defs><radialGradient id="g"><stop stop-color="#183d58"/><stop offset="1" stop-color="#071422"/></radialGradient></defs><rect width="600" height="560" fill="url(#g)"/><g fill="none" stroke="#78e4c5" stroke-width="2"><path d="M100 400 L300 70 L510 400 Z M100 400 L300 510 L510 400 M300 70 L300 510 M100 400 L400 230 L300 510 L200 230 L510 400"/><circle cx="300" cy="280" r="180" stroke="#7a8eef"/></g><g fill="#ffcf83"><circle cx="100" cy="400" r="9"/><circle cx="300" cy="70" r="9"/><circle cx="510" cy="400" r="9"/><circle cx="300" cy="510" r="9"/></g></svg>'''
  full=key=='sound-field'
  style='''*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:#08111f;color:#eef5ff;font-family:Arial,sans-serif;overflow:hidden}.frame{position:relative;width:1200px;height:630px;border:2px solid #28465d}.copy{position:absolute;left:55px;top:68px;width:495px;z-index:2}.brand{font-size:17px;letter-spacing:4px;color:#83e7cc}h1{font-size:46px;line-height:1.08;margin:26px 0 20px;max-height:206px;overflow:hidden}p{font-size:22px;line-height:1.4;color:#bfcede}.foot{position:absolute;left:55px;bottom:40px;font-size:17px;color:#8dacbf;z-index:2}.visual{position:absolute;right:25px;top:25px;width:555px;height:550px;overflow:hidden;border-radius:20px}.art{width:100%;height:100%;object-fit:contain}.mosaic{display:grid;grid-template-columns:1fr 1fr;gap:12px;height:100%}.mosaic img{width:100%;height:100%;min-height:0;object-fit:cover;border-radius:12px}svg{width:100%;height:100%}'''
  if key=='wave-worlds':style+=' .copy{top:28px;width:1090px}h1{font-size:46px;margin:14px 0}p{font-size:20px;margin:8px 0}.visual{left:55px;top:220px;width:1090px;height:350px}.foot{bottom:18px}'
  if full:style+='''.visual{inset:0;width:1200px;height:630px;border-radius:0}.art{object-fit:cover}.copy{top:42px;width:1090px}h1{font-size:52px;margin:14px 0}p{font-size:21px;max-width:950px}.foot{left:0;bottom:0;width:1200px;padding:17px 55px;background:#08111fe8}.copy{padding-bottom:18px;background:linear-gradient(#08111fe8,#08111f00)}'''
  markup='<html><head><style>'+style+'</style></head><body><div class="frame"><div class="visual">'+graphic+'</div><div class="copy"><div class="brand">WINGS OUT / HRL PORTFOLIO</div><h1>'+title+'</h1><p>'+desc+'</p></div><div class="foot">rmichaelglover.github.io/hrl-portfolio</div></div></body></html>'
  js('document.open();document.write('+json.dumps(markup)+');document.close();')
  js('Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))')
  js('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  capture(ROOT/item['image'],{'x':0,'y':0,'width':1200,'height':630})
  rendered+=1
  if index%20==0:print('Rendered',index+1,'/',len(manifest),flush=True)
 print('Rendered',rendered,'share cards.',flush=True);ws.close()
finally:proc.terminate();proc.wait(timeout=10)
