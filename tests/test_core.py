"""Tests for the relaxation-labeling core: correspondence, noise, priors."""
import numpy as np

from hrl import RelaxationLabeler, pairwise_distance_compatibility


# An asymmetric 4-point model with all-distinct pairwise distances, so the
# correspondence is uniquely recoverable from geometry alone.
MODEL = np.array([[0.0, 0.0], [3.0, 0.0], [0.0, 1.0], [1.0, 2.0]])


def _rotate(points, degrees):
    theta = np.radians(degrees)
    rot = np.array([[np.cos(theta), -np.sin(theta)],
                    [np.sin(theta), np.cos(theta)]])
    return points @ rot.T


def _make_observation(model, perm, *, degrees=37.0, shift=(5.0, -2.0), noise=0.005, seed=0):
    """Rotate/translate/permute the model into 'measured' points + tiny noise."""
    rng = np.random.default_rng(seed)
    moved = _rotate(model, degrees) + np.asarray(shift)
    obs = moved[perm] + rng.normal(scale=noise, size=moved[perm].shape)
    return obs


def test_recovers_correspondence():
    perm = np.array([2, 0, 3, 1])  # object p corresponds to label perm[p]
    objects = _make_observation(MODEL, perm)
    compat = pairwise_distance_compatibility(objects, MODEL, sigma=0.05)

    result = RelaxationLabeler(compat, max_iterations=100).run()

    assert np.array_equal(result.assignments, perm)
    assert result.converged
    np.testing.assert_allclose(result.strengths.sum(axis=1), 1.0, atol=1e-9)


def test_noise_label_absorbs_outlier():
    perm = np.array([2, 0, 3, 1])
    real = _make_observation(MODEL, perm)
    outlier = np.array([[42.0, 17.0]])          # nowhere near the model geometry
    objects = np.vstack([real, outlier])        # 5 objects, 4 labels

    compat = pairwise_distance_compatibility(objects, MODEL, sigma=0.05)
    result = RelaxationLabeler(compat, noise=True, max_iterations=100).run()

    # the 4 real points still get their true labels...
    assert np.array_equal(result.assignments[:4], perm)
    # ...and the geometrically-inconsistent 5th point is sent to noise (-1).
    assert result.assignments[4] == -1


# A deliberately symmetric "the two objects must take different labels" field:
# both perfect matchings ([0,1] and [1,0]) are equally good — a tie only a
# prior can break.
def _tie_compatibility():
    compat = np.zeros((2, 2, 2, 2))
    for i in range(2):
        for k in range(2):
            if i == k:
                continue
            for j in range(2):
                for l in range(2):
                    compat[i, j, k, l] = 1.0 if j != l else 0.0
    return compat


def test_prior_breaks_a_tie():
    compat = _tie_compatibility()

    favor_0 = np.array([[0.9, 0.1], [0.5, 0.5]])   # nudge object 0 toward label 0
    res0 = RelaxationLabeler(compat, favor_0, prior_strength=0.7).run()
    assert np.array_equal(res0.assignments, [0, 1])

    favor_1 = np.array([[0.1, 0.9], [0.5, 0.5]])   # flip the nudge
    res1 = RelaxationLabeler(compat, favor_1, prior_strength=0.7).run()
    assert np.array_equal(res1.assignments, [1, 0])


def test_uniform_prior_is_well_formed():
    compat = pairwise_distance_compatibility(MODEL, MODEL, sigma=0.05)
    result = RelaxationLabeler(compat, max_iterations=20).run()
    assert result.strengths.shape == (4, 4)
    np.testing.assert_allclose(result.strengths.sum(axis=1), 1.0, atol=1e-9)
    assert result.noise_index is None


if __name__ == "__main__":
    # Runnable without pytest: python tests/test_core.py
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all tests passed")
