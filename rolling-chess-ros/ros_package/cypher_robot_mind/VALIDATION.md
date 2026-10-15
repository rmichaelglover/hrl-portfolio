# Validation · 2026-10-15

## Build and model tests

- `colcon build --packages-select cypher_robot_mind --symlink-install` completed.
- `/usr/bin/python3 -m pytest test -q`: **11 passed**.
- Vendored HRL engine matches `Code/hrl-portfolio/hrl/core.py` byte for byte.
- Python modules and launch file compile.

Tests cover Bayesian occupancy and maximum-range handling, Kalman tracking and covariance, local/region HRL fields and unknown strengths, obstacle-aware planning, bounded attention, role permissions, HMAC tampering/expiry/replay, voice challenge comparison, silence rejection, and absence/sleep/hibernation timing. The 900-second hibernation interval is tested with an injected clock, not a real 15-minute wait.

## Live ROS and offline speech

Launched four ROS 2 Humble nodes on localhost, domain 71, dashboard port 8876. `test/live_check.py` exercised the real HTTP → offline recognizer → signed ROS command → world permission gate → sensor/mind/control loop:

- Stationary without authorization; direct HTTP text start rejected.
- Correctly recognized mission speech from a basic-role session rejected.
- High-role generated speech command started actual virtual motion and live beliefs.
- Public unauthenticated emergency stop halted motion; shutdown entered simulated hibernation.
- Basic-role voice wake did not resume the task.
- Final corrected-clearance run reached the goal with **zero blocked-motion attempts**.
- A separate unrenewed mission lost permission after the 30-second voice-presence interval.
- Left the simulation hibernating.

Generated eSpeak audio was used as a reproducible test fixture. No live microphone was activated. Recognition of synthesized speech directly demonstrates why voice recognition must not be described as human-liveness verification. Some utterances are rejected or misrecognized; the challenge/role gate must match before a task command can proceed. Human microphone recognition quality remains unmeasured.

An earlier run stopped with no route because full-cell obstacle inflation erased corridors. The final model uses geometric clearance at grid-cell centres and a short-range sensor guard; the revised route passed. No physical-world safety claim follows from this simulated trial.

## Browser

Chrome checks at 1440×1200 and 390×844 passed: live ROS connection status, observer role, nine-region display, all three world views, current-view button states, microphone preparation without activating audio, responsive stacking, and no horizontal overflow or JavaScript exceptions. Desktop and mobile screenshots were inspected/generated under `/tmp/robot-loop-*.png`.

RViz configuration and MarkerArray/OccupancyGrid/Path publishers are included. The RViz GUI itself was not launched during validation.

## Reproduce live check

With the simulator running on port 8876:

```bash
python3 ~/ros2_ws/src/cypher_robot_mind/test/live_check.py
```

Requires local eSpeak and reads the current private operator credentials from `~/.ros/robot_in_loop/operators-8876.json`. It changes only the simulation, uses generated speech instead of a microphone, and ends with public shutdown. Do not run it during an operator's active demonstration.


# Version 0.2 validation · 2026-10-15

- 38 automated tests pass after sourcing ROS Humble, including rolling-chess, topology/lifecycle, capture forecasts, autoplay/repeat behavior and native RViz geometry.
- Full numerical policy games: randomness on, White checkmate after 65 plies; randomness off, valid fifty-move draw claim after 161 plies. Both had zero blocked-motion attempts.
- An independent ROS subscriber received `/rolling_chess/state`, native MarkerArray geometry, the actual signed command topic and acknowledgement events.
- Public HTTPS state, the explicit origin allowlist, anonymous bounded playback/randomness controls and private setup controls passed.
- Black-black imprisonment, white-white source grouping, black-white release relays, finite-horizon capture checks and explicit release passed through the live ROS command path.
- Native RViz GUI was not launched; its actual message geometry and board transform were tested without a display.
