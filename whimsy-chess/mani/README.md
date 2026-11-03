# Maestro / Mani research workspace

Originating architecture and mission: **Michael Glover**. Implementation: Cypher / ChatGPT / Codex.

This first implementation gives Maestro a working research-to-accounting loop: import predictions and constraints, run relaxation labeling, inspect the graph, export and replay-verify receipts, allocate local demonstration credits 80/10/10, and calculate a revenue-funded Sanctuary scenario.

Open `index.html` through HTTPS or a localhost HTTP server. There are no dependencies or accounts. The workspace is linked from Maestro and the HRL landing page.

## Implemented

- A deterministic synchronous multiplicative relaxation-labeling solver with damping.
- User-supplied probability vectors and nonnegative, per-edge compatibility matrices; matrices transpose when following an edge backward.
- Explicit handling of isolated nodes, zero support, and zero initial probabilities.
- Inspection of initial/refined labels, weighted expected compatibility, optional labeled-node accuracy, and iteration records.
- Versioned challenge/result receipts committed with SHA-256; verification replays the solver and checks the commitment.
- A browser-local ledger, reverified on load, with duplicate commitment rejection. Each recorded completion yields 100 demonstration credits allocated 80 contributor / 10 science / 10 Sanctuary.
- Receipt export/import and a realized-revenue purchasing scenario.

The included challenge has six synthetic cells, fabricated prediction priors, two label groups, and known reference labels. The solver does not consult reference labels. They are used only to calculate accuracy after inference. This is an illustrative example, not independent biomedical validation, a trained neural model, or causal discovery. Generalization requires a separate, preregistered benchmark with independently held-out biological data.

## Challenge schema

Use the included editor as a complete example. Required fields: `id`, `labels`, `nodes`, `edges`, `iterations`, `damping`.

Each node has a distinct string `id` and a probability vector `prior` summing to one. Optional `truth` is a label index used only for evaluation. Each undirected edge has `source`, `target`, positive `weight`, and a square `compatibility` matrix indexed by source and target labels. Duplicate edges are rejected. Limits: 128 nodes, 16 labels, 2048 edges, 100 iterations, 2 MB imports. All compatibility entries are between zero and ten.

The update uses q_i(a) = sum_j weight_ij sum_b C_ij(a,b) p_j(b), followed by normalization of p_i(a) q_i(a) and a convex mixture with the prior iteration using the specified damping. This prototype does not establish universal convergence or monotonic improvement for arbitrary user-specified constraints. Zero-support nodes retain their distributions. Iteration ends at the specified bound or a maximum update below 1e-10.

## Receipts and accounting

Receipt verification checks consistency with the specified implementation. A hash is not an identity signature or a proof of compute expenditure, scientific utility, novelty, or consensus. Verification currently recomputes the full task; verifier cost is not asymptotically reduced. Local credits have no transferable value, redemption rights, or network-wide scarcity. Challenge renaming or resubmission in another browser is possible; the receipt store demonstrates accounting rather than adversarial token issuance.

Balances are derived from replay-verified receipts. At most 100 receipts are retained. Exports preserve individual receipts. A storage failure is surfaced and receipts remain available in memory for export. For integer allocations with totals not divisible by ten, residual units go to the contributor so total allocation is conserved.

The Sanctuary calculator takes independently specified realized distributable revenue, reserves 10%, subtracts delivery overhead, and calculates whole deliverable units. It does not infer cash from demo-credit balances. No funds are collected and no delivery claims are generated.

## Next engineering stages

1. Benchmark the combined neural-prediction / relaxation-labeling pipeline against neural-only, relaxation-only, and simpler interpretable baselines on a licensed scientific dataset.
2. Specify task admission, anti-replay rules, identity/attribution, evaluation governance, and reproducible numerical execution across heterogeneous nodes.
3. Measure verification overhead and assess whether a useful-work protocol can cover the actual workload. Matrix-product verification does not by itself validate nonlinear updates or scientific claims.
4. Deploy an independently tested network execution and settlement service before introducing transferable MNI. Define issuance, fees, custody, compute entitlement if any, and economic stress scenarios.
5. Connect a funded treasury to grant administration, supplier procurement, and independently confirmed delivery records.

CZI is a prospective alignment, not an announced partner. This implementation contains no CZI grant-disbursement API or automatic scientific validation.

## Research references

- Rafael Pass, [The Economics of Proof-of-Useful-Work](https://arxiv.org/abs/2606.06700): an equilibrium model with conditional inference-subsidy regimes, not a guaranteed MNI price floor.
- Pearl, [Proof of Useful Work](https://pearlresearch.ai/research/blog/proof-of-useful-work): the project's account of matrix-multiplication-based useful work.
- CZI, [Open Science Grants](https://chanzuckerberg.com/science/programs-resources/open-science/grants/) and [Science Funding](https://chanzuckerberg.com/science/science-funding/): institutional context.

## Verification

`node test-engine.cjs` tests deterministic replay, normalization, synthetic-label evaluation, isolated/zero-support nodes, damping, edge transpose invariance, malformed input rejection, and conservation of allocations.

Code and exports remain subject to the repository's existing [MIRL-1.0 terms](../../LICENSE). This implementation does not change project licensing or create ownership rights in third-party datasets.
