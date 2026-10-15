from builtin_interfaces.msg import Time
from cypher_robot_mind.chess_physics import ChessLab
from cypher_robot_mind.chess_ros_view import publish_scene


class Store:
    def publish(self,message):self.message=message
    def sendTransform(self,message):self.message=message


class Node:
    def get_clock(self):return self
    def now(self):return self
    def to_msg(self):return Time()


def test_actual_rviz_geometry_and_tilt_transform():
    lab=ChessLab();lab.tilt(5,5)
    scene,tf=Store(),Store();publish_scene(Node(),lab.snapshot(),scene,tf)
    assert len(scene.message.markers)>150
    namespaces={marker.ns for marker in scene.message.markers}
    assert {'pawn','rook','knight','bishop','queen','king','metal','squares'}<=namespaces
    assert tf.message.child_frame_id=='chess_board'
    q=tf.message.transform.rotation
    # Positive tilts slope down toward increasing file/rank, matching gravity.
    assert 2*(q.x*q.z-q.w*q.y)<0
    assert 2*(q.y*q.z+q.w*q.x)<0
