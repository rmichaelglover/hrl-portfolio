"""A body that heals itself — morphogenesis as relaxation labeling.

Run: ``python examples/morphogenesis_demo.py``

The same engine that tracks markers and grades theories now grows a body. Cells
are objects, anatomical region is the label, bioelectric gap-junction coupling is
the compatibility kernel, and a coarse pattern memory is the prior. Wound the
creature — punch a hole, or amputate the tail — and relaxation regenerates it.
"""
import numpy as np

from hrl.morphogenesis import body_plan, regenerate, LABELS

GLYPH = {0: " ", 1: "▒", 2: "▓", 3: "█"}     # background / head / trunk / tail


def render(grid, wound=None):
    rows = []
    for y in range(grid.shape[0]):
        row = ""
        for x in range(grid.shape[1]):
            row += "·" if (wound is not None and wound[y, x]) else GLYPH[grid[y, x]]
        rows.append(row)
    return rows


def show(target, wound, healed, title):
    print(f"\n  {title}   (· = wounded tissue)\n")
    dmg = render(target, wound)
    fix = render(healed)
    tgt = render(target)
    print(f"   {'damaged':<26}{'→ healed':<26}{'target':<26}")
    for d, f, t in zip(dmg, fix, tgt):
        print(f"   {d:<26}{f:<26}{t:<26}")


def main():
    target = body_plan(24, 24)
    print("=" * 80)
    print("Morphogenesis as relaxation labeling — a body heals itself")
    print("=" * 80)
    print("cells = objects · region = label · bioelectric coupling = compatibility · "
          "pattern\nmemory = prior")

    # 1) interior wound
    hole = np.zeros_like(target, bool)
    hole[9:15, 8:16] = True
    hole &= target > 0
    g1, _ = regenerate(target, hole, prior_strength=0.75)
    rec1 = (g1[-1][hole] == target[hole]).mean()

    # 2) amputation
    amp = target == 3
    g2, _ = regenerate(target, amp, prior_strength=0.82)
    rec2 = (g2[-1][amp] == target[amp]).mean()

    show(target, amp, g2[-1], "TAIL AMPUTATION → REGENERATION")
    print(f"\n  interior wound : {int(hole.sum())} cells stripped of identity → "
          f"{rec1:.0%} regenerated")
    print(f"  tail amputation: {int(amp.sum())} cells stripped of identity → "
          f"{rec2:.0%} regenerated")
    print("\n  No tail tissue remained — it regrew from the intact boundary and the")
    print("  coarse bioelectric memory, sharpened by neighbor coupling. The engine grew a body.")


if __name__ == "__main__":
    main()
