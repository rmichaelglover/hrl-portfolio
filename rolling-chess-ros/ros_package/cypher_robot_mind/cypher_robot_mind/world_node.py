"""Deterministic kinematic arena. Only this node accesses world truth."""
import json
import math
import os
import time
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped, PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster
from .authorization import CommandGate, PresencePolicy

WALLS = [(4., 1.5, .65, 4.0), (6., 6., 2., .6), (1.8, 6.2, .6, 1.6)]


class World(Node):
    def __init__(self):
        super().__init__('virtual_world')
        self.seed = int(self.declare_parameter('seed', 7).value)
        self.noise = float(self.declare_parameter('sensor_noise', .035).value)
        self.scan_pub = self.create_publisher(LaserScan, 'scan', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.hazard_pub = self.create_publisher(PoseWithCovarianceStamped, 'hazard_detection', 10)
        self.goal_pub = self.create_publisher(PoseStamped, 'goal', 10)
        self.truth_pub = self.create_publisher(String, 'world_truth', 10)
        self.epoch_pub = self.create_publisher(String, 'episode', 10)
        self.mode_pub = self.create_publisher(String, 'operator_state', 10)
        self.tf = TransformBroadcaster(self)
        self.gate=CommandGate(os.environ.get('CYPHER_COMMAND_SECRET',''))
        self.create_subscription(String,'operator_command',self.operator_command,10)
        self.create_subscription(Twist, 'cmd_vel', self.command, 10)
        self.reset()
        self.create_timer(.1, self.tick)

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self.position = np.array([1.25,1.25])
        self.goal = np.array([8.25,8.25])
        self.velocity = np.zeros(2)
        self.command_time = 0.
        self.t, self.collisions, self.epoch = 0., 0, time.time_ns()
        self.paused, self.disturbed = True, False
        self.policy=PresencePolicy(time.monotonic())

    def command(self, msg):
        v = np.array([msg.linear.x,msg.linear.y])
        self.velocity = v if np.isfinite(v).all() else np.zeros(2)
        norm = np.linalg.norm(self.velocity)
        if norm > .65:
            self.velocity *= .65/norm
        self.command_time = time.monotonic()

    def hazard(self):
        return np.array([6.4 + 1.2*math.sin(self.t*.45), 3.9 + .7*math.cos(self.t*.45)])

    def solid(self, point, radius=0.):
        x,y = point
        if min(x,y) < radius+.1 or max(x,y) > 9.9-radius:
            return True
        walls = WALLS + ([(2.6,3.,.7,.7)] if self.disturbed else [])
        for xx,yy,w,h in walls:
            if xx-radius <= x <= xx+w+radius and yy-radius <= y <= yy+h+radius:
                return True
        return bool(np.linalg.norm(point-self.hazard()) < .32+radius)

    def visible(self, point):
        delta = point-self.position
        distance = np.linalg.norm(delta)
        if distance > 4.:
            return False
        # Stop short of the target body; intervening walls still occlude it.
        return not any(self.solid(self.position+delta*t) for t in np.arange(0.,max(0.,1.-.4/max(distance,.01)),.025))

    def operator_command(self,msg):
        action=self.gate.verify(msg.data)
        if action is None:
            self.get_logger().warning('Rejected unauthenticated, expired, or replayed command.'); return
        if action=='reset':
            self.reset()
        elif action=='disturb':
            if np.linalg.norm(self.position-np.array([2.95,3.35]))<1.:
                self.policy.reason='Disturbance rejected: robot is too close.'
            else:
                self.disturbed=not self.disturbed
                self.policy.reason='Operator changed the environment; robot must sense it.'
        else:
            self.policy.apply(action,time.monotonic())
            if action in {'stop','shutdown','sleep','wake'}: self.velocity[:]=0

    def tick(self):
        mode=self.policy.tick(time.monotonic())
        self.paused=mode!='RUNNING'
        if np.linalg.norm(self.position-self.goal)<.32:
            self.paused=True; self.velocity[:]=0; self.policy.mode='WAITING'; self.policy.mission_until=0.
            self.policy.reason='Mission complete. Awaiting another command.'
        self.mode_pub.publish(String(data=self.policy.mode))
        if not self.paused:
            self.t += .1
            if time.monotonic()-self.command_time < .75:
                candidate = self.position+self.velocity*.1
                if not self.solid(candidate,.2):
                    self.position=candidate
                elif np.linalg.norm(self.velocity)>.01:
                    self.collisions += 1
        stamp = self.get_clock().now().to_msg()
        scan = LaserScan()
        scan.header.stamp=stamp; scan.header.frame_id='base_link'
        scan.angle_min=-math.pi; scan.angle_increment=2*math.pi/72; scan.angle_max=scan.angle_min+71*scan.angle_increment
        scan.range_min=.05; scan.range_max=4.; scan.scan_time=.1
        ranges=[]
        for i in range(72):
            angle=scan.angle_min+i*scan.angle_increment
            direction=np.array([math.cos(angle),math.sin(angle)])
            distance=4.
            for t in np.arange(.05,4.,.05):
                if self.solid(self.position+t*direction):
                    distance=float(np.clip(t+self.rng.normal(0,self.noise),.05,3.95)); break
            ranges.append(distance)
        scan.ranges=ranges
        odom=Odometry(); odom.header.stamp=stamp; odom.header.frame_id='map'; odom.child_frame_id='base_link'
        measured=self.position+self.rng.normal(0,.025,2)
        odom.pose.pose.position.x=float(measured[0]); odom.pose.pose.position.y=float(measured[1])
        odom.pose.pose.orientation.w=1.
        odom.pose.covariance[0]=odom.pose.covariance[7]=.025**2
        self.epoch_pub.publish(String(data=str(self.epoch)))
        transform=TransformStamped(); transform.header=odom.header; transform.child_frame_id='base_link'
        transform.transform.translation.x=float(measured[0]); transform.transform.translation.y=float(measured[1])
        transform.transform.rotation.w=1.; self.tf.sendTransform(transform)
        self.odom_pub.publish(odom)
        self.scan_pub.publish(scan)
        h=self.hazard()
        if self.visible(h):
            detection=PoseWithCovarianceStamped(); detection.header.stamp=stamp; detection.header.frame_id='map'
            measurement=h+self.rng.normal(0,.08,2)
            detection.pose.pose.position.x=float(measurement[0]); detection.pose.pose.position.y=float(measurement[1])
            detection.pose.pose.orientation.w=1.
            detection.pose.covariance[0]=detection.pose.covariance[7]=.08**2
            self.hazard_pub.publish(detection)
        goal=PoseStamped(); goal.header.stamp=stamp; goal.header.frame_id='map'
        goal.pose.position.x=float(self.goal[0]); goal.pose.position.y=float(self.goal[1]); goal.pose.orientation.w=1.
        self.goal_pub.publish(goal)
        truth={'position':self.position.tolist(),'goal':self.goal.tolist(),'hazard':h.tolist(),
               'walls':WALLS+([(2.6,3.,.7,.7)] if self.disturbed else []),
               'time':round(self.t,2),'paused':self.paused,'collisions':self.collisions,'epoch':self.epoch,
               'authorization_remaining':max(0,round(self.policy.mission_until-time.monotonic(),1)),
               'presence_remaining':max(0,round(self.policy.presence_timeout-(time.monotonic()-self.policy.last_presence),1)),
               'sleep_remaining':None if self.policy.sleep_since is None else max(0,round(self.policy.sleep_timeout-(time.monotonic()-self.policy.sleep_since),1)),
               'mode':self.policy.mode,'operator_status':self.policy.reason}
        self.truth_pub.publish(String(data=json.dumps(truth)))


def main(args=None):
    rclpy.init(args=args); node=World()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.try_shutdown()
