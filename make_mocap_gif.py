"""Render the marker tracker playing out frame-by-frame as an animated GIF.

Run: ``python make_mocap_gif.py``  ->  assets/mocap_tracking.gif

Real tracker output: a rigid body rotates and drifts while detections arrive
shuffled, with ghosts and dropouts. Each marker keeps a colored identity and a
growing trail; ghosts flash to a gray ✕ as the noise label rejects them; the
title shows the live per-frame identity accuracy.
"""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from hrl import track_sequence
from hrl.tracking import synthetic_sequence

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#0f1117"
BODY = np.array([[0., 0.], [2., .2], [.3, 1.6], [2.4, 1.9], [1.1, 3.]])
NAMES = ["head", "l-shoulder", "r-shoulder", "l-hip", "r-hip"]

frames, truth = synthetic_sequence(BODY, n_frames=30, noise=.02, rotate_deg_per_frame=4.,
                                   ghost_every=5, drop_every=7, seed=7)
asg = track_sequence(frames, BODY)
cols = plt.cm.tab10(np.linspace(0, 1, len(BODY)))

allpts = np.vstack(frames)
(xlo, ylo), (xhi, yhi) = allpts.min(0) - 1.0, allpts.max(0) + 1.0

fig, ax = plt.subplots(figsize=(7, 6.6))
fig.patch.set_facecolor(BG)

def draw(t):
    ax.clear()
    ax.set_xlim(xlo, xhi)
    ax.set_ylim(ylo, yhi)
    ax.set_aspect("equal")
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color("#333")
    ax.tick_params(colors="#444", labelsize=7)

    # rebuild trails from frames 0..t (idempotent)
    trails = {m: [] for m in range(len(BODY))}
    for tt in range(t + 1):
        for p, m in zip(frames[tt], asg[tt]):
            if m >= 0:
                trails[m].append(p)
    for m, pts in trails.items():
        if pts:
            pts = np.asarray(pts)
            ax.plot(pts[:, 0], pts[:, 1], "-", color=cols[m], lw=1.6, alpha=.45, zorder=2)

    # current frame
    fc = ft = 0
    for p, m, gt in zip(frames[t], asg[t], truth[t]):
        if gt >= 0:
            ft += 1
            fc += int(m == gt)
        if m < 0:
            ax.scatter(*p, marker="x", s=140, c="#8a8f98", linewidths=2.4, zorder=6)
            ax.annotate("ghost → noise", p, color="#8a8f98", fontsize=7.5,
                        xytext=(7, 6), textcoords="offset points")
        else:
            ax.scatter(*p, s=210, c=[cols[m]], edgecolors="white", linewidths=1.6, zorder=7)
            ax.annotate(NAMES[m], p, color="white", fontsize=8, fontweight="bold",
                        xytext=(8, 4), textcoords="offset points")

    acc = f"{fc}/{ft}" if ft else "—"
    ax.set_title(f"HRL marker tracker · frame {t + 1:2d}/{len(frames)} · "
                 f"identity this frame: {acc}",
                 color="white", fontsize=11.5, fontweight="bold", pad=12)
    ax.text(0.5, -0.07, "colored dots = tracked identity   ·   gray ✕ = ghost rejected to noise",
            transform=ax.transAxes, ha="center", color="#7a808a", fontsize=8.5)


# play through, then hold the final frame a beat
seq = list(range(len(frames))) + [len(frames) - 1] * 6
anim = FuncAnimation(fig, draw, frames=seq, interval=240)
out = ASSETS / "mocap_tracking.gif"
anim.save(out, writer=PillowWriter(fps=5), savefig_kwargs={"facecolor": BG})
print(f"wrote {out}  ({out.stat().st_size // 1024} KB, {len(seq)} frames)")
