# Receptors, memory, prediction, and regulation

Originating question and framework: **Michael Emanuel Glover**. Assistant:
implementation, numerical experiments, verification, and exposition.

This first experiment asks whether additional memory helps a receptor-bearing
compartment maintain an internal amount under fluctuating external input.
It uses stochastic receptor kinetics and an open-compartment transport model.
It is a synthetic, well-mixed control benchmark; spatial Brownian trajectories,
crowding, electrostatic potentials, ribosomes, and calibrated cellular parameters
are not implemented in this milestone. The existing measured IMPase study remains
a distinct empirical model, not a source of invented receptor parameters.

## Run

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
python3 -m unittest discover -s experiments/receptor -p 'test_*.py' -v
python3 experiments/receptor/experiment.py
./build/receptor_prediction_demo
```

Python requires NumPy and Matplotlib. The five Python checks also verify the
independent C++ observer and compartment equations. Source:
[experiment.py](experiment.py), [C++ classes](../../include/receptor_prediction.hpp).
All C++ state is value-owned and follows the Rule of Zero.

## Mechanisms and units

An imposed external reservoir has concentration C in µM. Each of 200 independent
receptors binds with rate `a = kon*C` and unbinds with rate `b = koff`, where
`kon = 1 µM^-1 s^-1` and `koff = 1 s^-1`. For a .1-second interval, the exact
endpoint transition probabilities at fixed C are

```
p01 = a/(a+b) * (1-exp(-(a+b)*dt))
p10 = b/(a+b) * (1-exp(-(a+b)*dt))
```

Binomial draws update initially free and initially bound populations separately.
These are endpoint occupancies, not a count of all intervening binding events.
Ligand depletion is neglected because the reservoir is externally imposed.
The receptor model itself retains physical state. The label `memoryless` means
**no added readout history**, not a universe without molecular memory.

The instantaneous concentration estimate is `p/(1-p)` in µM, using
`p=(bound+.5)/(N+1)` to avoid infinite estimates at endpoint counts. This
regularization is a scenario estimator, not a calibrated posterior interval.
Three fixed observers receive exactly the same receptor observations:

1. **Instantaneous:** predict using the current inverse-occupancy estimate.
2. **Filtered:** exponentially smooth its logarithm with a one-second time constant.
3. **Predictive:** extrapolate the filtered log estimate one second ahead, using
   a slope bounded to ±.5/s.

All forecasts are bounded to .15–6 µM. Each controller also receives the current
internal amount exactly, an explicit ideal-sensing assumption. The same feedback
law is used for all three:

```
u = clip((k*x_target + g*(x_target-x))/C_forecast, .1, 6)
```

Here `x_target=1 fmol`, `k=1/s`, `g=.8/s`, and u has units fmol/(s µM).
An actuator queue delays every command by ten intervals (one second). The
concentration of the interval controlled by that command is the forecast target.
Receptor measurements are interval-end readings; CSV time stamps mark that end.
Future concentration is stored for scoring and never supplied to an observer.

The internal compartment obeys `dx/dt = u_applied*C - k*x`. Its update is the
exact solution for constant influx during an interval. The ledger records
incoming material, outgoing material, and the new amount, satisfying
`before + incoming - outgoing = after`. This is an **open** material balance;
there is no assertion of conserved ligand in the externally driven reservoir.

Active uptake is assumed to hydrolyze one ATP per imported solute. The recorded
ATP amount equals the imported solute amount. ATP supply is not depleted in
this experiment. No ATP free-energy conversion, memory-maintenance cost, sensor
cost, computation cost, or complete thermodynamic dissipation is calculated.
Consequently this experiment cannot establish that memory saves total energy.

## Protocol and controls

Exploratory mechanism development used seeds 0–19. After adding the shared
internal feedback mechanism, final equations and constants were recorded in
[protocol.json](protocol.json), including the algorithm SHA-256, NumPy version,
and seed offsets. Seeds 100–119 were then evaluated without further numerical
controller changes. Each regime therefore has 20 held-out paired runs, with
all controllers sharing the same environment and receptor trajectory per seed.
There is no trained model or hyperparameter fit. Held-out here means withheld
from mechanism development, not a held-out human cohort.

Each run lasts 240 seconds. Metrics exclude the first 20 seconds and the last
one-second forecast horizon. The smooth regime is a log-concentration sinusoid
(period 18 seconds) plus correlated Gaussian noise. The independent regime uses
independent log-normal concentrations each interval. It changes both temporal
structure and the marginal concentration distribution; it does not isolate
temporal correlation alone.

The comparison reports forecast RMSE (µM), amount-regulation RMSE (fmol), and
ATP consumed during the same scored intervals (fmol ATP). Error bars show seed
standard deviations, not confidence intervals. All methods and failed comparisons
are retained. Constant-prior predictors and optimal controllers are not included;
this is not an exhaustive demonstration that memory is necessary.

## Held-out results

| Regime / observer | Forecast RMSE | Regulation RMSE | Transport ATP |
|---|---:|---:|---:|
| Smooth / instantaneous | .3141 | .1563 | 220.18 |
| Smooth / filtered | .4055 | .2115 | 220.16 |
| Smooth / predictive | .3130 | .1546 | 220.24 |
| Independent / instantaneous | .6617 | .1856 | 225.33 |
| Independent / filtered | .6231 | .1566 | 222.28 |
| Independent / predictive | .6635 | .1882 | 225.63 |

Prediction slightly improves regulation in the smooth regime, but does not
reduce transport ATP there. Filtering adds lag and worsens smooth-regime control.
In the independent regime, filtering performs better while trend extrapolation
performs slightly worse than the instantaneous policy. These are descriptive
results for the specified models, not evidence of universal biological benefits.
The mass balance also constrains ATP throughput: maintaining a similar mean
amount with the same efflux coefficient requires similar mean replenishment.

[Figure](comparison.png) · [PDF figure](comparison.pdf) ·
[all runs](runs.csv) · [development trajectory example](example.csv) ·
[held-out summary](summary.json).

## What this establishes—and the next mechanism

The benchmark separates sensing, prediction, delayed action, regulation, and
transport cost. Its internal amount feedback is a minimal homeostatic control
mechanism; predictive feedforward adds anticipation. The observer's memory is
an explicit modeled controller variable, not yet a chemically implemented
intracellular memory network. We have not established cellular experience,
self-awareness, optimal allostasis, or a causal mechanism that chooses rest.

The next spatial extension should replace the imposed reservoir with measured
or calibrated diffusion/reaction observations. Particle filtering would estimate
hidden trajectories; relaxation labeling would address competing associations
or binding assignments when those ambiguities actually arise. Neither MCMC
iterations nor label relaxation should be mistaken for physical elapsed time,
and electrostatic evidence should not be counted twice. Sampling refines an
inference; new measurements provide additional observational evidence.

Primary foundations:

- [McGuffee and Elcock (2010)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000694): spatial crowded-cytoplasm Brownian dynamics, a future physical extension.
- [Yi et al. (2000)](https://pmc.ncbi.nlm.nih.gov/articles/PMC18287/): integral feedback and robust adaptation. Our proportional controller is not a reproduction of that mechanism.
- [Still et al. (2012)](https://arxiv.org/abs/1203.3271): prediction and thermodynamics. Our transport ledger does not test their full thermodynamic result.
