"""Separate peaceful garden simulation, publishing modeled state, not cmd_vel."""
import json
from pathlib import Path
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import SetBool, Trigger
from ament_index_python.packages import get_package_share_directory
from .peaceful import Garden

class PeacefulGarden(Node):
    def __init__(self):
        super().__init__('peaceful_garden')
        default = str(Path(get_package_share_directory('cypher_robot_mind'))/'config'/'peaceful-profile.json')
        path = self.declare_parameter('profile', default).value
        self.profile = json.loads(Path(path).read_text())
        self.world = Garden(self.profile)
        self.paused = False
        self.pub = self.create_publisher(String, 'peaceful_garden/state', 10)
        self.create_service(SetBool, 'peaceful_garden/pause', self.pause)
        self.create_service(Trigger, 'peaceful_garden/reset', self.reset)
        self.create_timer(.5, self.tick)
    def pause(self, request, response):
        self.paused = request.data
        response.success = True
        response.message = 'Paused' if self.paused else 'Walking together'
        return response
    def reset(self, request, response):
        self.world = Garden(self.profile)
        response.success = True
        response.message = 'Everyone is home in the garden'
        return response
    def tick(self):
        if not self.paused:
            try: self.world.step()
            except RuntimeError as exc:
                self.paused = True
                self.get_logger().warning(str(exc))
        state = self.world.snapshot()
        state['paused'] = self.paused
        self.pub.publish(String(data=json.dumps(state)))

def main(args=None):
    rclpy.init(args=args)
    node = PeacefulGarden()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.try_shutdown()
