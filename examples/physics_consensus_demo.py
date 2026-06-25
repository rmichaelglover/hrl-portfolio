"""Relax a web of physics claims to vtrue / ish / vfalse.

Run: ``python examples/physics_consensus_demo.py``

Eight physics claims (and one deliberately contested ninth) are linked by an
agreement/contradiction web. Only two claims are *anchored* as trusted
observations. Relaxation propagates truth from those anchors across the whole
web — recovering the modern picture, rejecting the classical errors, and
parking the genuinely regime-limited claim on ``ish``.

Then a tiny example feeds raw sentences through the swappable text front-end.
"""
import numpy as np

from hrl.consensus import (
    anchor_prior, lexical_agreement, relax_truth, truth_report,
)

CLAIMS = [
    "Light travels at a finite speed.",                              # 0 true
    "The speed of light in vacuum is the same for every observer.",  # 1 true  (anchor)
    "Light propagates through a stationary luminiferous ether.",     # 2 false
    "There is no ether; light needs no medium to travel.",          # 3 true
    "Gravity acts instantaneously across any distance.",             # 4 false
    "Gravity is the curvature of spacetime and propagates at c.",    # 5 true
    "All objects fall at the same rate in a vacuum.",                # 6 true  (anchor)
    "Heavier objects fall faster than lighter ones.",                # 7 false
    "Newtonian gravity predicts planetary orbits accurately.",       # 8 ish
]

# Symmetric agreement web: +entail, -contradict, magnitude = strength.
LINKS = [
    (0, 1, 0.8), (1, 3, 0.7), (2, 3, -0.9), (4, 5, -0.9), (3, 5, 0.6),
    (6, 7, -0.9), (5, 6, 0.5), (2, 4, 0.5), (4, 7, 0.4),
    (8, 5, 0.3), (8, 4, 0.3),   # pulled equally toward a true and a false claim
]
ANCHORS = {1: 2, 6: 2}   # claim 1 and 6 are trusted observations -> vtrue (label 2)


def _web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


def headline():
    n = len(CLAIMS)
    agreement = _web(n, LINKS)
    prior = anchor_prior(n, ANCHORS, strength=0.9)
    report = truth_report(relax_truth(agreement, prior, prior_strength=0.4))

    print("=" * 70)
    print("Syncretistic truth consensus — relaxing a web of physics claims")
    print("=" * 70)
    print("anchored as trusted observations (vtrue): claims 1 and 6\n")
    counts = {"vtrue": 0, "ish": 0, "vfalse": 0}
    for claim, r in zip(CLAIMS, report):
        counts[r["truth"]] += 1
        anchor = "  <- anchor" if CLAIMS.index(claim) in ANCHORS else ""
        print(f"  [{r['truth']:>6} {r['score']:+.2f}]  {claim}{anchor}")
    print(f"\n  consensus: {counts['vtrue']} vtrue, {counts['ish']} ish, "
          f"{counts['vfalse']} vfalse")
    print("  two trusted observations propagated truth across the entire web,")
    print("  and the regime-limited claim settled — correctly — on ish.")


def text_frontend():
    print("\n" + "-" * 70)
    print("text -> agreement -> consensus  (swappable NLP front-end)")
    print("-" * 70)
    texts = [
        "The ether carries light through space.",       # 0
        "Space does not need an ether to carry light.",  # 1
        "Light travels through space without any ether.",  # 2  (anchor: true)
    ]
    agreement = lexical_agreement(texts)
    prior = anchor_prior(len(texts), {2: 2}, strength=0.9)  # trust the modern statement
    report = truth_report(relax_truth(agreement, prior, prior_strength=0.4))
    for text, r in zip(texts, report):
        print(f"  [{r['truth']:>6} {r['score']:+.2f}]  {text}")
    print("  (agreement inferred from raw text; swap in a real NLI model to "
          "scale to whole papers)")


if __name__ == "__main__":
    headline()
    text_frontend()
