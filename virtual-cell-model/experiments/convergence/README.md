# Compatibility fields: convergence and cost

Michael Emanuel Glover originated the compatibility-based Virtual Person research and this experiment's question: how does relaxation compare with Newton, especially when computation is constrained? Cypher implemented the shared-map benchmark, safeguards, tests and visualization. This experiment extends `include/compatibility.hpp` in the existing Virtual Cell C++ project.

## 1. One equation, three solvers

For each object i and label a, use the existing map

    T_i,a(p) = softmax_a(log prior_i,a + beta * sum_j,b C_ia,jb p_j,b).

Relaxation applies p <- p + eta (T(p)-p), with eta=0.5 or 1. Newton solves F(p)=T(p)-p=0, rather than claiming this signed compatibility map minimizes a specified objective. All start at exactly the same normalized prior. Binary coordinates x_i=p_i,0 and p_i,1=1-x_i preserve normalization. Strictly positive priors are required by this comparison wrapper; the underlying map still supports zero priors.

Success means max |T(p)-p| <= 1e-10, measured before the next update. A maximum of 500 updates is allowed, followed by a final residual evaluation. This residual is independent of damping. The older `CompatibilityField::run` API still uses its existing step-delta stopping rule; this benchmark deliberately uses the new solver interface and the shared `target` method.

Newton uses one-sided finite differences with h=+1e-6 for x<0.5, otherwise -1e-6. Each perturbed point remains feasible. Its dense Jacobian is solved by Gaussian elimination with partial pivoting and a 1e-12 pivot cutoff. A 0.99 fraction-to-boundary step and up to 24 halvings seek residual infinity-norm reduction by factor 1-1e-4*alpha. Failed solve/search falls back to half-step relaxation. All map evaluations, linear solves and fallbacks are counted. No fallback was used in these measured cases. This is a safeguarded numerical-Jacobian baseline, not an optimized Newton implementation.

## 2. Exactly reproducible synthetic fields

Objects form a periodic ring; each has two neighbors and two labels. Each neighbor edge contributes C=+0.5 for equal labels and -0.5 for unequal labels. The conflicting case reverses both signs. Missing entries in the heat map are zero. The effective coupling is beta*C; the heat maps show raw C.

| Case | Objects | beta | Prior label-zero strength |
|---|---:|---:|---|
| gentle-8 | 8 | 0.4 | 0.52+0.015 sin(i+0.3) |
| gentle-32 | 32 | 0.4 | same |
| near-critical | 8 | 0.98 | 0.50001+0.000001 sin(i+0.3) |
| strong-agreement | 8 | 4 | ordinary prior |
| conflicting-ring | 8 | 6 | ordinary prior, reversed compatibility |

For these binary rings, each row of the derivative of T has absolute sum at most beta: each neighbor contributes 2*beta*T_i*(1-T_i), at most beta/2. Thus the gentle and near-critical cases have a global contraction bound beta<1 in reduced-coordinate infinity norm. Near-critical is deliberately close to the bound, with priors near 0.5. The other cases have no such guarantee. The existing trainable relaxation model's separate parameter restrictions are not imposed here.

## 3. Read the results

`summary.csv` contains measured runtime and stopping outcomes; `traces.csv` contains every accepted-state residual and cumulative map count; `states.csv` records the actual terminal state; `compatibility.csv` records sparse raw matrices. Runtime is the median of 21 repetitions after one warmup per solver, alternating forward/reverse solver order. Min/max are the observed range, not confidence intervals. Timings include allocation, trace capture and solver overhead; exclude CSV and plotting. See `environment.txt` for machine and build details.

Newton takes two updates for each gentle case, but needs 69 map evaluations at n=32, versus 21 for full-step relaxation. In the captured run, full-step relaxation is faster for both gentle cases and strong agreement. Newton reaches the target near criticality and in the conflicting ring, where both relaxation settings exhaust their 500-update budget. These are budget-limited failures, not proofs that no solution exists.

The strong-agreement result is especially instructive: relaxation approaches label-zero strength about 0.9997, while Newton finds a different fixed point near 0.48–0.50. The latter is locally unstable under both tested relaxation maps. A root-finding solver can converge to a repelling fixed point. In the conflicting ring, Newton likewise finds a fixed point that is unstable under the tested iterations. `stability.csv` reports spectral radii of J_T and (I+J_T)/2 at terminal states, computed analytically from the binary map by the plotting script. A radius above one at a converged root establishes local instability; radii at nonconverged states only describe the local derivative there. Faster residual convergence does not establish better preference inference or identical solution selection.

## 4. Edge-computing research implication

This is a useful regression baseline for Michael's relaxation research: report residual, work, latency, failure and root selection together. Relaxation's inexpensive sparse iterations can beat Newton's lower iteration count. Critical slowing can reverse that result. Dense finite-difference Newton needs O(n) map calls per Jacobian, O(n^2) storage and O(n^3) dense elimination; the existing sparse field needs O(E+nK) work per target evaluation. These measurements are from a desktop x86 CPU, not an edge device or energy experiment. Next controlled comparisons can add analytic/sparse Jacobians, adaptive damping, asymmetric fields, wider label sets and measured edge-hardware power.

Five deterministic cases characterize these instances; runtime repetitions do not sample a population of compatibility problems. Keep fixed cases for regressions, then add held-out generated fields before making broad performance claims.

## 5. Run again

From this directory, run `bash run.sh`. It configures the existing CMake project in Release mode, builds the benchmark and the meaningful convergence checks, runs the checks, regenerates CSV measurements and renders figures. Requires CMake, a C++17 compiler, Python 3 with numpy and matplotlib. Python only renders measurements and computes the stated derivative diagnostics; both iterative solvers and all timed map work are C++.

The small OO components are `BinarySystem` (the equation), `Solver` (interface), `RelaxationSolver` and `NewtonSolver` (strategies), and `Result` (state and trace). Start reading `include/compatibility.hpp`, then `include/fixed_point_comparison.hpp`, then `src/convergence_benchmark.cpp`. This is a continuation of the existing Virtual Person program, not a replacement simulator.

## 6. Regular regression runs

The portfolio repository includes a weekly Monday GitHub Actions run and a manual trigger. It builds the existing native project, runs all CTest suites, and uploads the four C++ measurement CSVs as an artifact. Source changes also trigger it. Hosted-runner timings are a separate environment and do not replace the published desktop measurements. The workflow does not automatically rewrite the public report.
