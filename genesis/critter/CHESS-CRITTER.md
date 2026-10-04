# Chess Critter: shared multi-king habitat

Open `chess-life.html` in a browser. The engine and interface are local assets;
no external chess API, library, account, or model is required.

The default 18 × 13 habitat matches the Conway Critter's rectangular grid. It
starts with one conventional 32-piece, 8 × 8 formation placed by the RNG. Other
sizes support up to six army pairs. Initial formations have two-square gaps
where multiple formations fit. Those gaps and formation borders never restrict
movement. Pawns promote at the entire habitat's far edge, not a former region.

White is the home team, using the definitive Woodland cast from `maestro.html`:
King Ethelheim 🦁, Queen Dilorias 🐲, Castle Andora 🏰, Castle Hessenbach 🧱,
Sir Banyan Blithers 🦄, Dame Gertrude Goethe 🐎, Popette Christiana Carolina 🛕,
and Pope Francisco Finochitti 🧙. Pawns: Alexander Aaronson 🦊, Bartholomew
Bogerson 🦡, Cais Christianson 🦝, Dorothy Dryers 🦌, Ella Elouise 🦉,
Frank Fassenbecher 🐸, Georgiana Gina 🦎, Harriet Hissindorf 🦔.
Promotions retain identity and add a role badge. Black uses classical figurines.
Army corner marks distinguish matching identities in different armies.

## Explicit variant rules

- Teams alternate one global ply at a time. Any surviving piece of that team
  can move, subject to ordinary piece geometry on the larger bounded rectangle.
- Every surviving king of the moving team must be safe after a proposed move.
  Pinned enemy pieces still count as attacks. Kings cannot be captured.
- Each checked king is tested for an individual rescue by any allied piece.
  If no rescue exists, the king is checkmated and its original army retires,
  including troops that crossed into other regions. Retirement is a habitat
  lifecycle event, removes those pieces, and can uncover additional lines.
  Checkmate adjudication repeats for newly exposed moving-team kings.
- A team wins exactly when all opposing kings have retired through recorded
  checkmates. Capturing ordinary troops does not itself establish victory.
- If no global legal move exists and no king is checked, the habitat is drawn
  by stalemate. If kings have individual rescues but no move protects them all,
  it is a royal-deadlock draw rather than a fabricated checkmate.
- Bare kings are drawn. Threefold repetition and 100 plies without a capture
  or pawn move are automatic habitat draws. A 1,200-ply observation cap is
  separately labeled. Checkmate takes precedence over these counters.
- In the classical 8 × 8 single-king setting, king plus at most one minor piece
  and bishop-only endings with all bishops on one square color are also drawn
  for insufficient mating material. This test is not generalized to multiple kings.
- Castling uses a never-moved king and its own original never-moved rook, with
  clear intervening squares and safe transit. En passant lasts through one
  opposing global ply. All four promotion choices are supported.

These are a custom multi-king extension. They are not a claim that official
tournament chess permits multiple kings or larger boards. No Conway birth,
neighbor-count death, or arbitrary teleportation overrides chess movement.

## Observation

The habitat starts paused at a selectable one-ply-per-second pace. Use Observe,
One ply, manual legal moves, zoom, Fit habitat, and Show seed regions. Seed
regions are optional visual guides. Hover or select a node for its current
role, army, and legal destinations. Promotion is selectable for manual play.

Forage is a seeded one-ply heuristic favoring material gains and checks while
penalizing attacked destination squares. Random chooses among legal moves.
Neither policy claims strong chess play. Identical seed, habitat, army count,
policy, and action sequence reproduce the same run. Saved JSON records the
state, history, and full repetition counts required for exact search; the interface does not currently import saved states.

## Verification

Run from the repository root:

```sh
node genesis/critter/chess-engine.test.cjs
```

Tests cover standard initial-position perft counts 20, 400, and 8,902; pinned
pieces; castling and attacked transit; en passant exposing a rook check; all
promotions; sixteen distinct home emojis; forbidden king captures; single
and multiple king survival; stalemate and royal deadlock; region-crossing
movement; repetition; quiet-move and bare-king draws; deterministic RNG; and
population accounting over multi-army play.

Classical reference: [FIDE Laws of Chess](https://handbook.fide.com/chapter/E012023).

## Search toward an exact outcome

Search position pauses play and uses a Web Worker, keeping the interface responsive.
Choose a 1-, 5-, or 30-second budget; stop at any time or save the latest report.
Serve the page over HTTP for background workers.

`chess-solver.js` performs iterative deepening with sound integer minimax bounds.
Unexpanded branches contribute [-1,+1]; terminal positions contribute their exact
White-perspective outcome. White nodes maximize both endpoints, Black nodes minimize
them. Capture/promotion ordering affects speed, never certification. A forced win
can terminate search early; certifying a draw requires excluding winning alternatives
for both teams. Reports retain monotonic root bounds, per-move bounds, searched node
count, elapsed time, and completed search depth. Epsilon is upper minus lower.

No heuristic score is substituted for an exact leaf. No transposition cache merges
positions with different draw histories. Every branch copies army rights, moved flags,
en passant, quiet counter, ply count, and repetition counts. Saved analyses can be
rerun; they are search reports, not independently checkable full proof trees.
Older snapshots lacking repetition counts are rejected for certification.

This solver applies to this variant, including automatic draws and the 1,200-ply
cap. It does not claim to solve standard chess. Exhaustive finite-horizon coverage
converges to an exact result in principle; large starting positions can remain
unresolved at any practical budget. A current-position result does not prove that
an earlier repetition was forced. There is no HRL evaluator in this proof search yet.

```sh
node genesis/critter/chess-solver.test.cjs
node genesis/critter/solve-chess.cjs --ms=5000 --nodes=100000 --depth=1200
node genesis/critter/solve-chess.cjs saved-state.json --ms=30000
```
