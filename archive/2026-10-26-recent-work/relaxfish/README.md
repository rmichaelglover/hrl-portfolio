# RelaxFish — polished chess research prototype

Architecture and source concepts: Michael Emanuel Glover. Based on the October 19, 2026 Gemini notebooks and two supplied white papers. Implementation polish: October 25, 2026.

The prototype connects legal chess geometry to a tactical role network. Each actual piece receives a distribution over seven roles; a dual distribution maps each role back to individual pieces. A damped compatibility update refines those distributions. A one-ply move ranker evaluates legal successor positions with material, attack coverage, and the role model.

## Run

From this folder:

```bash
python3 relaxfish.py
python3 relaxfish.py --plies 6 --output examples/my-run.json
python3 -m unittest -v
```

The installed environment already contains the dependencies. In another environment, use a virtual environment and `python3 -m pip install -r requirements.txt`. The requirements record the versions used here. Jupyter is optional for opening the notebooks; the module and tests run directly with Python.

Use `--fen 'YOUR FEN'` to analyze a standard chess position. Output includes piece-role and role-piece distributions, the iteration count, convergence residual, and a legal move suggestion. `--plies` produces a bounded self-play PGN. An unfinished game has result `*`.

## Files

- `relaxfish.py`: shared implementation, command-line runner, complex amplitude model, contextual subboard ledger, and multiprocessing helpers.
- `notebooks/`: four cleaned notebooks using the shared implementation.
- `test_relaxfish.py`: nine behavioral tests.
- `examples/`: verified analysis, self-play PGN, subboard ledger, environment versions, and source-paper game audit.
- `REPORT.md`: findings, corrections, evidence, and limitations.
- `originals/`: unchanged supplied notebooks and PDFs, plus extracted PDF text for reference.

## Model and interpretation

For N pieces and L roles, P has shape N×L and D has shape L×N. Each row is normalized. The dual is D = row_normalize(Pᵀ); it is a conditional distribution, not a separate matching solver. Each update uses bounded exponential compatibility support, dual feedback, the geometry-based priors, and damping. Convergence is measured by max absolute change in P. The loop stops at its tolerance or iteration cap, reporting whether the tolerance was reached.

The compatibility coefficients and tactical priors are explicit hand-selected heuristics. They need calibration. Dense compatibility costs O(N²L²) memory and O(KN²L²) arithmetic over K iterations. Ranking M legal successors repeats the model M times. These bounds describe this implementation, not a proof that chess is solved in polynomial time.

Complex amplitudes are a separate experiment. Scaling and renormalization are not unitary operations. Phase-only changes do not change basis probabilities; `mix_roles` supplies a unitary rotation that can expose relative phase. This experiment does not influence move ranking yet.

`distributed_profiles` parallelizes independent complete positions with standard-library worker processes. It retains cross-board interactions. The original Spark demonstration has been replaced; this package does not implement a Spark cluster or distributed quadrant synchronization.

The 4×4/6×6 ledger persists context-aware heuristic records. Full FEN, originating position, move history, window size and origin prevent collisions between materially different contexts. It does not certify subgames, prune moves, or provide tablebase evaluations.

This is a runnable prototype with legal move generation, not an established-strength chess engine. It has no measured Elo, global optimality proof, trained compatibility model, or forced-win guarantee. The supplied cybersecurity, computer vision, and geopolitical/economic applications were not present in this ZIP.
