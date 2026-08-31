"""Gödel demo: decidable claims commit, self-referential ones stay ish."""
import importlib.util
import pathlib

import numpy as np

from hrl.consensus import relax_truth, TRUTH_VALUES

_DEMO = pathlib.Path(__file__).resolve().parent.parent / "examples" / "godel_consensus_demo.py"


def _demo():
    spec = importlib.util.spec_from_file_location("godel_consensus_demo", _DEMO)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_engine_tastes_incompleteness():
    d = _demo()
    n = len(d.CLAIMS)
    res = relax_truth(d.web(n, d.LINKS), d.build_prior(n), prior_strength=d.PRIOR_STRENGTH)
    scores = res.strengths[:, :3] @ TRUTH_VALUES / res.strengths[:, :3].sum(axis=1)
    v = lambda i: d.verdict(scores[i])

    # incompleteness: a consistent system is NOT complete and cannot prove its consistency
    assert v(0) == "vtrue"                        # F is consistent (anchor)
    assert v(1) == "vfalse" and v(2) == "vfalse"  # not complete; can't prove own consistency
    assert v(3) == "vtrue"                        # true-but-unprovable statements exist
    # the self-referential claims cannot be pushed off ish
    assert all(v(i) == "ish" for i in d.SELF_REF)
    # chess: finite => decidable in principle, and Gödel does NOT make it unsolvable
    assert v(7) == "vtrue"                        # chess is decidable
    assert v(9) == "vfalse"                       # "Gödel ⇒ chess unsolvable" is false
    assert v(10) == "vtrue"                       # finite ⇒ Gödel N/A


if __name__ == "__main__":
    test_engine_tastes_incompleteness()
    print("ok  test_engine_tastes_incompleteness")
