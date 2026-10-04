# To Cure Cancer: The Virtual Body

Michael Emanuel Glover. Developed in dialogue with Codex. 4 October 2026. Independent computational research dissertation.

80 pages; 22,280 words; 64 distinct color figures, including measured and analytic 3D views. First-person argument, rigorous scoped mathematics, measured assay prediction, nested-cell repairs and synthetic body-model stability. It does not establish a clinical cure.

Read VIRTUAL-BODY-DISSERTATION.pdf, VIRTUAL-BODY-DISSERTATION.txt or MANUSCRIPT.md. Page-ledger.json maps the eighty pages to their data and figures. Data products are under data/. The companion COMPUTATIONAL-SOURCE.zip contains the executable experiments and audit results. Raw private drive inventory and physiology metadata are excluded.

Rebuild with Python 3.10+, NumPy, pandas, SciPy, scikit-learn, Matplotlib, pdflatex and pdfinfo. Python versions are pinned in the companion computational archive. LaTeX requires geometry, lmodern, microtype, amsmath, amssymb, graphicx, xcolor, booktabs, tabularx, hyperref and fancyhdr.

The public Doench/Azimuth source table is not bundled. Download FC_plus_RES_withPredictions.csv from https://raw.githubusercontent.com/MicrosoftResearch/Azimuth/master/azimuth/data/FC_plus_RES_withPredictions.csv and set VIRTUAL_BODY_CRISPR_DATA to its path. Its SHA-256 must be 97a4fda9481985d5e4ea6b18bb52e17b1c953913fbb901f56a134ec3c31f2972. The original local project cache is recognized when present. Then run:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 generate.py

The figures are generated from archived predictions, trajectories and stability results. Regenerating underlying experiments uses the companion computational source; the highest-scoring historical boosted predictor is not reproduced by these Ridge/HRL grouped benchmarks.
