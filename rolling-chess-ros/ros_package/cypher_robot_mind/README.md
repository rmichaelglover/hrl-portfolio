# Robot in the Loop · Glover Labs

The separate [Rolling Possibilities chess/physics bench](CHESS_PHYSICS.md) tests metal spheres, a two-axis wooden maze, legal chess moves and PGN replay. Run it with `ros2 launch cypher_robot_mind chess_lab.launch.py`; it does not enable robot motion.

Version 0.2 includes a live ROS chess console with whole-game autoplay, actual RViz geometry, public playback controls, an easy randomness switch, and explicit merger/lifecycle constraints. See [the chess guide](CHESS_PHYSICS.md).

A runnable ROS 2 Humble virtual robot prototype. Cypher has simulated range sensing and odometry, Bayesian occupancy mapping, constant-velocity Kalman tracks, hierarchical relaxation labeling (HRL), bounded adaptive attention, and belief-based route planning. Its humanoid appearance is a display; motion uses a simple holonomic kinematic model. It does not play legal chess yet or ingest real camera perception.

## Run

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select cypher_robot_mind --symlink-install
source install/setup.bash
ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=71 ros2 launch cypher_robot_mind robot.launch.py port:=8876
```

Open http://127.0.0.1:8876/ to observe or stop. The launch output prints separate **private basic and admin operator links**. Current session credentials are also saved with mode 0600 to `~/.ros/robot_in_loop/operators-8876.json`. Open the appropriate link on this computer; its fragment token is moved into tab session storage. Do not share the admin link. Add `rviz:=true` to launch the RViz 3D view, or run:

```bash
rviz2 -d ~/ros2_ws/src/cypher_robot_mind/config/mind.rviz
```

The dashboard provides a 2.5D world, top-down view, belief map, HRL regional interpretation, attention activity, and decision journal. Task commands use locally processed microphone audio: prepare the phrase, press Record, then say it during the six-second recording. To start, say `robot go` (shown as “Start goal mission” in the menu). Commands are `robot go`, `robot wake`, `robot present`, `robot sleep`, `robot reset`, or `robot disturb`, followed by the displayed four-word challenge. `stop` and `shutdown` also work without speaking a challenge. Audio stays on this computer and is not saved. Offline recognition uses installed Ubuntu PocketSphinx 0.8 libraries and English models (`libpocketsphinx3`, `libsphinxbase3`, `pocketsphinx-en-us`); no cloud speech service is used.

## Permission and presence behavior

- **Anyone:** stop or shutdown, by voice or the public emergency controls. Stop clears mission authority and sleeps; shutdown enters simulated hibernation.
- **Basic authorization:** wake, sleep, or renew voice presence. The robot does not infer whether a person is “reasonable” from personal traits.
- **High authorization:** start the specific goal mission, reset the world, or change the simulated obstacle.
- Motion starts disabled. A start grants at most 90 seconds toward the displayed goal, and voice presence expires after 30 seconds. Say a fresh `robot present` challenge to renew presence.
- Missing voice-presence evidence cancels the mission and sleeps. After **900 seconds (15 minutes)** sleeping, it enters simulated hibernation. Waking never resumes a cancelled mission; a new high-authority start is necessary.
- Commands are HMAC authenticated, expire after five seconds, and reject replay. The launch supplies an ephemeral signing secret to the world and dashboard. Browser starts cannot bypass speech by calling a text start endpoint.
- Motor commands have a 750 ms watchdog. The mind commands zero velocity if pose/range evidence is older than 600 ms. Collision geometry is enforced by the simulator independently of the planner.

Voice recognition is **not speaker verification, human-liveness verification, or proof of physical hearing distance**. Recorded or synthesized speech may be recognized. The random spoken challenge limits straightforward reuse of old task utterances; it is not an anti-spoofing guarantee. Silence is treated conservatively as expired evidence, not proof that no human is present. General speech that is not recognized as a supported command does not grant permission. The local authenticated session supplies the role, not the sound of the speaker. Public stop intentionally allows any local viewer to interrupt.

This is a local simulation, not a certified safety controller. DDS participants run in a trusted local ROS environment; signing does not secure all sensor topics, prevent denial of service, or protect against a compromised host/signing process. SROS2/DDS security, enrolled identity/liveness checks, measured acoustic proximity, real hardware interlocks, and task-specific validation are future integration work. Nothing here controls banking systems, nuclear equipment, physical robots, or the computer's power state.

## ROS graph

All topics live under `/cypher`:

| Producer | Topics | Consumer |
| --- | --- | --- |
| World | `scan` (`LaserScan`), `odom` (`Odometry`), `hazard_detection` (`PoseWithCovarianceStamped`), `goal` (`PoseStamped`), `episode`, `operator_state` | Mind |
| Mind | `cmd_vel` (`Twist`, world-aligned x/y metres/second) | World's independent permission gate |
| Mind | `belief_map` (`OccupancyGrid`), `plan` (`Path`), `mind` (JSON `String`) | RViz / dashboard |
| Dashboard | `operator_command` (signed JSON `String`) | World command gate |
| World | `world_truth` (JSON `String`) | Display nodes only; never the mind |
| View | `visualization` (`MarkerArray`) | RViz |

The map frame is `map`, and simulated sensors are aligned with `base_link`; a pose TF is published for range visualization. Simulation runs at approximately real time on wall-clock ROS time; it does not publish `/clock` or require `use_sim_time`.

## HRL and criticality

`cypher_robot_mind/relaxation.py` is copied verbatim from `Code/hrl-portfolio/hrl/core.py` by R. Michael Glover, under the included MIRL-1.0 license. A small local scene plus nine region objects forms a single compatibility field with parent–child and spatial edges. Respected priors and an explicit unknown label reduce unsupported certainty. Contextual label strengths are distinct from Bayesian occupancy probabilities.

Attention is a bounded excitation model with local homeostatic gain adjustment. Surprise seeds activity across nine regions, and activity recruits a larger HRL iteration budget. This is a **criticality-inspired experiment, not evidence of self-organized criticality**, a measured branching ratio, or demonstrated cognitive superiority. No learning of control policies is claimed; HRL means hierarchical relaxation labeling here, not hierarchical reinforcement learning.

## Checks

```bash
cd ~/ros2_ws/src/cypher_robot_mind
source /opt/ros/humble/setup.bash
/usr/bin/python3 -m pytest test -q
```

Tests cover Bayesian updates, Kalman covariance and tracking, hierarchical interpretation, obstacle-aware planning, bounded attention, authorization/replay behavior, permission roles, and presence/sleep/hibernation transitions with a fake clock. Live ROS and browser checks are described in `VALIDATION.md` once run.
