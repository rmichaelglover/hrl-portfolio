# Systems of systems: evidence and recursive interpretation

Originating framework and integration thesis: **Michael Emanuel Glover**.
Assistant contribution: implementation, engine adapters, numerical comparisons,
verification, and exposition. Dedicated to James Calvin Glover.

This milestone connects the existing virtual Person and paired Eyes to Michael's
**actual HRL and GRRLE implementations**, copied byte-for-byte into `vendor/`.
The source hashes and repository base revision are recorded in
[vendor/PROVENANCE.json](vendor/PROVENANCE.json). Minimal package wrappers import
only the engines. WikiMRGRELE uses the same recursive engine for grounded claim
interpretation; its lexical frontends are not biological models and are not
silently substituted for one. The repository spells the recursive engine GRRLE.

## One model, several kinds of quantity

| Quantity | Meaning | Composition |
|---|---|---|
| Physical state | Counts, concentrations, voltage, elapsed time | Conserved chemistry and membrane dynamics |
| Likelihood | Compatibility of an observation with a specified generative hypothesis | Poisson observation model in this experiment |
| Bayesian posterior | Conditional uncertainty under that model | Prior odds times likelihood ratio |
| Fuzzy membership | Degree to which an observation satisfies a predicate | `mu_active = rate/(rate+5)`; memberships need not sum to one |
| HRL label strength | Normalized categorical support under factor rules | Prior-respecting multiplicative relaxation |
| GRRLE activation | Independent bounded support for a hypothesis | Recursive signed recurrent logistic update |
| Utility and Will | Objectives and permission to incorporate an interpretation | Existing multiobjective governor and explicit integration policy |

These are separate computational contracts, even when represented by doubles.
`PersonModel::boundary_evidence()` now returns owned evidence with its provenance,
the current observer's posterior, and two nonexclusive fuzzy memberships. It is a
`const` operation. It does not change a Cell, the Body, the Person's Will, or its
active self-representation. Missing observations are neutral rather than zero
observations in the sensory adapter.

## Equations and actual engines

For conditionally independent count channels of exposure t, the Bayesian unary
log-odds contribution is

`ell_c = n_c log(lambda_external,c/lambda_internal,c)
         - t (lambda_external,c-lambda_internal,c)`.

The default experiment uses equal hypothesis priors. Rates are estimated only
from training scenes with Gamma(1,1) smoothing. The independence assumption is
explicit and challenged by the shift control.

HRL contracts signed pairwise compatibility tensors against neighboring label
strengths and rescales support within each row. Its update is proportional to
`prior^0.85 * strength^0.15 * (1 + gain * normalized_support)`.
Its row rescaling means support magnitude alone does not express confidence.

GRRLE updates each hypothesis with a damped sigmoid of its prior logit plus
signed neighbor support. There are three sensor objects and a neutral parent,
with upward and downward relations. Upward weights average across sensors.
Parent evidence is not a repeated likelihood: it starts neutral. Recursive
feedback expresses a consistency preference, not new independent observations.
We expose the parent's score as `0.5 + 0.5*(external_activation-internal_activation)`;
this is a ranking score, not a calibrated probability.

A three-way factor is available in HRL, but no extra simplex is introduced here:
this experiment's rules are pairwise. Ordered windows and recursive levels remain
explicit. The existing simplicial tissue topology and relational memory survive.

## Held-out controls and results

Run `python3 experiments/relaxation/analyze.py` from the project root (NumPy and
Matplotlib required). Then run
`python3 -m unittest discover -s experiments/relaxation -p 'test_*.py' -v`.
C++ still builds without these Python dependencies.

There are 180 independent one-second scenes in each of four fixed groups:
training seed 1101; validation 2202; matched test 3303; shifted test 4404.
This is a scene split, not a split of correlated windows from one trajectory.
The candidate coupling grid is fixed at `{0, .25, .5, 1}`. Validation accuracy
chooses a gain, with smaller gain resolving ties; test results never select it.
Both engines select .25. The fuzzy rule and its thresholds are fixed in advance.
The zero-link, fixed-gain-one, and inverted-relation controls are reported too.
No model is automatically crowned the universal winner.

| Method | Matched test | Shared retinal disturbance |
|---|---:|---:|
| Bayesian unary combination | 100.0% | 57.8% |
| Fixed fuzzy conjunction | 95.0% | 95.0% |
| HRL, validation-selected | 99.4% | 55.6% |
| GRRLE, validation-selected | 99.4% | 55.6% |

The shifted generator adds a shared Poisson retinal activation to both eyes,
including internal-origin scenes. This both shifts the marginal rates and creates
conditional dependence. It does not isolate correlation alone. The fuzzy rule's
body-activity conjunct helps in this chosen shift; that is a testable result of
this generator, not a claim about all disturbances or human perception.

An abstention margin of .1 around .5 is an explicit comparison policy, not a
calibration guarantee. Both selected relaxation models have **zero coverage**
at this margin despite high matched classification accuracy. Gain one increases
coverage while inverted relations nearly reverse the matched classifications.
Convergence is therefore not correctness; greater activation is not stronger
empirical evidence. This result exposes a useful distinction between assignment
quality, strength scale, and a deployment decision. Classification accuracy
uses a fixed >.5 rule (ties select internal). Proper log loss and Brier scoring
are reported only for the generative Bayesian posterior.

[Raw predictions](predictions.csv), [summary](summary.json), and
[comparison figure](comparison.png) preserve all methods and failure controls.
No confidence interval or human generalization claim is inferred from this small
synthetic comparison. There is no fitted patient-level psychiatric model.

## Connection to the current Eyes and biochemical work

The adapter also reads 75 existing 100-ms windows across light, closed, one-eye,
endogenous activation, and declined-integration scenarios. Only differences of
left/right ganglion counts and elapsed exposure reach the engines. Photon audit
columns, endogenous-source flags, scenario names, and simulator truth labels do
not enter inference. Interoceptive evidence is absent and therefore neutral.
The one-second synthetic likelihoods are deliberately **unvalidated on retinal
spike trains**, so these outputs are inspectable transfer probes, not measured
attribution accuracy. Light and declined-integration traces yield identical
sensory inference: Will governs subsequent integration, not what photons did.

The 30 digitized IMPase measurements and held-out rate-law comparison remain the
empirical biochemical anchor. Their data hash is included in the report. They
are not repurposed as sensory labels, nor are optical assay units transformed
into invented human mood outcomes. Future measured sensory data should enter
through this same evidence boundary, with participant/session-level splits and
provenance, while assay parameters remain tied to measured conditions.

## Concept lifetime, naming, and MRGRELE

A definition/name can survive retirement of an active representation. Its next
activation can reuse the retained definition while revising its support from new
evidence. WikiMRGRELE's cited-claim layer is a natural future provenance bridge
for these definitions; the current adapter provides the hypothesis and evidence
contract, without claiming that a lexical relation is a physical cause.

Next experiments should compare measured observation models, uncertain rate
parameters, context-dependent compatibility, ablated hierarchy, and calibrated
abstention on additional development groups before opening a final test group.
Physics constrains feasible transitions; inference interprets observations;
preferences rank feasible actions. Each can be revised without identifying it
with the others.

## Primary foundations

- Zadeh (1965), [Fuzzy sets](https://doi.org/10.1016/S0019-9958(65)90241-X): graded membership.
- Hummel and Zucker (1983), [On the foundations of relaxation labeling processes](https://doi.org/10.1109/TPAMI.1983.4767390): consistency and compatibility.
- Repository engines and byte hashes above specify the algorithms actually run;
  neither algorithm is claimed equivalent to Bayesian inference.
