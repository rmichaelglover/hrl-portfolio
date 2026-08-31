"""Body position: postures are recovered, roll-over movement goes to noise."""
import numpy as np

from hrl import classify_session, synthetic_session, canonical_positions, POSITION_NAMES
from hrl.body_pos import affinity_prior


def _score(readings, times, truth):
    res = classify_session(readings, times=times)
    a = res.assignments
    real = truth >= 0
    pos_acc = (a[real] == truth[real]).mean()
    move = ~real
    noise_acc = (a[move] == -1).mean() if move.any() else 1.0
    return pos_acc, noise_acc


def test_postures_recovered_across_seeds():
    for seed in range(6):
        readings, times, truth = synthetic_session(seed=seed)
        pos_acc, _ = _score(readings, times, truth)
        assert pos_acc == 1.0, f"seed {seed}: posture accuracy {pos_acc}"


def test_rollovers_go_to_noise():
    accs = []
    for seed in range(6):
        readings, times, truth = synthetic_session(seed=seed)
        _, noise_acc = _score(readings, times, truth)
        accs.append(noise_acc)
    assert np.mean(accs) >= 0.9          # nearly all roll-overs quarantined
    assert min(accs) >= 0.8


def test_affinity_prior_picks_the_right_axis():
    positions, _ = canonical_positions()
    # A clean reading near each canonical position scores highest on that label.
    rng = np.random.default_rng(0)
    for j, p in enumerate(positions):
        reading = p + rng.normal(scale=0.3, size=3)
        prior = affinity_prior(reading[None, :], positions)[0]
        assert prior.argmax() == j


def test_prior_is_necessary_for_absolute_posture():
    # The canonical set is a symmetric octahedron, so relative geometry ALONE is
    # rotation-invariant and cannot pick an absolute posture. The absolute-fit
    # prior is what makes the problem solvable: with it, perfect recovery; with
    # a uniform prior, the geometry collapses symmetric axes together.
    from hrl import RelaxationLabeler
    from hrl.body_pos import session_compatibility
    positions, _ = canonical_positions()

    readings, times, truth = synthetic_session(seed=0)
    real = truth >= 0

    with_prior = classify_session(readings, times=times).assignments
    assert (with_prior[real] == truth[real]).mean() == 1.0

    compat = session_compatibility(readings, positions, times, temporal_strength=0.6)
    uniform = RelaxationLabeler(
        compat, prior=None, noise=True, noise_gain=1.2, max_iterations=60
    ).run().assignments
    assert (uniform[real] == truth[real]).mean() <= 0.5


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all body-position tests passed")
