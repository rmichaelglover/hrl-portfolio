"""A self-organizing map of the engine's truth-assignment space.

Run: ``python examples/som_demo.py``

The relaxation engine places every claim somewhere in label space (how much
vfalse / ish / vtrue). We collect those assignment vectors from all three
consensus demos (physics, chess, Gödel), project them to 2-D — truth score vs.
ish-mass — and train a SOM to learn the manifold. It self-organizes into
contiguous vtrue / ish / vfalse territory, with the undecidable claims at the
arch's peak. A model learning the shape of the engine's own output.
"""
import importlib.util
import pathlib

import numpy as np

from hrl.consensus import relax_truth
from hrl.som import SelfOrganizingMap

ROOT = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def strengths_for(name):
    d = _load(name)
    claims = getattr(d, "MAXIMS", None) or getattr(d, "CLAIMS", None)
    n = len(claims)
    web = d.web if hasattr(d, "web") else d._web
    if hasattr(d, "build_prior"):
        prior, ps = d.build_prior(n), getattr(d, "PRIOR_STRENGTH", 0.4)
    else:
        prior, ps = d.anchor_prior(n, d.ANCHORS, strength=0.9), 0.4
    res = relax_truth(web(n, d.LINKS), prior, prior_strength=ps)
    p = res.strengths[:, :3]
    return p / p.sum(axis=1, keepdims=True)


def assignment_points():
    """[N, 2] points: x = truth score (vtrue−vfalse), y = ish-mass."""
    P = np.vstack([strengths_for(n) for n in
                   ("physics_consensus_demo", "chess_maxims_demo", "godel_consensus_demo")])
    return np.column_stack([P[:, 2] - P[:, 0], P[:, 1]])


def main():
    data = assignment_points()
    som = SelfOrganizingMap(grid=(6, 6), dim=2, seed=0)
    before = som.quantization_error(data)
    som.train(data, epochs=40)
    after = som.quantization_error(data)

    print("=" * 70)
    print("Self-organizing map of the engine's truth-assignment space")
    print("=" * 70)
    print(f"  {len(data)} claim-assignments from physics + chess + Gödel demos")
    print(f"  quantization error:  {before:.3f}  ->  {after:.3f}   "
          f"({100 * (1 - after / before):.0f}% tighter)")

    # which truth-region does each SOM node settle into?
    regions = {"vtrue": 0, "ish": 0, "vfalse": 0}
    for i in range(som.gw):
        for j in range(som.gh):
            x = som.weights[i, j, 0]
            regions["vtrue" if x > 0.25 else "vfalse" if x < -0.25 else "ish"] += 1
    print(f"  the {som.gw}x{som.gh} map self-segments into truth territory: "
          f"{regions['vfalse']} vfalse · {regions['ish']} ish · {regions['vtrue']} vtrue nodes")
    print("  competitive learning + neighborhood coherence — the same idea as")
    print("  relaxation labeling, now mapping the engine's own assignment space.")


if __name__ == "__main__":
    main()
