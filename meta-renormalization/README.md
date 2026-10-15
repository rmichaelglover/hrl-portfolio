# Meta-Renormalization — Experiment 002

A specialized GRRLE-inspired interaction learner: all pairs are proposed from
raw components, active/inactive hypotheses exchange bounded support, and
selected disjoint pair objects can promote canonical fourth-order features.
Generating supports and coefficients are hidden from the learner.

Experiment 001's original supplied source is preserved byte-for-byte as
`meta_renormalization_experiment.py`. Its exact seed, binary input generator,
shuffled split and matched features are numerically reproduced by
`reproduce_001.py`, which avoids the original fixed `/mnt/data` plot path.
The original code reports **R²**, although the supplied summary called it
explained variance. Both are recorded in the reproduction artifact. Experiment
002 uses a distinct continuous-input generator and randomized hidden supports.

## Reproduce

Run from the repository root with Python 3.9+, NumPy, Matplotlib, ReportLab and
pytest available. The inference runtime only requires NumPy.

```sh
python3 -m pytest tests/test_meta_discovery.py -q
python3 meta-renormalization/reproduce_001.py
OPENBLAS_NUM_THREADS=1 python3 meta-renormalization/experiment.py
python3 meta-renormalization/build_report.py
python3 -m http.server 8796
```

Visit `http://localhost:8796/meta-renormalization/`. Read `WHITEPAPER.pdf` or
`WHITEPAPER.md`. `data/results.json` includes source hashes, parameters, means,
whole-seed bootstrap intervals, generator supports for a post-fit example, and
selection histories. `data/runs.csv` contains 400 seed/method/condition rows.
The 20 seeds per condition each have 12,000 observations: 6,000 fitting, 3,000
adaptive structure selection, and 3,000 sealed final testing. After selection,
coefficients are refitted on all 9,000 non-test observations.

`hrl/meta_discovery.py` never receives generating coefficients or support sets.
Its grammar, gates and compatibility topology are supplied priors; arbitrary
functions and compatibility kernels are not autonomously learned. The final
support-set scoring happens outside the learner. The full polynomial baseline
contains all square-free degree-one through degree-four monomials: 162 features
plus an intercept, without receiving the generating support list.

## Actual findings

For independent inputs with detectable pair parents, the learner recovers all
five true supports in all 20 seeds, with about 97.9% explained variance and MSE
0.09076, near expected noise MSE 0.09. It fits 14 parameters rather than 163.
The no-relaxation hierarchy obtains identical predictions in this condition;
the experiment therefore does not establish relaxation as the cause of the gain.

Pure hidden quartics are missed because no pair parent is selected. Correlated
inputs mislead the greedy search. Exhaustive polynomial regression is stronger
in both conditions. Extra selected capacity can overfit; the proposed
MetaRenorm >= Additive principle is a hypothesis, not a theorem.

Predictive equivalence prevents identifying a unique parenthesization of a
four-way product. We evaluate observable monomial supports rather than claiming
to recover an unidentifiable causal tree. Fixed pair averages are a lossy toy
projection, not a complete renormalization-group baseline.

## Files and licensing

- `../hrl/meta_discovery.py`: reusable learner and prediction object.
- `experiment.py`: actual generator, execution and held-out evaluation.
- `build_report.py`: PNG/PDF figures, Markdown paper and standalone report PDF.
- `figures/`: four scientific figure pairs.
- `data/`: all measured counts, per-seed metrics and example histories.

Original work follows the parent portfolio's MIRL license. This is
source-available and does not inherit the separate Virtual Earth MIT exception.
Prior work is linked in the report, including hierarchical interaction lasso.
No novelty priority, causal-discovery guarantee, or real-data validation is claimed.

Support indices in JSON and Python are zero-based; the exhibit displays x1–x8.
