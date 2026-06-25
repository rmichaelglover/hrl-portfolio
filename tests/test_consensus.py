"""Consensus: anchored truth propagation, ish for contested claims, NLP signs."""
import numpy as np

from hrl.consensus import (
    VFALSE, VTRUE, agreement_to_compatibility, anchor_prior,
    lexical_agreement, relax_truth, truth_report,
)


def _web(n, links):
    a = np.zeros((n, n))
    for i, k, w in links:
        a[i, k] = a[k, i] = w
    return a


# true {0,1,3,5,6}, false {2,4,7}, contested {8}; anchors are claims 1 and 6.
LINKS = [(0, 1, 0.8), (1, 3, 0.7), (2, 3, -0.9), (4, 5, -0.9), (3, 5, 0.6),
         (6, 7, -0.9), (5, 6, 0.5), (2, 4, 0.5), (4, 7, 0.4), (8, 5, 0.3), (8, 4, 0.3)]
TRUE_CLAIMS, FALSE_CLAIMS, ISH_CLAIMS = {0, 1, 3, 5, 6}, {2, 4, 7}, {8}


def test_anchored_web_sorts_truth():
    n = 9
    prior = anchor_prior(n, {1: VTRUE, 6: VTRUE}, strength=0.9)
    report = truth_report(relax_truth(_web(n, LINKS), prior, prior_strength=0.4))
    for i, r in enumerate(report):
        if i in TRUE_CLAIMS:
            assert r["truth"] == "vtrue", (i, r)
        elif i in FALSE_CLAIMS:
            assert r["truth"] == "vfalse", (i, r)
        else:
            assert r["truth"] == "ish", (i, r)


def test_anchor_breaks_sign_symmetry():
    # A pure contradiction pair is symmetric; the anchor decides which way.
    agreement = _web(2, [(0, 1, -0.9)])
    up = truth_report(relax_truth(agreement, anchor_prior(2, {0: VTRUE}), prior_strength=0.5))
    assert up[0]["truth"] == "vtrue" and up[1]["truth"] == "vfalse"
    down = truth_report(relax_truth(agreement, anchor_prior(2, {0: VFALSE}), prior_strength=0.5))
    assert down[0]["truth"] == "vfalse" and down[1]["truth"] == "vtrue"


def test_contradiction_rewards_opposite_truth():
    compat = agreement_to_compatibility(np.array([[0.0, -1.0], [-1.0, 0.0]]))
    # claim0=vtrue, claim1=vfalse should be maximally compatible under contradiction
    assert compat[0, VTRUE, 1, VFALSE] == 1.0
    assert compat[0, VTRUE, 1, VTRUE] == 0.0


def test_lexical_frontend_signs():
    a = lexical_agreement([
        "Space needs an ether to carry light.",
        "Space does not need an ether to carry light.",
    ])
    assert a[0, 1] < 0  # negation polarity differs -> contradiction


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all consensus tests passed")
