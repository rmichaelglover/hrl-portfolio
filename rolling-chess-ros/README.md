# Rolling Possibilities · ROS Console 0.2

**[Open the live console](https://rmichaelglover.github.io/hrl-portfolio/rolling-chess-ros/)** · **[Download the ROS package](cypher_robot_mind-0.2.0.zip)** · [Detailed physics/merger guide](ros_package/cypher_robot_mind/CHESS_PHYSICS.md)

A real ROS 2 Humble node runs the rolling chess simulation. The public page connects to its HTTPS endpoint and shows the node, topics, ROS clock and publication sequence. Browser control commands cross the native ROS command topic and receive ROS acknowledgements. The node also publishes a real RViz scene and board transform. The page does not claim ROS is running inside the browser.

Watch a whole game, pause/resume, start a new game, or turn **Injected randomness** off with the prominent checkbox. It is on by default, with seed 2026. A new game begins after a ten-second end-of-game pause; pausing cancels the repeat. Everyone shares the same live board, so public playback changes are shared. Full apparatus, PGN, merger and capture-search controls require the host's private operator link.

The live backend runs on the host machine behind an HTTPS tunnel. That machine, ROS process and tunnel must remain online. The public client explicitly reports backend disconnection. The source package and validation artifacts remain available even when the live host is offline.

## Run your own ROS instance

Unzip the package into a ROS 2 workspace's `src` directory, then:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select cypher_robot_mind --symlink-install
source install/setup.bash
ros2 launch cypher_robot_mind chess_lab.launch.py
```

Open http://127.0.0.1:8877/. Add `rviz:=true` for native RViz, `autoplay:=false` for a manual apparatus, or `public_playback:=false` to require an operator token for every control. Dependencies include Python 3.10, ROS 2 Humble, numpy and the installed python-chess module. See the package guide for permissions and modeling assumptions. No robot motor/voice endpoints are exposed by this chess console.

## What is modeled

- An 80 cm wooden chessboard/maze with roll and pitch, fixed 240 Hz substeps, replenishable white/black solid-metal move tokens, resistance and damped collisions.
- Legal chess, king safety, castling, en passant, four promotions, material conservation, and separate movement/position repetition ledgers.
- Shaped pieces in the web view and native RViz `MarkerArray` geometry.
- Black/black basin mergers, white/white source groups, and directed black/white release relays.
- Stable piece identities, imprisonment/constrained/free mobility, captured records, and bounded adversarial capture forecasts.
- Exact square-observation filtering and physical-rollout ordering. A rollout failure never proves an ordinary legal move impossible.

The holes are fictional source/destination fixtures, not general-relativistic objects. A horizon entry or imprisonment does not by itself establish capture. No almost-sure capture probability is invented. Merger mobility constraints are an explicit opt-in variant; standard chess and variant-state diagnostics remain separate.

## Actual ROS graph

| Topic | Type |
| --- | --- |
| `/rolling_chess/state` | `std_msgs/msg/String` |
| `/rolling_chess/command` | `std_msgs/msg/String` |
| `/rolling_chess/events` | `std_msgs/msg/String` |
| `/rolling_chess/markers` | `visualization_msgs/msg/MarkerArray` |
| `/tf` | `tf2_msgs/msg/TFMessage` |

## Validation

- **38 automated tests passed**, including physical rolling, material changes, repetition, merger lifecycle, bounded capture analysis, autoplay and real ROS message geometry.
- An independent ROS node received actual state, markers, command requests and acknowledgement messages.
- HTTPS live state, public randomness controls, private apparatus controls, merger imprisonment/release and bounded capture were exercised end to end.
- The physics policy completed two games from the normal initial position: **65 plies to White checkmate with randomness on**, and **161 plies to a valid fifty-move draw claim with randomness off**, both with zero blocked-motion attempts.

The following are accelerated numerical model runs, not recordings of a ROS subscriber or claims of strong chess play:

- [Validated game, randomness on](validated-random.pgn)
- [Validated game, randomness off](validated-deterministic.pgn)
- [Whole-game numerical results](whole-game-validation.json)

The deterministic PGN records the intended move supporting its prospective fifty-move draw claim. A known PGN replay is a consistency test, not discovery or proof of faster chess search. In the initial apparatus, all 20 opening moves had physical witnesses; the demonstrated 20 → 2 → 1 branch reduction comes from known source and observed destination evidence.

Glover Labs · R. Michael Glover & Cypher · [License](LICENSE)
