# hrl — hierarchical relaxation labeling

**One engine that assigns labels under context.** Give it a set of *objects*, a
set of *labels*, and a *compatibility* function that says how much one labeled
pair reinforces another. It iteratively relaxes the whole field into a
mutually-consistent labeling — the way scene-labeling, point correspondence,
and constraint satisfaction were meant to work.

The same engine, with only the compatibility kernel and prior changed:

| Domain | objects | labels | what compatibility encodes |
| --- | --- | --- | --- |
| **Motion capture** | measured 3-D points | named skeleton markers | inter-point distances match the model |
| **Strategy** | chess pieces | tactical roles | roles that co-occur in a real plan |
| **Model consensus** | observations / regimes | candidate theories | theories that agree in this regime |

This repository is a working, tested core plus a runnable demo. It's the spine
of a larger portfolio applying relaxation labeling to **markerless motion
capture** and to a **syncretistic, weighted consensus of physical models**.

---

## ▶ Open Chess Maestro (live demo)

Try the interactive Chess Maestro (Maestro) in your browser — no install required.

- Live site: https://rmichaelglover.github.io/hrl-portfolio/

Click the link above to open Maestro (it will load as the site root). You can paste or upload PGNs using the Load panel inside Maestro.

---

## 🖼️ Gallery

**🎞️ The marker tracker, playing out frame-by-frame** — colored dots keep their
identity through the motion, gray ✕ ghosts are rejected to the noise label
(`python make_mocap_gif.py`):

![tracker animation](assets/mocap_tracking.gif)

**🧬 …and a body that heals itself** — morphogenesis as relaxation labeling: an
amputated tail regrows, a wound closes (Michael Levin, in code):

![Morphogenesis](assets/morphogenesis.gif)

**⚖️ The Truth-O-Meter** — claims sliding to vtrue / ish / vfalse and lighting up
as the relaxation labeling iterates (`python make_consensus_viz.py`):

| Physics claims | Chess maxims |
|---|---|
| ![physics consensus](assets/consensus_physics.gif) | ![chess consensus](assets/consensus_chess.gif) |

**🌌 …across the cosmos** — relativity, quantum gravity, and the dark sector
weighted by how proven each is (the speculative frontier rests honestly at `ish`):

![Cosmic consensus](assets/quantum_consensus.gif)

**🌀 …and tasting incompleteness** — Gödel's theorems, chess solvability, and a
little Kierkegaard; the self-referential claims stay pinned at `ish`:

![Gödel incompleteness](assets/godel_consensus.gif)

**🗺️ …and a self-organizing map** learning the topology of that truth-space —
the net unfolds to drape the manifold, undecidable claims at its peak:

![SOM unfolding](assets/som_unfold.gif)

**🕊️ …and the leap of faith** — where Gödel's chasm meets Kierkegaard: refuse to
cross and starve, or leap by the absurd and flourish:

![The leap of faith](assets/leap_of_faith.gif)

One engine, many worlds — every chart is real output (`python make_figures.py`,
full set in [`assets/`](assets/README.md)):

| 🎯 Core | 🕺 Mocap tracking |
|---|---|
| ![core](assets/core_convergence.png) | ![mocap](assets/mocap_tracks.png) |
| **⚛️ Physics consensus** | **♟️ Chess maxims** |
| ![consensus](assets/consensus_physics.png) | ![chess](assets/chess_maxims.png) |

## ♟️ Applied: Whimsy-Chess

The same engine, [played for fun](whimsy-chess/README.md) — a narrated, musical,
emoji chess studio (the **Chess Maestro** PWA + a **Vim** version). The terrain
overlay *is* relaxation-labeling board segmentation; the role overlay *is* the
HRL labeler; and the [chess-maxims demo](examples/chess_maxims_demo.py) grades
the book's rules of thumb against real games.

![Chess Maestro](whimsy-chess/media/maestro_kadas.gif)

→ **[Browse the whimsy-chess showcase »](whimsy-chess/README.md)**

## 🧬 Morphogenesis — the engine grows a body

The circle closes. The same `RelaxationLabeler` that tracks markers, grades
theories, and tastes incompleteness now **regenerates a body** — Michael Levin's
picture of morphogenesis cast as relaxation labeling:

- **cells** are the objects, on a grid
- their **anatomical region** is the label (head / trunk / tail)
- **bioelectric gap-junction coupling** is the compatibility kernel — adjacent
  cells want to share an identity
- a coarse **pattern memory** (the blurred target morphology) is the respected
  prior — Levin's bioelectric setpoint

Wound the creature — punch a hole, or amputate the tail — and relaxation
propagates identity inward from the intact boundary, guided by the memory, until
the form grows back. Interior wounds heal to **100%**; an amputated tail regrows
**~88%** from boundary + memory alone.

```bash
python examples/morphogenesis_demo.py
```

![Morphogenesis — a body heals itself](assets/morphogenesis.gif)

## 🔬 From the original research

The clean core in this repo is the distilled version of a longer body of work —
relaxation labeling applied to chess-piece roles, 3-D fiducial correspondence,
and more. Here is the **real role-labeler converging**: the Hummel–Zucker
strength of each piece's winning role climbing over 40 iterations (some pieces
commit fast, the runner takes its time), and the role-compatibility heatmap that
drives it.

| Strength over iterations | Role compatibility |
|---|---|
| ![role strength over time](assets/research/role_strength_over_time.png) | ![role compatibility](assets/research/role_compatibility_heatmap.png) |

## What makes this core different

Classic relaxation labeling (Rosenfeld–Hummel–Zucker) has two well-known
failure modes. This implementation fixes both:

- **Priors that are respected, not just seeded.** A naive labeler uses the
  prior only as iteration 0 and then lets the field wash it out — which can
  collapse every object onto one popular label. Here the prior is folded into
  the multiplicative base of *every* update. `prior_strength` slides from
  classic Hummel–Zucker (`0.0`) to a Bayesian "posterior ∝ prior × evidence"
  update (`1.0`).
- **A noise label for robustness.** An optional trailing "none of the above"
  class absorbs objects that are incompatible with the rest of the field —
  outliers, spurious detections, ghost markers — instead of forcing them into a
  wrong label. It doubles as a regularizer against over-confident labelings.

## Install

```bash
pip install -e .          # numpy is the only runtime dependency
```

## Use

```python
import numpy as np
from hrl import RelaxationLabeler, pairwise_distance_compatibility

# measured points (objects) and model markers (labels)
compat = pairwise_distance_compatibility(measured_points, model_markers, sigma=0.05)

result = RelaxationLabeler(
    compat,
    prior=None,        # or an [n_objects, n_labels] array of beliefs
    noise=True,        # add the "unlabeled" escape hatch
    prior_strength=0.5,
).run()

result.assignments     # object -> label index, or -1 for noise/unlabeled
result.confidence      # winning strength per object
result.strengths       # full per-object label distribution
```

## Demo

```bash
python examples/core_demo.py
```

```
1) MARKER CORRESPONDENCE  (motion-capture flavor)
   converged in 19 iterations
   measured point 0 -> r-shoulder  (0.57)  [OK]
   measured point 1 -> head        (0.57)  [OK]
   measured point 2 -> pelvis      (0.57)  [OK]
   measured point 3 -> l-shoulder  (0.57)  [OK]

2) NOISE LABEL  (an outlier is quarantined, not mislabeled)
   measured point 4 -> ** NOISE / unlabeled **

3) RESPECTED PRIOR  (a weak nudge settles a perfect tie)
   prior nudges object 0 toward label 0  -> assignment [0, 1]
   prior nudges object 0 toward label 1  -> assignment [1, 0]
```

## Motion-capture marker tracking

Single-frame correspondence becomes *tracking* with one addition: **memory,
expressed as a prior.** Each frame, the previous frame's labeled positions
predict where every marker should be now; that prediction is the prior for this
frame. Geometry keeps the constellation self-consistent, memory keeps
identities stable, and the noise label quarantines ghost detections.

```bash
python examples/mocap_tracking_demo.py
```

A rigid 5-marker body rotates and drifts for 30 frames; detections arrive
shuffled, with periodic ghosts and dropouts:

```
real-marker identity  : 146/146 correct (100.0%)
ghosts -> noise label : 4/5 quarantined
identity switches     : 0
```

Every marker holds its identity through the motion — note the two hip tracks
*cross* near the middle without swapping — and the gray ✕ ghosts are sent to
the noise label instead of corrupting a track.

```python
from hrl import track_sequence
assignments = track_sequence(frames, model_markers)   # per frame: detection -> marker id (-1 = noise)
```

## Syncretistic model consensus

Every model is a simplification of the world, so the "true" picture is a
weighted reconciliation of many models against each other and against the
observations we trust most. The same engine does this: **claims are objects,
the labels are the three Trool truth values `{vfalse, ish, vtrue}`**, an
agreement/contradiction web is the compatibility kernel, and a few trusted
observations *anchor* the field and break its sign symmetry.

```bash
python examples/physics_consensus_demo.py
```

Eight physics claims plus one deliberately contested ninth, with only **two**
claims anchored as trusted observations:

```
[ vtrue +0.94]  The speed of light in vacuum is the same for every observer.  <- anchor
[vfalse -0.51]  Light propagates through a stationary luminiferous ether.
[ vtrue +0.48]  Gravity is the curvature of spacetime and propagates at c.
[ vtrue +0.96]  All objects fall at the same rate in a vacuum.  <- anchor
[vfalse -0.48]  Heavier objects fall faster than lighter ones.
[   ish +0.02]  Newtonian gravity predicts planetary orbits accurately.
```

Truth propagates from the two anchors across the whole web — recovering the
modern picture, rejecting the classical errors, and parking the genuinely
regime-limited claim on `ish` (`score ≈ 0`).

The agreement matrix is the only NLP-dependent part, and it is fully
**swappable** — hand-authored, the bundled lexical heuristic, or a real
natural-language-inference / embedding / LLM-judge front-end:

```python
from hrl.consensus import lexical_agreement, relax_truth, anchor_prior, truth_report
agreement = lexical_agreement(sentences)            # raw text -> agreement web
result = relax_truth(agreement, anchor_prior(n, {trusted_idx: VTRUE}))
truth_report(result)                                # per claim: truth + signed score
```

### Real NLP backends

The lexical heuristic is the floor. Two real models drop in as the agreement
provider — same signed-matrix interface, so nothing downstream changes:

- **NLI** (`hrl.nli.NLIAgreement`, `pip install -e '.[nli]'`) — a DeBERTa-v3
  natural-language-inference model reads every claim pair and scores
  `P(entail) − P(contradict)`. Entailing claims pull toward the same truth
  value, contradicting ones toward opposite. Runs locally, offline after the
  one-time model download.
- **Claude LLM-judge** (`hrl.llm_judge`, `pip install -e '.[llm]'` + an API key)
  — `extract_claims_llm` pulls atomic claims out of a *whole paper*, and
  `LLMAgreement` judges them with real world knowledge. The strongest backend
  for abstract or knowledge-heavy claims.

```bash
python examples/paper_consensus_demo.py        # NLI builds the web from raw prose
```

```
NLI-inferred relations (entail = +, contradict = -):
  c0 contradict c3   (-1.00)      # "X reduces mortality"  vs  "X has no effect"
  c3 agree    c4   (+0.98)        # the two null-result claims agree
  ...
anchored claim c1 as a trusted observation (vtrue):
  [ vtrue +0.55]  c0: Compound X significantly reduces patient mortality.
  [vfalse -0.52]  c3: Compound X has no effect on patient mortality.
```

The NLI model inferred the entire agreement web from raw text; relaxation then
propagated truth from one anchored replication across it.

## ### Grading chess theory — the whimsy-chess bridge

The same consensus engine grades **chess rules of thumb**, with the evidence
prior drawn from a corpus of *real games that break the book and win anyway*
(the narrated whimsy-chess study games — Maestro / Vim / Roblox). Maxims are
claims, the labels are `{vtrue, ish, vfalse}`, and the daring wins anchor the
field:

```bash
python examples/chess_maxims_demo.py
```

```
[   ish -0.05]  Control the center with your pawns and pieces.   (REFUTED by every Kadas game)
[ vtrue +0.45]  Develop all your pieces before you attack.
[ vtrue +0.45]  Castle early to keep your king safe.
[   ish -0.05]  Material advantage decides the game.   (REFUTED by Houdini won down ~9 points)
[ vtrue +0.93]  Storm the enemy king with a flank pawn.   (PROVEN by the Kadas wins)
[ vtrue +0.93]  Daring and initiative outweigh following the book.
```

Sound rules hold at `vtrue`; the dogmas the daring games refute relax to `ish`
— rules of thumb with real exceptions. It's the whimsy-chess thesis (creativity
over the engine's book) made quantitative, on the *same* relaxation engine that
labels chess pieces by role and physics claims by truth.

### Real NLP backends

The lexical heuristic is the floor. Two real models drop in as the agreement
provider — same signed-matrix interface, so nothing downstream changes:

- **NLI** (`hrl.nli.NLIAgreement`, `pip install -e '.[nli]'`) — a DeBERTa-v3
  natural-language-inference model reads every claim pair and scores
  `P(entail) − P(contradict)`. Entailing claims pull toward the same truth
  value, contradicting ones toward opposite. Runs locally, offline after the
  one-time model download.
- **Claude LLM-judge** (`hrl.llm_judge`, `pip install -e '.[llm]'` + an API key)
  — `extract_claims_llm` pulls atomic claims out of a *whole paper*, and
  `LLMAgreement` judges them with real world knowledge. The strongest backend
  for abstract or knowledge-heavy claims.

```bash
python examples/paper_consensus_demo.py        # NLI builds the web from raw prose
```

... (rest unchanged)
