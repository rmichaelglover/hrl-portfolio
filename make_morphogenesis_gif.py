"""Animate a body healing itself — morphogenesis as relaxation labeling.

Run: ``python make_morphogenesis_gif.py``
  assets/morphogenesis.png  + assets/morphogenesis.gif
"""
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation, PillowWriter

from hrl.morphogenesis import body_plan, regenerate, COLORS

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BG = "#070912"
RGB = np.array([mcolors.to_rgb(c) for c in COLORS])
GRAY = np.array([0.30, 0.31, 0.36])

T = body_plan(24, 24)
HOLE = np.zeros_like(T, bool); HOLE[9:15, 8:16] = True; HOLE &= T > 0
AMP = T == 3
G_HOLE, _ = regenerate(T, HOLE, prior_strength=0.75)
G_AMP, _ = regenerate(T, AMP, prior_strength=0.82)


def img(grid, wound=None):
    im = RGB[grid].copy()
    if wound is not None:
        im[wound] = GRAY
    return im


def sequence(grids, wound):
    frames = [img(T, wound)] * 3 + [img(g) for g in grids]    # show the wound, then heal
    return frames


F_AMP = sequence(G_AMP, AMP)
F_HOLE = sequence(G_HOLE, HOLE)
L = max(len(F_AMP), len(F_HOLE))
F_AMP += [F_AMP[-1]] * (L - len(F_AMP) + 10)
F_HOLE += [F_HOLE[-1]] * (L - len(F_HOLE) + 10)


def draw(t):
    for ax, frames, title in [(axL, F_AMP, "tail amputation → regrowth"),
                              (axR, F_HOLE, "wound → healing")]:
        ax.clear()
        ax.imshow(frames[t], interpolation="nearest")
        ax.set_title(title, color="#cdd3e0", fontsize=11, pad=8)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#222")
    step = min(t, L - 1)
    fig.suptitle(f"Morphogenesis as relaxation labeling — a body heals itself"
                 f"      step {step:>2}", color="white", fontsize=13.5, fontweight="bold")


fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.4, 4.6))
fig.patch.set_facecolor(BG)
fig.subplots_adjust(left=0.03, right=0.97, top=0.84, bottom=0.04, wspace=0.08)

if __name__ == "__main__":
    draw(len(F_AMP) - 1)
    fig.savefig(ASSETS / "morphogenesis.png", facecolor=BG, dpi=130)
    print("wrote assets/morphogenesis.png")
    anim = FuncAnimation(fig, draw, frames=len(F_AMP), interval=140)
    anim.save(ASSETS / "morphogenesis.gif", writer=PillowWriter(fps=8),
              savefig_kwargs={"facecolor": BG})
    print(f"wrote assets/morphogenesis.gif ({len(F_AMP)} frames)")
