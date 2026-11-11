#!/usr/bin/env python3
"""Reproduce the synthetic lithium demonstration and its four-panel figure."""
import csv
import json
from pathlib import Path
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
raw = subprocess.check_output([str(ROOT / "build/lithium_demo")], text=True)
(OUT / "trajectories.csv").write_text(raw)
rows = list(csv.DictReader(line for line in raw.splitlines() if not line.startswith("#")))
for row in rows:
    for key in row:
        if key != "profile":
            row[key] = float(row[key])

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 2, figsize=(11, 8), layout="constrained")
colors = {0.0: "#555555", 0.5: "#368884", 1.0: "#4466a1", 2.0: "#b65738"}
for initial, color in colors.items():
    selected = [r for r in rows if r["profile"] == "coupled" and r["external_initial_li_mm"] == initial]
    times = [r["time_s"] for r in selected]
    label = f"Initial external Li: {initial:g} mM"
    for ax, key in ((axes[0, 0], "free_li_inside_mm"),
                    (axes[0, 1], "productive_fraction"),
                    (axes[1, 0], "inositol_mm"),
                    (axes[1, 1], "response_proxy")):
        ax.plot(times, [r[key] for r in selected], color=color, label=label)
null = [r for r in rows if r["profile"] == "uncoupled" and r["external_initial_li_mm"] == 1]
axes[1, 1].plot([r["time_s"] for r in null], [r["response_proxy"] for r in null],
               "--", color="#999999", label="Uncoupled: all exposures overlap")
labels = [("A  Passive salt exchange", "Free intracellular Li (mM)"),
          ("B  Competing metal binding", "Productive Mg-bound site fraction"),
          ("C  IMPase-linked hydrolysis", "Inositol (mM)"),
          ("D  Synthetic downstream coupling", "Response proxy (dimensionless)")]
for ax, (title, ylabel) in zip(axes.flat, labels):
    ax.set(title=title, xlabel="Simulation time (s)", ylabel=ylabel)
    ax.grid(alpha=0.15)
axes[0, 0].legend(fontsize=8)
axes[1, 1].legend(fontsize=8)
fig.suptitle("Lithium across scales: an illustrative conserved biochemical model\n"
             "Synthetic parameters and timescales; response proxy is not clinical efficacy", fontsize=13)
fig.savefig(OUT / "lithium-model.png", dpi=180)
fig.savefig(OUT / "lithium-model.pdf", metadata={"CreationDate": None, "ModDate": None})
final = [r for r in rows if r["time_s"] == 60]
summary = {"parameter_status": "illustrative, not fitted",
           "model_time_seconds": 60, "final_states": final}
baseline = next(r["response_proxy"] for r in final
                if r["profile"] == "coupled" and r["external_initial_li_mm"] == 0)
exposed = next(r["response_proxy"] for r in final
               if r["profile"] == "coupled" and r["external_initial_li_mm"] == 1)
summary["declared_reference_range_examples"] = []
for lower, upper in ((1.35, 1.42), (1.45, 1.50)):
    distance = lambda value: max(lower - value, 0, value - upper)
    summary["declared_reference_range_examples"].append({
        "range": [lower, upper], "unexposed_distance": distance(baseline),
        "exposed_distance": distance(exposed),
        "interpretation": "synthetic evaluation convention, not clinical benefit or harm"})
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
