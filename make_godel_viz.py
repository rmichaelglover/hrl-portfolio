"""Visualize the engine tasting incompleteness.

Run: ``python make_godel_viz.py``
  assets/godel_truthometer.png  — static final gauge
  assets/godel_consensus.gif    — decidable claims settle to vtrue/vfalse while
                                  the self-referential ones stay pinned, quivering,
                                  in the central UNDECIDABLE band.
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
BG = "#0d0f16"
BAND = {"vtrue": "#2ecc71", "ish": "#f1c40f", "vfalse": "#e74c3c"}
SELF = "#9b8cff"  # self-reference highlight


def verdict(s):
    return "vtrue" if s > 0.25 else "vfalse" if s < -0.25 else "ish"


def load_demo():
    spec = importlib.util.spec_from_file_location("g", ROOT / "examples" / "godel_consensus_demo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = load_demo()
N = len(G.CLAIMS)
RES = relax_truth(G.web(N, G.LINKS), G.build_prior(N), prior_strength=G.PRIOR_STRENGTH,
                  max_iterations=80, record_history=True)
SEQ = [S[:, :3] @ TRUTH_VALUES / S[:, :3].sum(1) for S in RES.history]  # [iters][N]


def draw(ax, scores, it=None, nit=None):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-0.7, N - 0.3)
    ax.invert_yaxis()
    ax.axvspan(-1.12, -0.25, color="#e74c3c", alpha=0.10)
    ax.axvspan(-0.25, 0.25, color="#f1c40f", alpha=0.12)
    ax.axvspan(0.25, 1.12, color="#2ecc71", alpha=0.10)
    ax.axvline(0, color="#3a4150", lw=1, ls=":")
    ax.text(0, -0.62, "U N D E C I D A B L E", ha="center", va="center",
            color="#7a6f3a", fontsize=8.5, fontweight="bold", style="italic")
    t = it if it is not None else len(SEQ) - 1
    for i in range(N):
        s = scores[i]
        selfref = i in G.SELF_REF
        c = SELF if selfref else BAND[verdict(s)]
        ax.plot([-1, 1], [i, i], color="#1c2230", lw=2.5, zorder=1, solid_capstyle="round")
        pulse = (1 + 0.45 * np.sin(t * 0.7)) if selfref else 1.0   # self-ref markers quiver
        ax.scatter(s, i, s=1100 * (0.25 + 0.75 * abs(s)) * pulse + (260 if selfref else 0),
                   color=c, alpha=0.20, edgecolors="none", zorder=2)
        ax.scatter(s, i, s=200, color=c, edgecolors="white", linewidths=1.6, zorder=3,
                   marker=("o"))
        if selfref:
            ax.scatter(s, i, s=430, facecolors="none", edgecolors=SELF, linewidths=1.6,
                       zorder=3)
        ax.text(-1.18, i, G.SHORT[i], ha="right", va="center",
                color="#c9cdd6" if not selfref else SELF, fontsize=9)
        tag = "↯ undecidable" if selfref else verdict(s).upper()
        ax.text(1.18, i, tag, ha="left", va="center", color=c, fontsize=8, fontweight="bold")
    ax.set_yticks([])
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["vfalse", "ish", "vtrue"], color="#9aa0aa", fontsize=9)
    ax.tick_params(colors="#3a4150", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    sub = f"      iteration {it:>2}/{nit}" if it is not None else "      (converged)"
    ax.set_title("The engine tastes incompleteness" + sub,
                 color="white", fontsize=13.5, fontweight="bold", pad=14)


def main():
    fig, ax = plt.subplots(figsize=(10.4, 0.62 * N + 1.8))
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.30, right=0.82, top=0.92, bottom=0.07)

    draw(ax, SEQ[-1])
    fig.savefig(ASSETS / "godel_truthometer.png", facecolor=BG, dpi=130)
    print("wrote assets/godel_truthometer.png")

    frames = list(range(len(SEQ))) + [len(SEQ) - 1] * 10
    anim = FuncAnimation(fig, lambda t: draw(ax, SEQ[t], t, len(SEQ) - 1),
                         frames=frames, interval=150)
    anim.save(ASSETS / "godel_consensus.gif", writer=PillowWriter(fps=7),
              savefig_kwargs={"facecolor": BG})
    print(f"wrote assets/godel_consensus.gif ({len(frames)} frames)")


if __name__ == "__main__":
    main()
