# Whole-model update: embodied identity, compatibility, and experience

Michael Emanuel Glover originates the framework, its metaphysical and relational
interpretations, and its application to the virtual Person. The assistant
implemented this C++ teaching prototype and its validation checks.

## Portfolio exploration

This update examined the following local hrl-portfolio sources:

- `hrl/core.py`: prior-respecting label strengths, signed compatibility,
  explicit convergence reporting, and optional noise labeling.
- `hrl/tracking.py`: temporal memory expressed through a prior.
- `hrl/recursive_grounding.py`: bounded, damped representation updates with
  measurement anchors and validation checkpoint selection.
- `reciprocal-grounding/README.md`: name/referent distinctions, mutual matching,
  abstention, audit, and the failure of agreement under a shared wrong dictionary.
- `grrle-strong/README.md`: recursive structure and the distinction between
  numerical convergence and physical truth.
- `hrl/consensus.py`: a specific three-label consensus application. Its ternary
  labeling is not needed or imported here.

Portfolio files are unchanged. The new compatibility implementation is independently
written; it is not a numerical port of the Python core or reciprocal experiments.

## Shared runtime

`PersonModel` composes HomoSapiens, Brain, SummaryStore, and MultiObjectiveGovernor.
It preserves the existing abstract Person hierarchy and biological examples.

```
PersonModel
  HomoSapiens → Body → Organ → Tissue → Cell → Molecules
  Brain → relational memory + self-model + opponent models
  SummaryStore → observations attached to memory contexts
  MultiObjectiveGovernor → feasible frontier → explicit weighted selection
  Experience records → predicted/observed outcomes + provenance
```

Body and brain now have a common owner, but physiological coupling is not yet
implemented. Behavioral action energy has its own explicit budget and expenditure
ledger; it is not silently equated with cellular energy. Execution rechecks current
permission and budget. It represents budget consumption, not the actual effects
of a chess move or a social activity on biology. Candidate permission is supplied
by the caller, and the cellular Person policy remains a separate mechanism.

Names map to memory identities. Multiple names can resolve to one NodeId. This
version rejects ambiguous rebinding rather than inventing name disambiguation.
The referent is a modeled identity, not the external person or physical object.

## Optional compatibility field

For an object i and label a, each synchronous iteration computes:

```
support(i,a) = sum C(i,a,j,b) * strength(j,b)
target(i,:) = softmax(log(prior(i,:)) + coupling * support(i,:))
next = (1 - damping) * current + damping * target
```

The prior remains an anchor every round. Zero prior entries remain zero, so a
positive prior floor is needed if all labels should stay possible. Signed edges
support or inhibit assignments. Finite budgets, damping, maximum change, and a
convergence flag make the iteration inspectable. Convergence is not guaranteed;
budget exhaustion returns `converged=false`. These are compatibility strengths,
not calibrated probabilities, truth values, physical laws, or utility scores.
No fixed number of labels, ternary logic, implicit triangle, or unknown class
is imposed. Sparse edges avoid a dense four-index tensor for this small example.

Temporal carryover is explicit: the previous field can initialize a later prior.
This preserves information; it is not independent corroboration. The demo's
cooperation labels are handcrafted and do not calculate chess legality. Optional
compatibility results are not automatically inserted into action utility; a
validated mapping would be required to connect that inference to behavior.

## Observations and revision

An Experience retains the context, action, predicted and observed objective
vectors, forecast success probability, observed success, and provenance. The
model reports mean absolute error per objective and a binary Brier score. Summary
surprisal uses p for a success and 1-p for a failure, rather than always applying
-log(p) to both outcomes. The predictions and scores in the demo are illustrative;
the chess motif alone comes from the previously reviewed PGN.

Recording a discrepancy does not retrain a model or automatically change its
weights. This first feedback loop makes errors available for review. Portfolio
ideas such as bounded representation updates, validation checkpoints, rollback,
and reciprocal audits remain future extensions; implementing them requires a
specific learning task and independent observations. Agreement cannot substitute
for those observations.

Summaries still traverse the membership graph with shared-node deduplication.
Simplicial tissue contacts remain separate from that graph and from ordered routes.
The earlier tool maker and subjective chooser remain available as Person roles.
There is no neural network training, ant-colony optimizer, or generalized
probability implementation in this update.

## Run and inspect

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
./build/person_model_demo
```

Start with `src/person_model_demo.cpp`, followed by `include/person_model.hpp`.
`include/compatibility.hpp` is the optional inference component.

Validated: four test suites, including all previous tests, plus normalization,
positive/negative compatibility, no-coupling baseline, arbitrary label count,
iteration-budget exhaustion, alias identity, feasibility, action energy ledger,
predicted/observed discrepancies, failure surprisal, and rejected invalid inputs.

Next step: use a small recorded chess forecasting task to compare the same model
with and without relational support. Keep outcomes and evaluation separate from
the labels and parameters used to construct that support.


## Evidence integration milestone

[The systems-of-systems integration](experiments/relaxation/README.md) connects
PersonModel evidence and paired-Eye traces to exact HRL/GRRLE engine snapshots,
with separate Bayesian probabilities, fuzzy memberships, and recursive strengths.
Independent synthetic scene groups expose both success and shift failures;
the empirical IMPase calibration retains its own measurement provenance.


## Situated household milestone

[Alex at home](experiments/household/README.md) adds subjective map estimates,
optical-frame motion, remembered food, independent parental preferences,
cooperative permissions, and separate music-practice states. Household choices
combine the existing goal proxies with explicit joy, peace, stimulation and
autonomy weights. All new classes own state by value.


## ROS 2 observation and sleep milestone

[Passive tracking and real sleep replay](experiments/observation/README.md) adds
a separately owned external tracker, an optional ROS 2 Humble C++ node, real
local PSG EOG feature extraction, and timestamped reference sleep-stage epochs.
Tracking and sleep remain separate sessions. ReflectivePractice belongs to
PersonModel and records contextual attention revisions and named mantra rewards.


## Receptor prediction experiment

[The first molecular-control benchmark](experiments/receptor/README.md) separates
stochastic receptor readout, observer memory, future concentration prediction,
delayed uptake, internal feedback, and transport ATP consumption. Synthetic
held-out comparisons retain both improvements and failures; they do not establish
whole-system energetic efficiency or a molecular implementation of cognition.


## Trainable relaxation milestone

[Learning through the field](experiments/learning/README.md) implements the
existing categorical CompatibilityField update with trainable unary and shared
compatibility parameters. C++ reverse mode includes initialization and repeated
unary injection, agrees with finite differences and independent PyTorch autograd,
and retains an explicit contraction bound under projected training. Measured
sleep-data evaluation is recording-disjoint and remains in local study outputs.
