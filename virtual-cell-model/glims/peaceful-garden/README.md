# Room for Everyone — Virtual Person's peaceful joint preferences

Originating concept, named characters, peaceful chess analogy, and direction:
**Michael Emanuel Glover**. Assistant: implementation, interface, and verification.

Alex retains the original Virtual Person's preference for prosthetic support.
The extension represents Alex, Rosy, Mama, Papa, and Cypher as people with their
own destinations and rose interests. A joint planner anticipates their preferred
next actions, routes around residents who may stay, and scores compatible joint
moves. Waiting, detouring, and pausing are available; captures are absent.

## Chess evidence and transfer

`source-game.pgn` contains three games from the portfolio's existing archives:
DItWyjG9 (51 plies), LEHEVWbn (38), and WC1AuJwO (91). All 180 recorded moves
pass python-chess legal-move checks. The first and third feature mannyfresher.
The profile retains game identities and SHA-256 of the exact PGN input.

For N recorded plies, q is the non-capture fraction. For each resulting board,
a is the fraction of legal replies landing on squares attacked by the preceding
mover, averaged across all plies. Empty reply sets contribute zero.
Progress weight = 1+q; anticipation weight = 1+a. Here q=0.755556 and a=0.282823.
The mapping is explicitly designed, not fitted or an inference about the players'
personalities. Protecting frogs, personal-space clearance, and enjoying roses are
Michael's authored world values. More PGNs can inform the same aggregate profile.
No claim of improved planning performance from these mappings is made yet.

## Joint decision rule

Every turn, each person proposes staying or one cardinal grid step. Routes use
shortest grid distances respecting hedges and others' current occupied space.
The planner evaluates up to 5^5 = 3,125 combinations. Individual utility rewards
progress and up to two rose pauses; idle waiting away from goals has a small cost.
Joint score is summed utility plus 0.2 times the least utility, minus the
chess-informed weight times obstructions of other people's preferred destinations.
A rotating tie priority avoids assigning every equal tie to Alex. This is a
centralized one-step coordination model; preferences are not private or inferred.
It is not a general guarantee of fairness, completion, or optimality.

A hard feasibility check measures the minimum separation along two simultaneous
linear moves: people remain at least 0.75 grid units apart and at least 0.65 from
the frog's complete scripted hop. Stationary residents participate in the check.
Swaps and crossing trajectories are rejected, not just coincident endpoints.
If no joint action passes, no movement is committed and the ROS node pauses.
The frog follows a known modeled trajectory. The clearance result applies to
these exact simulated trajectories and radii.

## Measured scenario

The deterministic 40-turn record brings all five people to their destinations by
turn 24. Alex and Rosy each pause twice at roses. All turns preserve pairwise
and frog clearance. Six behavioral tests cover crossing/swaps, complete replay
and arrivals, frog edge swaps, preference changes, PGN-derived weight changes,
and no-action behavior. The browser displays the computed replay, with actual
and preferred actions for each selected turn; it does not run a planner or connect
to ROS telemetry.

## Reproduce

Install Python 3 and python-chess; no API is involved.

```sh
python3 export_replay.py --pgn source-game.pgn --output . --turns 40
python3 -m unittest -v test_peaceful.py
g++ -std=c++17 -Wall -Wextra -pedantic virtual_person.cpp -o /tmp/virtual_person
/tmp/virtual_person
```

`export_replay.py` regenerates the profile, trace, and C++ constants. C++ is the
small teaching example; `peaceful.py` is the full joint planner. ROS uses that
same Python module. The C++ lesson demonstrates compatibility and yielding,
not the whole five-person search.

## ROS2 integration

Source additions are also published in
`rolling-chess-ros/ros_package/cypher_robot_mind/`. In the local ROS2 workspace:

```sh
source /opt/ros/humble/setup.bash
colcon build --packages-select cypher_robot_mind --symlink-install
source install/setup.bash
ros2 run cypher_robot_mind peaceful_garden
ros2 topic echo /peaceful_garden/state
ros2 service call /peaceful_garden/pause std_srvs/srv/SetBool '{data: true}'
ros2 service call /peaceful_garden/reset std_srvs/srv/Trigger '{}'
```

The profile path is a ROS parameter, `profile`. A different exported profile can
be supplied with `--ros-args -p profile:=/absolute/path/chess-profile.json`.
The separate node publishes modeled state every half-second and supports pause
and reset. It does not issue `cmd_vel` or change the existing world authorization.
Live local ROS checks verified state delivery, pause with frozen tick, and reset.
