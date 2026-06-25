"""Consensus: anchored truth propagation, ish for contested claims, NLP signs."""
import numpy as np

from hrl.consensus import (
    VFALSE, VTRUE, agreement_to_compatibility, anchor_prior,
    extract_claims, lexical_agreement, relax_truth, truth_report,
)
from hrl.nli import NLIAgreement


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


class _FakeNLI:
    """Stand-in for a transformers NLI pipeline (no model download in tests)."""
    def __call__(self, pairs, batch_size=16):
        out = []
        for p in pairs:
            a, b = p["text"], p["text_pair"]
            base_a, base_b = a.replace("not ", ""), b.replace("not ", "")
            if base_a == base_b and ("not" in a) != ("not" in b):
                scores = {"entailment": 0.0, "neutral": 0.1, "contradiction": 0.9}
            elif a == b:
                scores = {"entailment": 0.9, "neutral": 0.1, "contradiction": 0.0}
            else:
                scores = {"entailment": 0.1, "neutral": 0.8, "contradiction": 0.1}
            out.append([{"label": k, "score": v} for k, v in scores.items()])
        return out


def test_nli_agreement_signs_and_threshold():
    agg = NLIAgreement(threshold=0.15)
    agg._pipe = _FakeNLI()                       # inject the fake; no real load
    a = agg(["it works", "not it works", "something else"])
    assert a[0, 1] < 0                            # opposite polarity -> contradiction
    assert a[0, 1] == a[1, 0]                     # symmetric
    assert a[0, 2] == 0 and a[1, 2] == 0          # weak/neutral edge dropped


def test_extract_claims_splits_and_filters():
    text = "Compound X reduces mortality. It was tested widely, e.g. in mice. Short."
    claims = extract_claims(text, min_words=4)
    assert len(claims) == 2                       # "Short." dropped (too short)
    assert any("e.g. in mice" in c for c in claims)   # abbreviation not split


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all consensus tests passed")
