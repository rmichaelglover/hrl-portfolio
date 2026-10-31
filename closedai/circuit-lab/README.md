# Relax Circuit Lab

Executed controlled study for ClosedAI. **Synthetic planted circuits only.** No Mythos internals, LLM weights, or training data are used.

Read `REPORT.md` (or `publication/REPORT.md` in the complete source bundle) for the findings and limitations. The primary result is lower intervention-effect prediction error within the familiar generator. The study also finds perfect planted labels with worse causal forecasts under a new motif, no downstream intervention-choice improvement, nonselective suppression, and a null/unfavorable active-questioning result.

## Reproduce

Use the versions in `requirements.txt` (Python 3.10 used for the recorded run). Dependencies were already installed in the study environment.

```
python3 -m unittest -v
python3 experiment.py --out results
python3 active.py
python3 make_report.py
```

`active.py` reads the gain selected by the primary run from `results/results.json`. Its holdout circuits are new. `make_report.py` regenerates figures, report, and replay examples. A disjoint development run can be run with `python3 experiment.py --smoke --out smoke-results`.

Figures require Matplotlib; primary/active experiments need NumPy, SciPy, scikit-learn, and threadpoolctl. Files under `results/` and `active-results/` preserve the executed outcomes. Recorded wall time varies; statistics and seeded bootstrap intervals reproduce exactly in the recorded environment.

`DESIGN.md` and `ACTIVE-DESIGN.md` record the design boundaries. These are local prospective design notes, not a formal independent preregistration. The collateral-effect endpoint was added after the disjoint smoke run and before the full primary test, as recorded in `DESIGN.md`.

The categorical inference variant is inspired by the user's GRRLE/RelaxEngine work but does not call those engines directly. Do not describe these experiments as an LLM circuit-tracing replication or a demonstrated correction of AI motivation.
