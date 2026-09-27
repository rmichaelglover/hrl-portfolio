# Super Monkey Chessballs · Tri-Engine

A tiny C++17 prototype for the story’s three coupled systems:

1. **Marble physics** — gravity, attraction toward a luminous triangle, wall bounce, and ball-ball collision.
2. **Chess story** — a deterministic Crazyhouse-flavored move ribbon from Captain Bananas’ extra-ball gambit.
3. **Render bridge** — newline-delimited JSON snapshots that a raw OpenGL front end can draw as spheres, paths, and chessboard geometry.

The simulation core uses only the C++ standard library. OpenGL stays at the edge: a renderer can consume the snapshots without contaminating the portable physics build with a windowing or graphics dependency.

## Build and run

```sh
g++ -std=c++17 -O2 -Wall -Wextra -pedantic -o tri_engine tri_engine.cpp
./tri_engine 120 > snapshots.json
```

The first JSON object describes the engine and frame count. Each snapshot contains the current story move plus normalized ball positions and velocities in the unit square. Feed those values into OpenGL however you like: a silver sphere for ball `0`, colored orbiters for balls `1` and `2`, a triangular attractor, and a chessboard labyrinth beneath them.

This is a playful physics sketch, not a chess engine or a physically calibrated simulator. The next OpenGL layer can add camera motion, lighting, trail buffers, and a proper Crazyhouse board while keeping this deterministic STL-only core as its testable heart.
