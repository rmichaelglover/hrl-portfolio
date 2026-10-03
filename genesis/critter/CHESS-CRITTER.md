# Chess Critter: shared multi-king habitat

Open `chess-life.html` in a browser. The engine and interface are local assets;
no external chess API, library, account, or model is required.

The default 18 × 13 habitat matches the Conway Critter's rectangular grid. It
starts with one conventional 32-piece, 8 × 8 formation placed by the RNG. Other
sizes support up to six army pairs. Initial formations have two-square gaps
where multiple formations fit. Those gaps and formation borders never restrict
movement. Pawns promote at the entire habitat's far edge, not a former region.

White is the home team. Every starting home army has sixteen distinct emoji:
king 👑; queen 👸; rooks 🏰 and 🗼; bishops 🧙 and 🔮; knights 🐴 and 🦄;
pawns 🌱 🌿 🍀 🌾 🍃 🌵 🌴 🌳. Promotions retain the plant identity and add a
role badge. Black uses classical figurines. Army corner marks distinguish
matching identities in different armies.

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
state and history; the interface does not currently import saved states.

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
