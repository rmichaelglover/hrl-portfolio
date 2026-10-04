# Virtual Body Cancer Research Prototype

An initial multiscale research scaffold using Michael Emanuel Glover's existing sparse HRL engine. Synthetic, dimensionless, uncalibrated; not a cancer cure or a patient treatment tool.

Read `RESEARCH-PLAN.md` for equations, provenance, limitations, data sources and the validation programme. Open `report.html` for plots and results.

```sh
python3 -m pip install -r requirements.txt
python3 run.py
python3 verify.py
python3 analyze_extinction.py
python3 check_nested_cells.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 benchmark_existing_crispr.py
python3 build_report.py
```

Python 3.10+; NumPy and Matplotlib. `model.py` implements the coupled three-site model; `run.py` executes four control comparisons, 24 parameter configurations, and a separate HRL annotation ablation. `output/` contains raw trajectories, results and verification. `vendor/hrl_engine.py` is an unchanged local-source snapshot. Do not interpret the fictional input values as clinical dosing.

## Expanded audit and measured-data calculations

Read `AUDIT-RESULTS.md`. The measured CRISPR dataset is not bundled. Set `VIRTUAL_BODY_CRISPR_DATA` to a local copy of `FC_plus_RES_withPredictions.csv` from the MicrosoftResearch/Azimuth repository, with the SHA-256 listed in the audit report. The benchmark also recognizes the original local project cache. The portable sequence-feature extraction and isolated audited HRL2026 snapshot are included under `vendor/`. Raw drive inventory and private physiology metadata are excluded from the source archive.

`check_nested_cells.py` additionally reports the original project failure when the original local path exists; the repaired snapshot is portable. `analyze_extinction.py` gives local stability and reserve-feasibility results restricted to constant exposure in the synthetic model.
