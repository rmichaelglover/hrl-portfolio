"""Morphogenesis: wounded tissue regenerates back to the target form."""
import numpy as np

from hrl import body_plan, regenerate


def test_interior_wound_heals():
    target = body_plan(22, 22)
    wound = np.zeros_like(target, bool)
    wound[8:13, 7:14] = True
    wound &= target > 0
    grids, _ = regenerate(target, wound, prior_strength=0.75, iterations=60)
    assert (grids[-1][wound] == target[wound]).mean() > 0.95   # the hole fills back


def test_amputated_tail_regrows():
    target = body_plan(24, 24)
    wound = target == 3                                          # remove the tail entirely
    grids, _ = regenerate(target, wound, prior_strength=0.82, iterations=60)
    assert (grids[-1][wound] == target[wound]).mean() > 0.8     # tail regrows from boundary + memory
    assert (grids[-1] == target).mean() > 0.95                  # the whole body is nearly perfect


if __name__ == "__main__":
    test_interior_wound_heals()
    test_amputated_tail_regrows()
    print("ok  morphogenesis tests")
