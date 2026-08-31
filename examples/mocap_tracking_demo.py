"""Marker tracking through motion, shuffled detections, ghosts, and dropouts.

Run: ``python examples/mocap_tracking_demo.py``

A rigid 5-marker body rotates and drifts across 30 frames. Every frame the
detections arrive in random order, sometimes with a spurious ghost point or a
missing marker. The tracker keeps each marker's identity stable using geometry
(compatibility) + memory (the temporal prior), and sends ghosts to the noise
label. If matplotlib is present it also saves ``mocap_tracks.png``.
"""
import numpy as np

from hrl import track_sequence
from hrl.tracking import synthetic_sequence

# An asymmetric 5-marker body (head, shoulders, hips) — distinct geometry.
BODY = np.array([[0.0, 0.0], [2.0, 0.2], [0.3, 1.6], [2.4, 1.9], [1.1, 3.0]])
NAMES = ["head", "l-shoulder", "r-shoulder", "l-hip", "r-hip"]


def main():
    frames, truth = synthetic_sequence(
        BODY, n_frames=30, noise=0.02, rotate_deg_per_frame=4.0,
        ghost_every=5, drop_every=7, seed=7,
    )
    assignments = track_sequence(frames, BODY)

    real_total = real_ok = ghost_total = ghost_ok = switches = 0
    prev = {}
    for tru, asg, det in zip(truth, assignments, frames):
        seen = {}
        for t, lbl, p in zip(tru, asg, det):
            if t == -1:
                ghost_total += 1
                ghost_ok += int(lbl == -1)
            else:
                real_total += 1
                real_ok += int(lbl == t)
                if lbl >= 0:
                    seen[lbl] = p
        # an identity "switch" = a marker that jumped discontinuously frame-to-frame
        for m, p in seen.items():
            if m in prev and np.linalg.norm(p - prev[m]) > 1.0:
                switches += 1
        prev = seen

    print("=" * 60)
    print("Marker tracking — relaxation labeling across time")
    print("=" * 60)
    print(f"frames                : {len(frames)}")
    print(f"real-marker identity  : {real_ok}/{real_total} correct "
          f"({100 * real_ok / real_total:.1f}%)")
    print(f"ghosts -> noise label : {ghost_ok}/{ghost_total} quarantined")
    print(f"identity switches     : {switches}")
    print("\nThe prior is the tracker's memory: geometry says which point is "
          "which,\nmemory keeps it that way, and the noise label eats the ghosts.")

    _maybe_plot(frames, assignments)


def _maybe_plot(frames, assignments):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("\n(matplotlib not installed — skipping the trajectory plot)")
        return

    colors = plt.cm.tab10(np.linspace(0, 1, len(BODY)))
    fig, ax = plt.subplots(figsize=(7, 6))
    tracks = {m: [] for m in range(len(BODY))}
    for det, asg in zip(frames, assignments):
        for p, m in zip(det, asg):
            if m >= 0:
                tracks[m].append(p)
            else:
                ax.scatter(*p, c="0.6", marker="x", s=40, zorder=1)
    for m, pts in tracks.items():
        pts = np.asarray(pts)
        ax.plot(pts[:, 0], pts[:, 1], "-o", color=colors[m], ms=3, lw=1.2,
                label=NAMES[m], zorder=2)
    ax.scatter([], [], c="0.6", marker="x", label="ghost -> noise")
    ax.set_title("Recovered marker tracks (color = stable identity)")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_aspect("equal")
    fig.tight_layout()
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mocap_tracks.png")
    fig.savefig(out, dpi=120)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
