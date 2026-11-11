# From reaction stages to molecular timing

Originating framework and direction: **Michael Emanuel Glover**. C++ teaching,
implementation, numerical analysis and documentation developed with the assistant.

This milestone turns our C++ snippets into an explicit candidate reaction cycle,
with exact-event simulation, a population master equation, an analytical reference,
and inspectable results. The preceding [empirical IMPase analysis](../impase/README.md)
provides the measured assay layer. Its fitted apparent constants are not assigned
to microscopic rates that those measurements cannot uniquely identify.

## States and allowed transitions

```
Free --substrate binding--> SubstrateBound --catalysis--> ProductsBound
  ^                              |                         |     |
  |------- substrate unbinding --|                         |     | Li binding
  |                                                        |     v
  |---------------- product release ----------------------|  ProductsBound + Li
  |                                                               |
  |---------------- joint products + Li release -------------------|

ProductsBound + Li --Li unbinding--> ProductsBound
```

The `EnzymeState` enum retains our three reaction stages; a separate Boolean
records lithium occupancy. Lithium is allowed only in a products-bound state.
`release_products()` clears that occupancy and increments completed cycles once.
A second release cannot increment it again. Direct methods express allowed
transitions; `advance()` samples their timing from rate constants.

The joint release arrow is an explicit candidate assumption: lithium returns to
the buffer along with products. It is needed to define the destination of the
positive, Li-bound product-release rate discussed in our lesson. It is not a
measured elementary IMPase step. A future, evidence-driven mechanism can split
inositol and phosphate release into separate states and allow Li on a retained
phosphate state. This model currently combines both products.

[Leech et al. (1993)](https://doi.org/10.1111/j.1432-1033.1993.tb17707.x)
provides evidence motivating investigation of product-associated lithium and
release kinetics. It does not identify all the transition rates used here.

## Rate, probability, and competing events

For a fixed, isolated release hazard k over interval t,

```
p = 1 - exp(-k*t) = -expm1(-k*t)
```

At one second, k=1 gives 0.6321 and k=0.2 gives 0.1813. A slower rate gives a
lower probability over the same positive interval. The getter does not execute
an event. `release_probability()` returns zero outside a products-bound stage.

If Li can bind/unbind or other reactions compete during the interval, that
single exponential is not the probability of completed release through the
whole network. The full simulation accounts for those transitions. A constant
hazard is a buffered, well-mixed assay approximation; it is not a conscious
choice or a behavioral governor's permission.

## Assay assumptions and units

Substrate and Li are held at fixed buffered concentrations. Association constants
have units mM^-1 s^-1; dissociation, catalysis and product release have units s^-1.
The defaults are substrate=1 mM, substrate association=2, substrate off=0.5,
catalysis=3, product release=1, Li-associated product release=0.2,
Li association=1 and Li off=0.5. All are illustrative.

This is an open-assay reduction: substrate enters and products/lithium return
to reservoirs. It does not claim a closed elemental ledger. The separate
[conserved compartment model](../lithium/README.md) remains available. Mg, pH
speciation, reverse chemistry, atomistic energetics, product-specific release,
and finite buffer depletion are not represented in this reduced cycle.

## Exact-event and population implementations

The molecular simulation uses Gillespie waiting times and competing event rates.
The ensemble propagates the four-state continuous-time Markov chain by Poisson
uniformization, including expected product-release counts as a transition reward.
Large intervals are subdivided to keep each Poisson mean at most 10. Positive
probabilities and total enzyme population are retained, with truncation checked.
The ensemble's fractions are expected population values, not fractional states
assigned to a single enzyme. Seeded statistical tests verify sample means against
its finite-time expected cycle count.

For an independent analytical check, let a be substrate association times its
buffered concentration, c catalysis, d substrate dissociation, r unbound release,
s Li-bound release, b Li association times Li concentration, and u Li dissociation.

```
D = r*(s+u) + b*s
mean products-bound dwell = (s+u+b)/D
mean free dwell per completed cycle = (1+d/c)/a
mean substrate-bound dwell per completed cycle = 1/c
stationary flux = 1 / [mean free dwell + mean substrate dwell + mean product dwell]
```

The stationary state fractions follow their dwell contributions. At zero
substrate, flux is zero. If s=r, lithium occupancy changes but throughput is
unchanged: the model contains a useful no-effect control. Under the default
slower bound-release assumption, Li reduces turnover. Neither result is a
prediction of a person's response or evidence for the assumed microscopic rates.

## Results and reproduction

[Four-panel figure](reaction-cycle.png) · [Vector PDF](reaction-cycle.pdf) ·
[Trajectories](trajectories.csv) · [Summary](summary.json)

From the project root:

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
./build/enzyme_cycle_demo
python3 experiments/enzyme-cycle/analyze.py
```

The C++ code uses only the standard library. Plotting uses NumPy and Matplotlib.
Seven CTest suites include allowed/rejected transitions, count invariants,
fixed-rate probabilities, positive normalized population fractions, analytic
stationarity and flux, interval-splitting equivalence, stochastic agreement,
zero substrate, and the equal-release-rate null case. Five Python checks in
`experiments/impase` separately validate empirical fitting and C++ agreement.

The next scientific milestone is to constrain product-release steps with matched
transient measurements. Steady-state apparent constants alone cannot determine
all of this model's individual rate constants.
