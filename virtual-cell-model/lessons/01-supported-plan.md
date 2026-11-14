# One reusable task, one change in memory

Michael Emanuel Glover's Virtual Person / constructor-theoretic direction.
Assistant: implementation and teaching notes.

We continue the existing `virtual-cell` program. `vision::make_seeing_alex()`
creates our existing embodied Alex. We use his existing `PersonModel`, brain,
relational memory, context identities and directed support relations.

This lesson has one task:

> Given a context, an evidence identity and a plan identity, record the plan in
> that context if the memory already contains evidence supporting the plan.

The transformation is from a context without that plan to a context containing
it. `RecordSupportedPlan` retains the ability to apply the same rule again. It is
a constructor-like software model; it is not an assertion that the software is
an ideal physical constructor.

## Read these pieces in order

1. `include/supported_plan.hpp`: the result type and reusable task.
2. `src/supported_plan_demo.cpp`: Alex uses that task.
3. `tests/supported_plan_tests.cpp`: the behavioral contract is checked.

The essential call is:

```cpp
const RecordSupportedPlan skill;
const auto result = skill.apply(memory, context, evidence, plan);
```

`memory` is passed by reference: the task changes Alex's actual memory, not a
copy. The trailing `const` on `apply` means applying the task does not change the
skill object. The three `NodeId` values identify existing objects; they are not
new copies of the person, evidence, or plan.

`enum class RecordPlanResult` gives three named outcomes: absent support, an
existing record, or a new record. This is a small, domain-specific return type,
not a theory requiring every decision to have three categories.

The task validates its inputs before changing membership. Support is directed:
`evidence -> plan` is distinct from `plan -> evidence`. Repeating a successful
application does not duplicate the plan. The class performs no printing; a CLI,
rendered world or test can interpret its result separately.

## Run

From the existing project directory:

```sh
cmake -S . -B ../virtual-cell-local/joint-build
cmake --build ../virtual-cell-local/joint-build -j 4
../virtual-cell-local/joint-build/supported_plan_demo
ctest --test-dir ../virtual-cell-local/joint-build --output-on-failure
```

Expected demonstration:

```text
Without supplied support, plan recorded: false
With supplied support, plan recorded: true
Repeating the task recognizes the existing record: true
Plans in this context: 1
```

The support relation is an explicit authored input in this lesson. Recording a
supported plan is not a legal-move check, proof of a good chess move, inference of
an opponent's thoughts, or a model of subjective experience. The next small
lesson can distinguish a candidate plan from evidence produced by our C++ verifier.
