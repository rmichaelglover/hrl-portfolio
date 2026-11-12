# Passive observation: ROS 2, movement, and real sleep physiology

Originating framework and direction: **Michael Emanuel Glover**.
Assistant contribution: C++ observation core, ROS 2 adapters, EDF extraction,
replay, verification, and exposition. No hardware is needed for this milestone.

## What actually runs

The installed ROS 2 distribution is **Humble**. The `alex_observation` package
builds a C++ subscriber using the installed ROS message definitions. The core
`include/study_observer.hpp` remains independent of ROS and is covered by CTest.
A Python publisher sends synthetic optical poses and planar lidar scans through
real DDS topics. Optional measured sleep epochs travel through a separate topic.
The acceptance runner records the graph into a real SQLite rosbag2 bag.

```
synthetic room trajectory → optical PoseWithCovarianceStamped ─┐
synthetic surface returns → LaserScan ─────────────────────────┤
                                      passive C++ observer → tracking status
local PSG EDF + scored epochs → calibrated EOG features → separate sleep topic
```

The observer owns external measurement state. It has no Person reference and
no command path into Alex's Body, Will, objectives, or self-model. The simulation
therefore injects no disturbance from being tracked. This is a scenario
assumption, not a measured statement about a real participant's comfort.
The external tracker is distinct from Alex's internal subjective map.

## Build and replay

From the Virtual Cell project root:

```sh
source /opt/ros/humble/setup.bash
colcon build --base-paths ros2 --build-base /tmp/alex-build \
  --install-base /tmp/alex-install --packages-select alex_observation
source /tmp/alex-install/setup.bash
ros2 run alex_observation observer_node
```

In another terminal with ROS sourced:

```sh
python3 experiments/observation/replay.py --steps 30
```

The normal CMake build still needs only C++17 and CMake. ROS is an optional
adapter; EDF extraction additionally uses NumPy, SciPy, and Matplotlib.

| Topic | Message | Contract |
|---|---|---|
| `/alex/mocap/pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | Synthetic optical position in meters, `room` frame, session-relative source time |
| `/alex/lidar/scan` | `sensor_msgs/msg/LaserScan` | Synthetic planar returns, radians/meters, same calibrated room origin |
| `/alex/tracking/status` | `diagnostic_msgs/msg/DiagnosticArray` | Fresh optical evidence and number of nearby valid returns |
| `/alex/sleep/epochs` | `diagnostic_msgs/msg/DiagnosticArray` | Separate recording ID, relative onset, duration, scored stage, calibrated EOG features |

The diagnostic sleep payload requires `onset_seconds`, `duration_seconds`,
`eog_left_rms_uv`, and `eog_right_rms_uv`. The status name is
`alex/sleep_epoch`, hardware ID carries the recording session, and the message
carries its scored stage. This is an explicit small payload convention, not a
standard ROS sleep-message definition. The C++ receiver constructs and validates
a typed `SleepEpoch` value. Raw voltage samples remain available in the EDF.

The tracker rejects frame/session mismatches and reversed optical timestamps.
Scans require an optical pose no older than .25 seconds. Invalid/missing ranges
are discarded. A .5-meter association gate counts surface returns near that pose;
it does not identify a person from lidar alone or shift a body center to a
biased surface centroid. Position variance is retained from the optical input;
there is no claim of optimal covariance fusion. The prototype consumes a scalar
position variance, not the complete 6×6 covariance or orientation estimate.

ROS uses X forward, Y left, Z up. The existing optical model uses Z forward and
X right: an eventual calibrated adapter must convert coordinates as
`optical(x,y,z) = ROS(-y,z,x)`, with matching orientation and covariance transforms.
This observer does not silently rewrite eye poses from external tracking data.
A hardware driver would require timestamp alignment, calibration/TF transforms,
and identity association; these are explicit extension interfaces.

Replay emits all scan rays at one source timestamp and assumes a stationary
scanner. It does not implement scan deskew. Bag receive times, motion-session
source times, and sleep-recording source times are different clock domains.
No `/clock` or historical wall-time reconstruction is implied. Sleep replay is
accelerated transport of labeled epochs, not a speeded-up physiological model.

## Real local sleep data

`sleep_extract.py` reads the existing local PSG and scoring files without
copying patient header fields or raw recordings into this project. It extracts
physical microvolts from fixed-record little-endian EDF using each channel's
physical and digital calibration extrema. Both `E1-M2` and `E2-M2` channels are
present in the inspected recording.

The scored stage codebook is derived by joining scorer event-stage names to
matching epoch numbers. Conflicting names fail explicitly; unrecognized codes
remain Unknown. Thirty-second epoch spacing is checked against clock times,
including midnight rollover. Alignment uses the PSG's header start clock and
its own scoring clock, not a delay for a separate HDP device. Source-file SHA-256
hashes, the derived codebook, incomplete-window counts, and timing offset are
saved in the local manifest.

Example invocation, using paths to the existing local inputs:

```sh
python3 experiments/observation/sleep_extract.py \
  --edf /path/to/study_psg.edf \
  --stages /path/to/study_sleepstage.csv \
  --events /path/to/study_events.csv \
  --output /path/outside/public-project/sleep-session \
  --session local-sleep-session-1
```

Each complete epoch receives two .3–5 Hz band-filtered EOG RMS values and two
slope-RMS values (µV and µV/s), plus raw peak-to-peak amplitude and flatline flags.
A flat signal remains a data-quality flag; it is not inferred to mean peaceful
rest, absent eye motion, or a different scored sleep stage. The third-order Butterworth filter is applied
forward/backward within each offline epoch. Its boundary effects and noncausal
operation matter for future real-time work; this is an offline feature extractor.
The filter band is a proposed exploratory choice, not a validated REM detector.
These electrical measurements do not determine calibrated eyeball rotation,
dream content, or a diagnosis. Reference REM labels remain separate from EOG
features: no classifier is trained on its own reference label.

Actual local extraction, figures, manifests, feature CSVs, and mixed-data bags
are stored outside the published source tree. Public artifacts contain code,
the synthetic protocol, and synthetic unit-test fixtures. The real sleep
recording is not represented as a measurement of the fictional Alex or as
simultaneous optical/lidar capture.

## Acceptance test and bag

```sh
python3 experiments/observation/smoke_test.py \
  --observer /tmp/alex-install/alex_observation/lib/alex_observation/observer_node \
  --output /path/to/new-local-run \
  --epochs /path/to/local-sleep-session/epochs.csv
ros2 bag info /path/to/new-local-run/bag
python3 experiments/observation/verify_bag.py /path/to/new-local-run/bag
```

Use a fresh output directory. The test uses a local-only ROS domain (173), starts
the actual C++ observer and rosbag recorder, then publishes 30 poses and scans.
When supplied a real feature CSV, it selects the first scored REM epoch and
replays up to 30 subsequent epochs in their original order and relative timing
fields. The graph test verifies tracking reports and passage of REM-reference
messages. It does not infer synchronization between those independent sessions.
Source timestamps are retained even though publication is accelerated.

`python3 -m unittest discover -s experiments/observation -p 'test_*.py' -v`
checks calibrated EDF channel extraction across record boundaries, stage-code
conflicts, EOG band response, and midnight arithmetic. C++ tests cover stale
tracking, session/frame rejection, invalid ranges, epoch validation, and
reflective-practice bookkeeping.

## Melody, context, and mantras

Alex's `PersonModel` now owns a `ReflectivePractice` by value. A musical-context
revision stores an explicit contextual description and revisable attention
weight. It is a first motivation interface, not an audio-language recognizer
or an objective measure of beauty. It does not assert that appreciation must
converge to a final perfect model. These state variables are available to a
future attention policy; the current household action scores are not yet
conditioned on musical-context revisions.

```cpp
alex.reflection().revise_musical_context(.8, "hearing melody in a new context");
alex.reflection().say(mind::flowers_mantra());
// Happiness reward counter increments by one in this explicit scenario rule.
```

The remembered mantra is Michael's wording: “There are always flowers, for those
who choose to see.” Its attribution to Henri Matisse is stored as an attribution;
the exact historical wording and occasion are not asserted as verified.
Health support, happiness, knowledge, and good are named reflective reward
counters. Incrementing them does not modify assay measurements, physiological
health, or empirical knowledge automatically. Counter changes are proposed
reinforcement signals and are not independent evidence of a health benefit.

Melody's changing context motivates open-ended modeling. It supplies no theorem
about prime-number prediction; exact prime-generation algorithms remain a
separate mathematical fact.

## Primary technical references

- Installed ROS 2 Humble message definitions are the implementation contract;
  [ROS geometry interfaces](https://github.com/ros2/common_interfaces/tree/humble/geometry_msgs/msg)
  and [LaserScan definition](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg).
- [rosbag2](https://github.com/ros2/rosbag2/tree/humble): record/replay transport.
- [EDF specification](https://www.edfplus.info/specs/edf.html): channel scaling and fixed-record layout.
- [PhysioNet Sleep-EDF Expanded](https://physionet.org/content/sleep-edfx/1.0.0/):
  an optional public future source with EOG and independently scored sleep stages;
  it is distinct from the local PSG actually processed here.
