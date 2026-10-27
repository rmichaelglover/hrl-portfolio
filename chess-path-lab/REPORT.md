# Chess paths from motion and endpoints — first measured experiment

## Real-game witness

Mannyfresher–zxcvbnmasfesgjejwj, 1–0, 51 plies, from the user's downloaded October 27, 2026 Lichess tournament PGN. Public game: https://lichess.org/game/DItWyjG9 . The exact selected game is in witness.pgn. Every source move was checked against python-chess legal moves before replay. This establishes a connecting legal sequence; no claim is made about engine-assessed move quality or optimal play.

## Three distinct questions

1. Can anonymous piece centers be tracked through rendered movement without consulting the game's moves?
2. Can chess legality resolve uncertain identities between observed positions?
3. Given only start and target states and an exact ply budget, how many distinct legal UCI move sequences connect them, and can necessary movement constraints reduce the work without changing that count?

A fourth experiment adds an observed midpoint. It intentionally changes the inference problem and may reduce the number of admissible solutions.

## Motion experiment

The legal PGN generates a deliberately simplified raster board: identical blue dots for White, identical orange dots for Black. Each move is animated with eight straight interpolated subframes. Initial identities are known from the starting position. The detector reads color masks and connected-component centers from the raster frames. Its outputs have no identity labels.

Geometry-only tracking uses minimum-distance one-to-one assignment separately by color, a 50-pixel displacement gate, and a two-frame missing-detection grace period. It receives no chess moves. Same-color overlaps and captures can break identities.

The constrained tracker receives the initial board and anonymous occupied squares at each move boundary. It enumerates legal next moves and retains every successor whose per-color occupancy matches the observation. Its piece identity map is advanced by that inferred move, including castling, capture, and en passant. Promotion choices with identical dot observations remain separate hypotheses. It never receives witness moves. Hypotheses are capped at 4,096; exceeding that cap raises an error rather than silently dropping alternatives.

Results: 409 rendered frames, 52 move-boundary snapshots. Geometry-only tracking correctly assigns 1,395 of 1,521 visible identity locations (91.7%). The constrained tracker has exactly one hypothesis at every snapshot, with all 52 identity maps matching the witness. This result depends on clean color segmentation, known orientation and initial state, and observing every ply. It is not an actual desktop screen recording or a noisy-camera benchmark.

### Important animation distinction

A piece sliding from A to B on screen is an interface animation, not a legal chess path through every intervening screen coordinate. A knight can animate along a straight line. Jumping from the first board to the last can interpolate many pieces simultaneously and does not reveal the intervening move order. The animation supplies correspondence evidence; legal move constraints apply between board states. The current experiment does not recover hidden moves from Lichess's beginning/end jump animation.

## Endpoint search

Each search fixes its exact depth to a three- or four-ply window of the real game. Search receives the starting board, final board, and ply budget; it does not consume the recorded interior moves or tracked identities. The witness is used afterward to confirm that it is among the recovered sequences.

States include piece placement, side to move, castling rights, and legally available en-passant. Halfmove/fullmove counters, prior repetition history, claimable draws, and automatic draw termination are excluded. The task is legal-movement reachability in standard chess under that explicit state model, not game-outcome solving.

Uniqueness means distinct ordered UCI move sequences. Transpositions may share cached suffix counts but still count as different histories; a global visited-set would incorrectly erase those paths. At most 12 example paths are retained for display; in this run all complete windows have four or fewer paths, so their bound-mode lists are exhaustive. A node cap of 300,000 is used. Aborted searches report `complete=false` and `paths=null`, never an exhaustive partial count.

Three endpoint-only methods use the same legal move generator:

- Legal: memoized search with no endpoint pruning before leaves.
- Material: turn parity, irreversible castling rights, non-increasing piece/pawn counts, and sufficient opponent capture turns.
- Bound: those checks plus a minimum-cost assignment of current pieces to surviving target pieces. Costs are optimistic empty-board move distances, including knight geometry, bishop square colors, pawn direction/double step, possible promotions, and king castling displacement. Obstacles and check are relaxed for the bound; actual moves still pass full legality.

### Why the bound can prune safely

Every target piece must descend from a distinct surviving current piece. For each such correspondence, its empty-board distance is no greater than the number of moves that piece actually makes. Minimizing across correspondences cannot increase this lower bound. Castling is the exception to summing individual piece moves: one turn moves king and rook. The implementation allows the king's castling displacement and subtracts one from a color's sum whenever it still has castling rights. A side can castle at most once, so this is conservative. Promotion candidates include pawn travel to promotion plus subsequent promoted-piece movement, with relaxed promotion-file availability. Captured pieces need not be assigned to targets.

If this optimistic sum exceeds the side's remaining turns, no legal continuation can reach the target within budget. This argument is specific to the implemented standard-chess model; it is not a justification for pruning on an unverified tracker prediction, an HRL score, or visual similarity.

## Measured endpoint counts

| Start ply / depth | Legal nodes | Material nodes | Bound nodes | Endpoint paths | Paths with observed midpoint |
|---|---:|---:|---:|---:|---:|
| 0 / 4 | 77,861 | 72,887 | 396 | 4 | 1 |
| 8 / 3 | 19,935 | 16,613 | 166 | 2 | 1 |
| 20 / 3 | 29,326 | 25,371 | 249 | 2 | 1 |
| 38 / 3 | 2,040 | 1,876 | 73 | 1 | 1 |
| 47 / 4 | capped at 300,001 attempted nodes | 255,864 | 215 | 2 | 1 |

All completed endpoint-only methods agree on counts, and the recorded witness is present in each bound-mode path list. The final-window unpruned baseline exceeded its cap; material and bound modes completed and agreed on two paths. Counts measure newly encountered state/depth entries, including leaves and rejected entries; cache hits and generated edges are separate fields in results.json. Timing is recorded but is not a controlled performance benchmark.

The opening window visits approximately 197 times fewer nodes with the bound (99.49% fewer). Adding a uniquely reconstructed midpoint reduces four endpoint-compatible histories to one at 121 visited nodes. This is a conditional reconstruction, not preservation of all endpoint-only solutions. Midpoint states come from the legal observation tracker, not from its PGN move list. In real footage, uncertain midpoint candidates would require maintaining alternatives; they must not be treated as certified hard facts.

## Validation and limits

Seven tests exercise equal endpoint counts with distinct transposed histories; castling, underpromotion, capture and en-passant bounds; randomized known-path lower-bound checks; node-limit reporting; castling state identity; midpoint conditioning; and visual tracking of special moves. Promotion dots deliberately retain all four legal promotion types. These are targeted checks and a conditional argument, not an exhaustive verification across all chess states.

This first implementation uses color segmentation, assignment, legal successor filtering, and combinatorial search. It does not claim an HRL-specific speedup, import the earlier KRK solver, analyze all 51 plies exhaustively, solve arbitrary proof games, establish chess outcomes, or turn endpoint identity matching into a unique history. Exact ply budgets are supplied. The actual number of possible game lengths is not inferred.

Next useful steps: noisy/occluded screenshots and board calibration; uncertain observation domains rather than single guessed identities; staged geometry → pseudo-legal → king-safe ablations; longer proof-game windows; certified intermediate constraints; and bidirectional search preserving castling/en-passant and capture/promotion provenance. The surviving candidates can be evaluated by a chess engine afterward, but finding the recorded game is not proof that it is the only or best one.

## Reproduce

```sh
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python3 study.py
python3 -m unittest -v test_paths
```

Open the static page through a local HTTP server to explore the recorded replay and path tables. Python files perform the analysis; the browser only displays recorded results. Original research and other local files remain unchanged.
