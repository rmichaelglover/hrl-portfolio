"""Robot mind: measurements in, beliefs/interpretations/actions out."""
import json
import math
import time
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry, OccupancyGrid, Path
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from .model import (Attention, BeliefMap, KalmanTrack, SIZE, RESOLUTION,
                    cell, center, plan, relax_scene)


class Mind(Node):
    def __init__(self):
        super().__init__('robot_mind')
        self.cmd_pub=self.create_publisher(Twist,'cmd_vel',10)
        self.state_pub=self.create_publisher(String,'mind',10)
        self.map_pub=self.create_publisher(OccupancyGrid,'belief_map',10)
        self.path_pub=self.create_publisher(Path,'plan',10)
        self.create_subscription(Odometry,'odom',self.odometry,10)
        self.create_subscription(LaserScan,'scan',self.scan,10)
        self.create_subscription(PoseWithCovarianceStamped,'hazard_detection',self.detection,10)
        self.create_subscription(PoseStamped,'goal',self.set_goal,10)
        self.create_subscription(String,'episode',self.episode,10)
        self.create_subscription(String,'operator_state',self.operator_state,10)
        self.mode='WAITING'
        self.epoch=None; self.reset()
        self.create_timer(.2,self.think)

    def reset(self):
        self.belief=BeliefMap(); self.attention=Attention()
        self.track=None; self.hazard=None; self.goal=None; self.last_odom=None; self.latest_scan=None
        self.odom_time=self.scan_time=self.hazard_time=0.
        self.hazard_stamp=None; self.surprise=0.; self.steps=0
        self.last_signal='WAIT'; self.events=[]
        self.last_state={}

    def episode(self,msg):
        if self.epoch != msg.data:
            self.epoch=msg.data; self.reset()

    def operator_state(self,msg):
        self.mode=msg.data

    def odometry(self,msg):
        p=msg.pose.pose.position
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        measurement=[p.x,p.y]
        if self.track is None:
            self.track=KalmanTrack(measurement, max(.0001,msg.pose.covariance[0]))
        else:
            dt=max(.001,min(.5,stamp-self.last_odom))
            self.track.predict(dt)
            self.surprise=max(self.surprise,self.track.correct(measurement,max(.0001,msg.pose.covariance[0]))*3)
        self.last_odom=stamp; self.odom_time=time.monotonic()

    def scan(self,msg):
        self.latest_scan=msg; self.scan_time=time.monotonic()
        if self.track is not None:
            before=self.belief.occupancy.copy()
            self.belief.scan(self.track.position,msg.ranges,msg.angle_min,msg.angle_increment,msg.range_max)
            self.surprise=max(self.surprise,float(np.max(np.abs(self.belief.occupancy-before)))*3)

    def detection(self,msg):
        p=msg.pose.pose.position
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
        if self.hazard is None or time.monotonic()-self.hazard_time>2:
            self.hazard=KalmanTrack([p.x,p.y],.08**2)
        else:
            self.hazard.predict(max(.001,min(2.,stamp-self.hazard_stamp)))
            self.surprise=max(self.surprise,self.hazard.correct([p.x,p.y],max(.0001,msg.pose.covariance[0])))
        self.hazard_stamp=stamp; self.hazard_time=time.monotonic()

    def set_goal(self,msg):
        self.goal=np.array([msg.pose.position.x,msg.pose.position.y])

    def think(self):
        cmd=Twist(); now=time.monotonic()
        if self.mode in {'SLEEPING','HIBERNATING'}:
            self.cmd_pub.publish(cmd)
            sleeping={**self.last_state,'signal':self.mode,'route':[],'velocity':[0.,0.],
                      'reason':'Task cancelled. Showing last awake beliefs; wake never resumes the mission.'}
            self.state_pub.publish(String(data=json.dumps(sleeping)))
            return
        if self.track is None or self.goal is None or now-self.scan_time>.6 or now-self.odom_time>.6:
            self.cmd_pub.publish(cmd)
            self.state_pub.publish(String(data=json.dumps({'signal':'WAIT','reason':'Waiting for fresh range and pose measurements.'})))
            return
        self.steps+=1
        position=self.track.position
        hazard_age=now-self.hazard_time
        predicted=None if self.hazard is None or hazard_age>2 else self.hazard.future(min(2.,hazard_age+1.))
        cx,cy=cell(position)
        region=min(2,cy*3//SIZE)*3+min(2,cx*3//SIZE)
        attention=self.attention.update(self.surprise,region)
        # Attention recruits a larger, bounded interpretation budget.
        scene=relax_scene(self.belief,position,self.goal,predicted,
                          max_iterations=4+attention['active_regions'])
        route=plan(self.belief,position,self.goal,predicted,scene)
        distance=float(np.linalg.norm(position-self.goal))
        nearest=min((r for r in self.latest_scan.ranges if math.isfinite(r) and r>0),default=4.)
        threat_distance=float('inf') if predicted is None else float(np.linalg.norm(position-predicted))
        signal,reason='OPPORTUNITY',f'Route available: {max(0,len(route)-1)} cells toward the goal.'
        target=center(route[1]) if len(route)>1 else self.goal
        delta=target-position
        speed=.55
        if distance<.32:
            signal,reason='ARRIVED','Goal reached. Holding position.'; speed=0.
        elif threat_distance<1.15:
            signal,reason='DANGER','Predicted moving obstacle is close. Stop and observe.'; speed=0.
        elif not route:
            signal,reason='UNCERTAIN','No route in the current belief map. Stop, scan, and reconsider.'; speed=0.
        else:
            # Current raw range data provides a short-horizon collision guard.
            angle=math.atan2(delta[1],delta[0])
            forward=[r for i,r in enumerate(self.latest_scan.ranges)
                     if abs(math.atan2(math.sin(self.latest_scan.angle_min+i*self.latest_scan.angle_increment-angle),
                                       math.cos(self.latest_scan.angle_min+i*self.latest_scan.angle_increment-angle)))<.4
                     and math.isfinite(r)]
            if forward and min(forward)<.35:
                signal,reason='DANGER','Range guard: obstacle in the commanded direction.'; speed=0.
        direction=delta/max(.001,float(np.linalg.norm(delta)))
        cmd.linear.x=float(direction[0]*speed); cmd.linear.y=float(direction[1]*speed)
        self.cmd_pub.publish(cmd)
        if signal!=self.last_signal:
            self.events=([{'step':self.steps,'signal':signal,'reason':reason}]+self.events)[:15]
            self.get_logger().info(f'{signal}: {reason}')
            self.last_signal=signal
        state={'signal':signal,'reason':reason,'position':position.tolist(),'goal':self.goal.tolist(),
               'velocity':[cmd.linear.x,cmd.linear.y], 'position_covariance':self.track.p[:,0,0].tolist(),
               'hazard':None if predicted is None else predicted.tolist(),
               'hazard_age':None if self.hazard is None else round(hazard_age,2),
               'occupancy':self.belief.occupancy.tolist(),'seen':self.belief.observations.tolist(),
               'route':[center(p).tolist() for p in route], 'scene':scene,'attention':attention,
               'surprise':self.surprise,'distance':distance,'nearest_range':nearest,'steps':self.steps,
               'events':self.events,'sensor_age':round(now-self.scan_time,3)}
        self.state_pub.publish(String(data=json.dumps(state)))
        self.last_state=state
        self.surprise*=.5
        stamp=self.get_clock().now().to_msg()
        grid=OccupancyGrid(); grid.header.frame_id='map'; grid.header.stamp=stamp
        grid.info.resolution=RESOLUTION; grid.info.width=grid.info.height=SIZE
        grid.info.origin.orientation.w=1.
        values=np.rint(self.belief.occupancy*100).astype(int)
        values[self.belief.observations==0]=-1
        grid.data=values.ravel().tolist(); self.map_pub.publish(grid)
        path=Path(); path.header=grid.header
        for point in route:
            pose=PoseStamped(); pose.header=grid.header
            xy=center(point); pose.pose.position.x=float(xy[0]); pose.pose.position.y=float(xy[1]); pose.pose.orientation.w=1.
            path.poses.append(pose)
        self.path_pub.publish(path)


def main(args=None):
    rclpy.init(args=args); node=Mind()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        if rclpy.ok(): node.cmd_pub.publish(Twist())
        node.destroy_node(); rclpy.try_shutdown()
