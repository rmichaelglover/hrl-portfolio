"""Live ROS 2 chess lab: HTTP -> signed ROS command -> simulation -> topics."""
import hashlib
import gzip
import hmac
import json
import os
from pathlib import Path
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import chess
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import MarkerArray
from tf2_ros import TransformBroadcaster
from ament_index_python.packages import get_package_share_directory
from .chess_physics import ChessLab
from .chess_ros_view import publish_scene


class ChessPhysicsNode(Node):
    def __init__(self):
        super().__init__('rolling_chess_lab')
        self.port=int(self.declare_parameter('port',8877).value)
        self.public_playback=bool(self.declare_parameter('public_playback',True).value)
        self.lab=ChessLab('*');self.lock=threading.RLock();self.pending={};self.sequence=0;self.ticks=0
        self.lab.loop_games=True
        self.lab.set_playing(bool(self.declare_parameter('autoplay',True).value))
        self.publisher=self.create_publisher(String,'state',10)
        self.commands=self.create_publisher(String,'command',10)
        self.events=self.create_publisher(String,'events',10)
        self.markers=self.create_publisher(MarkerArray,'markers',10)
        self.tf=TransformBroadcaster(self)
        self.create_subscription(String,'command',self.ros_command,10)
        self.token=secrets.token_urlsafe(32);self.command_secret=secrets.token_bytes(32)
        folder=Path.home()/'.ros'/'robot_in_loop';folder.mkdir(parents=True,exist_ok=True)
        self.origin_file=folder/f'chess-public-origin-{self.port}.txt'
        credentials=folder/f'chess-{self.port}.json'
        fd=os.open(credentials,os.O_WRONLY|os.O_TRUNC|os.O_CREAT,0o600);os.fchmod(fd,0o600)
        with os.fdopen(fd,'w') as f:json.dump({'token':self.token},f)
        page_path=Path(get_package_share_directory('cypher_robot_mind'))/'web'/'chess.html'
        node=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def allowed_origin(self):
                origins={f'http://127.0.0.1:{node.port}',f'http://localhost:{node.port}',
                         'https://rmichaelglover.github.io'}
                if node.origin_file.exists():origins.add(node.origin_file.read_text().strip())
                return self.headers.get('Origin') in origins
            def respond(self,status,payload,kind='application/json'):
                body=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
                compressed='gzip' in self.headers.get('Accept-Encoding','') and len(body)>1200
                if compressed:body=gzip.compress(body,compresslevel=3)
                self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store')
                if compressed:self.send_header('Content-Encoding','gzip')
                if self.allowed_origin():
                    self.send_header('Access-Control-Allow-Origin',self.headers['Origin']);self.send_header('Vary','Origin')
                    self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers','Authorization, Content-Type, ngrok-skip-browser-warning')
                    self.send_header('Access-Control-Allow-Private-Network','true')
                self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def do_OPTIONS(self):
                self.respond(204 if self.allowed_origin() else 403,b'')
            def authorized(self):return hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+node.token)
            def do_GET(self):
                if self.path=='/':self.respond(200,page_path.read_bytes(),'text/html; charset=utf-8')
                elif self.path=='/api/state':
                    with node.lock:state=node.snapshot()
                    state.update(operator=self.authorized(),public_playback=node.public_playback)
                    self.respond(200,state)
                elif self.path=='/api/export':
                    with node.lock:result=node.lab.export()
                    self.respond(200,result)
                else:self.respond(404,{'error':'Not found'})
            def do_POST(self):
                public=node.public_playback and self.path in {'/api/playback','/api/randomness','/api/restart'}
                if not public and not self.authorized():
                    self.respond(401,{'error':'Open the private operator link for apparatus/setup controls.'});return
                if self.headers.get('Origin') and not self.allowed_origin():
                    self.respond(403,{'error':'Origin rejected'});return
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<=70000:raise ValueError('Request size invalid.')
                    self.connection.settimeout(10);body=json.loads(self.rfile.read(length))
                    if not isinstance(body,dict):raise ValueError('Expected a JSON object.')
                    identifier=secrets.token_hex(16);event=threading.Event();holder={}
                    with node.lock:
                        if len(node.pending)>=16:raise ValueError('Command queue is full.')
                        node.pending[identifier]=(event,holder)
                    payload={'id':identifier,'path':self.path,'body':body,'time':time.time()}
                    encoded=json.dumps(payload,sort_keys=True,separators=(',',':'))
                    signature=hmac.new(node.command_secret,encoded.encode(),hashlib.sha256).hexdigest()
                    node.commands.publish(String(data=json.dumps({'payload':payload,'signature':signature})))
                    if not event.wait(15):
                        with node.lock:node.pending.pop(identifier,None)
                        self.respond(504,{'error':'ROS command acknowledgement timed out.'});return
                    self.respond(holder.get('status',500),holder.get('result',{'error':'No ROS result'}))
                except (ValueError,KeyError,TypeError,TimeoutError) as error:self.respond(400,{'error':str(error)})
        self.server=ThreadingHTTPServer(('127.0.0.1',self.port),Handler);self.server.daemon_threads=True
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.create_timer(1/30,self.tick)
        self.get_logger().info(f'Live ROS viewer: http://127.0.0.1:{self.port}/')
        self.get_logger().info(f'Private apparatus operator: http://127.0.0.1:{self.port}/#token={self.token}')
        self.get_logger().info(f'Credentials: {credentials}; public playback controls: {self.public_playback}')

    def snapshot(self):
        state=self.lab.snapshot()
        state['ros']={'runtime':'ROS 2 Humble','node':self.get_fully_qualified_name(),
            'state_topic':self.publisher.topic_name,'command_topic':self.commands.topic_name,
            'event_topic':self.events.topic_name,'marker_topic':self.markers.topic_name,
            'publish_sequence':self.sequence,'clock_ns':self.get_clock().now().nanoseconds,
            'state_subscribers':self.publisher.get_subscription_count(),'fixed_frame':'chess_board',
            'domain':int(os.environ.get('ROS_DOMAIN_ID','0'))}
        return state

    def ros_command(self,message):
        try:
            envelope=json.loads(message.data);payload=envelope['payload']
            encoded=json.dumps(payload,sort_keys=True,separators=(',',':'))
            expected=hmac.new(self.command_secret,encoded.encode(),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected,envelope['signature']) or abs(time.time()-payload['time'])>10:return
            identifier=payload['id']
            with self.lock:
                pending=self.pending.pop(identifier,None)
                if pending is None:return
                event,holder=pending
                try:
                    result=self.apply(payload['path'],payload['body']);holder.update(status=200,result=result)
                except (ValueError,KeyError,TypeError) as error:holder.update(status=400,result={'error':str(error)})
                self.events.publish(String(data=json.dumps({'id':identifier,'path':payload['path'],'status':holder['status'],
                                                           'result':holder['result'],'ros_sequence':self.sequence})))
                event.set()
        except (ValueError,KeyError,TypeError):return

    def apply(self,path,body):
        if path in {'/api/merge','/api/release','/api/variant'} and self.lab.active and self.lab.active.mode=='falling':
            raise ValueError('Wait for the falling token to finish before editing topology.')
        if path=='/api/playback':
            if not isinstance(body.get('playing'),bool):raise ValueError('playing must be true or false')
            self.lab.set_playing(body['playing'])
        elif path=='/api/randomness':
            if not isinstance(body.get('enabled'),bool):raise ValueError('enabled must be true or false')
            self.lab.randomness=body['enabled']
        elif path=='/api/restart':
            noise=self.lab.randomness;self.lab.load('*');self.lab.randomness=noise;self.lab.loop_games=True;self.lab.set_playing(True)
        elif path=='/api/tilt':self.lab.tilt(float(body.get('roll',0)),float(body.get('pitch',0)))
        elif path=='/api/select':self.lab.set_playing(False);self.lab.select(str(body['square']))
        elif path=='/api/drive':self.lab.set_playing(False);self.lab.drive(body.get('uci'))
        elif path=='/api/load':self.lab.load(str(body['pgn']));self.lab.loop_games=True
        elif path=='/api/test':self.lab.set_playing(False);return self.lab.experiment_all()
        elif path=='/api/merge':
            self.lab.topology.merge(str(body['left']),str(body['right']),str(body.get('policy','imprison')));self.lab.topology_changed()
        elif path=='/api/release':self.lab.topology.release(str(body['piece']));self.lab.topology_changed()
        elif path=='/api/variant':
            if not isinstance(body.get('enabled'),bool):raise ValueError('enabled must be true or false')
            self.lab.topology.enforced=body['enabled'];self.lab.topology_changed()
        elif path=='/api/forecast':return self.lab.topology.forecast(self.lab.board,str(body['piece']),body.get('depth',3))
        elif path=='/api/retry':
            self.lab.set_playing(False)
            if self.lab.source is None:raise ValueError('Select a piece first.')
            self.lab.select(chess.square_name(self.lab.source))
        elif path=='/api/clear':
            self.lab.set_playing(False);self.lab.parked=[];self.lab.active=None
            if self.lab.source is not None:self.lab.select(chess.square_name(self.lab.source))
        elif path=='/api/observe':
            moves=self.lab.observation_candidates(body.get('source'),body.get('destination'),body.get('promotion'))
            return {'candidates':moves,'count':len(moves),'basis':'Exact square evidence; not a chess-value proof.'}
        else:raise ValueError('Unknown operation')
        return {'ok':True,'transport':'acknowledged by ROS command subscriber'}

    def tick(self):
        with self.lock:
            self.lab.tick();self.ticks+=1
            if self.ticks%3:return
            self.sequence+=1;snapshot=self.snapshot()
        self.publisher.publish(String(data=json.dumps(snapshot)))
        publish_scene(self,snapshot,self.markers,self.tf)

    def destroy_node(self):
        self.server.shutdown();self.server.server_close();return super().destroy_node()


def main(args=None):
    rclpy.init(args=args);node=ChessPhysicsNode()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.try_shutdown()
