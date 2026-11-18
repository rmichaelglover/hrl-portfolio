"""Publish the creek ledger and coupled garden on native ROS 2 topics."""
import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .angel_creek import DT, run


class AngelCreek(Node):
    def __init__(self):
        super().__init__("angel_creek")
        csv_path = self.declare_parameter("csv_path", "").value
        seed = self.declare_parameter("seed", 7).value
        self.records = run(Path(csv_path) if csv_path else None, seed)
        self.ledger = self.create_publisher(String, "angel_creek/ledger", 10)
        self.garden = self.create_publisher(String, "angel_creek/garden", 10)
        self.timer = self.create_timer(DT, self.tick)

    def tick(self):
        try:
            record = next(self.records)
        except StopIteration:
            self.timer.cancel()
            self.get_logger().info("Creek trace complete.")
            return
        except (OSError, ValueError, KeyError) as exc:
            self.timer.cancel()
            self.get_logger().error(f"Creek input stopped: {exc}")
            return
        garden = record.pop("garden")
        self.ledger.publish(String(data=json.dumps(record)))
        self.garden.publish(String(data=json.dumps(garden)))


def main(args=None):
    rclpy.init(args=args)
    node = AngelCreek()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
