# The Stalemate Gambit Explained

A seven-chapter draft study in Chess Maestro, hosted with the existing portfolio
on GitHub Pages. Publication to Lichess waits until Manny is happy with the study.

`study.pgn` is the portable chess source: one game per chapter, standard starting
positions or FEN/SetUp headers, comments, recursive variations and colored-square
annotations. `build_study.py` authors the chapters and derives `study.json` with
legal moves and board frames using python-chess. Run `python3 build_study.py` after
an authoring change. It validates every position and parses the exported PGN back.
The founding game is retained in `source-game.pgn` with its original annotations.

The page uses Maestro's own board and character cast through a same-origin iframe
adapter. All displayed positions and lesson move choices come from the validated
PGN tree. Authored moves are clickable; legal alternatives outside the tree are
identified as outside the chapter rather than silently inserted. The download
contains all seven chapters; the web view defaults to hiding lesson solutions.

## Later Lichess import

Import `study.pgn` into a new Standard chess study. Check chapter titles and order,
FEN starts, comments, alternative lines and colored squares after import.
Set chapters 3, 4, 6 and 7 to Interactive lesson manually. Keep chapters 1, 2
and 5 in normal analysis mode. Configure hints and chapter orientation manually;
interactive lesson settings and hint UI are not portable PGN fields.

The chapter 3 rook offer is a trap: Black can decline it. Chapter 4 asks for rook
underpromotion to avoid immediate stalemate while retaining mating material.
Chapter 6's Kh5 is forced but does not force a draw. Chapter 7 deliberately asks
for stalemate, then offers the neighboring checkmate as a comparison variation.
Checkmate alternatives in chapter 1 are all three mates in one from the original
position: Qf5#, Qg5# and Qe2#.

## Sources

- Founding game: https://lichess.org/rdt2NZGH
- Original study chapter: https://lichess.org/study/j16jtkbK/rXyGL1Mr
- Study structure: https://lichess.org/@/lichess/blog/study-chess-the-lichess-way/V0KrLSkA
- Rules: https://handbook.fide.com/chapter/e012023

The term Stalemate Gambit is a creative study theme, not a claim to an established
opening or a forced draw from the starting position. Chapters 3, 4 and 7 are
composed teaching positions. Black had two queens at the historical finish.
