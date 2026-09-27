import numpy as np

from grrle import Role, build_strong_demo


def test_tree_and_roles_are_deterministic():
    tree = build_strong_demo(seed=7)
    assert len(tree.nodes) == 20
    assert sum(node.role is Role.LABEL for node in tree.nodes) == 16
    assert all(np.all(np.abs(node.tau) <= 0.4) for node in tree.nodes)


def test_relaxation_is_bounded_and_reports_observables():
    tree = build_strong_demo(seed=7)
    history = tree.relax(steps=20, eta=0.02, momentum=0.0, log_every=999)
    assert history
    assert all(np.isfinite(history))
    assert all(np.all(np.abs(node.tau) <= 1.0) for node in tree.nodes)
    obs = tree.observables()
    assert obs["n_nodes"] == 20.0
    assert all(np.isfinite(v) for v in obs.values())


def test_promote_decompose_and_depth_increase():
    tree = build_strong_demo(seed=3)
    top = max(tree.nodes, key=lambda node: node.depth)
    promoted = tree.promote(top)
    assert promoted.parent_uid is None
    assert promoted.depth == top.depth + 1
    children = tree.decompose(promoted, n_children=2)
    assert len(children) == 2
    assert all(child.parent_uid == promoted.uid for child in children)
    before = len(tree.nodes)
    result = tree.deepen_and_check(extra_depth=2, relax_steps=0)
    assert len(tree.nodes) == before + 2
    assert result["after"]["n_nodes"] == float(before + 2)


def test_invalid_depth_is_rejected():
    tree = build_strong_demo()
    try:
        tree.deepen_and_check(extra_depth=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative extra_depth must be rejected")


if __name__ == "__main__":
    for name in sorted(globals()):
        if name.startswith("test_"):
            globals()[name]()
    print("PASS: tree construction, bounded relaxation, duality, depth increase, and validation")
