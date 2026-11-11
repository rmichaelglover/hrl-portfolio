# Virtual Cell research manuscript

**Compositional virtual persons link cellular state, relational memory and multi-objective governance**

Michael Emanuel Glover — originating framework, project direction and author.
Dedicated to James Calvin “Jimmy” Glover.

The manuscript uses a Nature-style research progression with a summary, results,
methods, supplementary notes and extended figures. Its scientific evidence is
computational and synthetic; biological and philosophical extensions are stated
as proposals. It is an independent manuscript, with no journal affiliation or
arXiv submission implied.

## Deliverables

- `VIRTUAL_CELL_MANUSCRIPT.pdf`: complete illustrated manuscript.
- `virtual-cell-arxiv-source.tar.gz`: clean pdfLaTeX source and used figures.
- `virtual-cell-reproducibility.zip`: frozen C++ model, experiments, CSV data,
  analysis, original PDF/PNG figures, manuscript and manifest.
- `SUBMISSION_NOTES.md`: metadata draft and arXiv packaging notes.

There are 12 numbered figures (six main, six extended), eight tables, 16
supplementary notes and two mathematical propositions with proofs.

## Reproduce

Requires g++ with C++17, CMake, Python 3, NumPy, Matplotlib, python-chess and
pdfLaTeX with ordinary TeX Live packages. No network is used by the build.

```sh
python3 reproduce.py --experiments  # regenerate data, run frozen-model tests, build all artifacts
python3 reproduce.py                # use saved data; regenerate figures, audit and build
```

To compile just the arXiv source, extract it into an empty directory and run:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The bibliography is embedded, so BibTeX and a custom journal class are unnecessary.
Raw artifacts and code use registry IDs and toy units documented in the paper.
The included model is a frozen snapshot, independent of future portfolio changes.

## Evidence

The primary labeling experiment runs 200 graphs with 64 nodes under four
conditions. A separate sensitivity grid runs 400 configurations. The policy grid
contains 5,151 weights; probability diagnostics use 20,000 events. Summary and
bookkeeping fixtures test declared invariants. Every primary number is derived
from archived CSV files. The audit checks data counts and exact structural
relationships, and the manifest lists SHA-256 hashes.

GCC standard-library normal distributions can differ across platforms; archived
CSV data define the reported numerical artifact. Bootstrap intervals resample
whole seeds and use a fixed analysis seed. Weight-grid ties are explicitly
reported because floating-point comparisons split seven mathematical ties.

The two chess positions are legally replayed from included selected PGNs. They
are case studies, not a trained chess benchmark or a psychological dataset.
