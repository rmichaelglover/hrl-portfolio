# IMPase: evidence before behavior

Originating framework, project direction and biochemical research objective:
**Michael Emanuel Glover**. The assistant performed literature retrieval,
manual figure digitization, implementation, fitting and report preparation.

## The empirical step

We have moved from hypothetical parameters to a conditional, testable enzyme
assay analysis. Thirty published figure markers are reconstructed with explicit
pixel coordinates. They are not invented replicates. The program fits multiple
rate laws and evaluates measurements excluded from fitting. A C++ implementation
agrees numerically with every fitted Python rate prediction.

The first evidence is recombinant **bovine** IMPase, not a human patient or human
cell. Our result is an assay calibration with a local predictive check. It does
not yet establish a human physiological mechanism or treatment-response model.

## Source conditions and provenance

[Strasser, Pelton & Ganzhorn (1995)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1136688/),
Biochemical Journal 307:585–593, doi:10.1042/bj3070585.
Figure 1 provides natural-substrate Mg rates; Figure 6a provides ribose/Li rates.
Assays: 37 °C, pH 7.5, 50 mM Tris/HCl and 0.1 mM EGTA; coupled A360 readout.
Figure 1: 0.5 mM Ins1P, 6 nM enzyme. Figure 6a: 3 mM nominal Mg, 87 nM enzyme.
Original rate replicates and their errors are unavailable here. Source-image
URLs and SHA-256 hashes, axis calibration, marker identities, and split labels
are retained in `data/`. Ambiguous overlapping low-Mg symbols are excluded.

The chosen digitization tolerance is ±2 pixels on both axes. It is an explicit
reading-error sensitivity, not an experimentally estimated noise model. Mg and
Li concentrations are nominal additions, not computed free-ion activities.
Optical rates remain Delta A360/min; no unreported path length is assumed.

## Competing equations

For magnesium M, compare:

```
Hill:              v = V / [(Ka/M)^h + 1]
Hill + inhibition: v = V / [(Ka/M)^h + 1 + M/Kmg]
Single-site:       v = V / [Ka/M + 1 + M/Kmg]
```

The last is the h=1 nested case. Ka is a conditional half-activation parameter,
not a proven microscopic dissociation constant. V is a fitted conditional scale.
The single-site label names the h=1 curve, not an established count of metal
ions bound to IMPase. The activation-only Hill fit hits its h=8 upper bound;
this does not repair its inability to turn downward at high Mg.

For substrate S and lithium L, use the general mixed rate law:

```
alpha = 1 + L/Kis
alpha_prime = 1 + L/Kii
v = V*S / [alpha*Km + alpha_prime*S]
```

Competitive fixes alpha_prime=1; uncompetitive fixes alpha=1; pure
noncompetitive constrains Kis=Kii; mixed allows them to differ. These are
phenomenological classes. An uncompetitive initial-rate pattern alone cannot
determine whether the microscopic lithium-bound state contains substrate or
product. No enzyme-state binding assignment is inferred from a curve fit.

Each dataset has its own scale and parameters. Ribose and Ins1P data are not
pooled as though the substrates were interchangeable. The natural-substrate
Mg experiment contains no lithium; the lithium fits concern ribose specifically.

## Fitting, selection and validation

Positive parameters are optimized in logarithmic coordinates with eight starts.
Training residuals use the actual digitized plot coordinate: rate for Figure 1,
reciprocal rate for Figure 6a. This treats an equal pixel error on its native
axis equally. It does not imply experimental rate errors were homoscedastic.
Reciprocal-space fitting is appropriate here for the reading-error question;
raw initial-rate measurements should instead use their experimental likelihood.

AICc counts kinetic parameters plus one estimated residual variance parameter.
The winner is selected on training AICc alone. Test RMSE is evaluated afterward,
with native-rate errors supplied for both datasets. Split labels were fixed
before numerical fitting, but after visually inspecting the published figures:
this is a retrospective within-figure validation, not prospective replication.
The withheld lithium series is 1.5 mM, extrapolating beyond training 0–1 mM.

## Results: ins1p_magnesium

Training markers: 7; held-out markers: 3. Selected: **single_site_inhibition**.

| Model | Training AICc | Test RMSE in fit coordinate | Test rate RMSE |
|---|---:|---:|---:|
| hill | -35.1389 | 0.00983935 | 0.00983935 |
| hill_inhibition | -15.6768 | 0.00234516 | 0.00234516 |
| single_site_inhibition | -53.2019 | 0.00347084 | 0.00347084 |

Rate RMSE units are Delta A360/min. AICc values compare models within this dataset only.

| Parameter | Fit | Pixel sensitivity 5th–95th percentile |
|---|---:|---:|
| V | 0.126738 | 0.111812–0.1423 |
| Ka | 0.559244 | 0.395759–0.72793 |
| Kmg | 2.41888 | 2.0348–2.96178 |

V is Delta A360/min; concentration constants are mM; h is dimensionless. Sensitivity ranges are not confidence intervals.

Log-parameter Jacobian condition number: 22.16. This local numerical diagnostic does not prove global or structural identifiability.

| Held-out ID | Observed rate | Predicted rate |
|---|---:|---:|
| mg_02 | 0.0641902 | 0.0614872 |
| mg_06 | 0.0504012 | 0.0523099 |
| mg_08 | 0.0405349 | 0.0355159 |

## Results: ribose_lithium

Training markers: 15; held-out markers: 5. Selected: **mixed**.

| Model | Training AICc | Test RMSE in fit coordinate | Test rate RMSE |
|---|---:|---:|---:|
| competitive | 60.9824 | 12.6085 | 0.00604351 |
| uncompetitive | 28.9426 | 3.59919 | 0.000890569 |
| pure_noncompetitive | 33.8368 | 4.54566 | 0.00117827 |
| mixed | 19.1327 | 2.18226 | 0.000305551 |

Rate RMSE units are Delta A360/min. AICc values compare models within this dataset only.

| Parameter | Fit | Pixel sensitivity 5th–95th percentile |
|---|---:|---:|
| V | 0.0985235 | 0.0900655–0.108838 |
| Km | 1.6092 | 1.38671–1.87636 |
| Kis | 2.71259 | 2.10251–3.66264 |
| Kii | 0.407495 | 0.351162–0.472132 |

V is Delta A360/min; concentration constants are mM; h is dimensionless. Sensitivity ranges are not confidence intervals.

Log-parameter Jacobian condition number: 56.48. This local numerical diagnostic does not prove global or structural identifiability.

| Held-out ID | Observed rate | Predicted rate |
|---|---:|---:|
| ribose_1.5_0 | 0.0191304 | 0.0190169 |
| ribose_1.5_1 | 0.0159585 | 0.0159719 |
| ribose_1.5_2 | 0.0140639 | 0.0137332 |
| ribose_1.5_3 | 0.0116226 | 0.0120274 |
| ribose_1.5_4 | 0.0112 | 0.0107751 |

## What the evidence changes

The natural-substrate dataset turns over at high magnesium, so a saturating
activation-only curve misses important structure. A Hill exponent is optional
complexity: retain it only if the available measurements support it. Sparse
low-Mg coverage limits what these selected markers can tell us about cooperativity.
The full source study reports cooperative activation. Our h=1 selection on just
seven training markers does not overturn that finding: the small-sample AICc
penalty is severe and ambiguous low-Mg markers were deliberately omitted. The
cooperative inhibitory fit has lower held-out error here. The evidence supports
activation plus inhibition more strongly than a unique activation exponent.
The ribose dataset tests whether both slope and intercept changes are needed;
its fitted lithium constants must not be transferred to Ins1P or humans.

The old synthetic model is preserved as a separate demonstration. Its constants
have not been silently replaced with bovine optical-assay constants. A complete
coupling needs enzyme abundance, free-ion speciation, assay-to-cell transfer,
product effects, compartmentation, and the actual substrate in question.

[Leech et al. (1993)](https://doi.org/10.1111/j.1432-1033.1993.tb17707.x)
reported product-associated lithium effects and substrate-dependent inhibition,
including a change at higher lithium. This motivates testing product-release
states rather than automatically interpreting uncompetitive kinetics as binding
only to an enzyme–substrate complex.

## Assumptions that still need testing

- Calibration is specific to preparation, buffer, temperature, pH and substrate.
- Apparent constants combine several processes; they are not atomistic energies.
- Small within-figure holdouts share experimental and digitization systematics.
- Pixel perturbations cannot recover missing biological replication or error bars.
- Model selection is conditional on this candidate family and its error objective.
- Two-metal activation, product retention, pH-dependent speciation, and transient
  bursts need experiments that distinguish them; more states are not automatically
  more identifiable.

## Next measurement to seek

The next empirical target is a natural-substrate lithium × magnesium × substrate
initial-rate matrix with matched enzyme preparation and known pH and temperature.
Add phosphate as an intervention, then a transient product-release time course.
Fit steady-state and transient observations jointly only when their conditions
are compatible. Hold out an entire concentration or experiment, report predictive
error and uncertainty, and test whether additional states improve prediction.

An informative design samples low and high substrate with and without lithium:
competitive and uncompetitive limits separate there. To identify Mg activation
and inhibition separately, include measurements below the rise, around the peak,
and beyond the fall. Independent human recombinant IMPA1 data are needed before
claiming species transfer. The existing Person architecture can later consume
validated cellular observables without equating an assay rate to a mental state.

## Reproduce and inspect

From the project root:

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
python3 experiments/impase/analyze.py
python3 -m unittest discover -s experiments/impase -p 'test_*.py' -v
```

Python analysis requires NumPy, SciPy and Matplotlib. `requirements.txt` records
versions used. The C++ library itself has no external runtime dependencies.
Files: `data/digitized.csv`, `data/provenance.json`, `results/fit-results.json`,
`results/held-out-predictions.csv`, three four-/two-panel figures in PDF/PNG,
and `results/IMPASE_ASSAY_REPORT.pdf`. The source article is linked, not bundled.
