"""Local ROS dashboard: offline voice commands, roles and public stop."""
import hmac
import json
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .authorization import sign, permitted
from .voice import OfflineVoice


class Dashboard(Node):
    def __init__(self):
        super().__init__('mind_dashboard')
        port=int(self.declare_parameter('port',8876).value)
        self.snapshot={'world':{},'mind':{}}; self.lock=threading.Lock(); self.voice_lock=threading.Lock()
        self.create_subscription(String,'world_truth',lambda msg:self.update('world',msg),10)
        self.create_subscription(String,'mind',lambda msg:self.update('mind',msg),10)
        self.secret=os.environ.get('CYPHER_COMMAND_SECRET','')
        if len(self.secret)<32: raise ValueError('Use ROS launch to provision the command gate.')
        self.tokens={role:secrets.token_urlsafe(32) for role in ['basic','admin']}
        credentials=Path.home()/'.ros'/'robot_in_loop'/f'operators-{port}.json'
        credentials.parent.mkdir(parents=True,exist_ok=True)
        descriptor=os.open(credentials,os.O_CREAT|os.O_WRONLY|os.O_TRUNC,0o600)
        os.fchmod(descriptor,0o600)
        with os.fdopen(descriptor,'w') as stream: json.dump(self.tokens,stream)
        self.commands=self.create_publisher(String,'operator_command',10)
        self.voice=None; self.voice_error=None; self.challenges={}
        try: self.voice=OfflineVoice()
        except (OSError,RuntimeError) as error: self.voice_error=str(error)
        page=(Path(get_package_share_directory('cypher_robot_mind'))/'web'/'index.html').read_bytes()
        node=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def respond(self,status,payload,kind='application/json'):
                content=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
                self.send_response(status); self.send_header('Content-Type',kind)
                self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(content)))
                self.end_headers(); self.wfile.write(content)
            def role(self):
                authorization=self.headers.get('Authorization','')
                for role,token in node.tokens.items():
                    if hmac.compare_digest(authorization,'Bearer '+token): return role
                return 'public'
            def do_GET(self):
                if self.path=='/': self.respond(200,page,'text/html; charset=utf-8')
                elif self.path=='/api/state':
                    with node.lock: payload=dict(node.snapshot)
                    payload.update(role=self.role(),voice_available=node.voice is not None,voice_error=node.voice_error)
                    self.respond(200,payload)
                elif urlparse(self.path).path=='/api/challenge':
                    action=parse_qs(urlparse(self.path).query).get('command',['stop'])[0]
                    if action not in {'start','stop','shutdown','sleep','wake','present','reset','disturb'}:
                        self.respond(400,{'error':'Unsupported voice command'}); return
                    words=['blue','green','red','gold','one','two','three','four','five','six','seven','eight','nine']
                    phrase=' '.join(secrets.choice(words) for _ in range(4))
                    challenge_id=secrets.token_hex(16)
                    with node.lock:
                        node.challenges={k:v for k,v in node.challenges.items() if time.monotonic()-v[1]<30}
                        if len(node.challenges)>100:
                            self.respond(429,{'error':'Too many pending voice challenges'}); return
                        node.challenges[challenge_id]=(phrase,time.monotonic(),self.role(),action)
                    self.respond(200,{'id':challenge_id,'phrase':phrase,'role':self.role()})
                else: self.respond(404,{'error':'Not found'})
            def do_POST(self):
                origin=self.headers.get('Origin')
                if origin and origin not in [f'http://127.0.0.1:{port}',f'http://localhost:{port}']:
                    self.respond(403,{'error':'Origin rejected'}); return
                if self.path in ['/api/stop','/api/shutdown']:
                    action=self.path.split('/')[-1]
                    node.commands.publish(String(data=sign(node.secret,action)))
                    self.respond(202,{'message':'Stop sent; task permission cancelled.'}); return
                if self.path!='/api/voice':
                    self.respond(405,{'error':'Task and general commands require microphone speech.'}); return
                if node.voice is None:
                    self.respond(503,{'error':node.voice_error or 'Offline voice unavailable'}); return
                try: length=int(self.headers.get('Content-Length','0'))
                except ValueError: length=0
                if not 3200<=length<=320000 or length%2:
                    self.respond(400,{'error':'Expected 0.1–10 seconds of 16 kHz mono PCM'}); return
                with node.lock:
                    challenge=node.challenges.pop(self.headers.get('X-Voice-Challenge',''),None)
                if not challenge or time.monotonic()-challenge[1]>30 or challenge[2]!=self.role():
                    self.respond(403,{'error':'Voice challenge expired. Record again.'}); return
                self.connection.settimeout(10)
                try: pcm=self.rfile.read(length)
                except TimeoutError:
                    self.respond(408,{'error':'Audio upload timed out'}); return
                if not node.voice_lock.acquire(blocking=False):
                    self.respond(429,{'error':'Another utterance is being processed'}); return
                try: action,transcript=node.voice.decode(pcm,challenge[0],challenge[3])
                except (ValueError,RuntimeError) as error:
                    self.respond(400,{'error':str(error)}); return
                finally: node.voice_lock.release()
                if action is None:
                    self.respond(422,{'error':'No matching command heard. No permission granted.','heard':transcript}); return
                if action!=challenge[3] and action not in {'stop','shutdown'}:
                    self.respond(422,{'error':'Heard a different command. No task permission granted.','heard':transcript}); return
                if not permitted(self.role(),action):
                    self.respond(403,{'error':f'{action} requires a higher operator role.','heard':transcript}); return
                node.commands.publish(String(data=sign(node.secret,action)))
                self.respond(202,{'message':f'Voice command sent: {action}.','heard':transcript})
        self.server=ThreadingHTTPServer(('127.0.0.1',port),Handler); self.server.daemon_threads=True
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.get_logger().info(f'Read-only + public stop: http://127.0.0.1:{port}/')
        self.get_logger().info(f'Private operator credentials saved to {credentials}')
        for role,token in self.tokens.items():
            self.get_logger().info(f'Private {role} operator link: http://127.0.0.1:{port}/#token={token}')

    def update(self,key,msg):
        with self.lock:
            self.snapshot[key]=json.loads(msg.data); self.snapshot[key+'_received']=time.time()

    def destroy_node(self):
        self.server.shutdown(); self.server.server_close()
        if self.voice: self.voice.close()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args); node=Dashboard()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.try_shutdown()
