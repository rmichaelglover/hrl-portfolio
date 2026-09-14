# A small tutor that earns its next feature

## Product boundary

The first user is an 850–1250 Lichess player who takes tempting material
without checking a reply, or refuses sound captures from fear of hidden traps.
The first session should take about 5–10 minutes. The outcome is a repeatable
pause-and-check routine, not a promised rating gain.

Build one useful chess lesson loop. Keep inference domain-neutral; keep the
supported product chess-only. Do not build a general chatbot, ontology editor,
marketplace, payment flow or account system yet.

## 0.1 — implemented local vertical slice

Six legally checked exercises, decision and prediction, hints, replay,
explanations, first-attempt progress and deterministic GRRLE-style scheduling.
No machine learning or engine dependency in the shipped application.

## 0.2 — an independently reviewable pilot

- Have a chess educator review the exact wording and positions.
- Add at least 12 genuinely different authored positions: sound captures,
  recaptures, and abandoned defenses, including protected-but-profitable trades.
- Separate teaching positions from unseen assessment positions; do not count
  mirrored variants as independent transfer evidence.
- Ask for the threatened square or concrete reply, not just a yes/no guess.
- Provide a short session end card with observed errors and one practice cue.
- Add explicit content versioning and progress migration before changing IDs.
- Compare adaptive scheduling with a fixed sequence; GRRLE must earn its role.

A practical pilot: 5–10 consenting players in the target band, with a short
unassisted pre-check, the lesson, and new unassisted positions afterward.
Collect results with consent; no silent telemetry. Record capture-decision
accuracy, reply prediction, hint use, completion, and incorrectly declined
sound captures separately. A small pilot informs usability, not efficacy proof.

## 0.3–0.5 — verified explanations and retention

Add a local legal-move adapter and narrowly bounded forcing-line verification.
Generate feedback only when a verified line supports it; otherwise say the
position is outside the tutor's scope. Add multi-step exchanges and forks only
after existing lessons survive independent review. Introduce spaced revisits
and delayed unseen checks before describing any skill as retained.

Consider richer GRRLE factors linking move, threat, defender, and consequence.
Compare against the simple baseline. Keep intermediate labels inspectable.
No model training is required for these milestones.

## 1.0 — a narrow product worth distributing

A reviewed capture-safety curriculum, reliable mobile/accessibility behavior,
reproducible builds, documented data handling, and evidence from learner tests.
Define support and maintenance responsibilities. Decide licensing explicitly:
the current repository is source-available, not an OSI-approved FOSS release.

Potential first offering: a short coached course for individual learners or a
club lesson package. Test willingness to use and pay with real users before
adding subscriptions. A free prototype can demonstrate value while optional
human coaching or a maintained curriculum is evaluated as a business model.
No price, sales forecast, or effectiveness claim is established yet.

Release gate: can a new learner complete the loop without developer help,
explain one danger in their own words, and make better decisions on new
positions without becoming afraid of every offered piece?
