# Experiment 002: questions as controlled measurements

Recorded after experiment 001 results, before generating this experiment's held-out circuits. This is a follow-up, not part of experiment 001's original design.

Use new circuit seeds 40000–40099 (familiar) and the same seed range with the novel motif. Reuse only experiment 001's training data and validation-selected relational strength. Do not tune on these new outcomes.

Each circuit's six units are randomly partitioned into three query-eligible units and three fixed forecast targets. Neither policy may query a target. At budgets 0, 1, and 2, predict effects on exactly the same three targets. This prevents an apparently successful policy from improving its score merely by removing the hardest measured units from the scoring set.

Compare unary and relational inference, each with random-query and disagreement-query policies. The disagreement policy chooses the eligible unit with the greatest variance among training role-effect templates under its current soft label supports. This is a transparent heuristic, not a calibrated expected-information-gain calculation. The random policy uses an independently seeded eligible-unit order. Within each method, policies have the same query budget.

A query measures the unit's zero-ablation effect in the synthetic circuit. Update its unary score using a Gaussian role-effect likelihood estimated from training, with a 0.03 probability-change standard-deviation floor. Then re-run inference. This likelihood is an analyst assumption, not a known causal law. A shifted mechanism can invalidate it.

Primary descriptive outcomes: target effect MAE and paired difference between query policies at budget 2, with 1,000 paired bootstrap resamples across circuits. Also report changes from budget 0. Compare both base and novel-motif circuits, retain all unfavorable outcomes, and distinguish querying a system from asking it to narrate an explanation. This prototype implements the former only.
