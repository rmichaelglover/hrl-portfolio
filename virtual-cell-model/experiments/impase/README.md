# Empirical IMPase assays

Start with [REPORT.md](REPORT.md) for findings, assumptions, equations, fitted
parameters, withheld predictions, and the experimental route toward human IMPA1.

- [Four-page illustrated PDF](results/IMPASE_ASSAY_REPORT.pdf)
- [Calibration figure](results/fig01-calibration.png)
- [Model comparison](results/fig02-model-comparison.png)
- [Digitization sensitivity](results/fig03-digitization-sensitivity.png)
- [Digitized measurements](data/digitized.csv) and [provenance](data/provenance.json)
- [Fit results](results/fit-results.json) and [held-out predictions](results/held-out-predictions.csv)

The dataset contains 30 manually digitized measurements from a recombinant
bovine enzyme study. The analysis is conditional on those assays. It does not
replace the synthetic lithium model or fit a Person's mood.

Build the project and run its seven CTest suites, then run `analyze.py` from the
project root. See the report for commands. Python dependencies and used versions
are in `requirements.txt`. Five additional Python checks cover extraction,
held-out concentration, independent linear fitting, synthetic parameter
recovery, and C++/Python agreement.

Run `python3 experiments/impase/reproduce.py` from the project root to rebuild,
check, analyze and create a complete source/data/results ZIP with a SHA-256
manifest. The earlier manuscript's frozen experiment snapshot is independent
of this package.
