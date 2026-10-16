# Larger-field exploratory probe

One seed at 48 and 64 objects, with the same input construction and update as the first pilot. The aggressive preset was added during development; this is an exploratory follow-up, not an independently registered confirmation. All timings include constructor copies, cache packing, audits, and result assembly.

| Objects | Policy | Seconds | Speedup | Work ratio | Finalized | Disagreements |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 48 | off | 0.20220 | 1.000× | 1.000 | 0 | 0 |
| 48 | audited | 0.20639 | 0.980× | 0.782 | 12 | 0 |
| 48 | permanent | 0.17184 | 1.177× | 0.624 | 12 | 0 |
| 48 | aggressive_audited | 0.05474 | 3.694× | 0.095 | 48 | 0 |
| 48 | aggressive_permanent | 0.05399 | 3.745× | 0.095 | 48 | 0 |
| 64 | off | 0.63788 | 1.000× | 1.000 | 0 | 0 |
| 64 | audited | 0.60464 | 1.055× | 0.766 | 16 | 0 |
| 64 | permanent | 0.50885 | 1.254× | 0.613 | 16 | 0 |
| 64 | aggressive_audited | 0.16194 | 3.939× | 0.125 | 64 | 0 |
| 64 | aggressive_permanent | 0.15565 | 4.098× | 0.116 | 64 | 0 |

These are two particular synthetic constellations, not a proof of general speedup or correctness. A full-update residual can remain nonzero after assignment finalization. The delayed-swap failure and recovery case remains in REPORT.md.
