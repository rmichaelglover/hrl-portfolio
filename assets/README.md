# 🖼️ Gallery

Every figure here is **real output from the engine** — regenerate them all with
`python make_figures.py` from the repo root.

---

## 🎯 Core — relaxation labeling
![core](core_convergence.png)

*Left:* each measured point's winning-label strength climbing to a confident,
stable assignment. *Right:* the final object × marker strength matrix — the
permuted-diagonal lights up because every point found its true marker.

---

## 🕺 Motion-capture marker tracking
![mocap](mocap_tracks.png)

Five markers on a rigid body, rotating and drifting for 30 frames with shuffled
detections, ghosts, and dropouts. Each colored track holds a **stable identity**
(the two hip tracks even cross without swapping); the gray ✕ ghosts are routed
to the noise label. **146/146 identity, 0 switches.**

**🎞️ Animated, frame-by-frame** (`python make_mocap_gif.py`):

![mocap animation](mocap_tracking.gif)

---

## 🛏️ Body-position labeling
![body position](body_pos.png)

*Left:* a wearable accelerometer's gravity vector lives on the gravity sphere
and snaps to one of six canonical postures (colored anchors); roll-over spikes
fly off the sphere and flash gray ✕ to the noise label. *Right:* the night's
hypnogram, labeled by relaxation — **100% posture, every roll-over quarantined.**
The absolute-fit prior is essential: the canonical directions form a symmetric
octahedron, so without it the geometry alone collapses opposite axes together.

**🎞️ Animated, settling over iterations** (`python make_body_pos_gif.py`):

![body position animation](body_pos.gif)

---

## ⚛️ Physics consensus
![consensus](consensus_physics.png)

The claims as a graph — **green = agree, red = contradict**, blue-ringed nodes
are the two anchored observations. From those anchors, relaxation propagates
truth across the whole web and sorts every claim into 🟢 `vtrue` / 🟡 `ish` /
🔴 `vfalse` (bars, right).

**⚖️ Physics Truth-O-Meter** — and animated, claims lighting up as it iterates
(`python make_consensus_viz.py`):

![physics meter](truthometer_physics.png)
![physics gif](consensus_physics.gif)

---

## ♟️ Chess maxims — the whimsy-chess bridge
![chess](chess_maxims.png)

The book's rules of thumb, graded against a corpus of **daring wins that break
the book and win anyway**. Sound rules stay 🟢 `vtrue`; the dogmas your Kádas
wins refute ("control the center", "material decides") relax into the 🟡 `ish`
band. Right: the conflict graph — the only tensions run *center/material vs.
daring*.

**⚖️ Chess Truth-O-Meter** — static, and animated as the verdicts settle:

![chess meter](truthometer_chess.png)
![chess gif](consensus_chess.gif)

---

## 🧠 Real NLI model
![nli](nli_agreement.png)

Raw output of a **DeBERTa-v3 NLI model**: the agreement matrix it infers from
raw prose (🟩 entail, 🟥 contradict). This is what feeds the consensus engine
when you point it at real text.
