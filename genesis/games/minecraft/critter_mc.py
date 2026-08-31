#!/usr/bin/env python3
"""THE CRITTER — a self-relaxing simplicial organism, painted live into Minecraft.

A port of hrl-portfolio/genesis/critter. The same autopoiesis loop (relaxation-label ->
grow -> groom -> bud, self-tuning its temperature to criticality) runs here on an integer
grid, and each cell is drawn as a block of coloured wool on the ground in front of you.

SETUP (Java Edition, the classic hobby stack)
  1. Run a Spigot/Paper server with the RaspberryJuice plugin (or use the Minecraft: Pi
     Edition / an ELCI setup). RaspberryJuice opens the API on TCP 4711.
  2. pip install mcpi
  3. Stand in a flat, open area. Run:  python3 critter_mc.py
     (or  python3 critter_mc.py --dry  to watch the organism live in the terminal, no server)

It grows a living, colour-shifting mat of wool that spreads, prunes itself, and seeds child
colonies nearby. Ctrl-C to stop.
"""
from __future__ import annotations
import argparse, math, random, time

K = 3
WOOL_ID = 35
WOOL = {0: 5, 1: 10, 2: 4}          # lime, purple, yellow  (wool colour data values)
AIR = 0
NMAX, NMIN = 220, 8

cells: dict[tuple[int, int], list[float]] = {}
ages: dict[tuple[int, int], int] = {}
T = 0.5
gen = 0

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


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
    global T
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
    act = changed / cnt if cnt else 0.0
    if act < 0.03:
        T = min(1.2, T * 1.03)
    elif act > 0.12:
        T = max(0.15, T * 0.97)
    return act


def morph():
    """grow (the 'can') / groom (the 'cannot') / bud a child colony. Returns (added, removed)."""
    global gen
    N = len(cells)
    added, removed = [], []
    groomP = 0.02 + 0.06 * (N / NMAX)
    for k in list(cells):
        if N > NMIN and max(cells[k]) < 0.45 and ages.get(k, 0) > 6 and random.random() < groomP:
            del cells[k]; ages.pop(k, None); removed.append(k)
    growP = 0.5 * (1 - len(cells) / NMAX)
    if growP > 0:
        for (x, z) in list(cells):
            if len(cells) >= NMAX:
                break
            p = cells[(x, z)]
            empt = [(x + dx, z + dz) for dx, dz in N4 if (x + dx, z + dz) not in cells]
            if empt and max(p) > 0.5 and random.random() < growP * 0.4:
                nk = random.choice(empt)
                cells[nk] = list(p); ages[nk] = 0; added.append(nk)
    # REPRODUCE: a big coherent body seeds a child colony nearby
    if len(cells) > NMAX * 0.7 and random.random() < 0.03:
        coh = sum(max(p) for p in cells.values()) / len(cells)
        if coh > 0.66:
            xs = [k[0] for k in cells]; zs = [k[1] for k in cells]
            cx = random.randint(min(xs) - 12, max(xs) + 12)
            cz = random.randint(min(zs) - 12, max(zs) + 12)
            if all((cx + dx, cz + dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                seed_patch(cx, cz); gen += 1
    return added, removed


def render(mc, base_y):
    for (x, z), p in cells.items():
        mc.setBlock(x, base_y, z, WOOL_ID, WOOL[dom(p)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="run without a Minecraft server (terminal only)")
    ap.add_argument("--steps", type=int, default=100000)
    ap.add_argument("--tick", type=float, default=0.25)
    ap.add_argument("--y", type=int, default=None, help="ground Y level to draw on")
    args = ap.parse_args()

    mc = None; base_y = args.y or 4; cx = cz = 0
    if not args.dry:
        from mcpi.minecraft import Minecraft            # requires: pip install mcpi + RaspberryJuice
        mc = Minecraft.create()
        pos = mc.player.getTilePos()
        cx, cz = pos.x, pos.z + 5
        base_y = args.y if args.y is not None else pos.y - 1
        mc.postToChat("The Critter awakens...")
    seed_patch(cx, cz)

    last = set()
    try:
        for step in range(args.steps):
            relax()
            added, removed = morph()
            if mc:
                render(mc, base_y)
                for (x, z) in removed:
                    mc.setBlock(x, base_y, z, AIR)
            if step % 20 == 0:
                print(f"step {step:5d} | cells {len(cells):4d} | T {T:.2f} | colonies-budded {gen}")
            time.sleep(0.0 if args.dry else args.tick)
    except KeyboardInterrupt:
        print("\nthe critter rests.")
    if args.dry:
        print(f"\nDRY RUN complete: cells={len(cells)}, T={T:.2f}, buds={gen} — alive & stable.")


if __name__ == "__main__":
    main()
