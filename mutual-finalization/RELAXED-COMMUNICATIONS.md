# Relaxed Communications
## A theory of countably infinite communications modeled with relaxation labeling

**Michael Emanuel Glover — research proposal and conditional mathematical results**
Working note, October 16, 2026. Mathematical formalization and computational assistance: Cypher.

I want communication to have room to change its mind. A message arrives, but its meaning does not arrive alone. It comes into a world of other messages, expectations, objects, relationships, and possible interpretations. Those relationships supply support. As the world changes, the interpretation may change with it.

Call this **Relaxed Communications**: communication modeled as a network of provisional interpretations that repeatedly adjust under relational support. The network may be countably infinite as a mathematical object, while every actual computation remains finite. We should ask precisely what that finite computation establishes.

This note proposes a model and proves sufficient conditions for convergence and approximation. It does not claim that every communication process satisfies those conditions, that convergence establishes truth, or that the model is a new result in the existing literature. Novelty requires a separate literature comparison. (Cypher)

### 1. What is being labeled?

Let messages or communicative events be indexed by the natural numbers, V = {0, 1, 2, …}. A node could represent an utterance, a symbol occurrence, a robot observation, or a candidate relationship. Fix a finite vocabulary A of possible interpretations. Each node i has a distribution P_i over A and a strictly positive prior distribution π_i.

The labels need not be exclusive between nodes: several messages can express the same meaning. This differs from one-to-one object correspondence, where a label denotes a particular identity that can be assigned only once. The mutual-best finalization implementation in this directory addresses that latter case; applying its label-reservation rule to ordinary shared meanings would impose the wrong constraint.

For each directed relationship i ← j, assign a nonnegative weight w_ij with Σ_j w_ij ≤ 1. Let C_ij(a,b) lie in [−1,1]. It measures how much interpreting j as b supports interpreting i as a. Signed compatibility permits conflict as well as agreement.

Define support by

    S_i(P,a) = Σ_j w_ij Σ_b C_ij(a,b) P_j(b).

This series converges absolutely: every inner expectation has magnitude at most one, and the weights are summable. Countability alone would not suffice; the summability condition does the work.

### 2. A precise relaxation operator

For a finite inverse-temperature parameter β ≥ 0, define

    T_i(P,a) = π_i(a) exp(β S_i(P,a))
               / Σ_c π_i(c) exp(β S_i(P,c)).

Update every distribution by P^(t+1) = T(P^t). Priors preserve independent evidence; relational support can revise the balance between interpretations. This is a chosen, analytically tractable operator. It is **not** the multiplicative, row-normalized operator used by the existing dense HRL engine, so the following proof must not be transferred to that engine without further analysis. (Cypher)

An interpretation distribution is a state of the model, not automatically a calibrated probability of truth. Compatibility must come from somewhere: measurements, learned relationships, rules, or explicit assumptions.

### 3. A convergence result, with its assumptions visible

Use the distance

    d(P,Q) = sup_i Σ_a |P_i(a) − Q_i(a)|.

The space of these distribution families is complete under this metric: a uniformly Cauchy sequence has coordinatewise limits in the closed finite-dimensional probability simplex, and convergence to those limits is uniform in i.

Support obeys

    sup_(i,a) |S_i(P,a) − S_i(Q,a)| ≤ d(P,Q).

For softmax, a perturbation h of its logits has derivative

    dp_a = p_a (h_a − Σ_b p_b h_b).

Consequently Σ_a |dp_a| ≤ 2 ||h||∞. Integrating along the line between two logit vectors gives a Lipschitz bound of two from logit sup norm to distribution L1 norm. Thus

    d(T(P),T(Q)) ≤ 2β d(P,Q).

**Proposition.** If 0 ≤ β < 1/2, T has a unique fixed point P*, and synchronous iteration converges to it from any starting family of distributions.

**Proof.** With q = 2β < 1, T is a contraction on the complete space just described. The contraction mapping theorem gives existence, uniqueness, and convergence. Since d(P^0,P*) ≤ 2,

    d(P^k,P*) ≤ 2 q^k.

The bound is sufficient and conservative; no sharp threshold is claimed. At larger β this proof stops applying. That does not itself prove divergence. A unique mathematical equilibrium also does not establish correct interpretation of the world. (Cypher)

### 4. Finite work on an infinite network

There are two different routes to a finite calculation.

**Finite neighborhoods.** If every node has finitely many incoming neighbors, then k synchronous iterations at a finite set of query nodes depend on a finite incoming k-hop neighborhood and its initial states. With computable inputs, these iterations can be evaluated to chosen numerical precision. Under the contraction assumptions, their query error is at most 2q^k, plus numerical evaluation error. Neighborhood size can grow rapidly with k; finite does not mean inexpensive.

**Controlled tails.** Suppose a truncated operator drops edges whose total weight is at most r at every node, leaves the remaining weights unchanged, and treats dropped support as zero. The support error is at most r. Therefore

    d(T(P), T_truncated(P)) ≤ 2βr.

Both operators remain contractions with factor at most q. Their fixed points satisfy

    d(P*, P*_truncated) ≤ 2βr / (1 − 2β).

To see this, insert T(P*_truncated) between the two fixed-point expressions, apply the triangle inequality, and rearrange E ≤ qE + 2βr. Renormalizing the retained edges changes the operator and requires a revised error bound.

A prefix of node indices need not supply a uniformly small tail. On an infinite chain, every node can depend entirely on its successor; for every finite prefix, some node has all its support outside that prefix. Local finiteness does not imply uniform prefix approximation. Use a demonstrated uniform tail bound or a query-local dependency argument.

For example, weights w_ij = 2^(−j−1) for every i have omitted mass 2^(−N) after retaining j = 0 through N−1. At β = 1/4, the fixed-point truncation bound is 2^(−N). This is an analytic illustration, not an experimental performance result.

### 5. The best object may not exist

The original performance idea asks two questions: which label is best for this object, and which object is best for this label? On a finite candidate set, maxima exist. On a countably infinite candidate set, they need not.

For one label, let object i have score 1 − 2^(−i−1). Each object is beaten by another. The supremum is one, but no object attains it. No finite search can legitimately announce a global winner from these scores.

To certify a winner across unseen objects, we need additional structure: for example, a valid upper bound U_a(N) on the scores of every unexamined object for label a. An observed candidate must beat that bound as well as every observed competitor, with approximation error included.

If each score differs from its target score by at most ε, an observed winner with gap greater than 2ε retains its lead over the compared candidates. This certifies an argmax relative to that error bound and target—not the semantic truth of the assignment, and not immunity to a later change in the model.

Three consecutive wins are useful evidence of persistence. They are not a theorem about unobserved competitors or future information. (Cypher)

### 6. Communication is usually an open process

An infinite graph specified in advance and a stream revealing new messages are different mathematical situations. New messages may change priors, compatibility, weights, or even the label vocabulary. They may also change the equilibrium.

Suppose time-varying operators T_t share a contraction factor q < 1 and have fixed points P*_t. If the algorithm takes one update P_(t+1) = T_t(P_t), then

    d(P_(t+1),P*_(t+1))
        ≤ q d(P_t,P*_t) + d(P*_t,P*_(t+1)).

If fixed-point motion is bounded by δ, the eventual tracking-error bound is δ/(1−q). If operator changes satisfy sup_P d(T_(t+1)(P),T_t(P)) ≤ η, then fixed-point motion is at most η/(1−q), yielding the corresponding tracking bound η/(1−q)^2. These statements require the stated uniform bounds. An unrestricted stream can keep changing its meaning indefinitely.

### 7. Settling an assignment without silencing its influence

Here the practical HRL feature returns. A strong, persistent mutual match can stop consuming the same update work on every sweep, while its settled distribution continues supplying support to other objects. Cached influence preserves that role. Periodic audits allow a match to reopen.

The accompanying implementation requires three consecutive eligible mutual-support wins by default, with strength, margin, and change gates. It freezes a soft distribution rather than replacing it with certainty. It separates a finalized assignment from a numerical fixed point and reports the full unfrozen update residual.

This is an engineering heuristic with measurable costs and failure modes. A delayed-evidence test demonstrates that permanent finalization can lock the wrong answer; auditing recovers on that fixture. Auditing is not a universal recovery guarantee. Reduced support arithmetic is also not automatically reduced wall-clock time: cache construction and bookkeeping cost time and memory.

For open communication, I would treat finalization as a revocable commitment with provenance: what was assigned, which evidence supported it, which competitors were considered, what error bound was available, and what new evidence should reopen it. The current finite implementation snapshots its inputs; changing evidence requires a new run. A persistent online system remains future work.

### 8. Countably many meanings

The main model uses a finite vocabulary and countably many messages. A countably infinite vocabulary can also be considered: use a strictly positive summable prior over labels. With bounded support and finite β, its exponential normalizer is finite and nonzero. Implementing it requires computable label-tail bounds as well as control of message tails. Countability does not guarantee computability, and a nameable infinite system is not an executable infinite computation.

### 9. What we have established—and what remains

We have a precise proposed communication model, an absolute-convergence condition for relational support, a sufficient contraction condition, finite-depth and controlled-tail approximation arguments, and a concrete obstruction to global mutual-best selection over infinitely many candidates.

Separately, we have an executable finite correspondence scheduler, tests, and synthetic measurements in this directory. Those experiments evaluate the scheduler; they do not validate the infinite communication theory or demonstrate natural-language understanding.

Next research steps are to compare the theory with established probabilistic and constraint-based message-passing literature; choose communication datasets with independent reference labels; measure accuracy, calibration, revision latency, computation, and reopening rates; and develop explicit certificates for unseen competitors. Any stronger claim should come with its assumptions, evidence, and a reproducible test.

The ambition is substantial: a communication system that can keep listening, keep reconciling relationships, and spend less effort repeating what it has already settled. Our mathematical responsibility is to say exactly what has settled, under which assumptions, and what could still change it.
