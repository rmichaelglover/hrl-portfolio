# Hyperspace: Physical–Informational Geometry and Anchored Consistency

**All Roads Lead to Home** — Michael Emanuel Glover (Manny Glover), with Cypher.

A 16-page illustrated research note, dated October 8, 2026. A modeling proposal, original derivations of specified finite models, and synthetic numerical experiments. It does not establish new physical dimensions or an empirical theory of human semantics. Established averaging, harmonic, and relaxation-labeling literature is credited in the bibliography.

## Reproduce

Requires Python 3, NumPy, Matplotlib, and pdfLaTeX with AMS, Latin Modern, geometry, microtype, fancyhdr, and hyperref.

```sh
python3 build.py
```

The script reproduces eight figures in PDF and PNG, `metrics.json`, `convergence.csv`, and `results.tex`; compiles twice; and rejects missing glyphs, overfull horizontal/vertical boxes, and unresolved references. The final file is `HYPERSPACE.pdf`.

Numerical assertions check absorption weights, simplex preservation, harmonic residual, the exact small-chain inverse, and the stopping certificate. All calculations use synthetic inputs; seed 20261008. Floating-point tolerances accompany the symbolic derivations rather than substituting for proofs.

Publication checks include page-count verification, text extraction, and rasterized inspection of all pages and enlarged mathematical pages. The companion site presents four figure previews and links to all reproduction files.

## Contents

Physical–informational fibers; typed composition and mixture; Lorentzian causality and a product metric on a spacelike slice; geographic/informational graphs; simplex invariance; stationary means; primitive consensus; anchored block contraction; multiple anchors and hitting probabilities; Dirichlet energy; ternary visualization; nonlinear multiplicative compatibility and exact logit amplification; symmetry limits; periodic and decaying-weight counterexamples; toy network experiments; stopping certificates; first-order sensitivity; a worked home chain; geographic-world applications and held-out evaluation; six bibliography entries.
