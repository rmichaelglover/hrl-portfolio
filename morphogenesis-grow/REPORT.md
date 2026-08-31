# 🌱 Morning Report — Growing-Graph Morphogenesis (Levin Milestone 2)

*Built overnight, 2026-06-30. The hard part is won.*

## What you asked for
A tougher build: morphogenesis on a **growing graph** — a body that grows from a single
seed-cell (division/death as relaxation on a *dynamic* graph, not a fixed lattice),
regenerates after injury, and reproduces the two-headed result on a living substrate.

## What was built — and it works ✅
**`morphogenesis_v3.py`** + a live animated demo:
→ **https://rmichaelglover.github.io/hrl-portfolio/morphogenesis-grow/**

```
VERIFICATION — growing-graph morphogenesis
  cells grown (wt): 369 / 369 target slots
  wild-type    final: head_ant=True head_post=False  (one head)
  reprogrammed final: head_ant=True head_post=True   (TWO HEADS)
```

The animation shows, side by side, the full life-cycle in 33 frames:
1. **Grow** 🌱 — from **1 seed-cell** the body recruits in-target neighbours (division),
   spreading outward and self-labelling into head / trunk / tail.
2. **Amputate** ✂️ — the posterior third is removed at frame 17.
3. **Regrow** 🐛 — the boundary re-recruits the empty slots; relaxation relabels them.
   Wild-type regrows a **tail** (one head); the setpoint-reprogrammed regrows a **second
   head** (two heads) — *same kernel, same labels, only the prior edited*.

Screenshot-verified at frames 6 (growing), 17 (amputated), 32 (regrown).

## How it works (the method)
- **Dynamic graph:** cells are occupied slots on a body-shaped morphospace; gap-junction
  edges connect occupied 4-neighbours. The graph **changes every step** as cells are
  recruited (division) or cleared (injury).
- **The engine, in sparse form:** each step runs a sparse **persistent-prior
  Hummel–Zucker relaxation** — the distinguishing feature of the `hrl` engine (a prior
  that is re-folded every iteration and does not wash out), here scaled to the changing
  graph instead of a dense `[N,L,N,L]` tensor. New cells start at the coarse bioelectric
  **setpoint field** (a blurred target memory) and are sharpened by coupling to their
  already-labelled neighbours.
- **The edit:** the wild-type setpoint remembers *tail* at the posterior; the
  reprogrammed one remembers *head*. Nothing else differs — the coupling kernel and the
  label set (the "genome") are identical. This is the in-silico analogue of Levin's
  bioelectric two-headed planaria, now on a body that *grew itself*.

## Honest limitations
- **Division is geometric, not yet decision-driven.** Cells recruit any empty in-target
  neighbour; a more faithful model would let the relaxed field *gate* division (grow only
  where the setpoint wants tissue that isn't there) and let the **noise label** drive
  apoptosis. The scaffolding is here; this is the next refinement.
- **Morphospace is a fixed slot-grid.** True growth would place daughter cells in
  continuous space with mechanical relaxation, not snap them to a lattice.
- **Single hierarchy level.** This is still one scale (cell→region). Milestone 3 (cell ↔
  tissue ↔ axis, cross-scale compatibility) is not yet done.
- **No data grounding.** The kernel and setpoint are hand-built, not parametrised from
  voltage imaging. Falsifiability requires that grounding (see the proposal).

## Suggested next steps
1. **Decision-driven division + apoptosis** via the noise label (most faithful, moderate effort).
2. **Milestone 3:** a 2-scale hierarchy (axis label gating region labels).
3. **Continuous morphospace** with mechanical relaxation.
4. **Data grounding** against Levin-lab bioelectric/morphology datasets.

## Files
- `morphogenesis_v3.py` — the sim + animation generator
- `morphogenesis-grow/index.html` — the live demo (mirrored to both repos)
- `morphogenesis/proposal.md` — the research proposal (Milestone 1 ✅, now Milestone 2 ✅)

*Memory updated under `levin-hrl-research`. The same engine that reads the Bible now grows
a body from one cell — and a one-line edit to its memory gives it two heads.* 🧬
