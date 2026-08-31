"""The leap demo: the synthesis verdicts hold, and refusing to leap starves."""
import importlib.util
import pathlib

_DEMO = pathlib.Path(__file__).resolve().parent.parent / "examples" / "kierkegaard_leap_demo.py"


def _demo():
    spec = importlib.util.spec_from_file_location("kierkegaard_leap_demo", _DEMO)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_rational_irrationality_verdicts():
    d = _demo()
    scores = d.relax()
    v = lambda i: d.verdict(scores[i])
    assert v(0) == "vtrue"                  # faith begins where reason ends (anchor)
    assert v(1) == "vfalse"                 # God provable by pure reason → false
    assert v(7) == "vfalse"                 # "faith = mere abandonment of reason" → false
    assert v(11) == "vtrue"                 # faith is rational AND irrational → true
    assert all(v(i) == "ish" for i in d.SELF_REF)   # the self-relating self stays undecidable
    assert v(9) == "vfalse"                 # "refusing to explore flourishes" → false


def test_refusal_starves_leap_flourishes():
    d = _demo()
    _, v_refuse = d.leap(do_leap=False)
    _, v_leap = d.leap(do_leap=True)
    assert v_refuse[-1] < 0.05              # refuse to commit → vitality drains to ~0 (starves)
    assert v_leap[-1] > 0.7                 # the leap → vitality blooms (flourishes)
    assert v_leap[-1] > v_refuse[-1]


if __name__ == "__main__":
    test_rational_irrationality_verdicts()
    test_refusal_starves_leap_flourishes()
    print("ok  kierkegaard leap tests")
