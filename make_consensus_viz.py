"""The Truth-O-Meter: visualize claims relaxing to vtrue / ish / vfalse.

Run: ``python make_consensus_viz.py``
Produces, for both physics and chess:
  assets/truthometer_<domain>.png   — static final gauge
  assets/consensus_<domain>.gif     — claims lighting up as relaxation iterates

Each claim rides a red→gold→green track. Its glowing marker sits at the
*expected truth* (−1 false … +1 true) and slides outward, brightening, as the
relaxation labeling converges.
"""
import importlib.util
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from hrl.consensus import relax_truth, TRUTH_VALUES

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#0f1117"
BANDCOL = {"vtrue": "#2ecc71", "ish": "#f1c40f", "vfalse": "#e74c3c"}


def band(s):
    return "vtrue" if s > 0.25 else "vfalse" if s < -0.25 else "ish"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "examples" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scores_of(strength):
    real = strength[:, :3]
    norm = real / real.sum(axis=1, keepdims=True)
    return norm @ TRUTH_VALUES


def draw_meter(ax, scores, labels, title, it=None, nit=None):
    n = len(scores)
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-0.7, n - 0.3)
    ax.invert_yaxis()
    ax.axvspan(-1.12, -0.25, color="#e74c3c", alpha=0.10)
    ax.axvspan(-0.25, 0.25, color="#f1c40f", alpha=0.10)
    ax.axvspan(0.25, 1.12, color="#2ecc71", alpha=0.10)
    ax.axvline(0, color="#3a4150", lw=1, ls=":")
    for i, (s, lab) in enumerate(zip(scores, labels)):
        c = BANDCOL[band(s)]
        ax.plot([-1, 1], [i, i], color="#222831", lw=2.5, zorder=1, solid_capstyle="round")
        ax.scatter(s, i, s=1200 * (0.25 + 0.75 * abs(s)), color=c, alpha=0.20,
                   edgecolors="none", zorder=2)                       # glow ∝ confidence
        ax.scatter(s, i, s=190, color=c, edgecolors="white", linewidths=1.5, zorder=3)
        ax.text(-1.18, i, lab, ha="right", va="center", color="#dfe3ea", fontsize=9.5)
        ax.text(1.18, i, band(s).upper(), ha="left", va="center", color=c,
                fontsize=8.5, fontweight="bold")
    ax.set_yticks([])
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["vfalse\n−1", "ish\n0", "vtrue\n+1"], color="#9aa0aa", fontsize=9)
    ax.tick_params(colors="#3a4150", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    sub = f"      iteration {it:>2}/{nit}" if it is not None else "      (converged)"
    ax.set_title("⚖  " + title + sub, color="white", fontsize=13, fontweight="bold", pad=14)


def render(labels, agreement, prior, prior_strength, slug, title):
    res = relax_truth(agreement, prior, prior_strength=prior_strength,
                      max_iterations=60, record_history=True)
    seq = [scores_of(S) for S in res.history]      # expected truth per iteration
    n = len(labels)
    fig, ax = plt.subplots(figsize=(9.4, 0.62 * n + 1.6))
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.30, right=0.84, top=0.86, bottom=0.12)

    # static final gauge
    draw_meter(ax, seq[-1], labels, title)
    fig.savefig(ASSETS / f"truthometer_{slug}.png", facecolor=BG, dpi=130)
    print(f"  wrote assets/truthometer_{slug}.png")

    # animated: every iteration + a hold on the final
    frames = list(range(len(seq))) + [len(seq) - 1] * 8
    anim = FuncAnimation(fig, lambda t: draw_meter(ax, seq[t], labels, title, t, len(seq) - 1),
                         frames=frames, interval=200)
    anim.save(ASSETS / f"consensus_{slug}.gif", writer=PillowWriter(fps=6),
              savefig_kwargs={"facecolor": BG})
    plt.close(fig)
    print(f"  wrote assets/consensus_{slug}.gif  ({len(frames)} frames)")


def physics():
    d = _load("physics_consensus_demo")
    n = len(d.CLAIMS)
    labels = ["finite light speed", "c same for all  ⚓", "luminiferous ether",
              "no ether needed", "gravity instant", "gravity = curvature",
              "equal fall in vacuum  ⚓", "heavier falls faster", "Newtonian orbits ok"]
    render(labels, d._web(n, d.LINKS), d.anchor_prior(n, d.ANCHORS, strength=0.9),
           0.4, "physics", "Physics Truth-O-Meter")


def chess():
    d = _load("chess_maxims_demo")
    n = len(d.MAXIMS)
    labels = ["control center", "develop pieces", "castle early", "rooks open files",
              "knight on rim dim", "queen stays home", "material decides",
              "storm the wing", "daring > book"]
    render(labels, d.web(n, d.LINKS), d.build_prior(n), d.PRIOR_STRENGTH,
           "chess", "Chess Truth-O-Meter")


if __name__ == "__main__":
    print("rendering truth-o-meters into assets/ ...")
    physics()
    chess()
    print("done.")
