import audioop,json,re,subprocess,time,urllib.request,urllib.error,wave
from pathlib import Path
base='http://127.0.0.1:8876'
tokens=json.loads((Path.home()/'.ros/robot_in_loop/operators-8876.json').read_text())
def request(path,role='public',data=None,extra={}):
 headers=dict(extra)
 if role in tokens:headers['Authorization']='Bearer '+tokens[role]
 try:
  with urllib.request.urlopen(urllib.request.Request(base+path,data=data,headers=headers),timeout=10) as r:return r.status,json.load(r)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def state():return request('/api/state')[1]
def voice(action,role='admin',attempts=12):
 for _ in range(attempts):
  code,ch=request('/api/challenge?command='+action,role)
  spoken='go' if action=='start' else action
  phrase='robot '+spoken+' '+ch['phrase']
  subprocess.run(['espeak','-v','en-us','-s','130','-w','/tmp/robot-live-fixture.wav',phrase],check=True)
  with wave.open('/tmp/robot-live-fixture.wav') as w:pcm=audioop.ratecv(w.readframes(w.getnframes()),2,1,w.getframerate(),16000,None)[0]
  status,result=request('/api/voice',role,pcm,{'Content-Type':'audio/L16','X-Voice-Challenge':ch['id']})
  if status==202 and result.get('heard','').startswith('robot '+('start' if action=='start' else action)+' '):return status,result
  if status==403:return status,result
 raise AssertionError(('Speech fixture never recognized',action,status,result))
# No movement without explicit command, including a plain HTTP start request.
s=state();origin=s['world']['position'];time.sleep(1)
assert state()['world']['position']==origin
assert request('/api/start','admin',b'')[0]==405
assert voice('start','basic')[0]==403
print('PASS stationary by default, text start rejected, basic role cannot start',flush=True)
assert voice('reset')[0]==202;time.sleep(.5)
assert voice('start')[0]==202;time.sleep(2)
s=state();assert s['world']['mode']=='RUNNING',s['world']
assert sum((a-b)**2 for a,b in zip(s['world']['position'],[1.25,1.25]))>.04,s['world']
assert s['mind']['scene']['regions'] and s['mind']['occupancy']
print('PASS offline audio → authenticated mission → ROS motion and live beliefs',flush=True)
assert request('/api/stop',data=b'')[0]==202;time.sleep(.5)
s=state();assert s['world']['mode']=='SLEEPING'
stopped=s['world']['position'];time.sleep(1)
assert state()['world']['position']==stopped
assert request('/api/shutdown',data=b'')[0]==202;time.sleep(.5)
assert state()['world']['mode']=='HIBERNATING'
assert voice('wake','basic')[0]==202;time.sleep(.5)
assert state()['world']['mode']=='WAITING'
assert state()['world']['position']==stopped
print('PASS public stop/shutdown, basic wake, no task resumption',flush=True)
assert voice('reset')[0]==202;time.sleep(.5)
assert voice('start')[0]==202
start=time.monotonic();last_renew=start
while time.monotonic()-start<55:
 time.sleep(1);s=state();w=s['world'];m=s['mind']
 Path('/tmp/robot-latest.json').write_text(json.dumps(s))
 if time.monotonic()-last_renew>18:
  voice('present','basic');last_renew=time.monotonic()
 if sum((a-b)**2 for a,b in zip(w['position'],w['goal']))<.32**2:
  print('PASS goal reached; blocked-motion attempts:',w['collisions'],flush=True);break
else:
 Path('/tmp/robot-route-limit.json').write_text(json.dumps(s))
 print('LIMIT route run ended:',{k:w[k] for k in ['position','mode','collisions']},m.get('reason'),flush=True)
# Explicitly exercise presence loss on a fresh mission, without renewing the lease.
voice('reset');time.sleep(.5);voice('start');time.sleep(32)
s=state();assert s['world']['mode'] in ['SLEEPING','WAITING'],s['world']
assert s['world']['authorization_remaining']==0
request('/api/shutdown',data=b'')
print('PASS live presence expiry cancels permission; left in simulated hibernation',flush=True)
