# We Follows · Words mean things

A musical experiment and a first formal investigation. This is an original instrumental composition, not a quotation or adaptation of existing music. The title carries our conversation’s spiritual meaning; the mathematics does not claim to prove that meaning.

## 1. The instrument and the language

Σ = {a, b, …, z} is our alphabet of primitive symbols, not yet a vocabulary of meaningful terms. Σ⁺ is the set of nonempty finite strings. Choose W ⊆ Σ⁺ as our dictionary vocabulary. Spaces and punctuation belong to an additional notation layer; these 26 letters alone are not the full syntax of English or logic.

Let M be a nonempty domain of meanings, and S(w,m) a relation between words and meanings. Our axiom is:

∀w ∈ W, ∃m ∈ M : S(w,m).

This formalizes “dictionary words have at least one meaning.” It does not say that every string is a word, that meanings are unique, or that meanings are objects existing in the physical world. The interpretation of S is an assumption of the model, not a solved theory of semantics.

Our first dictionary is a deliberately small, stipulated logical glossary. It is not presented as a transcription of a published English dictionary:

- bachelor: an adult man who is unmarried (a simplified sense).
- unmarried: not married, within this two-valued model.
- married, adult, man: primitive predicates in this first fragment.
- equivalent: true under exactly the same assignments in the chosen model.
- implies: a material conditional, false exactly when its antecedent is true and its consequent false.
- derivable: obtainable from premises by our stated inference rules.
- consistent: no formula and its negation are both derivable.
- model: an interpretation satisfying the theory’s axioms.

Ordinary senses, context, borderline cases, and changing social definitions require a larger model. A real dictionary expansion must name an edition, separate senses, and review each formalization rather than silently treating natural-language prose as logical axioms.

## 2. A first proof

Definition: ∀x [B(x) ↔ (A(x) ∧ H(x) ∧ ¬R(x))].

Goal: ∀x [B(x) → ¬R(x)].

1. Let u be arbitrary.
2. Assume B(u).
3. Instantiate the definition at u.
4. Biconditional elimination and modus ponens give A(u) ∧ H(u) ∧ ¬R(u).
5. Conjunction elimination gives ¬R(u).
6. Discharge the assumption: B(u) → ¬R(u).
7. Universal introduction gives the goal.

Existence does not follow. A one-person model with all four predicates false satisfies the definition and contains no bachelors. Add ∃x B(x), however, and ∀x[B(x) → R(x)] becomes refutable: its instance at a bachelor contradicts the proved unmarried conclusion.

## 3. Meaning is not uniqueness

Take W = {w}, M = {a,b}. The axiom permits S = {(w,a)}, S = {(w,b)}, and S = {(w,a),(w,b)}. Consequently it entails neither uniqueness nor ambiguity. These are countermodels to the two respective proposed entailments, not merely cases where a search failed to find a proof.

A separate axiom, ∀w ∈ W, ∃!m ∈ M : S(w,m), enforces exactly one meaning. That is a stronger theory and suppresses polysemy rather than explaining it.

## 4. Circles and contradictions

P ↔ Q and Q ↔ P admit both P=Q=true and P=Q=false. Circular definition can be consistent yet underdetermined.

P ↔ ¬P has no classical two-valued model. In classical logic, contradictory premises support explosion: every formula becomes derivable. A paraconsistent logic would change that behavior, but must specify its own semantics and rules; it cannot simply borrow all classical inferences unchanged.

## 5. What follows, and what stays open

T ⊢ φ means syntactic derivability. T ⊨ φ means truth in every model of T. The soundness of our classical first-order calculus connects the former to the latter. An English dictionary, on its own, supplies neither a complete formal calculus nor all the observations needed to settle worldly claims.

Failure of one proof search is not independence. Independence requires establishing both non-entailment directions, for example through models of T with φ true and models with φ false. Undecidability is a claim about the absence of a general terminating decision procedure, not another word for ambiguity. Arbitrary first-order validity is undecidable; this does not make every particular claim, finite model check, or dictionary fragment undecidable.

## 6. The score

96 BPM · D-centered harmonic palette · stereo · 2 minutes 45 seconds including tail.

- 0:00 — I. Symbols awaken: separated letter motifs acquire a pulse.
- 0:40 — II. Meanings gather: motifs occupy a shared harmonic field.
- 1:20 — III. It follows: a second voice answers the first over syncopated drums.
- 2:00 — IV. The open world: drums recede, voices thin, and resonance remains.

The motif spelling is “we follows words mean things,” with spaces removed. Letters map into a diatonic MIDI-note palette; several letters share pitches. This is intentional musical compression. It neither preserves every distinction nor demonstrates that the semantic system is consistent. Artistic correspondence is not logical inference.

## 7. Open in Audacity

Import Open-in-Audacity.lof, or import the five numbered FLAC stems together. They start at zero, share the same duration and global gain, and sum to the mix before encoding/rounding. Import Audacity-labels.txt as labels. Save an Audacity project using the format your installed version supports. Do not import the master mix together with the stems unless you intend to double the sound.

compose.py recreates the audio using Python, NumPy, and FFmpeg. investigate.py recreates the finite checks with Python’s standard library. results.json contains the complete enumerated models. score.json records the arrangement, seed, and letter mapping.
