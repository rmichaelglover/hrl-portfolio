# Magnum Chessicus: Native C++ Proof Search and Exact Helper Gates

**Michael Emanuel Glover · 13 November 2026**

Originating research framework, chess-solving programme and project: Michael
Emanuel Glover. Assistant: native implementation, validation, experiments and
reporting. Legal moves and PGN parsing: the separately credited Disservin library.

## Result and continuity

The existing sound-interval and bounded-certificate programme now runs in C++17.
It carries forward Magnum Chessicus's outcome intervals, Relaxfish's budget and
extremal-cutoff discipline, the bounded mate solver's replayable strategies, and
the earlier chess logic's shared-plan cosine compatibility and multiplicative
normalization. Earlier manuscripts, code and results remain intact.

The native reader replays 75 unique standard-rule games and 4,805 legal plies
from the six recent studies. One Crazyhouse chapter is excluded; a repeated game
is deduplicated. Two records start from supplied positions. The 47 records ending
in checkmate yield 141 roots one, three and five plies before the final move.
Both Michael's wins and losses are included. A played mating line does not prove
that an earlier root is a forced win; the search must cover the required replies.

Each ordering mode receives the same depth, a 20,000-search-node cap and a ten-second
solver cap. The solver, reader, experiment runner and standalone verifier are
native C++17. No Python, JavaScript, Stockfish or service performs the new searches.
This selected tactical suite measures proof search, not general engine strength.

## Three-mode ablation with exact helper gates

| Mode | Exact roots / 141 | Search nodes | Ordering candidates | Ordering child probes | Draw-claim child probes | Solver seconds |
|---|---:|---:|---:|---:|---:|---:|
| Legal enumeration | 66 | 1,496,026 | 0 | 0 | 948,786 | 5.40527 |
| Tactical prior | 77 | 1,241,396 | 1,321,421 | 119,841 | 812,241 | 4.58027 |
| Prior + relaxation | 77 | 1,244,554 | 1,322,420 | 122,292 | 798,273 | 5.30878 |

The prior uses approximately 17.0% fewer counted search nodes than legal order;
the relaxed version uses 16.8% fewer. These counts exclude helper probes, which
are recorded separately. Solver timing includes ordering, rule checks and proof
construction, but excludes certificate serialization/replay. Programs were built
with GCC 11.4 in CMake Release mode. Timings are local measurements.

Against the prior alone, relaxation reduces search nodes in 3 cases, increases
them in 7, and ties in 131. Both certify 77 roots. Thus tactical prioritization
provides the measured improvement; the extra relaxation rounds have not yet earned
an aggregate advantage. They remain an explicit research mode. `--prior-only`
selects the faster measured configuration for this suite.

Reversing execution order reproduces the intervals, node counts and proof totals.
Reversed legal/prior/relaxed solver totals are 5.42231 / 4.58451 / 5.31276 seconds.

## An exact necessary-condition gate

Let h be the current quiet-halfmove counter and c(p) the exact historical count
of position p. First preserve any claim already available now. If h < 99 and
all c(p) < 2, no one legal intended move can create a 50-move or threefold claim.

Proof: a quiet move increments h by at most one; pawn moves and captures reset
it. A next counter therefore cannot reach 100 from h < 99. A third occurrence
requires two earlier occurrences of the resulting exact position. If no position
has already occurred twice, that is impossible. The conjunction excludes both
intended-claim types without excluding an available current claim or a chess move.

Exact occurrence counts are maintained through make/unmake. The map compares
complete strings; a hash collision cannot identify unequal positions. En-passant
identity is based on legal capture availability, including pinned-pawn cases.
Certificate replay deliberately uses ungated claim examination and direct history
scans. The ordering routine also omits a child mate test for nonchecking moves:
checkmate requires check, so that test cannot succeed for such a move.

### Matched final-source gate-off/gate-on test

| Measurement | Ungated reference | Gated run |
|---|---:|---:|
| Position/mode pairs | 423 | 423 |
| Intended-claim child probes, all modes | 98,916,131 | 2,559,300 |
| Exact certificates | 220 | 220 |
| Legal-order search nodes | 1,496,026 | 1,496,026 |
| Prior-order search nodes | 1,241,396 | 1,241,396 |
| Relaxed-order search nodes | 1,244,554 | 1,244,554 |

This is a **97.4127% reduction** in intended-claim child probes. The native comparison
tool checks every interval and search-node count and byte-compares all 220 exact
certificates. All match. The standalone checker also replays the certificates.
The control uses the same final source and ordering features, disabling the claim
gate/cache lookup path in favor of direct history scans. Ordering helper counts
remain matched. Ungated solver totals are 26.9071 / 22.3679 / 23.6237 seconds;
gated totals are in the ablation table above. Both paths maintain the rule state.

## Why the bounds remain sound

Terminal nodes provide their declared rule outcome. A frontier retains [-1,+1],
optionally tightened by a legal zero-valued draw claim. White takes maxima of child
endpoints; Black takes minima. Monotonicity preserves enclosure. Unvisited legal
children remain unknown. A White lower bound of +1 or Black upper bound of -1
reaches the global payoff cap and justifies an exact local cutoff.

The verifier reconstructs these facts without ordering strengths. It rejects
false endings, forged intervals, illegal or duplicate edges, missing attacker
witnesses and missing required defensive replies. Search/replay share the legal
move library; replay is independent of ranking and search traversal, rather than
an independently implemented set of chess rules.

Exact roots return an outcome-optimal UCI move, a draw-claim action or `terminal`.
Unresolved roots provide no certified action. Distance to mate is not optimized.

## Initial-position continuation

| Computation | Search nodes | Initial interval |
|---|---:|---|
| Previous three-ply result reproduced in C++ | 9,323 | [-1,+1] |
| Four plies, exhaustive | 206,604 | [-1,+1] |
| Four plies, sound local cutoffs | 206,580 | [-1,+1] |

Eight extremal cutoffs remove 24 visits while preserving the enclosure. The
initial value remains unresolved. This extends the executed calculation and
reduces work in the finite tasks; it is not a new worst-case complexity bound
for arbitrary optimal chess play.

## Validation, scope and next work

Tests cover initial perft through four plies; castling-rich perft through three;
castling feature semantics; all underpromotions; mate/stalemate/conservative dead
material; current/intended claims; threefold versus fivefold; FEN/history distinction;
75-move mate priority; pinned en-passant identity; root restoration; budget honesty;
certified actions; disk replay; and deliberately corrupted certificates. A dedicated
forced-win fixture rejects a proof after a required defensive reply is removed.
A further 1,000 deterministic legal-walk states compare gated/ungated claims,
occurrence-cache counts and make/unmake restoration.

The 220 saved certificates include the same roots proved by different modes; they
are not 220 distinct solved games. The interface currently accepts depth 0–64
and replay trees up to ten million nodes. Clocks, resignation and agreed draws
are outside the board-play model. Automatic/optional draw rules are distinguished;
dead-position detection covers explicitly documented conservative material cases.
There is no exact endgame database or full-history transposition reduction yet.

The next experiment should retain the verified helper gate and tactical prior,
then concentrate relaxation on roots where it changes useful traversal. Any
structural or transposition reduction must preserve draw history and carry a
separate validity check. The continuing goal is less work per verified strategy
and progressively tighter sound outcome intervals.
