"""RViz scene; ground-truth subscription belongs to display, never planner."""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray


class View(Node):
    def __init__(self):
        super().__init__('robot_view')
        self.pub=self.create_publisher(MarkerArray,'visualization',10)
        self.create_subscription(String,'world_truth',self.world,10)
        self.create_subscription(String,'mind',self.mind,10)
        self.state={}

    def mind(self,msg):
        self.state=json.loads(msg.data)

    def world(self,msg):
        world=json.loads(msg.data); markers=[]
        def marker(name,kind,position,scale,color,text=''):
            m=Marker(); m.header.frame_id='map'; m.header.stamp=self.get_clock().now().to_msg()
            m.ns=name; m.id=len(markers); m.type=kind; m.action=Marker.ADD
            m.pose.orientation.w=1.
            m.pose.position.x=float(position[0]); m.pose.position.y=float(position[1]); m.pose.position.z=float(position[2])
            m.scale.x=float(scale[0]); m.scale.y=float(scale[1]); m.scale.z=float(scale[2])
            m.color.r,m.color.g,m.color.b,m.color.a=map(float,color)
            m.text=text; markers.append(m); return m
        clear=Marker(); clear.action=Marker.DELETEALL; markers.append(clear)
        marker('floor',Marker.CUBE,[5,5,-.07],[10,10,.1],[.12,.2,.25,1])
        for x,y,w,h in world['walls']:
            marker('walls',Marker.CUBE,[x+w/2,y+h/2,.4],[w,h,.8],[.43,.52,.57,1])
        x,y=world['position']
        marker('torso',Marker.CUBE,[x,y,.65],[.32,.38,.4],[.2,.85,.74,1])
        for dy in [-.13,.13]:
            marker('legs',Marker.CUBE,[x,y+dy,.23],[.14,.13,.42],[.45,.65,.69,1])
            marker('arms',Marker.CUBE,[x,y+dy*2,.65],[.12,.1,.38],[.7,.87,.8,1])
        marker('head',Marker.SPHERE,[x,y,1.],[.32,.32,.3],[.8,.95,.91,1])
        for dy in [-.09,.09]:
            marker('eyes',Marker.SPHERE,[x+.15,y+dy,1.03],[.06,.06,.06],[.08,.16,.2,1])
        hx,hy=world['hazard']; marker('moving_obstacle',Marker.SPHERE,[hx,hy,.32],[.64,.64,.64],[1,.4,.35,1])
        gx,gy=world['goal']; marker('goal',Marker.CYLINDER,[gx,gy,.04],[.6,.6,.08],[1,.78,.35,1])
        text=f"CYPHER · {self.state.get('signal','WAIT')}"
        marker('mind',Marker.TEXT_VIEW_FACING,[x,y,1.5],[0,0,.25],[1,1,1,1],text)
        if self.state.get('hazard'):
            px,py=self.state['hazard']
            marker('predicted_hazard',Marker.SPHERE,[px,py,.35],[.75,.75,.75],[1,.55,.35,.3])
        self.pub.publish(MarkerArray(markers=markers))


def main(args=None):
    rclpy.init(args=args); node=View()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.try_shutdown()
