"""Tracking: identities stay consistent through motion, shuffling, ghosts, drops."""
import numpy as np

from hrl import track_sequence
from hrl.tracking import synthetic_sequence

# Asymmetric 5-marker body (all-distinct pairwise distances).
BODY = np.array([[0.0, 0.0], [2.0, 0.2], [0.3, 1.6], [2.4, 1.9], [1.1, 3.0]])


def _score(frames, truth, assignments):
    real_total = real_ok = ghost_total = ghost_ok = 0
    for tru, a in zip(truth, assignments):
        for t, lbl in zip(tru, a):
            if t == -1:
                ghost_total += 1
                ghost_ok += int(lbl == -1)
            else:
                real_total += 1
                real_ok += int(lbl == t)
    return real_ok / real_total, (ghost_ok / ghost_total if ghost_total else 1.0)


def test_tracks_through_motion_and_shuffle():
    frames, truth = synthetic_sequence(BODY, n_frames=24, noise=0.02, seed=1)
    assignments = track_sequence(frames, BODY)
    real_acc, _ = _score(frames, truth, assignments)
    assert real_acc == 1.0


def test_ghosts_go_to_noise_and_dropouts_survive():
    frames, truth = synthetic_sequence(
        BODY, n_frames=24, noise=0.02, ghost_every=4, drop_every=6, seed=2
    )
    assignments = track_sequence(frames, BODY)
    real_acc, ghost_acc = _score(frames, truth, assignments)
    assert real_acc >= 0.98          # real markers keep their identity...
    assert ghost_acc >= 0.9          # ...and spurious detections are quarantined


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all tracking tests passed")
