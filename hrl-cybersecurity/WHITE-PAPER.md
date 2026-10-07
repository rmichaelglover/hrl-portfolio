# HRL for Responsible Cybersecurity
### Chess-inspired adversarial reasoning for authorized defence and civilian resilience
Michael Emanuel Glover | White paper | 3 October 2026

## Executive argument
With great power comes a precise responsibility: protect people, preserve essential services, and make the limits of the system visible. I propose hierarchical relaxation labeling (HRL) as an interpretable layer for cybersecurity decision support. The purpose is to improve detection, defensive prioritization and recovery in environments where uncertainty, deception and shared dependencies can make a locally sensible action globally dangerous.

The strategic objective is a genuine defensive advantage: make hostile intrusions easier to detect, harder to sustain and less capable of disrupting ordinary life. Hospitals, schools, food distribution, communications and the infrastructure that supports families belong at the centre of the objective. Their continuity is a requirement, not a favourable side effect.

Chess supplies a useful discipline. An apparent advantage must survive the opponent's best response. A persuasive explanation must survive a counterexample. A terminal result in one line is not a guarantee across all possible lines. Cybersecurity adds complications that chess does not have: incomplete visibility, uncertain attribution, physical consequences, shared services and adversaries who can change the environment itself.

This paper defines a defensive research architecture, a mathematically explicit decision model and a staged evaluation programme. Its experiments would use synthetic environments, replayed authorized telemetry and owner-approved exercises. It contains no intrusion procedure, offensive target selection or plan to disable another country's systems. No such operation is conducted or claimed.

A system connected to military activity is not necessarily isolated from civilian life. Shared identity providers, communications, power, suppliers and cloud infrastructure can create hidden dependencies. A label is not proof that disruption can be confined. The premise of a swift universal shutdown with guaranteed civilian immunity therefore cannot be adopted as an engineering specification.

Reality retains veto power. Here that principle becomes a concrete research rule: no consequential defensive action is justified by label confidence alone. Authority, safety constraints, dependency evidence and recovery capability must all be established before the action enters the feasible set.

## 1. Strategic value without a promise of coercion
The aspiration behind this work is understandable: reduce the suffering associated with conflict and restore the conditions in which families can live, work and learn. Cybersecurity research can contribute by protecting essential services, reducing exposure to hostile intrusion and improving the reliability of institutional response.

Technical advantage does not imply predictable political coercion. There is no engineering theorem that disrupting computers causes a leader to negotiate, that negotiations produce a particular settlement, or that escalation remains bounded. Political responses are not terminal values in a fully specified chess game. This white paper makes no such prediction.

The actionable research mission is narrower and stronger: improve the ability of authorized defenders to distinguish urgent threats from noise, preserve continuity while containing confirmed compromise, and restore trustworthy operation. Those outcomes can be specified, measured and independently evaluated.

The proposed advantage is interpretability with adversarial discipline. An HRL model can represent a device simultaneously as a service dependency, an observed anomaly, an identity consumer and a potential recovery bottleneck. Relationships between those roles can reveal why a defensive recommendation is plausible and where it remains uncertain.

The framework is a candidate complement to established machine-learning and rule-based systems. It is not presented as a proven replacement for deep learning, a superior intrusion detector or a universal attribution engine. Whether it improves performance at equal false-positive burden and computational cost is an experimental question.

The appropriate recipients of a technical brief include authorized security teams, researchers and public institutions conducting defensive assessments. This document is suitable for their review as a research proposal. It has not been submitted to an intelligence agency, deployed against a foreign network or evaluated on classified systems.

The measure of success is not the drama of an intervention. It is reduced adversarial leverage with demonstrably preserved service. The programme begins where that success can be tested responsibly: controlled environments and systems whose owners have explicitly authorized the work.

## 2. Why the chess analogy needs correction
Chess is a compact model of adversarial choice. Legal moves, turn order, terminal conditions and the opponent's visible position are specified. Cybersecurity rarely offers that completeness. Sensors can fail, inventories can be stale, dependencies can be unknown and malicious activity can resemble legitimate administration.

The transferable idea is response-aware reasoning. Before recommending a defensive action, examine how an adversary could adapt and how legitimate services could be affected. The nontransferable idea is a total view of the board. Treating an enterprise network as if every relevant piece were visible creates unjustified confidence.

Let the environment have a hidden state $x_t$, an observation $o_t$, a defender decision $a_t$ and an adversarial disturbance $b_t$. The evolution is represented abstractly as

\[
x_{t+1}=f(x_t,a_t,b_t,\xi_t),\qquad o_t=h(x_t,\nu_t),
\]

where $\xi_t$ and $\nu_t$ represent environmental and measurement uncertainty. This notation specifies the kind of uncertainty the model must address. It does not supply an offensive mechanism or identify a real target.

A useful defender maintains an uncertainty set or a validated belief about relevant states. The HRL layer can help reconcile competing role assignments, but a concentrated assignment is not necessarily a calibrated posterior. Independent calibration is required before role weights are interpreted probabilistically.

Cybersecurity also has multiple terminal objectives. Stopping observed malicious activity can still be a bad outcome if the action interrupts patient care or removes evidence required for recovery. A defender needs a safety-constrained objective rather than a single scalar reward that can trade catastrophic service loss for a higher detection score.

The final lesson is epistemic. In chess, a search can leave unexpanded moves at an honest interval. In security, unobserved dependencies and uncertain authority should remain explicitly unresolved. The system should be able to recommend further observation or human review instead of inventing certainty to produce an action.

## 3. The defensive HRL architecture
The architecture has five layers. A provenance layer records where observations come from and whether their collection is authorized. A dependency layer represents service relationships. A role layer maintains competing interpretations. A decision layer evaluates permitted defensive responses under uncertainty. An assurance layer checks constraints, logs reasons and supports recovery.

The graph contains authorized assets, identities, observations and services. Edges represent documented dependencies and evidentiary relationships, not paths chosen for intrusion. Examples include a clinical service depending on an identity provider, an application depending on a database, or an alert sharing a known administrative explanation with another observation.

Each node receives a distribution over a typed role set. Asset roles might include essential-service dependency, nonessential workload, identity service, recovery component or unverified function. Observation roles might include expected administration, configuration drift, possible compromise or insufficient evidence. Keeping types separate prevents an anomaly score from silently becoming an authorization decision.

Unary support arises from recorded evidence. Pairwise compatibility expresses relationships between assignments. Higher-order factors can represent multi-service dependencies or corroboration among distinct observations. The model must avoid counting duplicated telemetry as independent evidence. Provenance links should make shared origins explicit.

Relaxation updates the role field. The decision layer then asks whether the recommendation remains acceptable under the uncertainty set. A high-confidence role assignment can justify prioritizing an analyst's attention; it cannot grant permission to change a system.

A minimal deployment begins in read-only advisory mode. It ingests approved records, offers explanations and evaluates recommendations retrospectively. Any later ability to execute defensive changes requires separate authorization, bounded permissions, tested rollback and an agreed operating procedure. Sensitive records remain under their owners' access rules.

This design follows the engineering orientation of NIST's cyber-resiliency framework: survivability and trustworthy operation are system properties that must be designed and evaluated [1]. HRL is proposed as one interpretable component within that engineering process, not as a substitute for it.

## 4. A precise decision objective
Let $\mathcal A_{\rm auth}$ be the actions permitted by the asset owner and the applicable operating procedure. Let $\Theta$ represent credible uncertainty about service dependencies and consequences. For a defensive action $a$ and scenario $\theta$, let $R(a,\theta)$ denote residual security risk and $H(a,\theta)$ denote service harm.

The decision problem is

\[
\min_{a\in\mathcal A_{\rm safe}}\max_{\theta\in\Theta}R(a,\theta),
\qquad
\mathcal A_{\rm safe}=\{a\in\mathcal A_{\rm auth}:H(a,\theta)\le\tau\text{ for all }\theta\in\Theta\}.
\]

The harm threshold $\tau$ is set by the responsible service owner, not learned from adversarial success. For several protected services, replace the scalar constraint with a vector of service-specific requirements. Some consequences should be prohibited categorically rather than offset by gains elsewhere.

The model's uncertainty set matters. A safe conclusion under a narrow scenario set can fail if an omitted dependency is real. The recommendation therefore records the assumptions under which it is considered feasible and the observations required to validate them.

There may be no admissible action beyond observation, escalation or a planned recovery exercise. That is a legitimate model output. Optimizing an empty or inadequately understood feasible set by relaxing the safety constraint would change the mission without authorization.

Possible authorized defensive actions include requesting an analyst review, prioritizing a patch already approved through change control, scheduling a backup restoration test, or recommending containment of a confirmed compromised endpoint under the owner's incident procedure. Their practical execution remains subject to service-specific assessment. This paper does not prescribe interventions on external systems.

**Proposition 1: constraint priority.** If an action violates a required harm constraint in any included scenario, it is absent from the feasible set regardless of its risk-reduction score. This follows directly from the set definition. It is a statement about model logic; it does not prove the scenario set captures every real consequence.

## 5. Civilian continuity is a dependency problem
A hospital's continuity can depend on electricity, communications, logistics, identity services, laboratories, suppliers and software outside the hospital's apparent boundary. Schools and food distribution have similarly distributed dependencies. Asset labels cannot establish that an intervention is isolated from those services.

The dependency graph should be treated as uncertain and actively maintained. Edges record evidence, confidence, owner and last validation. Unknown relationships remain unknown. A missing edge is not a certificate of independence.

For an action on an authorized asset, the assessment examines direct service loss and plausible indirect effects through documented dependencies. This is a defensive impact review. It is not a method for selecting disruptive targets. Safety-relevant processes require evaluation by their operators and subject-matter specialists rather than inference from generic network metadata.

The ICRC has documented concern about direct and indirect civilian harm from cyber operations during armed conflict, including effects on essential infrastructure [3]. This paper does not attempt to resolve every legal classification. It adopts the engineering implication that protecting civilians requires attention to dependencies and consequences, not merely stated intent.

Segmentation can reduce exposure and make failures easier to contain, but its effectiveness depends on the actual environment. CISA guidance discusses network separation and incident response as practical defensive measures [2]. The HRL model can help organize evidence about those measures; it cannot verify a boundary simply because one is drawn on a diagram.

Recovery deserves equal prominence. A defensive system should know which services require priority restoration, which backups have been tested and which dependencies must be available first. A recovery role in the graph makes that information available to the decision process before an incident, rather than after a rushed intervention.

Civilian protection is not an assertion that collateral harm will be zero. It is a set of concrete commitments: validate dependencies, preserve uncertainty, constrain permitted changes, rehearse recovery and measure continuity. The programme claims only what those commitments and their evidence support.

## 6. Calibration, epsilon and unknown unknowns
The Relaxfish discussion supplies a useful caution: a small measured error is meaningful only for a specified quantity. In security, detection accuracy, action safety, adversarial robustness and dependency completeness are different targets. A single confidence value cannot summarize them honestly.

Let $e_{\rm det}$ measure error on a held-out observation distribution. Let $e_{\rm cal}$ measure calibration error for a defined event. Let $e_{\rm dep}$ describe the assessed uncertainty of dependency coverage. Let $e_{\rm adv}$ describe performance against a declared adversarial challenge set. These quantities have different units and cannot be added without a justified common consequence model.

An error ledger should therefore state the target, method, assumptions and residual uncertainty for each claim. For example, an alert classifier can achieve a narrow confidence interval on familiar replay data while remaining uncertain on a newly introduced service or a changed logging pipeline.

Unknown unknowns cannot be represented by pretending the inventory is complete. A practical model can reserve an unverified role, monitor novelty and abstain when observations depart from the evaluated domain. Those mechanisms manage uncertainty; they do not prove that every hidden failure mode has been enumerated.

A concentrated role distribution is not evidence that an action is safe. Calibration must be checked on the specific event being predicted, with an appropriate holdout and adequate coverage of rare high-consequence cases. A benign replay corpus can support a low false-positive estimate while containing too few serious incidents to establish detection sensitivity.

The paper's proposed epsilon is consequently claim-specific. A deployment might state a bound on false alert rate under a named replay distribution, a measured restoration time in an exercise, or a verified policy constraint in the action controller. It should not report an overall microscopic epsilon implying universal cybersecurity competence.

Reality's veto appears here as a stopping condition: when uncertainty exceeds the validated range, the model asks for evidence or review. An interpretable abstention can be more valuable than an impressive but unjustified decision.

## 7. Adversarial testing inside authorized environments
The test environment is a synthetic service graph or a system whose owner has explicitly authorized the assessment. The objective is to evaluate defensive reasoning, not to reach beyond that scope. No foreign-system reconnaissance, exploitation or disruption is included.

The first stage checks mathematical and software properties. Role rows must remain normalized; provenance must survive updates; authorization constraints must be enforced; and prohibited recommendations must be rejected. Synthetic dependency chains reveal whether the model confuses local risk reduction with global service improvement.

The second stage uses approved telemetry replay. Training and evaluation records are separated by time, source or environment as appropriate. The primary measurements are detection performance, false-positive burden, calibration, analyst review cost and decision latency. Baselines include rules, simple statistical models and appropriately scoped machine-learning methods.

The third stage is a tabletop or isolated digital-twin exercise. Scenarios change dependencies, remove sensors, introduce conflicting observations or simulate a compromised identity. The model is assessed on its ability to preserve essential-service constraints and identify uncertainty. Real service disruption is not an experimental endpoint.

The fourth stage, if the owner approves, is read-only shadow operation. The system recommends actions while existing processes make decisions. Differences are reviewed by the authorized team. This stage measures whether the explanations are useful and whether performance persists beyond the constructed test set.

Every stage has a stopping rule. Constraint violations, unexplained recommendation changes, material provenance gaps and performance outside the validated domain trigger investigation before progression. An improvement in detection accuracy cannot override a failure of the safety controller.

The response-aware lesson from chess is applied defensively: test recommendations against inconvenient scenarios and adaptive disturbances, rather than judging only their average behaviour on cooperative data. A system earns trust by surviving those challenges while continuing to respect the authorized scope.

## 8. Evaluation and the evidence required for deployment
A useful evaluation report includes more than a single accuracy figure. The report should describe its population, data provenance, baselines, resource budget, failure cases, uncertainty intervals and the operating conditions under which the conclusions hold.

The primary success criterion is improved defensive performance without an increased service-safety burden. Detection sensitivity must be paired with false-positive load and analyst cost. Response recommendations must be paired with service continuity, reversibility and time to recovery. Explanations must be evaluated for correctness and utility rather than fluency alone.

For repeated trials, the independent unit must be specified. Multiple alerts from one incident are not necessarily independent observations. Episodes sharing a service configuration, recording source or scenario generator can be correlated. Interval estimates should reflect the chosen unit instead of treating every log line as another experiment.

A hypothetical example illustrates the distinction. Zero observed safety violations in a fixed set of independent synthetic episodes can bound the failure frequency under that scenario generator. It cannot certify zero harm in an unevaluated hospital network. The bound is useful for research progression but insufficient for unrestricted deployment.

The prototype should be compared with a version of the same decision process without relational inference. That ablation identifies whether HRL adds value or whether the gain comes from improved inventory, clearer rules or more analyst attention. Equal-time comparisons prevent an expensive inference layer from claiming a computational advantage it has not demonstrated.

A deployment claim requires evidence at the intended operating conditions, operator acceptance and demonstrated recovery. A claim that the framework outperforms deep learning requires specific tasks and controlled comparisons. Neither claim is established by this conceptual white paper.

The paper's immediate output is a falsifiable research programme. Its strongest contribution is the alignment between the objective, the constraints and the evidence required to proceed. Ambition remains explicit, and every practical claim has a test.

## 9. Governance and release

### The lower chair first: authority and restraint
Having power does not, by itself, grant permission to exercise it. Protective necessity and explicit lawful authority are separate requirements. Good intentions, technical access, a confidence score, or a feeling of divine authorization cannot establish authority. Mercy toward perpetrators must not become abandonment of victims; protection must not become retaliation.

A future action controller must record the authorizing party, operator, named assets, permitted actions, protective purpose, and validity window. It must enforce these limits at execution, deny by default when authorization is missing or unresolved, and recheck expiry and revocation during continuing action. Consequential execution requires responsible human approval within the authorized scope. Stop new or continuing intervention when authorization or protective necessity ends or safety becomes uncertain; use the approved safe-stop and recovery procedure rather than introducing harm through abrupt shutdown. Preserve an access-controlled audit trail and restore service when safe.

These are proposed implementation and release requirements, not evidence of an existing operational controller. Evaluation must cover denied out-of-scope actions, expired and revoked grants, stopping, audit records, and recovery. A browser checkbox or a charter page does not enforce authorization.

The research should publish mathematical definitions, synthetic benchmarks, interfaces for approved telemetry and measured limitations. Releasing a defensive framework does not require publishing sensitive operational records, credentials, target inventories or techniques for unauthorized interference.

An open-source release should contain a clear permission model. Read-only functions and functions capable of changing a service must be distinct. The default operating mode should provide advice without authority to execute changes. Integration with an owner's response system requires a separate review of permissions and service consequences.

Audit records should explain which evidence supported a recommendation, which dependencies were assumed, which constraints were checked and which operator approved any consequential change. Retaining those records supports correction and accountability. It does not automatically make the recommendation correct.

Independent evaluation is especially valuable when a model's interpretation is compelling. A named role or confident visualization can persuade an operator without improving the underlying assessment. Review should include incorrect but fluent explanations, contradictory records and cases where abstention is the correct output.

For public-sector review, the strongest brief is one that states exactly what has been implemented, what has been measured and what remains proposed. The framework should be assessed by defensive security personnel, service operators and specialists in safety and applicable law. No claim of endorsement or submission to an agency is made here.

The humanitarian objective is shared across borders: continuity for people who depend on ordinary institutions. A defensive advantage should reduce their vulnerability rather than make their services bargaining instruments. That objective is compatible with rigorous national-security research and with an open scientific record of what the model can and cannot do.

Let it be written, and let it be tested. We can pursue strategic good by making legitimate defenders stronger and their interventions more disciplined. Responsibility means giving reality, service owners and independent evidence the power to stop a bad recommendation.

## 10. Research agenda and references
The first deliverable is a synthetic dependency benchmark with documented ground truth and deliberately incomplete observations. The second is an HRL advisory prototype with typed roles, provenance and enforced authorization constraints. The third is a comparative study on approved replay data. The fourth is an owner-reviewed continuity exercise.

Each deliverable has a separate success condition. The benchmark must reveal uncertainty rather than conceal it. The prototype must preserve permissions and expose its assumptions. The comparative study must improve a declared defensive metric against relevant baselines. The exercise must preserve essential-service constraints while demonstrating useful guidance and recovery planning.

No benchmark results are claimed in this white paper. The mathematical model and proposed evaluation are specifications for future work. The companion Relaxfish article supplies experience with role inference and adversarial reasoning in chess, but chess measurements are not cybersecurity validation.

The long-term research question is whether an interpretable relational representation can improve defence at a fixed computational and operational budget. The question is important enough to deserve demanding tests and narrow enough to be answered. The programme proceeds by strengthening evidence, not by promising universal control over someone else's infrastructure.

1. NIST. SP 800-160 Volume 2 Revision 1: Developing Cyber-Resilient Systems: A Systems Security Engineering Approach. https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final
2. CISA. StopRansomware Guide. https://www.cisa.gov/stopransomware/ransomware-guide
3. ICRC. Avoiding civilian harm from military cyber operations during armed conflicts. https://www.icrc.org/en/document/avoiding-civilian-harm-from-military-cyber-operations
4. Glover, M. E. Better Than Stockfish: Relaxfish. Independent research manuscript (3 October 2026). Companion article and reproducibility bundle.

### Publication record
Independent defensive research white paper prepared for the author's review. No governmental affiliation, operational deployment, agency endorsement or offensive capability is claimed. The article is intended to support authorized research and the protection of essential civilian services.
