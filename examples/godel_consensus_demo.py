"""The engine tastes incompleteness — Gödel, chess solvability, Kierkegaard.

Run: ``python examples/godel_consensus_demo.py``

Claims about formal systems, self-reference, the solvability of chess, and the
limits of reason are relaxed to vtrue / ish / vfalse. The point: a relaxation
field that rewards *consistency* settles the decidable claims with confidence —
incompleteness comes out true, "chess is unsolvable because Gödel" comes out
false — but it has nowhere to push the **self-referential** claims (the Liar,
the Gödel sentence, "the self relates to itself"). They hover at ``ish`` with
maximal entropy. That residue of uncertainty *is* undecidability, felt.

We also read each claim's **decidability** = 1 − H(truth distribution)/log 3:
the decidable claims approach 1; the self-referential ones stay near 0.
"""
import numpy as np

from hrl.consensus import relax_truth, TRUTH_VALUES, VFALSE, ISH, VTRUE

# full claims (what the engine reasons over) + short labels (for display)
CLAIMS = [
    ("Formal arithmetic F is consistent.", "F is consistent"),                         # 0 anchor T
    ("F is complete: every arithmetic truth is provable in F.", "F is complete"),       # 1 -> false (Gödel 1)
    ("F can prove its own consistency.", "F proves its own consistency"),               # 2 -> false (Gödel 2)
    ("There are true arithmetic statements F can never prove.", "true-but-unprovable exist"),  # 3 -> true
    ("The Gödel sentence G ('G is unprovable in F') is provable in F.", "G is provable"),  # 4 -> false
    ("This very statement is false.", "the Liar"),                                       # 5 -> ish
    ("This very statement cannot be proven true.", "Gödel self-reference"),              # 6 -> ish
    ("Chess is decidable in principle: a finite game with a definite value.", "chess is decidable"),  # 7 anchor T
    ("Chess has been strongly solved from the opening position.", "chess is solved"),    # 8 -> false
    ("Gödel's incompleteness means chess can never be solved.", "Gödel ⇒ chess unsolvable"),  # 9 -> false
    ("Because chess is finite, Gödel's theorems do not apply to it.", "chess finite ⇒ Gödel N/A"),  # 10 -> true
    ("Truth is subjectivity; the deepest truths are not objectively provable.", "truth is subjectivity"),  # 11 Kierkegaard -> ish
    ("Where reason reaches its limit, a leap of faith is required.", "leap of faith"),    # 12 Kierkegaard -> true-ish
    ("The self is a relation that relates itself to itself.", "the self-relating self"),  # 13 Kierkegaard self-ref -> ish
]
SHORT = [s for _, s in CLAIMS]
SELF_REF = {5, 6, 13}
KIERK = {11, 12, 13}

# logical structure: + entail/agree, - contradict (magnitude = strength)
LINKS = [
    (0, 1, -0.85),   # consistent ⟂ complete            (Gödel's 1st theorem)
    (0, 2, -0.85),   # consistent ⟂ proves-own-consistency (Gödel's 2nd theorem)
    (0, 3, +0.70),   # consistent ⇒ unprovable truths exist
    (1, 3, -0.70),   # complete ⟂ "unprovable truths exist"
    (0, 4, -0.70),   # consistent ⟂ "G is provable"
    (7, 10, +0.65),  # chess decidable ↔ Gödel doesn't apply to finite chess
    (7, 9, -0.65),   # chess decidable ⟂ "Gödel ⇒ chess unsolvable"
    (9, 10, -0.75),  # the misconception ⟂ the correct finitude point
    (3, 12, +0.45),  # "reason has limits" (incompleteness) ↔ "leap of faith at reason's limit"
    (11, 12, +0.40), # subjectivity ↔ leap of faith (Kierkegaard coherence)
    (6, 3, +0.25),   # the Gödel self-reference faintly echoes incompleteness...
    (5, 6, +0.20),   # ...and the Liar is its cousin (weak — they stay undecidable)
]
ANCHORS = {0: VTRUE, 7: VTRUE}     # we grant: F is consistent, chess is finite
LEAN = {VTRUE: [0.18, 0.27, 0.55], VFALSE: [0.55, 0.27, 0.18], ISH: [0.25, 0.50, 0.25]}
BOOK = {8: VFALSE}                  # chess "is solved" is just contingently false today
PRIOR_STRENGTH = 0.4


def build_prior(n):
    p = np.full((n, 3), 1.0 / 3.0)
    for i in range(n):
        if i in ANCHORS:
            row = [0.05, 0.10, 0.85] if ANCHORS[i] == VTRUE else [0.85, 0.10, 0.05]
            p[i] = row
        elif i in SELF_REF or i == 11:
            p[i] = LEAN[ISH]                      # self-reference / subjectivity start neutral
        elif i in BOOK:
            p[i] = LEAN[BOOK[i]]
    return p


def web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


def verdict(score, band=0.25):
    return "vtrue" if score > band else "vfalse" if score < -band else "ish"


def decidability(score):
    return abs(score)                              # distance from ish: 1 = decided, 0 = undecidable


def main():
    n = len(CLAIMS)
    res = relax_truth(web(n, LINKS), build_prior(n), prior_strength=PRIOR_STRENGTH,
                      max_iterations=80, record_history=True)
    scores = res.strengths[:, :3] @ TRUTH_VALUES / res.strengths[:, :3].sum(axis=1)

    print("=" * 76)
    print("The engine tastes incompleteness — Gödel · chess · Kierkegaard")
    print("=" * 76)
    print("granted (anchored true): F is consistent, chess is finite\n")
    print(f"  {'claim':<32} {'verdict':>7} {'score':>6}  decidability")
    for i in range(n):
        d = decidability(scores[i])
        bar = "█" * int(round(d * 12)) + "·" * (12 - int(round(d * 12)))
        flag = "  ← undecidable" if (verdict(scores[i]) == "ish" and i in SELF_REF) else ""
        print(f"  {SHORT[i]:<32} {verdict(scores[i]):>7} {scores[i]:+5.2f}  {bar} {d:.2f}{flag}")

    undec = [SHORT[i] for i in SELF_REF if verdict(scores[i]) == "ish"]
    print(f"\n  decidable claims settle with confidence — incompleteness comes out TRUE,")
    print(f"  'Gödel ⇒ chess unsolvable' comes out FALSE. But the self-referential claims")
    print(f"  ({', '.join(undec)}) cannot be pushed off ish.")
    print("  That residue of uncertainty is undecidability — the engine tasting its own limit.")


if __name__ == "__main__":
    main()
