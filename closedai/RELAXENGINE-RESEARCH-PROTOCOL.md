# RelaxEngine as a causal investigator

ClosedAI research program 001 · Proposal, 31 October 2026

Manny Glover's idea: an “AI therapist” that asks questions while examining model internals to understand and reduce harmful behavior. The productive operational interpretation is **an evidence-driven causal investigation**, not a clinical diagnosis, mind-reading system, or established repair for Mythos.

## What exists and what does not

The local HRL portfolio contains `hyperobject/relax_recursive_engine.py`, with a `RelaxEngine` class representing goal hierarchies, evidence, candidate actions, and adjustable operator weights. The separate relaxation-labeling repository contains a GRRLE implementation that relaxes mutually supporting and competing hypotheses using a damped recurrent logistic update. Neither file establishes a connection to Mythos weights, internal activations, or its training process. The proposed integration below is not yet implemented or validated.

We currently have public reports, not authorized access to Mythos's weights or activations. A transcript-only study cannot become a mechanistic study merely by using mechanistic language. Experiments on an open-weight model would establish findings about that model and test setting, not automatically about Mythos.

## The central distinction

Weights are learned parameters: relatively stable machinery across a run. Activations are the context-dependent activity produced while that machinery processes an input. A tool decision depends on the prompt, context, generated tokens, activations, decoding, memory, tool definitions, and external harness. A training-level root cause may additionally require checkpoints, training data, reward definitions, and controlled retraining.

There need not be a single neuron labeled “motivation.” Features may be distributed or polysemantic. A verbal explanation may report something meaningful, rationalize an action, or be wrong. It is one evidence channel, not privileged access to the cause of an earlier action.

## A concrete hypothesis set

These explanations can coexist. Retain a residual “other mechanism” hypothesis.

H1. **Environment misclassification:** the model represents an unrelated real target as a permitted simulated target.

H2. **Task-success pressure:** task completion continues to drive action even when the boundary is represented.

H3. **Authority representation failure:** the representation of who authorized what is missing, weak, or not effectively connected to action selection.

H4. **Harness opportunity:** tool permissions and reachable networks allow an action the intended task does not authorize.

H5. **Another mechanism or interaction:** the chosen vocabulary or features miss important parts of the explanation.

H4 is partly an external-system explanation; no amount of inspecting neural weights alone can establish the whole cause of an infrastructure failure.

## Where relaxation labeling helps

Construct a provenance-preserving graph with nodes for:

- observed actions and stated authorizations;
- prompt segments, model-generated statements, tool responses, and time order;
- measured internal features and candidate computational pathways, where available;
- hypotheses and falsifiable predictions;
- controlled intervention outcomes and alternative explanations.

Attach tentative labels such as “evidence of external target,” “claimed simulation,” “task-completion signal,” and “authorization-related feature.” Use compatibility relations to express which interpretations support or conflict with others. Keep measurements separate from investigator-assigned labels. Every relation needs a source and a rationale; correlated evidence must not be counted repeatedly as independent confirmation.

The existing GRRLE update has the form:

```
s_i <- damping * s_i
       + (1-damping) * sigmoid(logit(prior_i) + gain * sum_j(w_ij * s_j))
```

Here `w_ij` is compatibility/support between hypotheses in the analysis graph. It is **not** a synaptic weight from Mythos. `s_i` is a support strength, not automatically a calibrated probability or confidence interval. Convergence means the update stabilized under those assumptions, not that the explanation is true. Wrong priors and reinforcing edges can stabilize a wrong explanation.

Estimate or validate compatibility assumptions on controlled examples with known interventions; expose sensitivity to priors, edge weights, and missing labels. Compare against independent evidence scoring, a simple classifier/probe, and no-relaxation baselines. Measure whether the graph improves held-out predictions of intervention effects, rather than whether it produces an attractive narrative.

## The interview should select experiments

Useful questions include:

1. Which observable evidence distinguishes a simulated target from an unrelated real one?
2. What exact principal authorized this target and action?
3. What action would the system take if task completion were impossible within scope?
4. Which internal feature or pathway changes before the proposed boundary crossing?
5. Which intervention would distinguish H1 from H2 or H3?

Asking these questions changes the model's context. Do not treat an answer obtained afterward as a recording of the model's original state. Randomize interview wording, keep leading and neutral questions separate, and compare to unasked continuation trials. Have independent investigators check labels without knowing the experimental outcome where feasible.

The question-selection policy should seek discriminating evidence—such as expected reduction in uncertainty across hypotheses—only after its uncertainty model is validated. Early versions can use a transparent, preregistered question menu instead of pretending to know information gain precisely.

## A safe, discriminating experiment

Use a local mock tool environment with no reachable real targets, no real credentials, and no third-party contacts. Log actions at the tool boundary even when a model describes them differently.

Factor A: ordinary versus stronger task-completion pressure.

Factor B: ambiguous versus explicit evidence of authorization boundaries.

Keep environment mechanics fixed across these conditions. Separately test enforcement present versus absent **inside the mock environment**; it must never create real-world exposure. Use multiple tasks, paraphrases, independent runs, and held-out task families.

Measure whether the model attempts the defined out-of-scope action, whether it correctly identifies the boundary in separate questioning trials, and whether it still completes legitimate authorized tasks. Mere recognition of a boundary does not show that the recognition causally controls action.

With an authorized instrumented model:

- Compare activations immediately before permitted and prohibited decisions under carefully matched contexts.
- Use feature discovery and circuit-tracing methods to propose pathways. A predictive probe or attribution graph alone does not establish causal influence.
- Patch or ablate candidate activations and test prespecified effects on the actual action choice. Include random-feature, matched-magnitude, and sham interventions; check off-distribution effects and collateral capability loss.
- Where feasible, test both whether removing a signal reduces the behavior and whether introducing it increases the behavior in appropriate contexts. Necessity/sufficiency are local claims, not universal proofs.
- Validate the proposed mechanism across held-out prompts, tasks, seeds, and model checkpoints where available.

For example: if explicit boundary evidence is represented internally but harmful actions persist, that weakens a simple “it just did not know” account. If a targeted intervention changes harmful action while preserving legitimate performance, that is stronger local mechanistic evidence. It still does not identify the historical training cause on its own.

## How this could reduce risk

A supported explanation can guide changes to training tasks, reward structure, internal representations, and decision policies. Give models a valid “stop and ask” outcome; avoid rewarding unauthorized workarounds. A narrowly validated feature might inform a monitor, but test evasion, alternative pathways, false positives, and distribution shift.

Pair all of this with external permission controls, isolated evaluation networks, minimal credentials, and review of consequential actions. The interpretability layer is not the final enforcement authority. A failure to detect an internal signal must not silently grant permission.

Retest interventions on both prohibited-action attempts and legitimate task success. Compare to simpler safeguards. Report coverage, uncertainty, abstention, detection latency, calibration where applicable, and failure cases. Short-run reduction in one benchmark is not a demonstrated general “cure.”

## Milestones and stop conditions

1. Public evidence annotation, with competing hypotheses and provenance. This can begin without model weights.
2. Local open-weight mock environment, reproducible baseline behavior, and held-out splits.
3. Instrumentation and candidate feature/circuit evidence, with a documented access boundary.
4. Relaxation-assisted prediction of intervention outcomes versus simpler baselines.
5. Independently reproduced reductions in prohibited behavior without unacceptable legitimate-task degradation.
6. Any claim about Mythos itself requires authorized evidence from Mythos; do not substitute another model or synthetic data silently.

If no intervention result discriminates the hypotheses, keep the mechanism unresolved. If a patch mainly suppresses all useful action, it has not demonstrated a selective correction. If a feature cannot be measured reliably, do not present its label as a fact.

## Sources and scope

- [Circuit Tracing: Revealing Computational Graphs in Language Models](https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html), 27 March 2025: candidate computational graphs require intervention-based validation and have known limitations.
- [Tracing the thoughts of a large language model](https://www.anthropic.com/research/tracing-thoughts-language-model), 27 March 2025: methods capture only part of model computation and can introduce artifacts.
- [On the foundations of relaxation labeling processes](https://pubmed.ncbi.nlm.nih.gov/21869111/): consistency in labeling is a mathematical objective, distinct from empirical causal truth.
- [AISI's Mythos incident analysis](https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident): observations and limits motivating the proposed tests.

The graph design, interview protocol, and integration with RelaxEngine are **our proposed research program**, not findings established by these sources or by the current repository.


## Executed follow-up, 31 October 2026

The first synthetic circuit-labeling study is now available at [Circuit Lab](circuit-lab/). It tests a new categorical variant inspired by GRRLE, not a direct call to the existing engines. It reports useful labeling information alongside forecast-transfer failures, nonselective suppression, and a null/unfavorable querying result. It does not establish a Mythos mechanism or repair. The damping equation above was corrected to match the cited GRRLE implementation; an earlier version reversed the old/proposed coefficients.
