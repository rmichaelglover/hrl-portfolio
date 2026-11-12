#!/usr/bin/env python3
"""End-to-end ROS 2 graph test; outputs and optional real data stay local."""
from pathlib import Path
import argparse, csv, json, os, signal, subprocess, sys, time
import rclpy
from rclpy.node import Node
from diagnostic_msgs.msg import DiagnosticArray

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--observer', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--epochs', type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    os.environ['ROS_LOCALHOST_ONLY'] = '1'
    os.environ['ROS_DOMAIN_ID'] = '173'
    os.environ['ROS_LOG_DIR'] = str(a.output / 'ros_logs')
    rclpy.init()
    node = Node('alex_graph_acceptance')
    reports = []
    sleep = []

    def status(m):
        reports.extend(m.status)

    def epochs(m):
        sleep.extend(m.status)
    sub = node.create_subscription(DiagnosticArray, '/alex/tracking/status', status, 10)
    ss = node.create_subscription(DiagnosticArray, '/alex/sleep/epochs', epochs, 10)
    processes = []
    handles = []
    try:
        log = (a.output / 'observer.log').open('w')
        handles.append(log)
        observer = subprocess.Popen([a.observer], stdout=log, stderr=subprocess.STDOUT)
        processes.append(observer)
        baglog = (a.output / 'bag.log').open('w')
        handles.append(baglog)
        bag = subprocess.Popen(['ros2', 'bag', 'record', '-o', str(a.output / 'bag'), '/alex/mocap/pose', '/alex/lidar/scan', '/alex/tracking/status', '/alex/sleep/epochs'], stdout=baglog, stderr=subprocess.STDOUT)
        processes.append(bag)
        for _ in range(30):
            rclpy.spin_once(node, timeout_sec=0.1)
        cmd = [sys.executable, str(Path(__file__).with_name('replay.py')), '--steps', '30']
        if a.epochs:
            with a.epochs.open() as f:
                rows = list(csv.DictReader(f))
            first = next((i for (i, r) in enumerate(rows) if r['stage'] == 'REM'))
            cmd += ['--epochs', str(a.epochs), '--sleep-start-epoch', str(first)]
        replay = subprocess.Popen(cmd)
        processes.append(replay)
        deadline = time.monotonic() + 30
        while replay.poll() is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        if replay.poll() is None:
            raise RuntimeError('Replay timed out')
        if replay.returncode:
            raise RuntimeError('Replay failed')
        for _ in range(10):
            rclpy.spin_once(node, timeout_sec=0.1)
        counts = [int(v.value) for s in reports for v in s.values if v.key == 'nearby_lidar_returns']
        assert len(reports) >= 10 and max(counts) > 0, 'No supported track reports'
        if a.epochs:
            assert any((s.message == 'REM' for s in sleep)), 'No real REM epoch crossed ROS topics'
        result = dict(tracking_reports=len(reports), max_nearby_returns=max(counts), sleep_messages=len(sleep), contains_scored_rem=any((s.message == 'REM' for s in sleep)), motion_source='synthetic', sleep_source='local measured recording' if a.epochs else 'none', cross_session_fusion=False, tracking_disturbance_injected=False)
        (a.output / 'acceptance.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
    finally:
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        for h in handles:
            h.close()
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()
