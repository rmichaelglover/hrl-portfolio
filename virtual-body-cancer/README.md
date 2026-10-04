# Virtual Body Cancer Research Prototype

An initial multiscale research scaffold using Michael Emanuel Glover's existing sparse HRL engine. Synthetic, dimensionless, uncalibrated; not a cancer cure or a patient treatment tool.

Read `RESEARCH-PLAN.md` for equations, provenance, limitations, data sources and the validation programme. Open `report.html` for plots and results.

```sh
python3 -m pip install -r requirements.txt
python3 run.py
python3 verify.py
```

Python 3.10+; NumPy and Matplotlib. `model.py` implements the coupled three-site model; `run.py` executes four control comparisons, 24 parameter configurations, and a separate HRL annotation ablation. `output/` contains raw trajectories, results and verification. `vendor/hrl_engine.py` is an unchanged local-source snapshot. Do not interpret the fictional input values as clinical dosing.
