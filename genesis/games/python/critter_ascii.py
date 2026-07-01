#!/usr/bin/env python3
"""THE CRITTER — simplified Python mockup (runs in your terminal, zero setup).

The same self-relaxing organism as the Roblox / Minecraft ports and the browser version, drawn
live as coloured blocks in your terminal. It relaxation-labels itself (E-step), then grows where
coherent, grooms the undecided, buds child colonies, and self-tunes its temperature to the
critical edge (self-organized criticality).

    python3 critter_ascii.py                 # live animation (Ctrl-C to stop)
    python3 critter_ascii.py --plain --snapshot 300   # print one ASCII frame and exit (no colour)

This is the mockup I use to see the Roblox/Minecraft creature before it ever reaches an engine.
"""
from __future__ import annotations
import argparse, math, random, sys, time

K = 3
COL = [(95, 227, 160), (192, 96, 255), (232, 207, 112)]   # the three cell types
GLYPH = ["o", "*", "#"]                                     # for --plain
NMAX, NMIN = 220, 8
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))

cells: dict[tuple[int, int], list[float]] = {}
ages: dict[tuple[int, int], int] = {}
T = 0.5
gen = 0
activity = 0.0


def rndp():
    a, b, c = random.random(), random.random(), random.random()
    s = a + b + c
    return [a / s, b / s, c / s]


def dom(p):
    return max(range(K), key=lambda l: p[l])


def seed_patch(cx, cz):
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            cells[(cx + dx, cz + dz)] = rndp()
            ages[(cx + dx, cz + dz)] = 0


def relax():
    global T, activity
    beta = 1 / max(0.12, T)
    new = {}
    changed = cnt = 0
    for (x, z), p in cells.items():
        nb = [(x + dx, z + dz) for dx, dz in N8 if (x + dx, z + dz) in cells]
        if not nb:
            new[(x, z)] = p; continue
        sup = [0.0, 0.0, 0.0]
        for k in nb:
            pj = cells[k]
            for l in range(K):
                sup[l] += pj[l]
        inv = 1 / len(nb)
        sup = [s * inv for s in sup]
        h = [sup[0] + 0.35 * (sup[1] + sup[2]),
             sup[1] + 0.35 * (sup[0] + sup[2]),
             sup[2] + 0.35 * (sup[0] + sup[1])]
        mx = max(h); d0 = dom(p)
        np = [(p[l] ** 0.2) * math.exp(beta * (h[l] - mx)) for l in range(K)]
        zz = sum(np); np = [v / zz for v in np]
        np = [max(1e-4, v + (random.random() - 0.5) * 0.55 * T) for v in np]
        ss = sum(np); np = [v / ss for v in np]
        new[(x, z)] = np
        if dom(np) != d0:
            changed += 1
        cnt += 1
    cells.clear(); cells.update(new)
    for k in cells:
        ages[k] = ages.get(k, 0) + 1
    activity = changed / cnt if cnt else 0.0
    if activity < 0.03:
        T = min(1.2, T * 1.03)
    elif activity > 0.12:
        T = max(0.15, T * 0.97)


def morph():
    global gen
    N = len(cells)
    groomP = 0.02 + 0.06 * (N / NMAX)
    for k in list(cells):
        if N > NMIN and max(cells[k]) < 0.45 and ages.get(k, 0) > 6 and random.random() < groomP:
            del cells[k]; ages.pop(k, None)
    growP = 0.5 * (1 - len(cells) / NMAX)
    if growP > 0:
        for (x, z) in list(cells):
            if len(cells) >= NMAX:
                break
            p = cells[(x, z)]
            empt = [(x + dx, z + dz) for dx, dz in N4 if (x + dx, z + dz) not in cells]
            if empt and max(p) > 0.5 and random.random() < growP * 0.4:
                nk = random.choice(empt)
                cells[nk] = list(p); ages[nk] = 0
    if len(cells) > NMAX * 0.7 and random.random() < 0.03:
        coh = sum(max(p) for p in cells.values()) / len(cells)
        if coh > 0.66:
            xs = [k[0] for k in cells]; zs = [k[1] for k in cells]
            cx = random.randint(min(xs) - 12, max(xs) + 12)
            cz = random.randint(min(zs) - 12, max(zs) + 12)
            if all((cx + dx, cz + dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                seed_patch(cx, cz); gen += 1


def frame(vw, vh, plain):
    if not cells:
        return ""
    xs = [k[0] for k in cells]; zs = [k[1] for k in cells]
    cx = sum(xs) // len(xs); cz = sum(zs) // len(zs)
    x0, z0 = cx - vw // 2, cz - vh // 2
    out = []
    for row in range(vh):
        z = z0 + row; line = []
        for col in range(vw):
            x = x0 + col
            if (x, z) in cells:
                d = dom(cells[(x, z)])
                if plain:
                    line.append(GLYPH[d])
                else:
                    r, g, b = COL[d]
                    line.append(f"\x1b[38;2;{r};{g};{b}m█\x1b[0m")
            else:
                line.append(" " if plain else " ")
        out.append("".join(line))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plain", action="store_true", help="ASCII glyphs, no colour (for logs/screenshots)")
    ap.add_argument("--snapshot", type=int, default=0, help="run N steps, print one frame, exit")
    ap.add_argument("--w", type=int, default=70)
    ap.add_argument("--h", type=int, default=30)
    ap.add_argument("--tick", type=float, default=0.08)
    args = ap.parse_args()
    seed_patch(0, 0)

    if args.snapshot:
        for _ in range(args.snapshot):
            relax(); morph()
        print(frame(args.w, args.h, True))
        print(f"\ncells={len(cells)}  T={T:.2f}  activity={activity*100:.0f}%  colonies-budded={gen}")
        return

    try:
        while True:
            relax(); morph()
            sys.stdout.write("\x1b[H\x1b[2J")
            sys.stdout.write(frame(args.w, args.h, args.plain))
            sys.stdout.write(f"\n\x1b[0m cells {len(cells)} | T {T:.2f} | activity {activity*100:.0f}% | "
                             f"buds {gen}   (Ctrl-C to stop)\n")
            sys.stdout.flush()
            time.sleep(args.tick)
    except KeyboardInterrupt:
        print("\nthe critter rests.")


if __name__ == "__main__":
    main()
