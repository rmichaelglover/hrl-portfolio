# Mutual-best early finalization: first measured pilot

Michael Emanuel Glover · 16 October 2026 · synthetic correspondence experiments

Matched comparator: identical dense-to-matrix update with finalization disabled. Timing includes constructor copies, cache packing, audits, and result construction. Input generation is excluded for all methods. Three timing repetitions per case; four seeds at each of 12, 24, and 36 objects. These are exploratory local timings, not a calibrated risk guarantee.

| Scenario | Policy | Median speedup | Median work ratio | Disagreements / objects | Locked disagreements | Finalized |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| geometric | off | 1.000× | 1.000 | 0 / 288 | 0 | 0 |
| geometric | audited | 0.895× | 0.500 | 0 / 288 | 0 | 144 |
| geometric | permanent | 1.129× | 0.355 | 0 / 288 | 0 | 144 |
| near_duplicate | off | 1.000× | 1.000 | 0 / 288 | 0 | 0 |
| near_duplicate | audited | 0.516× | 0.522 | 0 / 288 | 0 | 134 |
| near_duplicate | permanent | 0.609× | 0.374 | 0 / 288 | 0 | 134 |
| tied_tail | off | 1.000× | 1.000 | 0 / 288 | 0 | 0 |
| tied_tail | audited | 4.106× | 0.118 | 0 / 288 | 0 | 240 |
| tied_tail | permanent | 4.349× | 0.118 | 0 / 288 | 0 | 240 |

## Delayed support reversal

A four-object fixed compatibility tensor makes two initially strong reciprocal winners swap after a weak driver gains strength. Permanent locking retains wrong early labels; periodic full support audits reopen them. This is one tested recovery case, not proof that auditing catches every late reversal.

- off: [2, 1, 0, 3]; 57 sweeps; 0 reopenings; full-update residual 5.31e-10.
- audited: [2, 1, 0, 3]; 30 sweeps; 2 reopenings; full-update residual 0.003768.
- permanent: [0, 1, 2, 3]; 17 sweeps; 0 reopenings; full-update residual 0.003768.

## Interpretation

The geometric cases use noisy, shuffled 3D point constellations and partial informative priors. The near-duplicate cases deliberately make two identities geometrically ambiguous. The tied-tail workload is a hand-built scheduling control with four unresolved tied rows, not an independent real-data benchmark. Ground-truth accuracy and unfrozen-reference agreement are separate columns in the CSV/JSON.

Frozen distributions remain soft. A stopped finalized solution can have a nonzero full-update residual and different strengths from the unfrozen solution. `converged` is true only when that full residual is below tolerance. Cache arithmetic, audits, and rebuilding are charged to the work count. Multiplication counts exclude memory copies, sorting, and allocation; wall-clock measurements include them.

Three observed mutual wins are an operational policy, not a theorem about future winners or truth. Column comparisons use raw support, which can be degree-biased on irregular graphs. Ordinary many-to-one class labeling is outside this policy. Real marker logs, larger label vocabularies, distribution shifts, and stronger assignment baselines remain future evaluation.
