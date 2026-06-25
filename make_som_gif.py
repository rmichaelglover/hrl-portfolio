"""Animate a self-organizing map unfolding over the engine's truth manifold.

Run: ``python make_som_gif.py``
  assets/som_map.png    — the trained map draped over the assignment space
  assets/som_unfold.gif — the SOM net unfolding from a crumpled blob to the manifold
"""
import importlib.util
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from hrl.som import SelfOrganizingMap

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BG = "#0d0f16"
BAND = {"vtrue": "#2ecc71", "ish": "#f1c40f", "vfalse": "#e74c3c"}


def verdict(x):
    return "vtrue" if x > 0.25 else "vfalse" if x < -0.25 else "ish"


def _demo():
    spec = importlib.util.spec_from_file_location("som_demo", ROOT / "examples" / "som_demo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


DATA = _demo().assignment_points()
COLORS = [BAND[verdict(p[0])] for p in DATA]
SOM = SelfOrganizingMap(grid=(6, 6), dim=2, seed=0)
HIST = SOM.train(DATA, epochs=40, record=True)


def draw(ax, W, ep=None, nep=None):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.08, 1.05)
    ax.axvspan(-1.15, -0.25, color="#e74c3c", alpha=0.07)
    ax.axvspan(-0.25, 0.25, color="#f1c40f", alpha=0.09)
    ax.axvspan(0.25, 1.15, color="#2ecc71", alpha=0.07)
    # data points (the engine's assignments)
    ax.scatter(DATA[:, 0], DATA[:, 1], c=COLORS, s=70, edgecolors="white",
               linewidths=0.6, zorder=4, alpha=0.95)
    # the SOM lattice (net)
    gw, gh, _ = W.shape
    for i in range(gw):
        ax.plot(W[i, :, 0], W[i, :, 1], color="#8ab4ff", lw=1.1, alpha=0.8, zorder=2)
    for j in range(gh):
        ax.plot(W[:, j, 0], W[:, j, 1], color="#8ab4ff", lw=1.1, alpha=0.8, zorder=2)
    ax.scatter(W[..., 0].ravel(), W[..., 1].ravel(), s=22, color="#dce8ff",
               edgecolors="#3b5bdb", linewidths=0.6, zorder=3)
    ax.set_xticks([-1, 0, 1]); ax.set_xticklabels(["vfalse", "ish", "vtrue"], color="#9aa0aa")
    ax.set_yticks([0, 1]); ax.set_yticklabels(["decided", "undecidable"], color="#9aa0aa", fontsize=8)
    ax.tick_params(colors="#3a4150", length=0)
    for sp in ax.spines.values():
        sp.set_color("#222")
    sub = f"   ·   epoch {ep:>2}/{nep}" if ep is not None else "   ·   organized"
    ax.set_title("A self-organizing map of the engine's truth-space" + sub,
                 color="white", fontsize=12.5, fontweight="bold", pad=12)


def main():
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.1)

    draw(ax, HIST[-1])
    fig.savefig(ASSETS / "som_map.png", facecolor=BG, dpi=130)
    print("wrote assets/som_map.png")

    frames = list(range(len(HIST))) + [len(HIST) - 1] * 8
    anim = FuncAnimation(fig, lambda t: draw(ax, HIST[t], t, len(HIST) - 1),
                         frames=frames, interval=140)
    anim.save(ASSETS / "som_unfold.gif", writer=PillowWriter(fps=8),
              savefig_kwargs={"facecolor": BG})
    print(f"wrote assets/som_unfold.gif ({len(frames)} frames)")


if __name__ == "__main__":
    main()
