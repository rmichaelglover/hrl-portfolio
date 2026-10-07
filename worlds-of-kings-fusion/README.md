# Worlds of Kings · Fusion (version 3)

A separate, playable local three-player Earth prototype. Versions 1 (`../worlds-of-kings/`) and 2 (`../worlds-of-kings-earth/`) remain unchanged, including their saves. Fusion uses `worlds-of-kings-fusion-v1`.

Choose three different countries with at least sixteen mapped administrative spaces. Each receives sixteen pieces. Pass the device between players. Select a piece on the map or through “Your piece”, then click a highlighted destination or use the destination selector. “Focus current player” zooms to the king. The default USA/France/South Korea opening has been verified for safe kings and legal moves. Other combinations are experimental; close geographic rivals can have opening checks.

## Combined rules

The copied little-world engine supplies legal moves, own-king safety, captures, queen/rook/bishop/knight/pawn movement, promotion, sequential turns, simultaneous round-end elimination, half-point stalemates, three alliance requests per rival, and whole-alliance acceptance. Armies vanish upon elimination. All remaining allied players share victory. Alliance consent is by the person holding the device, through a confirmation prompt; there is no remote opponent service. Promotion defaults to queen, with rook/bishop/knight available.

The real atlas supplies province and ocean cells and named geography. The match follows the first candidate connection in each compass sector. Missing connections stop a ray; repeated cells stop loops. Pawn movement has one forward route and two capture directions in this version. Knights jump two cardinal steps and one perpendicular step. Polar links carry a reversed heading. A pawn promotes on an ocean cell approaching foreign land after departing its own coast. Land outside the three participating countries is traversable neutral terrain, not another player's army. Distances remain route trivia.

These are **experimental geographic chess conventions**, not a claim that irregular real borders determine unique orthodox moves. Candidate diagonals can connect regions separated by two border steps. Coastal gaps and disconnected spaces remain from version 2. Small countries lacking sixteen mapped spaces cannot be selected yet; city-area supplements and full-country multiplayer remain future work. No timed manual deployment, country reservation, accounts, matchmaking, Elo, or online multiplayer in Fusion yet. The original remains the timed-deployment reference.

Ocean spaces start tan-brown/white. Occupied ocean endpoints permanently reveal the same parity in dark/light blue. Land uses green/yellow/grey, with brown as a fourth color. The source tolerance graph has 28 same-color neighbor connections; it is not certified planar. Borders and selections still make spaces distinguishable.

## Responsiveness and language choices

Browser UI, canvas rendering, spherical projections, and the adapted game rules use JavaScript. **C++17 performs build-time graph coloring and spatial indexing**. It completes in about 0.6 seconds on the development machine and ships only its JSON output. Visitors require no native program, compiler, plugin, or cross-origin WebAssembly settings. No runtime C++ speedup is claimed.

Python/Shapely performs topology-preserving cartographic simplification at 0.10 degrees; areas smaller than 0.15 square degrees keep their original geometry. Combined country/region vertices dropped from 653,295 to 187,485 (about 71% fewer). Geometry size drops from approximately 16.6 MB to 7.3 MB. Runtime coloring is skipped because C++ supplies colors, and a native-built 10-degree spatial index narrows exact spherical polygon hit tests. Tiny regions retain geography, and search/focus plus keyboard selectors provide access. Simplified adjacent borders can show small seams; source movement connections remain unchanged.

These are size/work reductions, not a measured FPS guarantee. Browser rendering is still the main runtime cost. A runtime C++/WebAssembly port can be evaluated if profiling shows rules rather than drawing dominate; a C++ source port alone would not run in a web browser.

## Build and check

Requires Python 3 with Shapely, `g++`, and JsonCpp development headers/library:

```
python3 worlds-of-kings-fusion/build.py
node worlds-of-kings-fusion/test-engine.cjs
```

The Python build loads version 2's attributed atlas, simplifies a copy, compiles the native preprocessor in a temporary directory, and writes only Fusion's data. The compiled executable is not committed.

Tests verify 48-piece deployment, default opening safety and mobility, a legal move/turn ownership, alliances/shared victory, native palette and spatial-index coverage, and original file hashes. Browser validation covers map lookup and pointer selection, a legal move through UI controls, save/reload, independent four-view projections, and mobile/desktop overflow.

## Sources and rights

Natural Earth v5.1.2, public-domain map data; [source manifest](../worlds-of-kings-earth/data/manifest.json) and [source notices](../worlds-of-kings-earth/data/SOURCE-NOTICES.md). Source counts include territories and disputed areas, not exclusively universally recognized states. Source population estimates are not live censuses. D3 7.9.0 and d3-geo-projection 4.0.0 are reused from version 2's locally hosted vendor files with their respective license notices. The [authority and restraint charter](../white-hat-hackers/authority.html) applies to future consequential features; game actions confer no authority over real people or systems.
