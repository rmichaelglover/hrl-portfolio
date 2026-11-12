#!/usr/bin/env python3
"""Publish synthetic tracking and optional real sleep epochs via ROS 2."""
import argparse, csv, math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from sensor_msgs.msg import LaserScan
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

def stamp(header, t):
    header.stamp.sec = int(t)
    header.stamp.nanosec = round((t - int(t)) * 1000000000.0)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--epochs')
    p.add_argument('--sleep-start-epoch', type=int, default=0)
    p.add_argument('--steps', type=int, default=30)
    a = p.parse_args()
    rclpy.init()
    node = Node('alex_observation_replay')
    optical = node.create_publisher(PoseWithCovarianceStamped, '/alex/mocap/pose', 10)
    lidar = node.create_publisher(LaserScan, '/alex/lidar/scan', 10)
    sleep = node.create_publisher(DiagnosticArray, '/alex/sleep/epochs', 10)
    rows = []
    if a.epochs:
        with open(a.epochs) as f:
            rows = list(csv.DictReader(f))[a.sleep_start_epoch:]
    for _ in range(20):
        rclpy.spin_once(node, timeout_sec=0.05)
    for i in range(a.steps):
        t = 1 + i * 0.1
        x = 2 + 0.1 * i
        y = 1.0
        pose = PoseWithCovarianceStamped()
        pose.header.frame_id = 'room'
        stamp(pose.header, t)
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y
        pose.pose.pose.orientation.w = 1.0
        pose.pose.covariance[0] = pose.pose.covariance[7] = 0.01
        pose.pose.covariance[14] = 0.04
        optical.publish(pose)
        rclpy.spin_once(node, timeout_sec=0.03)
        scan = LaserScan()
        scan.header.frame_id = 'room'
        stamp(scan.header, t)
        center = math.atan2(y, x)
        scan.angle_min = center - 0.04
        scan.angle_increment = 0.01
        scan.angle_max = center + 0.04
        scan.range_min = 0.1
        scan.range_max = 10.0
        scan.scan_time = 0.1
        scan.ranges = [math.hypot(x, y) - 0.1] * 9
        lidar.publish(scan)
        if i < len(rows):
            row = rows[i]
            msg = DiagnosticArray()
            stamp(msg.header, float(row['onset_seconds']))
            msg.header.frame_id = 'sleep_recording'
            status = DiagnosticStatus()
            status.name = 'alex/sleep_epoch'
            status.hardware_id = row['session']
            status.message = row['stage']
            status.values = [KeyValue(key=k, value=str(v)) for (k, v) in row.items() if k not in ['session', 'stage']]
            msg.status = [status]
            sleep.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.07)
    for _ in range(10):
        rclpy.spin_once(node, timeout_sec=0.05)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()
