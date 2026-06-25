"""Cosmic Truth-O-Meter: physics claims relaxing to vtrue / ish / vfalse.

Run: ``python make_quantum_viz.py``
  assets/quantum_truthometer.png  + assets/quantum_consensus.gif
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
BG = "#070912"
BAND = {"vtrue": "#3ddc84", "ish": "#f1c40f", "vfalse": "#e74c3c"}
CATCOL = {"confirmed": "#7fd6ff", "evidence": "#a0e0c0", "speculative": "#c9a0ff",
          "unsolved": "#ff9aa0", "interpretive": "#9b8cff"}


def verdict(s):
    return "vtrue" if s > 0.25 else "vfalse" if s < -0.25 else "ish"


def _demo():
    spec = importlib.util.spec_from_file_location("q", ROOT / "examples" / "quantum_consensus_demo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


Q = _demo()
N = len(Q.CLAIMS)
_, RES = Q.relax()
SEQ = [S[:, :3] @ TRUTH_VALUES / S[:, :3].sum(1) for S in RES.history]
SELF = {14, 15, 16}     # interpretive / self-referential indices


def draw(ax, scores, it=None, nit=None):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-0.7, N - 0.3)
    ax.invert_yaxis()
    ax.axvspan(-1.12, -0.25, color="#e74c3c", alpha=0.08)
    ax.axvspan(-0.25, 0.25, color="#f1c40f", alpha=0.10)
    ax.axvspan(0.25, 1.12, color="#3ddc84", alpha=0.08)
    ax.axvline(0, color="#33405a", lw=1, ls=":")
    t = it if it is not None else len(SEQ) - 1
    for i in range(N):
        s = scores[i]
        sr = i in SELF
        c = "#9b8cff" if sr else BAND[verdict(s)]
        ax.plot([-1, 1], [i, i], color="#161c2b", lw=2.4, zorder=1, solid_capstyle="round")
        pulse = (1 + 0.4 * np.sin(t * 0.7)) if sr else 1.0
        ax.scatter(s, i, s=1000 * (0.25 + 0.75 * abs(s)) * pulse + (220 if sr else 0),
                   color=c, alpha=0.18, edgecolors="none", zorder=2)
        ax.scatter(s, i, s=180, color=c, edgecolors="white", linewidths=1.4, zorder=3)
        ax.text(-1.18, i, Q.SHORT[i], ha="right", va="center",
                color=CATCOL[Q.CAT[i]], fontsize=9)
        ax.text(1.18, i, verdict(s).upper() if not sr else "ish ↯", ha="left", va="center",
                color=c, fontsize=8, fontweight="bold")
    ax.set_yticks([])
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["vfalse", "ish", "vtrue"], color="#9aa0aa", fontsize=9)
    ax.tick_params(colors="#33405a", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    sub = f"      iteration {it:>2}/{nit}" if it is not None else "      (converged)"
    ax.set_title("Syncretistic physics consensus" + sub, color="white",
                 fontsize=13.5, fontweight="bold", pad=14)


def main():
    fig, ax = plt.subplots(figsize=(10.6, 0.6 * N + 1.8))
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.28, right=0.84, top=0.93, bottom=0.06)
    draw(ax, SEQ[-1])
    fig.savefig(ASSETS / "quantum_truthometer.png", facecolor=BG, dpi=130)
    print("wrote assets/quantum_truthometer.png")
    frames = list(range(len(SEQ))) + [len(SEQ) - 1] * 10
    anim = FuncAnimation(fig, lambda t: draw(ax, SEQ[t], t, len(SEQ) - 1),
                         frames=frames, interval=150)
    anim.save(ASSETS / "quantum_consensus.gif", writer=PillowWriter(fps=7),
              savefig_kwargs={"facecolor": BG})
    print(f"wrote assets/quantum_consensus.gif ({len(frames)} frames)")


if __name__ == "__main__":
    main()
