#!/usr/bin/env python3
"""Read back serialized ROS 2 bag messages without launching DDS."""
import argparse, json
from collections import Counter
from pathlib import Path
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

def main():
    p = argparse.ArgumentParser()
    p.add_argument('bag')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=a.bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    types = {t.name: get_message(t.type) for t in reader.get_all_topics_and_types()}
    counts = Counter()
    rem = 0
    while reader.has_next():
        (topic, data, received) = reader.read_next()
        msg = deserialize_message(data, types[topic])
        counts[topic] += 1
        if topic == '/alex/sleep/epochs':
            for status in msg.status:
                values = {v.key: v.value for v in status.values}
                assert float(values['duration_seconds']) > 0
                rem += status.message == 'REM'
    assert counts['/alex/mocap/pose'] == 30 and counts['/alex/lidar/scan'] == 30
    assert counts['/alex/tracking/status'] >= 10
    report = dict(recorded_messages=sum(counts.values()), topic_counts=dict(counts), scored_rem_messages=rem)
    if a.output:
        a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
if __name__ == '__main__':
    main()
