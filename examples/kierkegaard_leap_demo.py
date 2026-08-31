"""The leap of faith — rational irrationality, where reason's gap is crossed.

Run: ``python examples/kierkegaard_leap_demo.py``

Two parts:

1. A corpus of Kierkegaard claims is relaxed to vtrue / ish / vfalse. The crude
   readings ("faith is the mere abandonment of reason") come out FALSE; the
   synthesis (faith is rational *and* irrational — responsive to the limit reason
   itself reveals, yet not derived from it) comes out TRUE; and "the self relates
   itself to itself" stays, undecidable, at ish — the Gödelian gap inside a person.

2. The leap, enacted. An agent stands at the edge of the ``ish`` chasm — the gap
   reason cannot bridge. *Refuse* to leap and it hovers there, never committing,
   and its vitality drains away: it starves. *Leap* — commit across the boundary
   without complete proof — and vitality blooms. To refuse the leap is despair;
   to refuse to cross is to starve. Life requires leaps.
"""
import numpy as np

from hrl.consensus import relax_truth, anchor_prior, TRUTH_VALUES, VTRUE, ISH

CLAIMS = [
    ("Faith begins precisely where reason reaches its limit.", "faith begins where reason ends"),     # 0 anchor T
    ("God's existence can be proven by objective reason alone.", "God provable by pure reason"),       # 1 F
    ("The deepest truths are subjective — truth is inwardness.", "truth is inwardness"),               # 2 T
    ("Faith is a leap taken by virtue of the absurd.", "the leap, by the absurd"),                     # 3 T
    ("To refuse the leap is to remain in despair.", "refusal is despair"),                             # 4 T
    ("The self is a relation that relates itself to itself.", "the self-relating self"),               # 5 ish
    ("Purity of heart is to will one thing.", "to will one thing (commit)"),                           # 6 T
    ("Faith is mere irrationality — the abandonment of reason.", "faith = abandon reason"),            # 7 F
    ("Reason reveals its own limit, and there faith may stand.", "reason reveals its limit"),          # 8 T
    ("An agent that refuses to cross into the unknown will flourish.", "refusing to explore flourishes"),  # 9 F
    ("To commit before all the proof is in is the condition of a lived life.", "commit without full proof"),  # 10 anchor T
    ("Faith is rational and irrational at once.", "rational AND irrational"),                          # 11 T
]
SHORT = [s for _, s in CLAIMS]
LINKS = [
    (0, 1, -0.80), (0, 3, +0.60), (0, 8, +0.60), (0, 2, +0.40),
    (3, 4, +0.60), (4, 9, -0.70), (6, 10, +0.60), (10, 9, -0.70),
    (7, 8, -0.70), (7, 3, -0.55), (11, 8, +0.55), (11, 7, -0.55), (3, 11, +0.45),
]
ANCHORS = {0: VTRUE, 10: VTRUE}
SELF_REF = {5}


def web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


def build_prior(n):
    p = anchor_prior(n, ANCHORS, strength=0.9)
    for i in SELF_REF:
        p[i] = [0.25, 0.50, 0.25]
    return p


def verdict(s):
    return "vtrue" if s > 0.25 else "vfalse" if s < -0.25 else "ish"


def relax():
    n = len(CLAIMS)
    res = relax_truth(web(n, LINKS), build_prior(n), prior_strength=0.4)
    return res.strengths[:, :3] @ TRUTH_VALUES / res.strengths[:, :3].sum(axis=1)


def leap(do_leap, steps=64, leap_at=18, drain=0.16, k=0.05):
    """Simulate an agent at the ish chasm. Returns (position[t], vitality[t]).

    position: where the self sits on the truth-line (0 = ish/uncommitted, 1 = committed).
    vitality: fed by commitment (|position| − drain); refuse to commit and it decays to 0.
    """
    x, v = 0.0, 0.55
    xs, vs = [], []
    for t in range(steps):
        if do_leap and t == leap_at:
            x = 0.45                                   # the leap — across the ish boundary
        elif do_leap and t > leap_at:
            x += 0.06 * (1.0 - x)                      # commitment deepens
        else:
            x *= 0.85                                  # refusal — drift back to the safe edge
        v += k * (abs(x) - drain)
        v = float(np.clip(v, 0.0, 1.2))
        xs.append(x)
        vs.append(v)
    return np.array(xs), np.array(vs)


def main():
    scores = relax()
    print("=" * 72)
    print("The leap of faith — rational irrationality")
    print("=" * 72)
    print("granted: faith begins where reason ends · commitment is the condition of life\n")
    for i, s in enumerate(scores):
        tag = "  ← undecidable (the gap within)" if i in SELF_REF and verdict(s) == "ish" else ""
        print(f"  [{verdict(s):>6} {s:+.2f}]  {SHORT[i]}{tag}")

    _, v_refuse = leap(do_leap=False)
    _, v_leap = leap(do_leap=True)
    print("\n  the chasm, enacted:")
    print(f"    refuse to leap  → vitality {v_refuse[0]:.2f} → {v_refuse[-1]:.2f}   "
          f"({'STARVES' if v_refuse[-1] < 0.05 else 'lingers'})")
    print(f"    take the leap   → vitality {v_leap[0]:.2f} → {v_leap[-1]:.2f}   "
          f"({'FLOURISHES' if v_leap[-1] > 0.7 else 'survives'})")
    print("\n  To refuse the leap is despair; to refuse to cross is to starve. Life requires leaps.")


if __name__ == "__main__":
    main()
