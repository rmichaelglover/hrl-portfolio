"""Test chess rules of thumb with the consensus engine — evidence from real games.

Run: ``python examples/chess_maxims_demo.py``

The bridge between the whimsy-chess project (narrated game studies, the Vim
manual, the Maestro PWA, the Roblox world) and the HRL portfolio. Classic chess
maxims become *claims*; the labels are the Trool truth values
``{vfalse, ish, vtrue}``; maxims that reinforce or clash form the agreement web;
and the **evidence prior comes from actual games** — a corpus of daring wins
that *break the book and win anyway*. Relaxation then settles each maxim onto a
truth value: the sound rules stay ``vtrue``, while dogmas the games refute fall
to ``ish`` — "true in general, but not when you play with nerve."

This operationalizes the whole whimsy-chess thesis: creativity and daring over
memorizing the engine's book. The engine literally relaxes the book's rules.
"""
import numpy as np

from hrl.consensus import relax_truth, truth_report, ISH, VFALSE, VTRUE

MAXIMS = [
    "Control the center with your pawns and pieces.",          # 0  classical dogma
    "Develop all your pieces before you attack.",              # 1  classical
    "Castle early to keep your king safe.",                    # 2  classical
    "Put your rooks on open files.",                           # 3  sound, style-neutral
    "A knight on the rim is dim.",                             # 4  classical
    "Do not bring your queen out early.",                      # 5  classical
    "Material advantage decides the game.",                    # 6  classical
    "Storm the enemy king with a flank pawn.",                 # 7  the Kadas heresy
    "Daring and initiative outweigh following the book.",      # 8  the thesis
]

# How the maxims relate. The only genuine conflicts run along the
# center/material vs. daring axis — sound rules (develop, castle, rooks,
# rim, queen) stand on their own and aren't dragged down by it.
# + reinforce, - clash (magnitude = strength).
LINKS = [
    (0, 7, -0.65), (0, 8, -0.45),   # "control the center" clashes with the wing storm / daring
    (6, 8, -0.55), (6, 7, -0.30),   # "material decides" clashes with daring sacrifices
    (7, 8, +0.80),                  # the wing attack *is* the daring style
]

# The corpus: daring wins that break the book (the whimsy-chess games).
# These are the OBSERVATIONS that anchor the field.
EVIDENCE = {
    7: ("PROVEN by", "Queen Dab, Kadas Stampede, Roundup, Houdini — wing storms that won"),
    8: ("PROVEN by", "Queen Dab (beat +482 Elo), Houdini (won from a lost position)"),
    6: ("REFUTED by", "Houdini won down ~9 points; Queen Dab & Stampede sacrificed material"),
    0: ("REFUTED by", "every Kadas game ignored the center and still won"),
}
ANCHORS = {7, 8}  # what the games positively demonstrate -> strong vtrue anchor
BOOK = {0: VTRUE, 1: VTRUE, 2: VTRUE, 3: ISH, 4: VTRUE, 5: VTRUE, 6: VTRUE, 7: VFALSE, 8: ISH}

LEAN = {VTRUE: [0.15, 0.25, 0.60], VFALSE: [0.60, 0.25, 0.15], ISH: [0.30, 0.40, 0.30]}
PRIOR_STRENGTH = 0.45


def verdict(score, band=0.25):
    """Band the expected truth score into a Trool label. A maxim that is true
    in some games and false in others has an expected truth near zero -> ish."""
    return "vtrue" if score > band else "vfalse" if score < -band else "ish"


def build_prior(n):
    prior = np.zeros((n, 3))
    for i in range(n):
        prior[i] = [0.05, 0.10, 0.85] if i in ANCHORS else LEAN[BOOK[i]]
    return prior


def web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


def main():
    n = len(MAXIMS)
    report = truth_report(relax_truth(web(n, LINKS), build_prior(n), prior_strength=PRIOR_STRENGTH))

    print("=" * 74)
    print("Testing chess rules of thumb — evidence from the whimsy-chess games")
    print("=" * 74)
    print("anchored by what the games PROVE: wing attacks win, daring beats the book\n")

    for i, (maxim, r) in enumerate(zip(MAXIMS, report)):
        note = f"   ({EVIDENCE[i][0]} {EVIDENCE[i][1]})" if i in EVIDENCE else ""
        print(f"  [{verdict(r['score']):>6} {r['score']:+.2f}]  {maxim}{note}")

    downgraded = [MAXIMS[i] for i, r in enumerate(report)
                  if BOOK.get(i) == VTRUE and verdict(r["score"]) == "ish"]
    print("\nThe sound rules hold at vtrue. But the dogmas your daring games refute —")
    for m in downgraded:
        print(f"   • {m}")
    print("relax to ISH: rules of thumb with real exceptions. Creativity over the book,")
    print("quantified — the same relaxation engine that scores chess pieces by role and")
    print("relaxes physics claims to truth, now grading chess theory itself.")


if __name__ == "__main__":
    main()
