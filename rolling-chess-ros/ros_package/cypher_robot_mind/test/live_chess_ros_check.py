import json,time,urllib.request,urllib.error,os
from pathlib import Path
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import MarkerArray
base='http://127.0.0.1:8877';public=os.environ.get('PUBLIC_CHESS_URL','https://janetta-nongelatinous-clemmie.ngrok-free.dev')
token=json.loads((Path.home()/'.ros/robot_in_loop/chess-8877.json').read_text())['token']
def api(path,body=None,operator=True,url=base,headers=None):
 h=dict(headers or {})
 if operator:h['Authorization']='Bearer '+token
 if body is not None:h['Content-Type']='application/json'
 h['ngrok-skip-browser-warning']='1'
 try:
  with urllib.request.urlopen(urllib.request.Request(url+path,data=None if body is None else json.dumps(body).encode(),headers=h),timeout=20) as r:return r.status,json.load(r),dict(r.headers)
 except urllib.error.HTTPError as e:return e.code,json.load(e),dict(e.headers)
def state():return api('/api/state')[1]
def move(uci):
 before=state()['ply'];assert api('/api/drive',{'uci':uci})[0]==200
 for _ in range(150):
  time.sleep(.1);s=state()
  if s['ply']>before:break
 assert s['ply']==before+1 and s['ledger'][-1]['uci']==uci,(uci,s['message'])
rclpy.init();probe=Node('rolling_chess_verification_probe');received={'state':[],'markers':[],'events':[],'command':[]}
subscriptions=[]
for name,kind in [('state',String),('markers',MarkerArray),('events',String),('command',String)]:
 subscriptions.append(probe.create_subscription(kind,'/rolling_chess/'+name,lambda message,key=name:received[key].append(message),10))
start=time.monotonic()
while time.monotonic()-start<1:rclpy.spin_once(probe,timeout_sec=.1)
assert received['state'] and received['markers'],'Actual ROS DDS messages missing'
assert len(received['markers'][-1].markers)>64
before=json.loads(received['state'][-1].data)['ros']['publish_sequence']
assert api('/api/playback',{'playing':False},False)[0]==200
assert api('/api/randomness',{'enabled':False},False)[0]==200
for _ in range(10):rclpy.spin_once(probe,timeout_sec=.1)
assert received['command'] and received['events'],'Command did not cross actual ROS topics'
assert json.loads(received['state'][-1].data)['ros']['publish_sequence']>before
assert state()['playback']['randomness'] is False
print('PASS actual external ROS subscriber receives state, MarkerArray, command and acknowledgement topics',flush=True)
# The HTTPS endpoint serves the actual ROS state and whitelisted CORS response.
code,s,headers=api('/api/state',operator=False,url=public,headers={'Origin':'https://rmichaelglover.github.io'})
assert code==200 and s['ros']['node']=='/rolling_chess/rolling_chess_lab'
assert headers.get('Access-Control-Allow-Origin')=='https://rmichaelglover.github.io'
assert api('/api/tilt',{'roll':2,'pitch':0},False)[0]==401
print('PASS public HTTPS live ROS state, origin allowlist, public randomness control, private apparatus controls',flush=True)
assert api('/api/load',{'pgn':'*'})[0]==200
assert api('/api/merge',{'left':'B:e3','right':'B:e4','policy':'imprison'})[0]==200
assert api('/api/merge',{'left':'W:w-n-b1','right':'W:w-n-g1','policy':'imprison'})[0]==200
assert api('/api/merge',{'left':'B:a6','right':'W:w-n-b1'})[0]==200
assert api('/api/variant',{'enabled':True})[0]==200
move('e2e4');move('a7a6')
s=state();pieces={p['id']:p for p in s['topology']['pieces']}
assert pieces['w-p-e2']['mobility']=='imprisoned' and pieces['w-p-e2']['existence']=='on-board'
assert pieces['w-n-b1']['mobility']==pieces['w-n-g1']['mobility']=='free'
assert 'e4e5' not in [m['uci'] for m in s['legal']] and 'g1f3' in [m['uci'] for m in s['legal']]
assert len(s['pieces'])==32
result=api('/api/forecast',{'piece':'b-p-a7','depth':1})[1]
assert result['status']=='forced within horizon' and result['probability'] is None
assert api('/api/release',{'piece':'w-p-e2'})[0]==200
assert 'e4e5' in [m['uci'] for m in state()['legal']]
print('PASS black-black prison, white-white source group, black-white release relay, legal move filtering, bounded capture test and release',flush=True)
assert api('/api/load',{'pgn':'*'})[0]==200
assert api('/api/randomness',{'enabled':True},False)[0]==200
assert api('/api/playback',{'playing':True},False)[0]==200
probe.destroy_node();rclpy.try_shutdown()
print('PASS reset to fresh standard whole-game autoplay with randomness on',flush=True)
