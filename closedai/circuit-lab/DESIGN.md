# Relaxation-assisted circuit interpretation: experiment 001

Design recorded 31 October 2026, before running the held-out evaluation.

Question: in a controlled family of planted nonlinear circuits, does relational inference improve labels for ambiguous internal features, and do those labels improve predictions of mean intervention effects?

This is a synthetic benchmark of a proposed analysis layer, not a replication of Anthropic's cross-layer-transcoder work, a trained language model, or a Mythos analysis. Its labeled computational units are supplied by construction; extracting comparable features from an actual network remains a separate problem.

## Ground truth and observations

Six sigmoid units have planted roles: pressure input relay (P), boundary input relay (B), task drive (D), authorization gate (G), action mediator (R), and output-disconnected decoy (Z). These are names assigned by the designer, not discoveries about AI motives. Continuous coefficients and biases vary by circuit. Unit indices are randomly permuted. Observational inputs are correlated; independently sampled evaluation inputs break that correlation.

The analyst receives activation statistics/correlations and signed directed adjacency. It does not receive test role labels or intervention outcomes. Source input names provide reference information for descriptors; this is stronger access than a black-box transcript study and weaker than giving away the planted label directly. The benchmark assumes one unit per role; all label-assignment methods receive that same one-to-one constraint. Real circuits need not satisfy it.

Intervention: clamp one supplied unit to zero (ablation) and re-execute downstream computation in the original planted circuit. Target: mean change in output probability over independent, balanced input draws. Zero ablation can be off-distribution; mean-replacement effects are also recorded as a sensitivity condition. No replacement model is used. This is an average local causal effect under the specified input distribution, not a training-level root cause or a measure of human intent.

## Splits and access boundary

Training circuits: 120 independent generator seeds starting at 1000. Validation: 50 seeds starting at 10000. Test: 100 seeds starting at 20000. No circuit appears in more than one split. All observations and interventions within a circuit stay in the same split. Exact counts may be reduced for development-only smoke tests using a separate seed range; final results must state their counts.

Fit descriptor normalization, unary label classifier, graph compatibility, and role-effect templates on training circuits only. Tune relational strength using validation mean absolute intervention-effect error, then freeze it. Test intervention effects are scored only after inference. The synthetic intervention server and analyst functions are separate in code; no inference function receives test ground truth.

## Comparisons

1. Uniform label support.
2. Unary multinomial logistic regression plus one-to-one assignment.
3. Unary plus generic graph-degree features (stronger topology baseline).
4. Categorical relaxation with learned signed-edge/nonedge compatibility and one-to-one soft assignment, followed by hard assignment.
5. Exact permutation search under the same relational objective: an optimization reference, not a causal oracle.
6. Relaxation on an independently permuted observed graph: broken-alignment control.
7. Direct supervised ridge prediction of intervention effects from descriptors and generic topology: a simpler alternative that need not label features.

Ablations: relational strength zero; observational descriptors only; graph corruption; a novel causal-motif condition. Use paired circuits within a condition and freeze hyperparameters before test conditions are evaluated.

## Outcomes

Primary endpoint: circuit-averaged mean absolute error predicting intervention-induced probability changes. Secondary: feature-label accuracy, signed-effect prediction, intervention choice regret (actual reduction achieved by chosen unit versus best available), convergence, runtime. A role-effect template uses only training intervention effects; its inability to predict new coefficient/motif effects is an explicit limitation. An accurate label does not guarantee an accurate intervention forecast.

Report paired bootstrap intervals resampling independent circuits (1,000 resamples; seed 65000) for key error differences. These intervals describe variability within this generator, not uncertainty about language models. Do not select the final narrative based only on the best condition. Report deterioration, null results, and strong baselines.

## Additional exploratory endpoint (recorded after the disjoint smoke run, before full test)

For the intervention selected by each method, report actual mean output change separately for negative boundary input (the planted permitted context) and positive boundary input (the planted blocked context). A reduction in both shows nonselective action suppression. This is descriptive, not a demonstrated preservation-of-capability test on real tasks. It does not affect hyperparameter selection or the primary endpoint.

## Failure criteria

The experiment does not support an added-value claim if relaxation fails to beat the unary baseline on the primary endpoint. Be explicit if it loses to the topology or direct-effect baseline. Improvement on planted data is feasibility evidence only. Strong sensitivity to topology corruption or an unseen mechanism weakens claims about deployment use. Support matrices are not calibrated causal probabilities.

## Connection to the paper

Circuit tracing supplies candidate feature interactions and stresses intervention validation; this experiment supplies an abstract feature-label inference layer, not a new tracing method. Relevant reading: https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html (feature labeling, supernodes, intervention validation, limitations).
