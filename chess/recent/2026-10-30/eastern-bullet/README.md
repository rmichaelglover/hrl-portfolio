# Bullet Manninja & the Queen-Sac Force

The supplied Eastern Bullet Arena export dated 30 October 2026 contains 29
mannyfresher games at 60+0. The review follows the user's requested bullet,
Force and queen-sacrifice theme with the latest House/Thursday ensemble and
existing Woodland pieces.

- `REVIEW.md`: the complete 29-game written review, including 107 anchored beats.
- `index.html`: seven featured scenes, exact replay of every game and three checkpoints.
- `original.pgn`: byte-for-byte copy of the supplied export, newest first.
- `reviewed.pgn`: chronologically ordered original mainlines with new cast comments.
- `review.json`: verified replay frames, identity-preserving Woodland pieces and notes.
- `analysis.json`: full finite-node Stockfish 14.1 audit.
- `selected-analysis.json`: nine rechecks at a larger node budget and MultiPV 3.
- `manifest.json`: source hash, counts and source cast references.

The recorded result is 4 wins, 1 draw and 24 losses. These are game results,
not arena points or a complete tournament ranking. Fifteen unmatched queen-loss
episodes are separated from nine immediate queen exchanges using the structural
rule stated in the review. Later recovery is not erased by that classification.
No per-move clocks appear in the original export.

Tara, Dasha, Michael, Emanuel and Glover are used as fictional review characters.
All their dialogue here is newly authored. Opponents retain their PGN identities;
no opponent dialogue or motives are invented. A physical whiteboard remains
available in the staged room. Existing source scripts and stories are unchanged.

To reproduce, use Python 3.10+, python-chess (`chess` module 1.10.0 in this run)
and `/usr/games/stockfish` (Stockfish 14.1 here):

```sh
python3 analyze.py
python3 deepen.py
python3 build_review.py
```

The primary audit searches each non-terminal position at 40,000 nodes. Rechecks
use 500,000 nodes with three candidate lines. Both use one thread and 64 MiB hash;
no tablebases are configured. These are finite-search estimates, not proofs of
optimal play or Lichess accuracy scores. Recorded checkmates are independently
verified from the legal board. Engine PVs and checkpoint continuations are
replayed legally before publication.

Serve this folder over HTTP to use the replay interface. It has no external
JavaScript dependencies. Build-time checks reject mismatched commentary SAN,
illegal checkpoint moves, missing frames and incorrect queen-departure counts.

Checkpoint diagram artwork retains its upstream GPL license; see
`diagrams/NOTICE.md` and `diagrams/LICENSE.txt`.
