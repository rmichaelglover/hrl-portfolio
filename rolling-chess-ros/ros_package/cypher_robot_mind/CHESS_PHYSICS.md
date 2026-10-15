# Rolling Possibilities · Glover Labs

A ROS-hosted chess/physics experiment with a two-axis wooden maze, solid metal spheres, legal chess transitions, PGN replay, and explicit branch-count measurements.

## Run

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select cypher_robot_mind --symlink-install
source install/setup.bash
ros2 launch cypher_robot_mind chess_lab.launch.py
```

Open http://127.0.0.1:8877/ to observe. The launch prints a **private operator link** for board controls and saves its token with mode 0600 in `~/.ros/robot_in_loop/chess-8877.json`. This bench is independent of the robot's motor permission and voice-presence gates; it never enables the robot or sends its motor commands. It publishes `/rolling_chess/state` on the local ROS domain (default 71).

The installed `python-chess` dependency supplies standard chess legality and PGN handling. The tested local chess module is 1.10.0. Python 3.10, ROS 2 Humble and this dependency are available in the current workspace. The package does not vendor python-chess; its own upstream license applies to it.

## What the objects mean

- **White source fixture (“white hole”):** the selected piece's present square. This remains a chess piece until a move commits.
- **Dark destination wells (“black holes”):** that piece's legal landing squares in the current position. These are absorbing physical fixtures, not gravitational black holes.
- **White/black metal sphere:** a replenishable move token for White/Black. Entering a legal well commits that piece's chess move; it does not throw the piece away.
- **Fresh supply each ply:** a correctly colored reserve token exists at every ply, even after previous metal balls become stranded. A source blocked by old tokens or wood can prevent release, but cannot exhaust the supply. Retry creates a fresh attempt without changing the chess position.
- **Retained tokens:** stranded spheres obstruct later rolls; spheres that entered wells are retained below the board. Clearing the metal tray changes only the apparatus, never chess pieces or chess history.
- **Chess location markers:** piece shapes are visual representations, not three-dimensional collider pieces. The wooden partitions and stranded metal tokens are physical obstacles.

Legal captures remove exactly one opposing piece, including en passant. Castling moves the rook too. A promotion well alone leaves four legal identities; choose queen, rook, bishop or knight separately. Kings cannot be captured or discarded, and king safety is checked by the chess engine. Losing a queen is possible in ordinary chess; queens are valuable but are not required for a legal position.

## Coordinates and mechanics

The local x coordinate runs from file a toward h; y runs from rank 1 toward 8. With forward defined along board depth, **roll** produces left/right slope and **pitch** near/far slope. **Yaw** would rotate the board in its own plane and is not actuated here. These are declared body-axis conventions; changing which direction is called forward changes the names, not the two required tilt degrees of freedom.

The board is 0.8×0.8 m, squares 0.1 m, sphere radius 0.012 m, hole radius 0.034 m, and physics uses fixed 1/240 s substeps. A uniform solid sphere has I=2mr²/5, giving no-slip acceleration a=(5/7)g along an incline. The implementation projects gravity along the two local tilt axes, adds illustrative rolling resistance and linear damping, and resolves wooden wall, rail and retained-ball contacts with damped restitution. Tilt is limited to ±10° per axis; speed is capped at 0.55 m/s for this demonstration.

Assumptions: quasi-static board orientation, rigid geometry, sufficient traction for no-slip rolling, stationary stranded-ball obstacles, and an absorbing-well capture model. It omits board actuator inertia, full angular contact dynamics, slipping, sphere wear, measured metal/wood friction, and high-speed rim collisions. The display's axle fixtures do not add additional forces. This is a simple computational apparatus, not a calibrated material experiment.

Reference for rolling equations: [OpenStax, Rolling Motion](https://openstax.org/books/university-physics-volume-1/pages/11-1-rolling-motion). Chess API behavior follows the installed module and [python-chess core](https://python-chess.readthedocs.io/en/latest/core.html) and [PGN documentation](https://python-chess.readthedocs.io/en/latest/pgn.html).

## Controls

1. Select a mover's piece. Only pieces with legal moves are offered.
2. Tilt manually with the roll/pitch sliders, or focus the board and hold arrow keys. Releasing the keys levels the board. Leveling removes the slope; resistance brakes the ball over time.
3. Choose a legal destination and use **Roll selected move** to test the finite-grid route controller. It avoids other open wells where it can. An uncommanded well entered by a manual roll still commits that corresponding legal move.
4. **Roll next PGN ply** attempts the next imported reference move. The sample's ten plies, including castling, passed the numerical replay check. A different legal hole ends that reference continuation; it does not silently pretend the PGN move was played.
5. **Test legal candidates** clones the apparatus and evaluates each legal move without changing the actual game. It reports witnesses and unresolved attempts, retaining all legal branches.
6. **Treat selected hole as observed** supplies exact source and destination square evidence and shows how many legal transitions match it.
7. Export JSON for the starting FEN, reference PGN, committed FEN transitions, move repetition counts, quantized trace repetition, trajectory samples, full time-stamped tilt changes, and physical parameters.

## Search-space claim: what is demonstrated

| Evidence in the standard initial position | Compatible legal transitions |
| --- | ---: |
| No source/destination observation | 20 |
| Source known to be e2 | 2 |
| Source e2 and entry into e4 observed | 1 |

These are constraints for reconstructing the move associated with an observed physical event. They do not establish the best chess move or solve the rest of the game. A known PGN already supplies the answer; replay is a consistency test, not discovery. Supplying its destination to the experiment must not be counted as independent search speedup.

In the initial supplied maze, the finite controller found physical witnesses for **all 20** opening moves. Thus this first setup supplies **no additional opening-move exclusion from physical reachability**. Physical timing and path results can order tests. A timeout, blocked sampled route, or failed controller is **unresolved**, never proof that a legal chess move is impossible. The grid is sampled, and its failure is not a continuous-reachability certificate.

A restrictive maze can obstruct a legal knight move or other move. That is a property of the apparatus. Rejecting that move would define a different physical chess variant, so the present program keeps it in the legal chess set. Future pruning needs extra validated observations or sound apparatus-specific exclusion certificates and an explicit claim about which game those certificates apply to.

## Repetitions

- The move ledger counts repeated color/from/to/promotion transitions.
- Trajectories also have a separate 1 cm quantized geometric path signature and repetition counter. This is approximate movement similarity, not an exact phase-space recurrence.
- Chess-position repetitions use placement, side to move, castling rights and **legal** en-passant availability. Clocks and repeated physical gestures alone do not identify the chess position.
- Threefold repetition remains a claimable draw. Fivefold repetition is automatic. The chess engine also handles its other standard automatic terminal conditions.

## Validation

```bash
cd ~/ros2_ws/src/cypher_robot_mind
/usr/bin/python3 -m pytest test/test_chess_physics.py -q
```

The 11 physics/chess tests cover the solid-sphere acceleration factor, rest and damping, wood collision, falling wells, real e2–e4 integration, replenishment with stranded tokens, source/destination filtering, all four promotions, capture/en passant/castling material changes, pins and king safety, chess versus movement repetition, failed-maze non-pruning, PGN validation and export transitions. The original robot model/policy tests remain separate.

## Version 0.2 · real ROS console and whole-game autoplay

The live node now publishes native ROS topics:

| Topic | ROS type | Role |
| --- | --- | --- |
| `/rolling_chess/state` | `std_msgs/msg/String` | Game, physics, lifecycle and runtime snapshots |
| `/rolling_chess/command` | `std_msgs/msg/String` | Signed command requests from the web bridge |
| `/rolling_chess/events` | `std_msgs/msg/String` | Command acknowledgements/results |
| `/rolling_chess/markers` | `visualization_msgs/msg/MarkerArray` | Actual RViz board, maze, piece shapes and metal spheres |
| `/tf` | `tf2_msgs/msg/TFMessage` | Tilting `map → chess_board` transform |

HTTP control requests are handled by the ROS command subscriber before acknowledgement. State and native RViz geometry publish at 10 Hz; physics still uses 240 Hz substeps. The web console displays actual node/topic names, ROS clock, publication sequence and subscriber count. Its public-hosted HTML is a client of this backend, not an embedded ROS emulator. If the backend is offline, it reports that condition instead of claiming a live connection.

```bash
ros2 launch cypher_robot_mind chess_lab.launch.py rviz:=true
```

The default is **whole-game autoplay with small seeded randomness on**. The live console starts another game after a ten-second end-of-game pause; Pause autoplay cancels that repeat. A visible checkbox disables both the ±12 centipawn move-order perturbation and ±0.0015 rad (about 0.086°) per-axis injected tilt perturbation. With noise off, future choices are deterministic given the current state and history; toggling does not undo previous moves. `New game` resets to the standard initial position. Autoplay uses a small two-ply material/development policy, not a strong or optimal engine. A loaded PGN main line is replayed first, then the policy continues. The player policy may claim a valid threefold/fifty-move draw; automatic terminal rules also remain in effect in standard mode.

Complete numerical games from the normal initial position, seed 2026, passed:

- Randomness on: White checkmated Black after **65 plies**, zero blocked-motion attempts.
- Randomness off: a valid fifty-move draw was claimed after **161 plies**, zero blocked-motion attempts.

Public viewers may use the bounded autoplay, restart and randomness controls by default. They share one live game, so those controls affect the same board for everyone. Apparatus changes, arbitrary PGN imports, merger edits and capture searches remain private operator controls. Launch with `public_playback:=false` to require the private token for all controls, or `autoplay:=false` for a stationary manual bench. These permissions are scoped only to the chess simulator; they do not enable or expose the separate robot motor/voice endpoints.

## Merger and event-horizon rules

These are explicit fictional topological rules, not general-relativistic black/white-hole models:

| Merger | Defined behavior |
| --- | --- |
| Black + black | Distinct destination mouths share a basin policy. Default: the arriving piece is imprisoned. No pieces are fused or discarded. |
| White + white | Stable source identities share a policy. Imprisonment can hold the individual pieces at their existing squares; they remain distinct. |
| Black → white | Directed release relay: entry into that basin frees the linked source group. It does not teleport or resurrect anything. |

The default same-role policy is **imprison until explicitly released**, as requested. Alternatives are restricting future destinations to the group's member squares, releasing group members, or recording associations without changing current mobility. A basin merger joins the policy/reservoir below its mouths; it does not deform the wooden surface or create a traversable corridor through it.

Each piece has independent state dimensions:

- **Existence:** on-board or captured. A capture is completed only by an actual legal capture. Captured records persist and cannot be released back onto the board.
- **Mobility:** free, constrained, imprisoned, or not applicable after capture.
- **Topology:** ordinary or singularity-associated, with a basin and horizon-entry/release record.
- **Exposure:** geometrically attacked, capturable by a currently legal move, or no current capture established. Pinned attack geometry and actual legal capture availability are reported separately. Kings use check/checkmate and are never captured.

Merger annotations can be inspected in standard mode. Turn on **Enforce mobility constraints as a chess variant** to filter the standard legal move set. Standard king-safety geometry is retained. The castling rook must also satisfy mobility constraints. A lack of variant moves is reported as blocked; it is not silently declared ordinary checkmate. Variant draw rules are not inferred from the baseline chess engine's repetition counters.

### A horizon entry is not a capture proof

`Captured` means the legal event already happened. `Capture available now` means a legal capture could be chosen now, not that the player will choose it. `Imprisoned` alone does not imply an eventual capture. The bounded capture inspector tests whether the opposing player **can force** the selected non-king's capture within 1–4 plies against every allowed defensive response. It reports a proof within that finite symbolic horizon, a failure to force within that horizon, or an exhausted node budget. It respects mobility constraints when enabled and preserves standard draw claims when checking standard chess. Its proof does not include successful execution of every future physical controller route.

**No “almost-sure” probability is fabricated.** Such a label would require a specified stochastic transition/policy model and evidence that the probability of eventually entering the capture-absorbing state is 1. A bounded deterministic forcing result, a physically stuck ball, and a statistical likelihood are different claims.

### Additional state in search and repetition

Stable piece identities survive movement and promotion. Symbolic signatures include piece identities, existence/mobility/topology, merger membership and policy, directed release links, ordinary chess rights and the enforcement mode. Merger order does not change a canonically equivalent signature. Baseline FEN repetitions are shown only as diagnostics in variant mode; they do not establish a variant draw.

The separate exact apparatus diagnostic key also includes wood geometry, active-ball position/velocity/falling state, stranded colliders, tilt, source selection, promotion, active controller/player state and random-generator states. It ignores serial numbers and inert below-board tokens because those do not change future physical behavior in the unlimited-reserve model. No transposition pruning is currently performed using that key, and the 1 cm quantized trajectory-repeat counter is never substituted for exact physical state.
