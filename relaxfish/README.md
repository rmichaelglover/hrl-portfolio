# Better Than Stockfish: Relaxfish

Michael Emanuel Glover, 3 October 2026. Independent research manuscript and
reproducible pilot. The title names the programme's target. The article reports
all actual measurements, including the four diagnostic losses. This is not an
accepted Nature paper or a demonstrated superiority result.

## Read

- `RELAXFISH.pdf`: 27-page article; eight colour figures, two 3D surfaces, four tables.
- `manuscript.md`: editable manuscript.
- `RELAXFISH.txt`: plain-text edition, including the rendered tables.
- `RELAXFISH.tex`: complete LaTeX source.
- `data/results.json`: 24 fixed positions, all selected moves and role traces,
  Stockfish identity/binary hash, and four complete diagnostic match continuations.
- `data/positions.csv`: tidy per-position results.
- `data/statistics.json`: exact paired agreement test and descriptive bootstrap.
- `data/habitat-start-analysis.json`: actual bounded search of the initial position.
- `figures/`: vector PDF and 300-dpi PNG outputs. Analytic surfaces are labelled.

## Reproduce

Python requirements are pinned in `requirements.txt`. The recorded local opponent
is Stockfish 14.1 at `/usr/games/stockfish`; use that version to reproduce the
comparison. The binary is not included. LaTeX compilation uses pdflatex, standard
article, geometry, lmodern, microtype, amsmath, amssymb, graphicx, booktabs,
xcolor, hyperref, fancyhdr, caption, and pdfinfo from Poppler.

```sh
OPENBLAS_NUM_THREADS=1 python3 experiment.py
OPENBLAS_NUM_THREADS=1 python3 verify.py
OPENBLAS_NUM_THREADS=1 python3 figures.py
python3 statistics.py
python3 build.py
node chess-engine.test.cjs
node chess-solver.test.cjs
```

The experiment is an implementation diagnostic, not an equal-time engine tournament.
The prototype recognizes claimable draws automatically. Fixed-node Stockfish
reference scores are noisy comparator estimates, not certified optimal values.
Opening pairs are not counted as independent games for a strength claim. The
small suite is not a representative tournament sample.

The prospective superiority and approximate-solving protocols in the article
are proposals for future confirmatory testing; they are not externally preregistered.
The copied habitat solver is a separate variant tool, not integrated with the Python
prototype. Tests cover integer interval soundness on small cases and legal moves;
they do not prove correctness of the complete software stack.

Existing measurements can be redrawn without rerunning Stockfish: use figures.py,
statistics.py, then build.py. Fixed input policies and fixture construction are
deterministic; timings and comparator outputs can vary by environment.
