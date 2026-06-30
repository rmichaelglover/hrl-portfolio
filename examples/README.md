# 🎬 `examples/` — runnable demos

Each demo is a self-contained story you can run in seconds. Pictures below are
real output; regenerate the gallery with `python make_figures.py`.

---

## 🎯 `core_demo.py` — the three core behaviors
```bash
python examples/core_demo.py
```
Correspondence recovery · the noise label quarantining an outlier · a weak prior
settling a perfect tie.

![core](../assets/core_convergence.png)

---

## 🕺 `mocap_tracking_demo.py` — marker tracking
```bash
python examples/mocap_tracking_demo.py
```
A rigid body rotates and drifts for 30 frames; detections arrive shuffled, with
ghosts and dropouts. **The prior is the tracker's memory** — every marker keeps
its identity, ghosts go to noise.

![mocap](../assets/mocap_tracks.png)

**🎞️ Watch it play out** (`python make_mocap_gif.py`):

![mocap animation](../assets/mocap_tracking.gif)

---

## 🛏️ `body_pos_demo.py` — sleep posture from an accelerometer
```bash
python examples/body_pos_demo.py
```
A wearable's gravity vector is labeled with a body position each sample. **The
prior is absolute fit** (which way is down?) — essential, because the six
canonical directions form a symmetric octahedron that pure geometry can't
orient. Roll-overs leave the gravity sphere and go to noise. **34/34 postures,
6/6 roll-overs quarantined.**

![body position](../assets/body_pos.png)

**🎞️ Watch it settle** (`python make_body_pos_gif.py`):

![body position animation](../assets/body_pos.gif)

---

## ⚛️ `physics_consensus_demo.py` — claims → truth
```bash
python examples/physics_consensus_demo.py
```
Eight physics claims + one contested; two anchored observations propagate truth
across the whole agreement web → **5 vtrue / 1 ish / 3 vfalse.**

![consensus](../assets/consensus_physics.png)

**⚖️ Truth-O-Meter, animated** (`python make_consensus_viz.py`):

![physics meter](../assets/consensus_physics.gif)

---

## ♟️ `chess_maxims_demo.py` — grading chess theory
```bash
python examples/chess_maxims_demo.py
```
The **whimsy-chess bridge**: the book's maxims graded against your daring wins.
Sound rules stay `vtrue`; the dogmas your Kádas games refute relax to `ish`.

![chess](../assets/chess_maxims.png)

**⚖️ Truth-O-Meter, animated** — the maxims settle as the engine iterates:

![chess meter](../assets/consensus_chess.gif)

---

## 🧠 `paper_consensus_demo.py` — real NLI from raw prose
```bash
pip install -e '.[nli]' && python examples/paper_consensus_demo.py
```
A DeBERTa-v3 NLI model reads raw text, infers the entire contradiction web, and
relaxation settles it from one anchored replication.

![nli](../assets/nli_agreement.png)

➡️ Full gallery: [`../assets/`](../assets/README.md)
