# Proof of Deterministic Distillation — experimental protocol v0

**Originating architecture: Michael Glover. Implementation: Cypher / ChatGPT / Codex.**

PoDD adds a portable numerical profile, content-addressed challenges, committed iteration traces, replay verification, and selected-transition audits to the Maestro / Mani workspace. It is an execution-verification substrate. It does not yet implement distributed consensus, authenticated proposer identities, staking, slashing, block production, treasury transfers, or scientific validation.

## Implemented components

- `podd.js`: dependency-free browser/Node library using BigInt arithmetic and SHA-256.
- `podd.schema.json`: JSON Schema 2020-12 definitions for receipt, normalized challenge, complete trace bundle, and audit openings. The default schema validates a bundle. Individual definitions are under `$defs`.
- `podd-node.cjs`: headless proposer/verifier and a loopback JSON-RPC service.
- `podd-ui.js`: create/export traces, sample/export openings, and import/verify bundles or audits inside Maestro.
- `test-podd.cjs`: deterministic regression vectors, protocol invariants, adversarial traces, Merkle tampering, and RPC routing tests.

The browser's original floating-point scientific view remains version 1. PoDD has its own arithmetic version: its results can differ slightly because of quantization. Neither format is silently treated as the other.

## Deterministic arithmetic: rl-fixed6-v1

Wire values for probabilities, damping, edge weights, and compatibilities are unsigned canonical decimal strings. Scale is 1,000,000. Probability rows sum exactly to that scale. All transition arithmetic uses arbitrary-precision integers.

The existing challenge importer quantizes priors by first rounding each input probability times 10^12, then applying largest-remainder normalization to a total of 1,000,000. Weights, compatibility values, and damping are rounded to the nearest multiple of 10^-6. A positive edge weight that becomes zero is rejected. This importer is a convenience; independent nodes execute the already-normalized integer challenge.

For each synchronous transition:

1. Compute neighbor support using exact sums of weight × compatibility × probability. Follow reversed edges using the transposed compatibility matrix.
2. Multiply each current probability by its support.
3. Normalize to scale using integer division. Assign remaining units by descending division remainder, breaking ties by label index.
4. Mix current and refined probabilities using the fixed-point damping value. Normalize again using the same rule.
5. Preserve the previous row when total support is zero. Initial zero entries stay zero.

Execute exactly N transitions, where 1 ≤ N ≤ 100. This version has no early-stop rule: repeated fixed-point states are valid. Initial state is index 0, final state index N. Label assignment uses maximum probability with the lowest-index tie break. The normalized challenge retains node/label/edge order. Relabeling or reordering is not graph-isomorphism canonicalization.

## Computational identity and canonical encoding

Challenge identity covers the complete normalized execution specification: arithmetic profile, scale, ordered nodes and priors, ordered labels, ordered weighted constraints and compatibility matrices, damping, and iteration count. The display name and evaluation-only truth labels are excluded. Changing either cannot manufacture a different computational identity.

Canonical encoding recursively sorts object keys in ECMAScript UTF-16 order, preserves array order, uses ECMAScript JSON string escaping, permits finite JSON numbers, and produces UTF-8 without whitespace. Committed numerical magnitudes use decimal strings; integer counts use JSON integers. This is a protocol-specific encoding, not a claim to implement a different canonical-JSON standard.

Domain-separated SHA-256 commitments:

- Challenge: `SHA256("mani/podd/challenge/v0" + NUL + canonical(challenge))`.
- State leaf i: `SHA256("mani/podd/state/v0" + NUL + canonical({iteration:i,state}))`.
- Internal branch: `SHA256("mani/podd/branch/v0" + NUL + leftHex + rightHex)`.
- Receipt ID: `SHA256("mani/podd/receipt/v0" + NUL + canonical(receiptWithoutReceiptId))`.

Branch children are their lowercase 64-character hexadecimal digests, not raw digest bytes. Every tree level duplicates its last node when odd. Leaves commit to ALL N+1 states, including their indices. This is an ordinary binary Merkle trace tree with selectively disclosed openings, rather than a sparse-key Merkle tree.

## Receipt and witness separation

A compact receipt contains:

```json
{
  "protocol": "mani-podd-0",
  "profile": "rl-fixed6-v1",
  "challengeId": "<64 lowercase hex characters>",
  "iterations": 40,
  "leafCount": 41,
  "traceRoot": "<64 lowercase hex characters>",
  "initialStateHash": "<64 lowercase hex characters>",
  "finalStateHash": "<64 lowercase hex characters>",
  "finalAssignments": [0, 0, 0, 1, 1, 1],
  "receiptId": "<64 lowercase hex characters>"
}
```

Damping and all execution parameters are in the challenge committed by `challengeId`; they are not independently mutable receipt fields. The example placeholders above are illustrative, not a valid receipt.

A full bundle contains `{receipt, challenge, states}`. Full verification checks all shapes and bounds, the initial-state anchor, every state commitment, the Merkle root, assignments, and all transitions. A receipt alone cannot supply the input data or prove execution.

An audit contains `{receipt, challenge, initial, final, transitions}`. Each state opening has `{iteration, state, siblings}`; sibling order and direction follow the leaf index and tree width. Each selected transition includes `before` and `after` openings. The verifier checks the anchored endpoints, membership proofs, exact requested indices, and selected state transitions. It does not need the complete trace.

Schemas validate structure; runtime checks additionally enforce cross-field dimensions, probability sums, permitted magnitudes, digest equality, tree geometry, and valid transitions.

## Sampling: what it establishes

The validator chooses a 32-byte seed AFTER the proposer commits the receipt. This prototype generates a local CSPRNG seed in the browser/CLI; it does not authenticate commitment publication time or provide a decentralized randomness beacon. Shared files do not establish independent seed selection.

For each step index i, derive a selection score from SHA-256 over domain `mani/podd/sample/v0`, receipt ID, seed, and i. Select the k distinct lowest scores, breaking ties by index. Verifiers recompute the selection. CLI `open` and `audit` bind the selection file to the receipt ID.

For m bad transitions among N fixed transitions, uniformly sampling k distinct transitions misses them with probability:

`C(N-m, k) / C(N, k)`.

For a single bad transition, this is `(N-k)/N`. Checking 5 of 40 steps can miss it with probability 87.5%. A false intermediate state can have a completely valid suffix. The tests construct exactly this counterexample: step 0 is forged, subsequent transitions are correct; a last-step audit passes, and full replay rejects it.

Statuses are therefore explicit:

- `full-replay-verified`: all transitions replayed from the anchored initial state.
- `all-transitions-verified`: authenticated openings and transition checks cover every transition.
- `sampled-transitions-consistent`: only requested transitions checked.

All statuses report `settlement: "none"`. No sampled audit creates credits or finality. A Merkle commitment does not prove data availability; withholding the challenge or trace can prevent verification.

## Headless workflow

Run from this directory using Node 20 or later:

```sh
node podd-node.cjs example > /tmp/mani-challenge.json
node podd-node.cjs create /tmp/mani-challenge.json > /tmp/mani-trace.json
node podd-node.cjs verify /tmp/mani-trace.json
node podd-node.cjs sample /tmp/mani-trace.json 5 > /tmp/mani-selection.json
node podd-node.cjs open /tmp/mani-trace.json /tmp/mani-selection.json > /tmp/mani-openings.json
node podd-node.cjs audit /tmp/mani-openings.json /tmp/mani-selection.json
```

The browser exports an audit envelope `{sample,audit}`. The CLI `open` command emits the raw audit; for browser import, wrap it with its selection as `{sample,audit}`. Do not supply a proposer-chosen seed as if it were independent validator randomness.

## JSON-RPC interface

```sh
node podd-node.cjs serve 8891
```

POST JSON-RPC 2.0 requests to `http://127.0.0.1:8891/rpc` with `Content-Type: application/json`. Requests require `id`, `method`, and object `params`. Batch requests/notifications are not supported in v0.

| Method | Params | Result |
|---|---|---|
| `podd_create` | `{challenge}` (original floating-point input schema) | Full trace bundle |
| `podd_verify` | `{bundle}` | Full replay status |
| `podd_sample` | `{receipt,seed,count}` | Selection indices and seed |
| `podd_open` | `{bundle,indices}` | Authenticated transition openings |
| `podd_verifyAudit` | `{audit,expectedIndices}` | Selected-transition verification status |

Transport is deliberately loopback-only, rejects browser Origin headers, limits requests to 8 MB, and serializes verification work. The caller must check `expectedIndices` against its independently selected audit. This is a local background verifier, not an authenticated peer network. No service is deployed by the static website and no endpoint is contacted by its browser UI.

## Dispute and settlement design: specified, not deployed

A production dispute system needs an authenticated claim, a data-availability deadline, an audit interval anchored to an actual consensus clock, proposer bonds, challenger bonds, timeout rules, and an agreed adjudicator.

A sensible claim lifecycle is:

`submitted → data available → pending audit → disputed / eligible for settlement → settled`.

An audit-window timeout is a protocol decision under explicit watcher assumptions. It does not convert a sampled mathematical check into a proof of all transitions.

For a disputed execution, commit both claimed traces against the same initial challenge. Bisect to an adjacent-state disagreement, authenticate openings, and execute that transition under the pinned arithmetic profile. A relaxation-labeling iteration may still contain many operations. A bounded on-chain verifier may need a second bisection down to VM instructions or a suitable succinct proof. WebAssembly execution alone is not a consensus mechanism or an on-chain proof.

The OP Stack's [fault-proof specification](https://specs.optimism.io/fault-proof/index.html) describes the separation between program, virtual machine and interactive dispute game, including reduction to an instruction step. It is a design reference, not a component incorporated into this prototype.

Resolve stake and reward consequences only after adjudication under the agreed rules. The current tools emit verification results without moving funds, penalizing identities, or updating global ledger state. Signatures, anti-replay task admission, Sybil resistance, rate limits for public peers, durable peer storage, and adversarial resource accounting are separate implementation stages.

Finally, the 80/10/10 split is an accounting policy. Execution correctness does not establish scientific utility. Publication/pinning requires actual storage funding and retention; a treasury allocation requires actual assets; a supplier payment requires procurement and delivery verification. PoDD can support this pipeline without asserting those external operations already occurred.

## Tests

```sh
node test-engine.cjs
node test-podd.cjs
node test-podd-http.cjs
```

Golden example receipt ID: `dab824621b19df0909fbd419e9690db7198ed5097a8c4810e58ec375a02ccae2`. A changed arithmetic rule, normalization convention, encoding, or commitment format must use a new protocol/profile version rather than silently changing this vector.
