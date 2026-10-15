# A world before names

A small, open-source virtual Earth: physical coastline geometry, a zoomable
mathematical surface, and a seeded agent-based ecological experiment. No country
outlines, place names, animal tags, or political regions are drawn.

Run `python3 -m http.server 8796` from the portfolio root and open
`http://localhost:8796/virtual-earth/`. No build or external network services
are required. All runtime dependencies and data are local.

## Explore

Drag the globe; scroll, pinch, or move the zoom slider. Click a surface point to
center it. Enter or the crosshair button enters the synthetic local ecosystem.
The local view is a separate scale model anchored to that coordinate, not a
continuous reconstruction of its real terrain. Drag to pan; select an animal
to follow it. Escape or the planet button returns to Earth. Space pauses.
Arrow keys and plus/minus work while the world canvas has focus.

The model panel (top right) exposes simulation rate, starting population, seed,
resource/population statistics, regeneration, and a complete JSON state export.
The field-mesh button reveals the local mathematical sampling structure.
Reduced-motion preferences start the simulation paused.

The same canvas and HTML controls can be viewed through the portfolio Matrix
terminal's **Live scene** adapter. Original ecological state is shared with
that renderer rather than simulated a second way.

## What is modeled

`model.js` is a dependency-free simulation shared by the browser and Node:

- A 1,400-unit periodic patch; a 72 × 72 renewable-food/moisture/height field.
- Seeded multiscale value noise for height; latitude modulates a synthetic
  moisture prior. A height threshold creates illustrative water patches.
- Deer-, hare-, fox-, bird-, and fish-inspired agents. These are procedural
  animal silhouettes and simplified behaviors, not validated species models or
  real observations. Terrestrial species are not assigned real distributions.
- Food replenishment, consumption, energy expenditure, local resource search,
  crowd avoidance, predator avoidance, predation, reproduction, and death.
- Local spatial bins for interactions; fixed 1/30 simulation steps; a cap of
  1,200 agents. No claim of a closed mass or energy conservation law is made.

The geometry distinguishes land from ocean when creating a patch. Ocean
patches contain fish-like agents; land patches use a synthetic mixed community.
Globe colors and flowing traces are mathematical illustrations, not measured
biomes, elevation, currents, winds, clouds, or weather forecasts. Local noise
is periodic by tiling the sampled patch, so seams are a modeling limitation.
The globe-to-patch transition is explicit; there is no fabricated fine-scale
Earth dataset behind the zoom.

## Reproduce and test

```sh
node virtual-earth/test-model.cjs
```

Tests check deterministic replay, exact checkpoint restoration, movement,
habitat constraints, bounded resources, and population accounting. Browser
verification separately covers globe rotation, zoom, local entry, pause,
settings, mobile layout, and the terminal live renderer.

An export contains camera/anchor, fixed step size, step count, all fields,
agent states, counters, and PRNG state. Restore the ecological checkpoint with
`VirtualEarthModel.Ecosystem.restore(record.ecosystem)`. Numerical replay is
intended for the same JavaScript runtime; cross-runtime bitwise identity is not
promised.

## Data, licensing, and next steps

Original code and documentation in this directory are **MIT licensed** under
[LICENSE](LICENSE), an explicit exception to the parent portfolio license.
Vendored D3 v7.9.0 uses its own ISC license; see
[vendor/D3-LICENSE.txt](vendor/D3-LICENSE.txt).

The public-domain Natural Earth v5.1.2 **50m physical land** layer supplies
coastlines without administrative boundaries. `build_land.py` removes every
property and combines the physical polygons. The pinned upstream URL and source
SHA256 are in that script. Rebuilding requires only Python's standard library
and the downloaded source file. Data terms:
https://www.naturalearthdata.com/about/terms-of-use/.

This is a first ecosystem prototype, not a full digital twin of Earth. A larger
model needs measured elevation, bathymetry, hydrology, land cover, atmospheric
state, and defensible ecological parameters with independent validation. Each
dataset should be pinned, attributed, and expose uncertainty separately from
procedural detail. Future compute allocation can refine patches according to
forecast sensitivity and measured approximation error, retaining global
coverage and checking against fixed-budget baselines.
