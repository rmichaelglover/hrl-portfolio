# Magnum Chessicus

Michael Emanuel Glover, developed in dialogue with Codex. Conditional draw-certificate theorems, sound bounded search and reproducible examples. The initial position is not solved; its executed enclosure is [-1,+1]. No unsupported superiority claim is made.

Run `python3 experiment.py`, then `python3 verify.py`, then `python3 write.py`. Requires Python 3, python-chess 1.999 (chess module 1.10.0), NumPy, Matplotlib and pdflatex. Fixtures are valid roots with explicitly supplied FEN and fresh histories. The initial root uses the complete initial move history; claims are optional actions, not automatic threefold endings.

Read WHITE-PAPER.pdf or WHITE-PAPER.txt. SOURCE.zip includes code, figures, data and the three small certificates. Archived Relaxfish data is copied and hashed, not rerun here. Exact finite-depth outcome bounds are distinguished from heuristic engine scores and hypothetical statistical plots.
