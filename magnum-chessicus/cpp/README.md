# Magnum Chessicus — pure C++ proof-search continuation

**Originating research direction, framework and project: Michael Emanuel Glover.**
Assistant contribution: native implementation, rule tests, certificate replay,
controlled experiments and reporting. Legal move generation uses the separately
credited, MIT-licensed Disservin chess-library.

This continues the existing work in place:

- `../experiment.py::interval`: sound White-perspective win/draw/loss intervals.
- `../../relaxed-chess-brain/solver/solve.py`: bounded proofs and replay checking.
- `../../relaxfish/chess-solver.js`: budgeted search and exact outcome cutoffs.
- `~/Code/relaxation-labeling/python/chess_logic.py::relax`: shared-plan cosine
  compatibility and normalized multiplicative support for move ordering.

The solver, PGN reader, benchmark, rules wrapper and standalone certificate checker
are C++17. They do not invoke Python, JavaScript, Stockfish or an external service.
The existing implementations and manuscripts remain intact.

## Build and use

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure

./build/magnum_cpp --fen '7k/8/5KQ1/8/8/8/8/8 w - - 0 1' \
  --depth 1 --prior-only --certificate mate.cert
./build/magnum_verify mate.cert

./build/magnum_cpp --depth 4 --unguided --nodes 500000 --seconds 60
```

For an exact result, `certified_action` gives an outcome-optimal UCI move, an
available draw-claim action, or `terminal`. It does not promise the fastest mate.
An unresolved root has no certified action. `--moves 'g1f3 g8f6 ...'` replays
actual root history from `--fen`; FEN alone does not invent earlier repetitions.

`--unguided` selects legal enumeration order; `--prior-only` selects the tactical
prior without relaxation. Default guided search applies eight relaxation rounds.
`--exhaustive` disables extremal cutoffs for a same-bounds baseline.
`--ungated-claims` disables the necessary-condition draw-claim gate.

## Sound intervals and replayable evidence

Payoffs are -1, 0, +1 from White's perspective. An unresolved continuation retains
[-1,+1]. White parents take maxima of child lower/upper bounds; Black parents take
minima. Unvisited legal moves remain [-1,+1]. A legal draw claim contributes an
optional zero-valued action. A proven winning child at a White node, or proven
Black-winning child at a Black node, reaches the global payoff cap and permits
an exact cutoff. No low heuristic score excludes a legal move.

The certificate records the initial FEN, complete replayed root moves, depth and
proof tree. A separate traversal recomputes legal moves, endings, draw claims,
unexpanded-child bounds and interval propagation. It never uses ordering weights
or accepts stored child values without replay. Omitting a necessary defensive
reply weakens the recomputed interval and invalidates a claimed win. The checker
shares legal move generation with search; it is independent of ranking/search,
not an independently implemented set of chess rules.

The current interface supports depths 0–64 and replay trees up to ten million nodes.
Node, time or depth exhaustion leaves an enclosing interval; it is not a draw.
The initial-position result remains unresolved. The executed C++ continuation
reproduces the previous depth-three 9,323-node result and advances to depth four.

## Draw semantics and exact identity

Checkmate and stalemate are checked first. The model distinguishes optional
threefold/50-move claims (including an intended legal move) from automatic
fivefold/75-move endings. Checkmate takes precedence at the 75-move boundary.
Conservative dead-material cases include bare kings, one minor, and same-colored
bishops without other material. Other dead positions need further analysis.
Clocks, resignation and draw agreements are outside this board-play model.

Repetition identity uses exact piece placement, side, castling rights and
**legally available** en passant. Halfmove counters stay in rule state, not in
repetition identity. Pinned en-passant captures do not distinguish equal positions.
Full strings are compared; an unordered-map hash collision cannot equate different
positions. The search does not merge different histories in a transposition table.

### Necessary-condition claim gate

After ruling out a claim already available now, an intended-move claim can only
become available if either:

1. the current quiet-move counter is at least 99, or
2. some exact position in the retained history has already occurred twice.

A move raises the quiet counter by at most one, and a third occurrence needs two
prior occurrences. If neither condition holds, probing every legal child for an
intended claim is unnecessary. The state maintains exact occurrence counts during
make/unmake. Certificate replay deliberately uses the ungated routine and direct
history scans, checking claims without this shortcut.

Mate-priority testing also probes a child only if its move gives check: a
nonchecking move cannot deliver checkmate. This changes feature-computation work,
not the ordering features or the game-theoretic bounds.

## Ordering and the contribution test

The C++ feature set is deliberately explicit: check, capture, promotion, minor
piece development, center proximity and queen role; a legal immediate mate has a
large prior bonus. Cosine compatibility connects shared plans, self-support is
removed, and eight normalized multiplicative rounds refine the strengths.
This carries forward the earlier relaxation mechanism with a smaller documented
feature set; it is not a claim of byte-for-byte equivalence to the Python model.

Three modes are compared on identical roots: legal order, tactical prior alone,
and tactical prior plus relaxation. The ablation is necessary because a strong
checking/mating priority can improve traversal without benefiting from relaxation.
The present data show the gain over legal order primarily comes from the tactical
prior. Relaxation's separate contribution is mixed and remains an optimization
question, not an assumed result.

## Study benchmark

The native reader imports all six published PGNs, skips the one Crazyhouse
chapter, deduplicates the repeated game, and legally replays 75 standard-rule games
containing 4,805 plies. Two games begin from supplied FENs. From the 47 recorded
checkmate games, roots one, three and five plies before the final mate produce
141 paired positions. Both sides' wins and losses are included.

Each mode receives a 20,000 search-node cap, a ten-second solver cap, and the same
finite depth. This is a selected tactical proof-search suite, not a general
engine-strength or arbitrary-position optimality benchmark. A played mating line
does not prove that the earlier root is a forced win; the solver must cover the
opponent's legal replies. All reported exact roots have saved replay certificates.

```sh
# From the portfolio root, after building the C++ project:
/path/to/build/magnum_benchmark magnum-chessicus/cpp/data/new-run \
  chess/recent/2026-11-13/controlled-provocation/inputs/*.pgn
/path/to/build/magnum_verify magnum-chessicus/cpp/data/new-run/certificates

# Reverse execution order without duplicating certificate files:
MAGNUM_REVERSE_ORDER=1 MAGNUM_NO_CERTIFICATES=1 \
 /path/to/build/magnum_benchmark magnum-chessicus/cpp/data/new-reverse \
 chess/recent/2026-11-13/controlled-provocation/inputs/*.pgn
```

Search nodes, ordering candidates, ordering child probes, draw-claim child probes,
solver seconds and certificate paths are recorded separately. Search-node counts
exclude helper probes. Solver timing includes ordering and rule work but excludes
certificate serialization/replay; it is a local measurement. Gate-off and gate-on
records permit direct comparison of helper work without changing proof outcomes.
See `REPORT.md` and the recorded tables on the project page for the executed data.

## Tests

Initial perft through depth four; castling-rich perft through depth three;
underpromotions; mate/stalemate/dead material; current/intended draw claims;
threefold versus fivefold; FEN/history distinction; 75-move mate priority;
pinned en-passant identity; root restoration; node-budget honesty; certified
winning actions; disk round trips; forged intervals, illegal/duplicate moves,
missing attacker witnesses and missing defensive replies. Stored benchmark
certificates are also replayed by the standalone C++ verifier.

Project source follows the repository's existing license. `vendor/LICENSE`
retains the chess-library MIT license; `vendor/PROVENANCE.md` pins the revision.
