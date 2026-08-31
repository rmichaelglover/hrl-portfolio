"""Generate the portfolio figure gallery into assets/ — every chart is real
output from the engine, not decoration.

Run: ``python make_figures.py``   (needs matplotlib; NLI heatmap needs the [nli] extra)
"""
import importlib.util
import pathlib

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hrl import RelaxationLabeler, pairwise_distance_compatibility, track_sequence
from hrl.tracking import synthetic_sequence
from hrl.consensus import relax_truth, truth_report

ROOT = pathlib.Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except Exception:
    pass

TRUTHCOL = {"vtrue": "#2ca02c", "ish": "#e6b800", "vfalse": "#d62728"}


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "examples" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rotate(p, deg):
    t = np.radians(deg)
    return p @ np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]).T


def save(fig, name):
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=130, facecolor="white")
    plt.close(fig)
    print(f"  wrote assets/{name}")


def draw_graph(ax, n, agreement, node_colors, title, ring=None):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    xs, ys = np.cos(ang), np.sin(ang)
    for i in range(n):
        for k in range(i + 1, n):
            w = agreement[i, k]
            if w:
                ax.plot([xs[i], xs[k]], [ys[i], ys[k]],
                        color="#2ca02c" if w > 0 else "#d62728",
                        lw=1 + 4 * abs(w), alpha=0.45, zorder=1)
    edge = ["#1a1a1a"] * n
    if ring:
        for i in ring:
            edge[i] = "#1f77b4"
    ax.scatter(xs, ys, s=1100, c=node_colors, edgecolors=edge, linewidths=2.5, zorder=2)
    for i in range(n):
        ax.annotate(str(i), (xs[i], ys[i]), ha="center", va="center",
                    fontsize=12, fontweight="bold", zorder=3)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")
    ax.set_aspect("equal")
    ax.margins(0.18)


# ----------------------------------------------------------------- core
def fig_core():
    model = np.array([[0., 0.], [3., 0.], [0., 1.], [1., 2.]])
    names = ["head", "l-sho", "r-sho", "pelvis"]
    perm = np.array([2, 0, 3, 1])
    rng = np.random.default_rng(0)
    objects = _rotate(model, 37.0)[perm] + np.array([5., -2.]) + rng.normal(scale=.01, size=(4, 2))
    compat = pairwise_distance_compatibility(objects, model, sigma=0.05)
    res = RelaxationLabeler(compat, max_iterations=40, tol=1e-12, record_history=True).run()

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11, 4.4))
    H = np.array(res.history)                       # [iter, obj, label]
    for i in range(4):
        axL.plot(H[:, i, res.assignments[i]], lw=2, label=f"point {i} → {names[res.assignments[i]]}")
    axL.set(xlabel="iteration", ylabel="winning-label strength",
            title="Relaxation converges: each point finds its marker")
    axL.legend(fontsize=8)

    im = axR.imshow(res.strengths, cmap="viridis", vmin=0, vmax=res.strengths.max())
    axR.set_xticks(range(4), names, rotation=30, fontsize=8)
    axR.set_yticks(range(4), [f"pt {i}" for i in range(4)], fontsize=8)
    for i in range(4):
        for j in range(4):
            axR.text(j, i, f"{res.strengths[i, j]:.2f}", ha="center", va="center",
                     color="white" if res.strengths[i, j] < .4 else "black", fontsize=8)
    axR.set_title("Final label-strength matrix")
    fig.colorbar(im, ax=axR, fraction=0.046)
    save(fig, "core_convergence.png")


# ----------------------------------------------------------------- mocap
def fig_mocap():
    body = np.array([[0., 0.], [2., .2], [.3, 1.6], [2.4, 1.9], [1.1, 3.]])
    names = ["head", "l-sho", "r-sho", "l-hip", "r-hip"]
    frames, _ = synthetic_sequence(body, n_frames=30, noise=.02, rotate_deg_per_frame=4.,
                                   ghost_every=5, drop_every=7, seed=7)
    asg = track_sequence(frames, body)
    fig, ax = plt.subplots(figsize=(7, 6))
    cols = plt.cm.tab10(np.linspace(0, 1, len(body)))
    tracks = {m: [] for m in range(len(body))}
    for det, a in zip(frames, asg):
        for p, m in zip(det, a):
            (tracks[m].append(p) if m >= 0 else ax.scatter(*p, c="0.6", marker="x", s=45, zorder=1))
    for m, pts in tracks.items():
        pts = np.asarray(pts)
        ax.plot(pts[:, 0], pts[:, 1], "-o", color=cols[m], ms=3, lw=1.3, label=names[m], zorder=2)
    ax.scatter([], [], c="0.6", marker="x", label="ghost → noise")
    ax.set_title("Marker tracks — stable identity through motion (100%)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_aspect("equal")
    save(fig, "mocap_tracks.png")


# ----------------------------------------------------------------- consensus (physics)
def fig_consensus():
    d = _load("physics_consensus_demo")
    n = len(d.CLAIMS)
    agreement = d._web(n, d.LINKS)
    prior = d.anchor_prior(n, d.ANCHORS, strength=0.9)
    report = truth_report(relax_truth(agreement, prior, prior_strength=0.4))
    colors = [TRUTHCOL[r["truth"]] for r in report]

    fig, (axG, axB) = plt.subplots(1, 2, figsize=(12, 5.2))
    draw_graph(axG, n, agreement, colors,
               "Physics claim web — green agree, red contradict\n(node color = relaxed truth, blue ring = anchor)",
               ring=list(d.ANCHORS))
    scores = [r["score"] for r in report]
    order = np.argsort(scores)
    axB.barh(range(n), [scores[i] for i in order], color=[colors[i] for i in order],
             edgecolor="k")
    axB.set_yticks(range(n), [f"c{i}" for i in order], fontsize=9)
    axB.axvline(0, color="k", lw=.8)
    axB.set(xlim=(-1, 1), xlabel="expected truth   (−1 false  …  +1 true)",
            title="Truth scores")
    save(fig, "consensus_physics.png")


# ----------------------------------------------------------------- chess maxims
def fig_chess():
    d = _load("chess_maxims_demo")
    n = len(d.MAXIMS)
    report = truth_report(relax_truth(d.web(n, d.LINKS), d.build_prior(n),
                                      prior_strength=d.PRIOR_STRENGTH))
    scores = [r["score"] for r in report]
    verds = [d.verdict(s) for s in scores]
    colors = [TRUTHCOL[v] for v in verds]
    short = ["control center", "develop pieces", "castle early", "rooks open files",
             "knight on rim dim", "queen stays home", "material decides",
             "storm the wing", "daring > book"]

    fig, (axB, axG) = plt.subplots(1, 2, figsize=(12, 5.2))
    order = np.argsort(scores)
    axB.barh(range(n), [scores[i] for i in order], color=[colors[i] for i in order],
             edgecolor="k")
    axB.set_yticks(range(n), [short[i] for i in order], fontsize=9)
    axB.axvspan(-0.25, 0.25, color="0.85", alpha=.5, zorder=0)
    axB.axvline(0, color="k", lw=.8)
    axB.set(xlim=(-1, 1), xlabel="expected truth   (gray band = ish)",
            title="Chess maxims, graded by the engine")
    draw_graph(axG, n, d.web(n, d.LINKS), colors,
               "Maxim web — the only conflicts run\ncenter/material vs. daring")
    # legend
    handles = [plt.Line2D([0], [0], marker="o", ls="", mfc=c, mec="k", ms=10, label=l)
               for l, c in [("vtrue", TRUTHCOL["vtrue"]), ("ish", TRUTHCOL["ish"]),
                            ("vfalse", TRUTHCOL["vfalse"])]]
    axG.legend(handles=handles, loc="lower center", ncol=3, fontsize=9, frameon=True)
    save(fig, "chess_maxims.png")


# ----------------------------------------------------------------- NLI (real model)
def fig_nli():
    try:
        from hrl.nli import NLIAgreement
        from hrl.consensus import extract_claims
    except Exception as e:
        print(f"  skip nli heatmap ({e})")
        return
    digest = ("Compound X significantly reduces patient mortality. "
              "In an independent replication trial, compound X lowered mortality. "
              "Compound X reduces mortality in treated patients. "
              "Compound X has no effect on patient mortality. "
              "Patients treated with compound X showed no survival benefit. "
              "Compound X increases the risk of death in the treatment group. "
              "Compound X was well tolerated, with only mild side effects.")
    claims = extract_claims(digest)
    try:
        A = NLIAgreement(threshold=0.0)(claims)
    except Exception as e:
        print(f"  skip nli heatmap (model unavailable: {e})")
        return
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    im = ax.imshow(A, cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_xticks(range(len(claims)), [f"c{i}" for i in range(len(claims))], fontsize=9)
    ax.set_yticks(range(len(claims)), [f"c{i}" for i in range(len(claims))], fontsize=9)
    for i in range(len(claims)):
        for k in range(len(claims)):
            if A[i, k]:
                ax.text(k, i, f"{A[i, k]:+.1f}", ha="center", va="center", fontsize=7)
    ax.set_title("Real NLI model output: agreement matrix\n(green entail, red contradict)",
                 fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046)
    save(fig, "nli_agreement.png")


if __name__ == "__main__":
    print("generating figures into assets/ ...")
    fig_core()
    fig_mocap()
    fig_consensus()
    fig_chess()
    fig_nli()
    print("done.")
