"""Animate the leap of faith across the ish chasm — cross, or starve.

Run: ``python make_leap_gif.py``
  assets/leap_of_faith.png  — the final frame
  assets/leap_of_faith.gif  — two selves at the edge of reason's gap: one refuses
                              and starves, one leaps by the absurd and flourishes.
"""
import importlib.util
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
BG = "#0b0d14"


def _demo():
    spec = importlib.util.spec_from_file_location("k", ROOT / "examples" / "kierkegaard_leap_demo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K = _demo()
XR, VR = K.leap(do_leap=False)      # refusal
XL, VL = K.leap(do_leap=True)       # the leap
NF = len(XR)


def draw(ax, t):
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.85, 1.85)
    # the chasm reason cannot bridge
    ax.axvspan(-0.25, 0.25, color="#10131f", alpha=1.0, zorder=0)
    ax.axvspan(-0.25, 0.25, color="#2a2f45", alpha=0.5, zorder=0, hatch="////", ec="#1c2030")
    ax.text(0, 1.7, "the chasm reason cannot bridge  (ish · undecidable)",
            ha="center", color="#5b6378", fontsize=8.5, style="italic")
    for y, label in [(1.0, "REFUSE  ·  hover at the edge"), (0.0, "LEAP  ·  cross by the absurd")]:
        ax.plot([-1.1, 1.1], [y, y], color="#1c2230", lw=2, zorder=1, solid_capstyle="round")
        ax.text(-1.12, y + 0.22, label, color="#8088a0", fontsize=9, fontweight="bold")

    # refusal self — vitality drains, it starves at the near edge
    xr, vr = XR[t], VR[t]
    cr = "#e74c3c" if vr < 0.25 else "#c98a3a"
    ax.scatter(xr, 1.0, s=300 * vr + 60, color=cr, alpha=0.18 + 0.4 * vr, edgecolors="none", zorder=2)
    ax.scatter(xr, 1.0, s=120, color=cr, edgecolors="white", linewidths=1.2, alpha=0.4 + 0.6 * vr, zorder=3)

    # leaping self — commits across, flourishes
    xl, vl = XL[t], VL[t]
    ax.scatter(xl, 0.0, s=300 * vl + 60, color="#2ecc71", alpha=0.18 + 0.35 * vl, edgecolors="none", zorder=2)
    ax.scatter(xl, 0.0, s=130, color="#2ecc71", edgecolors="white", linewidths=1.3, zorder=3)

    # vitality readouts
    ax.text(1.05, 1.0, f"vitality {vr:.2f}" + ("  ✝ starved" if vr < 0.05 else ""),
            ha="right", va="bottom", color=cr, fontsize=8)
    ax.text(1.05, 0.0, f"vitality {vl:.2f}" + ("  ✦ flourishing" if vl > 0.7 else ""),
            ha="right", va="bottom", color="#2ecc71", fontsize=8)

    ax.set_yticks([])
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["reason: false", "ish", "reason: true"], color="#7a808a", fontsize=9)
    ax.tick_params(colors="#222", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("The leap of faith — to refuse to cross is to starve",
                 color="white", fontsize=13, fontweight="bold", pad=14)


def main():
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(left=0.04, right=0.98, top=0.88, bottom=0.12)

    draw(ax, NF - 1)
    fig.savefig(ASSETS / "leap_of_faith.png", facecolor=BG, dpi=130)
    print("wrote assets/leap_of_faith.png")

    frames = list(range(NF)) + [NF - 1] * 10
    anim = FuncAnimation(fig, lambda t: draw(ax, t), frames=frames, interval=110)
    anim.save(ASSETS / "leap_of_faith.gif", writer=PillowWriter(fps=9),
              savefig_kwargs={"facecolor": BG})
    print(f"wrote assets/leap_of_faith.gif ({len(frames)} frames)")


if __name__ == "__main__":
    main()
