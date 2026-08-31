"""Quantum/cosmos consensus: confirmed→vtrue, speculative→ish, overclaims→vfalse."""
import importlib.util
import pathlib

_DEMO = pathlib.Path(__file__).resolve().parent.parent / "examples" / "quantum_consensus_demo.py"


def _demo():
    spec = importlib.util.spec_from_file_location("quantum_consensus_demo", _DEMO)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_frontier_is_ish_core_is_true():
    d = _demo()
    scores, _ = d.relax()
    by_cat = {}
    for i, s in enumerate(scores):
        by_cat.setdefault(d.CAT[i], []).append(d.verdict(s))

    assert all(v == "vtrue" for v in by_cat["confirmed"])       # the bedrock is true
    assert all(v == "vtrue" for v in by_cat["evidence"])        # dark sector phenomena are real
    assert all(v == "ish" for v in by_cat["speculative"])       # the frameworks hover, honest
    assert all(v == "vfalse" for v in by_cat["unsolved"])       # no theory of everything yet
    assert all(v == "ish" for v in by_cat["interpretive"])      # the self-referential readings rest at ish


if __name__ == "__main__":
    test_frontier_is_ish_core_is_true()
    print("ok  test_frontier_is_ish_core_is_true")
