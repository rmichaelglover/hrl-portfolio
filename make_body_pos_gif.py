"""Render body-position labeling: a night of sleep settling, as an animated GIF.

Run: ``python make_body_pos_gif.py``  ->  assets/body_pos.gif  +  assets/body_pos.png

Left: the accelerometer readings live on (and off) the gravity sphere; each
snaps to one of the six canonical postures (big anchors) as relaxation iterates,
while roll-over spikes fly off the sphere and flash gray ✕ to the noise label.
Right: the night's hypnogram fills in, marker brightness = confidence. The view
rotates and the title tracks live posture accuracy.
"""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from hrl import classify_session, synthetic_session, canonical_positions, POSITION_NAMES

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#0f1117"
NOISE_COL = "#8a8f98"

readings, times, truth = synthetic_session(seed=3)
positions, names = canonical_positions()
res = classify_session(readings, times=times, record_history=True)
hist = res.history                       # per-iteration strength snapshots
n_lab = len(names)
cols = plt.cm.tab10(np.linspace(0, 1, n_lab))

g = float(np.linalg.norm(positions[0]))
# a faint wireframe gravity sphere for context
u, v = np.mgrid[0:2 * np.pi:16j, 0:np.pi:10j]
sx, sy, sz = g * np.cos(u) * np.sin(v), g * np.sin(u) * np.sin(v), g * np.cos(v)

fig = plt.figure(figsize=(11, 5.2))
fig.patch.set_facecolor(BG)
ax3d = fig.add_subplot(1, 2, 1, projection="3d")
axtl = fig.add_subplot(1, 2, 2)


def snapshot(S):
    """argmax posture (incl. noise -> -1) and confidence from a strength matrix."""
    win = np.argmax(S, axis=1)
    conf = S[np.arange(len(S)), win]
    asg = np.where(win == n_lab, -1, win)
    return asg, conf


def draw(t):
    S = hist[min(t, len(hist) - 1)]
    asg, conf = snapshot(S)

    # ---- left: 3-D gravity sphere -------------------------------------------
    ax3d.clear()
    ax3d.set_facecolor(BG)
    ax3d.plot_wireframe(sx, sy, sz, color="#202833", linewidth=0.4)
    for p, nm, c in zip(positions, names, cols):
        ax3d.scatter(*p, s=520, facecolors="none", edgecolors=c, linewidths=1.6,
                     alpha=0.6, zorder=2)
        ax3d.text(p[0] * 1.42, p[1] * 1.42, p[2] * 1.42, nm, color=c, fontsize=8.5,
                  ha="center", va="center", fontweight="bold")
    for r, a, c in zip(readings, asg, conf):
        if a < 0:
            ax3d.scatter(*r, marker="x", s=80, c=NOISE_COL, linewidths=2.2, zorder=5)
        else:
            ax3d.scatter(*r, s=30 + 70 * c, c=[cols[a]], edgecolors="white",
                         linewidths=0.4, alpha=0.9, zorder=4)
    lim = 1.9 * g
    ax3d.set_xlim(-lim, lim); ax3d.set_ylim(-lim, lim); ax3d.set_zlim(-lim, lim)
    ax3d.set_box_aspect((1, 1, 1))
    ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])
    ax3d.xaxis.pane.fill = ax3d.yaxis.pane.fill = ax3d.zaxis.pane.fill = False
    for pane in (ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane):
        pane.set_edgecolor((0, 0, 0, 0))
    ax3d.view_init(elev=22, azim=-60 + 1.5 * t)
    ax3d.set_title("gravity vector → posture", color="#dfe3ea", fontsize=10, pad=0)

    # ---- right: hypnogram ----------------------------------------------------
    axtl.clear()
    axtl.set_facecolor(BG)
    for tt, tr in enumerate(truth):                # faint truth rings
        if tr >= 0:
            axtl.scatter(times[tt], tr, facecolors="none", edgecolors="#39424f",
                         s=120, zorder=1)
    for tt, (a, c) in enumerate(zip(asg, conf)):
        if a < 0:
            axtl.scatter(times[tt], n_lab, marker="x", s=55, c=NOISE_COL,
                         linewidths=1.8, zorder=3)
        else:
            axtl.scatter(times[tt], a, s=40 + 90 * c, c=[cols[a]],
                         edgecolors="white", linewidths=0.6, zorder=3)
    axtl.set_yticks(list(range(n_lab)) + [n_lab])
    axtl.set_yticklabels(names + ["noise"], color="#aeb6c2", fontsize=9)
    axtl.set_xlabel("time (samples)", color="#aeb6c2", fontsize=9)
    axtl.tick_params(colors="#39424f", labelsize=8)
    for sp in axtl.spines.values():
        sp.set_color("#39424f")
    axtl.set_xlim(times.min() - 1, times.max() + 1)
    axtl.set_ylim(-0.6, n_lab + 0.6)
    axtl.set_title("the night, labeled", color="#dfe3ea", fontsize=10)

    real = truth >= 0
    acc = (asg[real] == truth[real]).mean()
    quar = (asg[~real] == -1).mean() if (~real).any() else 1.0
    it = min(t, len(hist) - 1)
    fig.suptitle(f"HRL body-position labeling · iteration {it:2d}/{len(hist) - 1} · "
                 f"posture {acc * 100:3.0f}% · roll-overs→noise {quar * 100:3.0f}%",
                 color="white", fontsize=12.5, fontweight="bold", y=0.98)


# play through every iteration, then hold the converged frame
seq = list(range(len(hist))) + [len(hist) - 1] * 8
anim = FuncAnimation(fig, draw, frames=seq, interval=240)
fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.12, wspace=0.12)

out_gif = ASSETS / "body_pos.gif"
anim.save(out_gif, writer=PillowWriter(fps=5), savefig_kwargs={"facecolor": BG})
print(f"wrote {out_gif}  ({out_gif.stat().st_size // 1024} KB, {len(seq)} frames)")

draw(len(hist) - 1)  # converged state for the static still
out_png = ASSETS / "body_pos.png"
fig.savefig(out_png, facecolor=BG, dpi=130)
print(f"wrote {out_png}  ({out_png.stat().st_size // 1024} KB)")
