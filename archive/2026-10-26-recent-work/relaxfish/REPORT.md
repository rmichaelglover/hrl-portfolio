# RelaxFish implementation and source audit

October 25, 2026. Source: `2026-10-19-20261025T234912Z-1-001.zip`.

## Result

Delivered a standalone Python chess prototype and four cleaned notebooks. The design retains tactical role distributions, primary/dual assignment, geometric constraints, complex role amplitudes, subboard records, and parallel execution. Original files are preserved in `originals/`.

## Corrections

| Supplied issue | Polished behavior |
|---|---|
| `assert dim in, ...` prevents parsing | Validated 4×4/6×6 sizes and window bounds |
| Projection loop never advances its ray coordinates | Replaced hand-written projection with python-chess attack and legal-move maps |
| Dual shape 7×12 is multiplied by a 7×7 matrix | Dual is 7×N, using actual piece identities and explicit normalized feedback |
| No actual chess board or legal move integration in HRL solver | Complete standard chess positions, legal successor ranking, and PGN output |
| Negative support can create invalid probabilities | Nonnegative exponential weights, input checks, damping, normalized updates |
| No stopping criterion or numerical convergence evidence | Iteration cap, residual history, explicit convergence flag |
| Hunting and immobility functions return constants | Removed constant tactical assertions; attack coverage and legal terminal detection use board state |
| All Spark cells start identically and apply the same symmetric update | Parallel jobs analyze distinct complete positions; no artificial quadrant convergence claim |
| Phase changes are described as affecting role probabilities directly | Distinguish phase changes, amplitude scaling, and mixing; test their different effects |
| “Solved” crops and evaluation≈0 imply a draw certificate | Contextual heuristic ledger explicitly marks records uncertified |
| Position keys concatenate cell values without full game context | Structured serialization retains full position, window and history context |
| Role sampling uses uncontrolled global randomness | Caller-provided random generator enables reproducibility |

## Verification

Nine tests passed. Coverage includes normalized primary/dual matrices with changing piece counts; explicit iteration-limit reporting; attack versus legal destination semantics; queen attack composition; pins, castling, en passant and promotion; mate-in-one selection and terminal positions; phase invariance and relative-phase mixing; contextual ledger keys and bounds; serial/parallel agreement; and invalid numeric input.

Every code cell in each cleaned notebook executed successfully in the installed Python environment. Starting-position relaxation reached residual 7.55×10⁻⁹ after 38 iterations with tolerance 10⁻⁸. The six-ply command-line self-play completed, and the exported PGN was parsed back without errors. These checks establish execution and selected invariants; they do not establish playing strength or universal convergence.

## White-paper game audit

The PDFs contain different move scores. Replaying the score in `RelaxFish_Quantum_WhitePaper (1).pdf` accepts 87 plies and fails on **44...Qxc4**: Black no longer has a queen. Replaying the other PDF, after removing standard `?!` annotation suffixes, reaches the non-chess token **Point_Convergence** at Black's 50th move. Neither supplied text is a complete certified legal game as written. The original scores are preserved and have not been silently repaired. Machine-readable details are in `examples/paper-game-audit.json`.

The PDFs' claims of globally optimal equilibrium, eliminating timeouts, quantum behavior, and established strength are unsupported by the supplied implementations. Numerical stationarity is distinct from chess optimality. Unit normalization is distinct from unitary evolution. The polished documentation makes these distinctions explicit.

## Research limits and next milestones

The move selector uses one ply and heuristic weights. It can miss tactics beyond that horizon. No playing-strength benchmark or Elo estimate was performed. The dual is a normalized transpose with feedback, not a learned independent inverse network. Roles are soft scores, so low-probability assignments can describe atypical pieces. The amplitude experiment and subboard ledger are available but not incorporated into the move-ranking evaluation. There is no cross-scale relaxation propagation yet.

A meaningful next evaluation is a fixed tactical-position suite against material-only and geometry-only baselines, followed by controlled games with fixed budgets and recorded outcomes. Only measured improvements should justify stronger performance claims. Verified tablebase probes could later certify eligible full endgames; arbitrary cropped boards cannot inherit those guarantees.
