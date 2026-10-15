# Reciprocal Grounding

Things are objects and words are labels in one experiment. Words are objects
and things are labels in another. Differently informed, mutually supported
assignments become candidates for **provisional ground truth**, with an explicit
unknown option and a separate, revisable audit.

This research prototype is a synthetic unique-instance matching experiment,
not a general solution to word meaning or a claim that agreement proves truth.

## Read and explore

- `index.html`: interactive strength fields, threshold controls, measured tables,
  risk–coverage curves and static figures.
- `WHITEPAPER.pdf` / `WHITEPAPER.md`: full methods, findings, limitations and
  references.
- `../hrl/reciprocal.py`: reusable NumPy implementation.
- `data/results.json`: parameters, thresholds, result intervals, curves,
  representative state, source hashes and runtime metadata.
- `data/runs.csv`: all 800 held-out seed / method / condition count rows.
- `figures/`: three standalone PNG and PDF figure pairs.

Run `python3 -m http.server 8796` from the repository root and visit
`http://localhost:8796/reciprocal-grounding/`. No network dependency is used by
the exhibit. The Matrix terminal can display its canvases through Live scene.

## Reproduce

Python 3.9+ and NumPy are required by the engine/experiment. Plotting adds
Matplotlib; PDF generation adds ReportLab; tests use pytest. These report tools
are not imported by the `hrl` runtime.

```sh
python3 -m pytest tests/test_reciprocal.py tests/test_core.py -q
OPENBLAS_NUM_THREADS=1 python3 reciprocal-grounding/experiment.py
python3 reciprocal-grounding/plot_results.py
python3 reciprocal-grounding/build_report.py
```

The experiment uses seeds 0–19 for threshold selection and 100–139 for final
held-out evaluation. Thresholds are selected only on the independent-view
condition and remain frozen for all stress conditions. No test accuracy is
used to set thresholds. The accepted-accuracy validation target of 95% is
empirical, not a statistical guarantee. Bootstrap resamples whole seeds.

Run durations and PDF metadata can differ between rebuilds. On the same runtime,
numerical artifacts should reproduce after ignoring `runtime_seconds`.
Source hashes change if the source changes. The simulator's hidden assignments
are used only in evaluation, threshold validation, and the explicitly marked
oracle-audit illustration, never inside either fitted view.

## What the results say

The independent-view reciprocal policy accepts 332/800 pairs, 328 correctly:
98.80% accepted accuracy at 41.50% coverage. Forward-only accepts 401/800,
381 correctly: 95.01% at 50.12% coverage. These are different operating points;
inspect the curves for coverage-sensitive comparisons.

The copied-reverse baseline is strong despite adding no independent evidence.
The shared-wrong-dictionary condition makes reciprocal agreement completely
wrong among its accepted pairs. The uninformative reverse view sacrifices most
coverage. The small relaxation ablation does not establish a general advantage
for graph relaxation.

## API contract

`relax_view(logits, object_graph, label_graph)` returns normalized strengths,
iteration deltas and a convergence flag. The final logit column is unknown.
The implementation factors graph support as `A @ P_real @ B.T`; it does not
allocate the original core engine's four-index compatibility tensor.

`accept_reciprocal(F, R, ...)` requires `F: n × (m+1)` and
`R: m × (n+1)`, unique mutual winners, thresholds, winning margins including
unknown, and optional perturbation stability. Returned `-1` labels abstain.
A geometric-mean strength ranks candidates but is not a calibrated probability.
Mutual unique winners impose a one-to-one acceptance restriction. General
many-to-many relations and ambiguous names are outside this first contract.

`audit_anchors(result, verifier, previous=..., provenance=...)` emits provisional,
rejected and revoked records. It does not enforce evidence independence or
claim that a verifier cannot be wrong. `anchor_logits` adds a bounded logit bias for audited pairs to fresh base
evidence. Revocations remove the bias on the next fresh rebuild; conflicting
anchors are rejected. Shared anchors couple the views and cannot count as new
independent corroboration. This release does not automatically retrain, benchmark
multi-round anchor growth, or provide a validated external verification system.

Original work is covered by the parent portfolio's MIRL license. It is
source-available; this folder does not claim an OSI open-source license or
inherit the separate Virtual Earth MIT exception. See `../LICENSING.md`.
