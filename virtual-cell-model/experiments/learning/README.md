# C++ learning through a relaxation field

Originating framework and project direction: **Michael Emanuel Glover**.
Assistant contribution: C++ forward/reverse implementation, optimizer, data
adapters, independent numerical checks, and experimental execution.

The learning loop now runs in dependency-free C++17. Python prepares measured
EOG features, checks C++ gradients against PyTorch autograd, and orchestrates
recording-disjoint comparisons. PyTorch is not the training engine.

## Start with the checked loop

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
python3 -m unittest discover -s experiments/learning -p 'test_*.py' -v
python3 experiments/learning/synthetic_demo.py
```

The Python checks require NumPy, SciPy and PyTorch; plotting uses Matplotlib.
The C++ finite-difference and learning checks run without these Python packages.

[Implementation](../../include/trainable_relaxation.hpp) ·
[C++ command-line program](../../src/relaxation_learning.cpp) ·
[C++ tests](../../tests/learning_tests.cpp) ·
[Python independent checks](test_learning.py) ·
[synthetic learning figure](synthetic-learning.png).

The public figure is a four-example synthetic implementation check. Its
checkpoint loss uses the same examples, so it is not a generalization benchmark.
The separate real-data evaluation uses disjoint recordings and local outputs.

## Forward dynamics

Each object i has standardized features x_i and categorical strengths s_i.
A shared unary model produces b_i = x_i U + c. Let A be the normalized sparse
neighbor graph and C the learned label-compatibility matrix:

```
s_i^0     = softmax(b_i)
m_i^t     = sum_j A_ij s_j^t
q_i^t     = softmax(b_i + C m_i^t)
s_i^(t+1) = (1-alpha) s_i^t + alpha q_i^t
```

The same U, c and C are reused at every step. Real-data experiments use six
steps, alpha=.5, six EOG features and two labels: 18 parameters total. The unary
baseline has zero relaxation steps and 14 effective parameters. Zero steps is
ordinary softmax regression, not an untrained constant guess.

This categorical update matches the existing C++ `CompatibilityField`: its
anchored `softmax(log(prior)+support)` is equivalent because `prior=softmax(b)`.
The tests compare their forward outputs numerically. It is a trainable variant
of that engine, not a claim that the independent-sigmoid GRRLE implementation
or the generic multiplicative HRL engine uses the same update rule. No trinity
factor is introduced for this pairwise temporal task.

## Reverse dynamics

The task loss is mean negative log likelihood on nodes with reference labels:
`L = -mean_i log(s_i^T[y_i])`. A label of -1 masks that node's own supervised
loss; its features may still carry messages to labelled neighbors.

For a softmax probability vector p and incoming adjoint v, the vector-Jacobian
product is `p * (v - dot(p,v))`. Starting at the final task loss, reverse mode
walks backward through every update:

1. Send alpha times the strength adjoint into the proposed softmax.
2. Differentiate its compatibility messages and accumulate the shared C gradient.
3. Send messages backward along the **transposed** graph dependencies.
4. Carry the (1-alpha) direct residual contribution into the previous strengths.
5. Accumulate the unary-logit gradient from every step.
6. Differentiate the initial softmax too; the unary model also created s^0.

Omitting the last step, or forgetting repeated unary injection, gives incorrect
unary gradients. Omitting the transposed message dependencies gives incorrect
neighbor gradients. Both are exercised by directed, unequal-weight and isolated
node fixtures.

`RelaxationMachine` owns parameters by value. `Forward` owns cached states and
proposals; `Adam` owns its moments. No new raw owning pointers, manual memory
allocation or custom destructors are needed. Calling `forward()` never consults
reference-label values to calculate strengths. `loss_gradient()` supplies the
separate supervised operation.

```cpp
using namespace virtual_cell::learning;
RelaxationMachine model(2, 2, 6); // two features, two labels, six updates
Adam optimizer(model.parameters().size());

const auto before = model.loss_gradient(example);
optimizer.update(model, before.gradient, .02);
const auto after = model.loss_gradient(example);
```

One optimizer step is not guaranteed to lower every example's loss. The checked
synthetic training run demonstrates the behavior of the complete loop.

## Numerical verification

- C++ central finite differences check all ten fixture parameters for 0, 1 and
  6 steps, each at mixing .15, .5 and 1: **90 derivative comparisons**. Observed
  worst absolute disagreement is about 1.5e-10.
- An independent float64 PyTorch expression checks the complete three-step
  forward field, scalar loss, and all parameter gradients.
- C++ training reduces loss on a synthetic fixture while retaining parameter bounds.
- CLI checks exercise training, serialization and reloaded predictions.
- Labels can change without changing forward strengths.
- Metric tests check tied-score ROC AUC and average precision, macro F1, Brier,
  and calibration-bin arithmetic.
- Preparation tests preserve feature/label pairing under graph shuffling and
  check training-only feature statistics.

The synthetic verification artifacts are [gradient data](synthetic-check.json),
[optimization history](synthetic-history.csv), and [PDF figure](synthetic-learning.pdf).

## Stability and finite depth

Parameters are updated by full-batch Adam, with gradient of `.0005*sum(theta^2)`
added to the training task gradient (lambda=.001). Unary parameters are projected
to [-5,5]; each compatibility coefficient is projected to
`[-1.5/label_count, 1.5/label_count]`. Projection occurs after the optimizer step;
it is a constraint on training, not an extra derivative silently inserted into
the forward model.

Because neighbor rows have nonnegative weights summing to at most one and the
softmax Jacobian has infinity norm at most .5, the relaxation's contraction
bound is

```
L <= 1-alpha + alpha * .5 * ||C||_infinity <= .875   (alpha=.5).
```

For fixed inputs this bounds the inference dynamics even as C changes between
training updates. It does not imply correct classification. Six steps optimize
a finite-depth prediction, not an exact equilibrium loss. The last-update
residual is retained in predictions; it is not silently called converged.
No implicit differentiation or chaotic-inference training is claimed here.

## Measured sleep-data experiment

`prepare.py` calls the existing calibrated EDF EOG extractor for files in a
user-supplied local config:

```json
{
  "train": [{"edf": "/local/train.edf", "stages": "/local/train_sleepstage.csv", "events": "/local/train_events.csv"}],
  "validation": [{"edf": "/local/validation.edf", "stages": "/local/validation_sleepstage.csv", "events": "/local/validation_events.csv"}],
  "test": [{"edf": "/local/test.edf", "stages": "/local/test_sleepstage.csv", "events": "/local/test_events.csv"}]
}
```

Each entry is one recording; lists can contain several recordings. Duplicate
EDF paths and duplicate EDF contents are rejected across aliases and splits.
Recording IDs are distinct from verified participant identities: this adapter
does not establish that different recordings came from different people.

Only six measured features enter the model: left/right filtered EOG RMS,
slope RMS and raw peak-to-peak amplitude. Each is log1p transformed, standardized
using **training-only** mean/std, and clipped to [-6,6]. Reference stages and
scorer codes never enter the unary features. Unknown/unscored stages and epochs
with either channel flagged as flatline are excluded. REM is positive;
other scorable stages are negative. This is classification of reference REM
stages, not detection of individual rapid-eye-movement events.

Sequences are split into chunks of at most 64 usable epochs. Edges connect only
adjacent original epochs; missing epochs, chunk boundaries and recording
boundaries break connectivity. Graph inference is **offline and bidirectional**:
future EOG features can inform the current epoch. Six steps provide up to six
hops of context within a chunk. This is not an online causal classifier.

```sh
python3 experiments/learning/prepare.py \
  --config /local/input-config.json --output /local/prepared
python3 experiments/learning/train.py \
  --data /local/prepared --output /local/training-run
```

The `.model` file stores dimensions, mixing, unroll depth and parameters. It does
not store feature names or standardization statistics: retain the prepared-data
manifest and training protocol with it. These are inference checkpoints, not
serialized Adam states for exact training resumption.

The measured run has been executed locally. The source supplies the entire
preparation and training pipeline; measured features, fitted parameters,
predictions and cohort results remain outside the published checkout.

The runner fixes seeds 73/91/117, 160 maximum epochs, learning rate .02, and
regularization .001. Validation NLL selects checkpoints, with patience 35;
validation macro F1 selects a threshold from the fixed .05-to-.95 grid.
All model/threshold selection completes before test predictions are evaluated.
No test-based retraining or threshold rescue is performed. A training-prevalence
constant predictor is included alongside the unary and learned-relaxation models.

An inference ablation shuffles rows within each test chunk while moving features
and targets together. This preserves unary input/target pairs and changes their
adjacency. It also changes which observations are chunk-chain endpoints and
reconnects gaps within shuffled chunks, so it is a temporal-structure ablation,
not a perfectly degree-preserving graph intervention. It uses the original
validation threshold; test labels do not choose a new one.

Outputs retain per-recording and pooled metrics: macro F1, balanced accuracy,
ROC AUC, tie-aware average precision, NLL, Brier, and ten-bin calibration error.
Three initializations measure initialization variability on the same test
recordings, not participant-level uncertainty. Local learning curves and the
complete numerical protocol are saved with results. A trained classifier's
normalized output is not automatically a calibrated probability.

## Evidence and scope

The implementation checks establish that the differentiation and optimization
machinery works. Generalization is a separate result and can fail. The measured
run should be assessed from its local report, including the constant baseline
and shuffled-graph ablation. The task has not been promoted into Alex's Body or
used to alter physiological laws.

This work follows the strategy of unrolling inference as a recurrent computation;
[CRF-as-RNN](https://www.robots.ox.ac.uk/~tvg/publications/2015/crfasrnn_iccv2015.pdf)
is a relevant precedent, not an assertion of identical algorithms. Our explicit
stability bound is distinct from the learned Jacobian penalties studied by
[Bai et al.](https://proceedings.mlr.press/v139/bai21b.html).
