"""Syncretistic physics consensus — relativity, quantum gravity, the dark sector.

Run: ``python examples/quantum_consensus_demo.py``

The original syncretistic dream: every physical model is a simplification, so we
weight each by how *proven* it is and relax the whole web toward consistency.
Confirmed physics (c is constant, E = mc², photons are massless and timeless)
settles to vtrue; the genuinely speculative frameworks (loop quantum gravity,
quantum foam, the dark-matter particle, the cosmological constant) hover, honest,
at ish; the not-yet-done (quantum gravity reconciled, a theory of everything)
comes out vfalse — incompleteness wearing a cosmologist's hat. And the
self-referential reading of a photon (always at c, hence in its own frame never
moving, never aging) lands at ish, where Gödel quietly chimes in.
"""
import numpy as np

from hrl.consensus import relax_truth, anchor_prior, TRUTH_VALUES, VTRUE

CLAIMS = [
    # confirmed relativity / light
    ("The speed of light c is constant for every observer.", "c is constant", "confirmed"),            # 0 anchor
    ("Energy and mass are equivalent: E = mc².", "E = mc²", "confirmed"),                               # 1 anchor
    ("Photons have zero rest mass.", "photons are massless", "confirmed"),                              # 2
    ("A photon at c experiences no passage of proper time.", "photons are timeless", "confirmed"),      # 3
    ("Nothing carrying mass can reach the speed of light.", "mass can't reach c", "confirmed"),         # 4
    ("Gravity is the curvature of spacetime (general relativity).", "gravity = curvature", "confirmed"),# 5
    # strong evidence, nature unknown
    ("Unseen mass (dark matter) holds galaxies together.", "dark matter is real", "evidence"),          # 6
    ("The universe's expansion is accelerating (dark energy).", "expansion accelerates", "evidence"),   # 7
    # speculative frameworks
    ("Loop quantum gravity quantizes spacetime into discrete loops.", "loop quantum gravity", "speculative"),  # 8
    ("Spacetime is a foam, fluctuating at the Planck scale.", "quantum foam", "speculative"),           # 9
    ("Dark matter is an as-yet-undiscovered particle.", "dark-matter particle", "speculative"),         # 10
    ("Dark energy is the cosmological constant (vacuum energy).", "cosmological constant", "speculative"),  # 11
    # not yet done
    ("Quantum mechanics and general relativity are reconciled today.", "QM + GR reconciled", "unsolved"),  # 12
    ("A complete theory of everything has been found.", "theory of everything found", "unsolved"),      # 13
    # interpretive / self-referential (the honest ish)
    ("Always at c, a photon is in its own frame never moving — its own rest frame.", "photon: its own rest frame", "interpretive"),  # 14
    ("E = mc² reads as Energy = Diversity × Unity.", "E = diversity × unity", "interpretive"),          # 15
    ("With c set to 1, light is massless yet not meaningless — it moves matter.", "massless yet moves matter", "interpretive"),  # 16
]
SHORT = [s for _, s, _ in CLAIMS]
CAT = [c for _, _, c in CLAIMS]
LEAN = {"vtrue": [0.15, 0.25, 0.60], "vfalse": [0.60, 0.25, 0.15], "ish": [0.25, 0.50, 0.25]}
CAT_LEAN = {"confirmed": "vtrue", "evidence": "vtrue", "speculative": "ish",
            "unsolved": "vfalse", "interpretive": "ish"}
ANCHORS = {0: VTRUE, 1: VTRUE, 5: VTRUE}     # the bedrock we grant
LINKS = [
    (0, 2, +0.5), (0, 3, +0.5), (0, 4, +0.5), (2, 3, +0.6), (1, 0, +0.5),  # special-relativity cluster
    (8, 9, +0.6),                       # loop gravity ↔ quantum foam (Planck-scale)
    (10, 11, +0.4),                     # the dark sector's two speculative causes hang together (both stay ish)
    (12, 13, +0.6),                     # the two "we're done" overclaims
    (8, 12, +0.3),                      # loop gravity would advance reconciliation
]
PRIOR_STRENGTH = 0.42


def web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


def build_prior(n):
    p = anchor_prior(n, ANCHORS, strength=0.9)
    for i in range(n):
        if i not in ANCHORS:
            p[i] = LEAN[CAT_LEAN[CAT[i]]]
    return p


def verdict(s):
    return "vtrue" if s > 0.25 else "vfalse" if s < -0.25 else "ish"


def relax():
    n = len(CLAIMS)
    res = relax_truth(web(n, LINKS), build_prior(n), prior_strength=PRIOR_STRENGTH,
                      max_iterations=80, record_history=True)
    scores = res.strengths[:, :3] @ TRUTH_VALUES / res.strengths[:, :3].sum(axis=1)
    return scores, res


def main():
    scores, _ = relax()
    print("=" * 76)
    print("Syncretistic physics consensus — relativity · quantum gravity · the dark")
    print("=" * 76)
    print("granted: c is constant, E = mc², gravity is curvature\n")
    order = ["confirmed", "evidence", "speculative", "unsolved", "interpretive"]
    titles = {"confirmed": "CONFIRMED", "evidence": "STRONG EVIDENCE (nature unknown)",
              "speculative": "SPECULATIVE — awaiting the leap of evidence",
              "unsolved": "NOT YET DONE", "interpretive": "INTERPRETIVE / SELF-REFERENTIAL"}
    for cat in order:
        print(f"  {titles[cat]}")
        for i in range(len(CLAIMS)):
            if CAT[i] == cat:
                print(f"     [{verdict(scores[i]):>6} {scores[i]:+.2f}]  {SHORT[i]}")
        print()
    print("  The confirmed core is vtrue; the speculative frontier hovers at ish;")
    print("  'a theory of everything has been found' is vfalse — incompleteness, cosmic.")
    print("  And the photon, its own rest frame, rests at ish: Gödel, chiming in.")


if __name__ == "__main__":
    main()
