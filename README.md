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

![Recovered marker tracks](examples/mocap_tracks.png)

Every marker holds its identity through the motion — note the two hip tracks
*cross* near the middle without swapping — and the gray ✕ ghosts are sent to
the noise label instead of corrupting a track.

```python
from hrl import track_sequence
assignments = track_sequence(frames, model_markers)   # per frame: detection -> marker id (-1 = noise)
```

## Test

```bash
pytest            # or: python tests/test_core.py
```

## Layout

```
hrl/
  core.py       RelaxationLabeler — the prior-respecting, noise-aware engine
  kernels.py    pairwise_distance_compatibility — the marker-correspondence kernel
  tracking.py   temporal_prior + track_sequence — correspondence across time
examples/
  core_demo.py            the three core behaviors
  mocap_tracking_demo.py  marker tracking through motion, ghosts, dropouts
tests/
  test_core.py      correspondence recovery, noise quarantine, prior tie-break
  test_tracking.py  identity stability through motion / shuffle / ghosts
```

## Background

Relaxation labeling assigns labels to objects by iteratively maximizing the
mutual support among compatible assignments — a parallel, soft constraint
solver. This core grew out of work on **3-D fiducial / marker correspondence
for motion capture**, where the task is to decide which measured point is which
named marker using only the geometry the points share.

> A. Rosenfeld, R. Hummel, S. Zucker. *Scene labeling by relaxation
> operations.* IEEE Trans. SMC, 1976.
> R. Hummel, S. Zucker. *On the foundations of relaxation labeling processes.*
> IEEE Trans. PAMI, 1983.

## License

MIT — see [LICENSE](LICENSE).
