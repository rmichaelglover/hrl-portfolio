# Labels are not mechanisms: a controlled study of relaxation-assisted circuit interpretation

Manny Glover / ClosedAI · AI-assisted research prototype · 31 October 2026

**Status: executed synthetic study, not peer reviewed. No language model weights, Mythos internals, or human subjects were used.**

## Main findings

1. On 100 held-out familiar circuits, categorical relaxation reduced mean absolute intervention-effect prediction error from **0.06731 to 0.04484** relative to unary labeling, a **33.4% reduction in this error metric**. The paired difference was -0.02247, with a circuit-bootstrap 95% interval [-0.03207, -0.01371]. This is not a 33.4% reduction in real-world AI risk.
2. The learned graph model with exact permutation search matched relaxation's familiar-condition result. This supports the value of the provided relational information, not a unique benefit of iterative relaxation or a new state-of-the-art method.
3. Both familiar and novel-motif circuits achieved 100% planted-label accuracy under relaxation, while intervention forecast error rose from **0.04484 to 0.13761** in the novel motif. Knowing a feature's assigned role did not determine the magnitude of its causal effect.
4. The selected intervention had **the same mean regret as unary labeling** in the familiar condition (0.00764). Better effect forecasts did not improve the downstream choice in this benchmark.
5. The selected ablation lowered output probability by **0.37098 in permitted contexts** and **0.20371 in blocked contexts**. It suppressed activity in both: this does not demonstrate a selective safety repair.
6. In a separate follow-up using new circuits, label-disagreement-guided queries provided **no gain for relaxation in the familiar family** and slightly worsened its forecast error in the novel motif. The query scheme updated label beliefs but could not revise its learned mechanism-effect templates.

## Why this question matters

The circuit-tracing paper uses readable features and graphs to propose computational mechanisms, then tests them with interventions. Our proposal is narrower: use relaxation labeling as an analysis layer over ambiguous labels. This study asks whether that layer helps predict intervention outcomes when the true computation is available for scoring.

It does not train a cross-layer transcoder, reconstruct an LLM circuit, identify an intention, or replicate Anthropic's experiments. It uses six-unit, multi-stage sigmoid circuits with designer-assigned roles. Their mathematical nonlinearity does not make them a realistic language model.

## Experimental setup

The planted roles are pressure relay, boundary relay, task drive, authorization gate, action mediator, and a decoy branch disconnected from the output. Names refer to the designer's formulas, not empirically discovered psychological states. We randomize internal unit indices and continuously vary coefficients and biases. Some internal edges are optional.

The analyst sees noisy activation descriptors and signed directed adjacency. Descriptors summarize means, spread, quantiles, and correlations with three observed inputs and output under correlated observational inputs. Test intervention effects are measured under independently sampled, balanced inputs. Access to input references, a known six-role taxonomy, and a one-to-one assignment constraint makes this much simpler than real feature interpretation.

Training: 120 circuits. Validation: 50 independent circuits. Primary test: 100 circuits reused across familiar/noise/corruption observation conditions, plus 100 separate novel-motif variants. Thus the four test conditions are **not 400 independent circuits**. Follow-up query test: 100 new familiar circuits and 100 new novel variants, using a fresh seed range. Generated conditions share parameters/seeds where specified in the designs.

Fit scaling, classifier parameters, graph compatibilities, and role-effect templates on training only. Select graph strength from the fixed grid 0, .25, .5, 1, 2, 4, 8 by validation intervention error; **selected strength: 1.0**. Freeze it before test. No test labels or intervention outcomes enter the primary inference functions. Synthetic primary and active-design notes are included with the code; these are local recorded designs, not an independently registered study.

## What the algorithms do

Unary inference classifies each unit from its descriptors, then uses maximum-weight one-to-one assignment. The topology baseline adds generic signed in/out degrees. Relational compatibility is estimated from signed edge/nonedge patterns between training roles. Categorical relaxation alternates compatibility messages and soft one-to-one normalization, damping updates before hard assignment. It is a new experimental variant inspired by the local GRRLE engine, **not a direct call to RelaxEngine or the existing GRRLE implementation**.

Exact graph MAP enumerates all 720 permutations under the same discrete objective. Shuffled-graph inference independently scrambles the observed adjacency while retaining descriptors. Zero gain reproduces unary assignment. A supervised ridge baseline forecasts effects directly without assigning roles. The uniform reference predicts the mean training role effect.

For every label-based method, predicted intervention effects come from training mean effects for each assigned role. This deliberately simple prediction layer is shared across methods. Its failure under changed wiring is a limitation of the analysis pipeline, not proof that relaxation itself causes that failure.

The primary causal measurement is the average output probability change after clamping one unit to zero and recomputing all downstream units in the original planted circuit. We also record mean-replacement interventions. Zero ablation can be off-distribution; neither intervention proves a historical training cause. The output is a scalar synthetic action propensity, not an actual harmful act.

## Primary results

Mean absolute error in output-probability changes; lower is better.

| Method | Familiar | Noisy descriptors | Damaged graph | Novel motif |
|---|---:|---:|---:|---:|
| Unary labels | 0.06731 | 0.09150 | 0.06731 | 0.20300 |
| Topology classifier | 0.06829 | 0.07213 | 0.08192 | 0.14031 |
| Relaxation | 0.04484 | 0.05121 | 0.04943 | 0.13761 |
| Shuffled graph | 0.09096 | 0.09946 | 0.08500 | 0.20687 |
| Exact graph MAP | 0.04484 | 0.04922 | 0.04714 | 0.13761 |
| Direct-effect ridge | 0.09156 | 0.10338 | 0.13476 | 0.17194 |

All relaxation runs met the recorded numerical stopping criterion. That says the inference stabilized, not that its explanation was causally complete. Novel-motif labels were perfect because the supplied role taxonomy remained identifiable, while new interactions changed how those roles affected the output.

The exact search sometimes outperformed relaxation when observations or graphs were damaged. The experiment therefore offers no claim of globally optimal relaxation inference. More expressive nonlinear direct-effect baselines and graph-neural baselines were not tested; the ridge and degree-classifier comparisons do not exhaust alternatives.

## Budgeted questioning follow-up

Each circuit has three query-eligible units and three fixed prediction targets. Targets cannot be queried. At budgets 0, 1, and 2, score the same target set. A query reveals one eligible unit's measured ablation effect. The analyst updates label scores using a Gaussian likelihood estimated from training role effects, with a fixed 0.03 standard-deviation floor.

The disagreement policy selects the eligible unit with the largest variance among role-effect templates under its current supports. This is **not calibrated expected information gain**. The random policy uses a separate seeded order. This is querying a synthetic experiment, not asking a language model for its stated reasons.

| Condition / inference / query policy | 0 queries | 1 query | 2 queries |
|---|---:|---:|---:|
| familiar / unary / random | 0.05993 | 0.05793 | 0.05663 |
| familiar / unary / disagreement | 0.05993 | 0.05312 | 0.05312 |
| familiar / relaxation / random | 0.04714 | 0.04714 | 0.04714 |
| familiar / relaxation / disagreement | 0.04714 | 0.04714 | 0.04714 |
| novel_motif / unary / random | 0.19988 | 0.19222 | 0.18787 |
| novel_motif / unary / disagreement | 0.19988 | 0.19607 | 0.17936 |
| novel_motif / relaxation / random | 0.14356 | 0.14521 | 0.14422 |
| novel_motif / relaxation / disagreement | 0.14356 | 0.14395 | 0.14650 |

For novel-motif relaxation, disagreement minus random at budget 2 was +0.00228 error, with bootstrap interval [0.00000, 0.00505]. This is a small generator-specific degradation, not a broad statistical claim about active learning. The unary policy comparisons had intervals including zero. Label uncertainty alone is insufficient when labels are already correct and the mechanism-to-effect mapping is wrong.

## Interpretation: what should RelaxEngine ask next?

Separate **label uncertainty** (what role does this feature play?) from **mechanism uncertainty** (how does this particular network implement that role?) and **model mismatch** (does our hypothesis family omit an interaction?). A useful investigator must be able to reject or revise its hypothesis family, not just increase confidence in its existing labels.

The next question should sometimes be: “Which observation would falsify our current interaction model?” A causal response that is inconsistent with every predicted role should trigger an explicit mismatch state or abstention. This study has identified the need for such a mechanism; it has **not implemented and validated that improvement**.

Further steps: repeat with other generators; add mechanisms that intentionally share or split roles; compare one-pass message passing and stronger nonlinear effect predictors; distinguish role prediction from direct quantitative circuit models; then test on instrumented trained networks with held-out intervention outcomes. No claim about Mythos can be made without evidence from Mythos or a carefully justified transfer argument.

## Reproducibility and limits

Eight implementation tests passed: causal-null decoy; actual downstream recomputation; zero-gain equivalence; exact-search reference; unit-permutation equivariance; reproducibility/access separation; query budget/target exclusion; fixed-target policy behavior. These check implementation properties, not the truth of the research hypothesis.

Independent-circuit paired bootstraps use 1,000 resamples. Intervals are conditional on this generator, not evidence of external validity. We did not correct exploratory contrasts for multiple comparisons and do not claim population-level significance outside the benchmark. Runtime in the raw records is shared across methods per circuit, not a method-specific speed benchmark.

The primary code's SHA-256 is `b7c14c6bc2d186ed0a0f75642bdc862cc71bf87c4dae099e8f10e235d4f1c2d7`. The executed environment was Python 3.10.12, NumPy 1.26.4, SciPy 1.15.3, scikit-learn 1.7.2. No dependencies were downloaded for this execution.

## Files and sources

- `DESIGN.md`, `ACTIVE-DESIGN.md`: prospective primary and follow-up designs, with the exploratory endpoint explicitly dated relative to the disjoint smoke run.
- `experiment.py`, `active.py`: reproducible computational experiments.
- `test_experiment.py`, `test_active.py`: implementation tests.
- `results/results.json`, `results/records.json`, `active-results/results.json`, `active-results/records.json`: aggregates and per-circuit outcomes, including null/unfavorable results.
- `study-figure.svg`, `study-figure.png`, `study-figure.pdf`: standalone figures.
- [Circuit Tracing: Revealing Computational Graphs in Language Models](https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html), 27 March 2025. Inspiration and methodological distinction; no claim of replication.
- Local foundations: the HRL portfolio's `hyperobject/relax_recursive_engine.py` and the separate relaxation-labeling repository's `python/grrle/engine.py`. Those programs are not executed by this benchmark.

AI assistance was used for design, code, analysis, and drafting. This is an initial public computational research note with reproducible artifacts, not a peer-reviewed paper or an independent audit of an AI vendor.
