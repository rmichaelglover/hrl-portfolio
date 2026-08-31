"""The chess-maxims integration: daring games refute dogma -> ish."""
import importlib.util
import pathlib

from hrl.consensus import relax_truth, truth_report

_DEMO = pathlib.Path(__file__).resolve().parent.parent / "examples" / "chess_maxims_demo.py"


def _demo():
    spec = importlib.util.spec_from_file_location("chess_maxims_demo", _DEMO)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_games_refute_dogma_to_ish():
    d = _demo()
    n = len(d.MAXIMS)
    report = truth_report(
        relax_truth(d.web(n, d.LINKS), d.build_prior(n), prior_strength=d.PRIOR_STRENGTH)
    )
    v = lambda i: d.verdict(report[i]["score"])

    # what the games positively demonstrate
    assert v(7) == "vtrue" and v(8) == "vtrue"
    # the dogmas the daring games refute relax to ish (not vtrue, not vfalse)
    assert v(0) == "ish" and v(6) == "ish"
    # the sound, style-neutral rules keep their truth
    assert all(v(i) == "vtrue" for i in (1, 2, 4, 5))


if __name__ == "__main__":
    test_games_refute_dogma_to_ish()
    print("ok  test_games_refute_dogma_to_ish")
