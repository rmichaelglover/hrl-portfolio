# Virtual Cell

Latest statistical milestone: [actual HRL/GRRLE evidence integration](experiments/relaxation/README.md)
compares Bayesian, fuzzy and recursive interpretations with independent scene
splits, missing-channel handling, and adverse compatibility controls.
[Small C++ lesson](experiments/relaxation/TUTORIAL.md).

Latest sensory milestone: [Alex’s pair of Eyes](experiments/eyes/README.md)
connects photon arrivals to a reduced retinal pathway, uncertain source attribution,
and an explicit attended-integration policy. [Gradual lesson](experiments/eyes/TUTORIAL.md).

Latest daily milestone: [a value-owned bioelectric Brain and Body](experiments/bioelectric/README.md)
adds membrane physics, reduced spikes, delayed synapses and organ-labelled
electrical compartments to the existing HomoSapiens hierarchy.
[Gradual C++ lesson](experiments/bioelectric/TUTORIAL.md).

Latest reaction-cycle milestone: [from stages to timing](experiments/enzyme-cycle/README.md)
adds exact-event sampling, a population master equation and an analytical
turnover check. Its candidate microscopic mechanism remains distinct from
the measured assay calibration below.

Latest empirical extension: [IMPase assay calibration](experiments/impase/README.md)
fits competing rate laws to traceable published enzyme measurements, with
held-out prediction and digitization sensitivity. This is distinct from the
earlier illustrative lithium response model.

Latest integrated example: `./build/person_model_demo`. See
[MODEL_UPDATE.md](MODEL_UPDATE.md) for the portfolio connections, equations,
implemented behavior, validation, and remaining extensions.

Originating framework and project direction: Michael Emanuel Glover.
C++ implementation and teaching examples developed with the assistant.

Dedicated to Michael's brother James Calvin Glover, often known as Jimmy:
a kind and gifted Kennesaw State University biochemistry graduate who wanted
to study prosthetics. This project connects practical learning with that interest.

## Build and run

Requires a C++17 compiler and CMake; no external libraries or downloads.

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
./build/virtual_cell_demo
```

Start reading `src/main.cpp`, then follow the types into `include/virtual_cell.hpp`.
The earlier lessons remain in the neighboring `metabeing-cpp` directory.

## What is represented

The containment tree is:

```
HomoSapiens (derived from abstract Person)
  Body → Organs → Tissues → Cells → MolecularCollections → Molecules
```

Containers own values. Adding an organ or tissue copies its state; it does not
create a reference to the original. Each stored cell has its own mutable state.
Tissue cell indices are stable because this version fixes its cell collection
at construction. References obtained from containers should not be retained
across operations that might reallocate those containers.

Neutral glycine has composition C2H5NO2. Elemental counts do not encode bonds,
charge, stereochemistry, or molecular identity by themselves. The tiny organ
containers do not yet implement heart or liver physiology.

## Governance and decision theory

The Person owns the top-level permission and preference policy. A Tissue combines
that with its own policy; a Cell's local Governor evaluates the resulting signal.
Body and Organ currently provide containment and routing, not separate policies.
This hierarchy is Michael's computational proposal; it is not a claim that a
conscious person directs individual cellular transitions.

1. Predict an outcome using cell features.
2. Check higher-level permission and the available energy store.
3. Compare expected utility plus tissue and Person biases with remaining.
4. Execute the chosen transition and record the decision.

Expected utility = success probability × benefit − cost. Failure contributes zero
benefit, cost is unconditional, and biases share the utility scale. Energy is a
separate scale in arbitrary toy units. Utility ties select Remain. This is a
restricted expected-utility model, retaining ordinary probabilities; no ternary
logic or generalized probability is introduced.

`TeachingForest` averages three handwritten decision trees. It has no training
data, fitted parameters, biological validation, or probability calibration.
It demonstrates the prediction interface for a future trained random forest;
predictions do not override hard constraints.

`Governor::choose` only returns a Decision. `Cell::deliberate_and_execute` then
applies it synchronously against current state. An arbitrary externally created
Decision cannot be submitted as authorization. Differentiation is a single toy
state transition, allowed once; no target lineage or reaction network exists yet.
Spent energy moves into a transition ledger rather than silently disappearing.
That ledger is bookkeeping, not a thermodynamic model. Molecule transfer conserves
the modeled molecule instances. Differentiation does not yet transform molecules.

## Why topology appears only within Tissue

Containment needs a tree, not filled simplices. A separate finite abstract
simplicial complex records relations among a tissue's cells:

- A vertex represents one cell index.
- An edge declares pairwise contact.
- An explicitly added triangle declares a three-cell cooperative group.

Adding a triangle automatically includes its edges, vertices, and empty face.
Three edges alone do not imply a triangle. This implementation supports dimensions
zero through two and rejects repeated or unknown vertices. It does not use ternary
logic: a three-vertex simplex is a geometric/combinatorial object, not three truth
values. Geometry, spatial distance, homology, and contact-dependent biochemical
effects are not implemented. The demo contrasts a loop with a filled triangle;
topology does not yet influence governor scores.

## Preserved directions

HomoTechnicus and HomoEconomicus remain concrete Person subclasses. The former
constructs a toy Tool description; the latter evaluates time saved against price.
HomoSapiens can later acquire these capabilities through composition, without
equating an actual human with one role.

Chess can supply experience records: observed state, proposed action,
prediction, decision, and observed outcome. The chess-memory demo now manually
encodes two verified historical game endings; no PGNs are automatically imported.
The metaphysical discussion remains a source of conceptual distinctions—identity,
names, relations, and governance—without making theological propositions numerical
facts in the biochemical model.

Next increments: named cell types; compartments and concentrations; atom-balanced
reactions; separate maintenance energy; organ policies; shared identity where
needed; experimentally grounded data and trained predictive models; prosthetic
interfaces. Introduce each abstraction when a concrete example requires it.

## Checks

The test executable checks transfer conservation, copy independence, topology face
closure and loop/triangle distinctions, permission and energy gates, utility ties,
state transitions and energy bookkeeping, repeated-action rejection, Person policy
propagation, and invalid numeric inputs. It uses explicit runtime checks so tests
remain active in Release builds.

## Relational memory and ordered routes

Run `./build/chess_memory_demo`. Read `include/relational_memory.hpp` and
`src/chess_memory.cpp`. Michael's NullSet is an abstract container interface,
not the mathematical empty set or a universal set. Root is its variable-size
concrete implementation. One, Two, and Three enforce exactly one, two, and three
distinct immediate members. A member can itself contain many other nodes.
The memory centrally owns nodes through unique_ptr; NodeIds reference them.
Explicit Root membership can create cycles, and traversal uses a visited set.
This is a finite recursive graph, not a claim about unrestricted set theory.

Directed, typed relations distinguish Supports, Attacks, LeadsTo, and Models.
An ordered Route must follow LeadsTo edges. Structural validation is not a chess
legality check: the demo manually records the observed sequence from carla227–
mannyfresher, UYo057a7, dated 2026-11-11 in Rancid Randi. It also records the
stalemate after 27.Qxf3 against olk, g3J5EH39. These were checked with python-chess
when reviewing the PGN. The source PGN remains unchanged in Documents.

Three stores a three-member set; it does not implicitly insert a filled triangle
into Tissue's SimplicialComplex. Routes are ordered separately from membership.
Ant-colony route exploration, opponent reply search, learned neural models, and
optimality comparisons remain future work; there is no route optimizer yet.

## Self and other

Michael's proposal: the modeled self includes a model of the other, while the
other remains a separate person. Brain owns a SelfModel and distinct OpponentModels.
It is currently a standalone component ready for later composition into Person;
the biological Person classes have not acquired a Brain member yet.

ForecastRecord stores a count and mean squared binary probability error (Brier
score). SelfModel separates predictions of one's own behavior from predictions
about whether one's opponent model will predict successfully. OpponentModel
records forecasts of observable opponent moves. A concrete future prediction
must specify its event and success criterion before observing the outcome.
The demo uses explicitly illustrative probabilities, not historical mind-reading
or probabilities extracted from the PGNs. Lower Brier scores mean better binary
probability predictions on the evaluated observations; a single score does not
establish calibration, strategic power, or utility.

Improved self-understanding may help identify where an opponent model is useful;
that is a hypothesis to evaluate using held-out observations, rather than a
guarantee encoded as a rule. Physical interaction and any proposed psychical
interaction are distinct from the representations; no mechanism for the latter
is assumed or simulated. Game-theoretic expansion will require alternative
actions, opponent responses, and utilities, beyond the observed historical route.

Memory tests cover cardinalities, invalid references, duplicate membership,
cyclic traversal, route direction, probability scoring, and separation of models.

## Multiple objectives and hierarchical summaries

Run `./build/objectives_demo`. The implementation is in `include/objectives.hpp`
and `include/hierarchical_summary.hpp`, with checks in `tests/objectives_tests.cpp`.

ObjectiveVector retains five distinct dimensions: health, security, relationships,
learning, and resources. Higher scores are better. The illustrative demo uses
comparable dimensionless 0–10 proxies. Scores are not dollars, direct measurements
of love, or values fitted from human or biological data. Application-specific
measurement and normalization remain necessary before comparing real outcomes.

MultiObjectiveGovernor first filters actions by permission and energy, then
returns the feasible Pareto frontier. Strict dominance means no worse in every
dimension and strictly better in at least one. Equal vectors do not dominate
each other. Choosing from that frontier uses explicit nonnegative weights
normalized to sum to one. Equal scores select the first frontier entry in input
order. No feasible action yields an empty optional, not an invented action.
The governor only describes a selection; it does not mutate cellular state.

The demo compares two policies over the same candidate outcomes. Equal weights
select sharing a meal; resources-only weights select overtime. These choices are
consequences of the supplied toy scores and weights, not findings about morality
or empirical economic behavior. A dominated option and an unaffordable ideal
demonstrate why constraints and dominance precede weighted selection.

SummaryStore attaches observations to existing Memory node IDs. A summary queries
the root's reachable membership graph, including local and descendant records,
and computes observation-weighted means and population standard deviations.
Shared descendants and cycles are visited once per query. Different records
stored at different nodes remain distinct observations: callers must not record
an already aggregated parent summary again as if it were independent raw data.
This initial implementation traverses records directly; it does not cache or
incrementally propagate child summaries. Hierarchy depth remains separate from
simplicial dimension.

Summaries retain observation counts, visited-node counts, and explicit notes
about omitted detail. Score dispersion is descriptive variation, not a calibrated
uncertainty interval or proof that a model generalizes. An empty summary has no
mean surprisal and count zero; its zero-initialized score arrays are placeholders,
not evidence. SummaryStore must be queried with the same Memory used for recording;
NodeIds are local to that Memory.

Surprisal uses -log(p) in nats, where p is the model's probability for the event
that occurred, assigned before observation. p=1 gives zero; p=0 gives infinity,
which is counted explicitly and retained in the mean rather than clipped. Invalid
probabilities and non-finite objective scores are rejected. Surprisal is recorded
separately from utility; this version does not automatically reward predictable
environments, optimize information gain, or infer a neural mechanism.

The new components compose with Brain's existing relational memory. They do not
replace the cellular governor, train a forest, implement ecological markets, or
introduce ternary logic. Next useful examples include chess forecasts attached to
position nodes and comparisons between predicted and observed objective vectors.
# Lithium and biochemical state evolution

The new [lithium extension](experiments/lithium/README.md) adds unit-labelled ion
amounts, compartments, reversible LiCl transport, competing Li/Mg enzyme binding,
IMPase-inspired balanced hydrolysis, and a synthetic downstream response to an
optional physiology owned by `PersonModel`. Molecular state evolves separately
from behavioral governance. [Research and primary sources](LITHIUM_RESEARCH.md).

Build with CMake, run `ctest --test-dir build --output-on-failure`, and execute
`./build/lithium_demo`. Recreate plots with `python3 experiments/lithium/plot.py`.
The parameters are illustrative; no clinical response predictor is implemented.
