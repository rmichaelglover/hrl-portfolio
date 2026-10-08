# HRL Lab: live relaxation inspector

The handwritten-digit experiment shows its images beside the exact numeric update. Click a digit, use the sample selector, or follow a neighbor link. Pause, step, replay the same seeds, change speed, or select new random seeds. Small screens stack the panels.

The inspector shows all five labels: prior, previous strength, raw neighbor support, row-minmax scaled support, next normalized strength, and signed change. Neighbor vectors are from the same previous state used for the displayed update. Plots show the selected sample's complete strength history and maximum absolute change across all samples. Mean entropy excludes the five seed samples.

`relaxation.js` implements the page's existing pairwise update without changing its prior exponent (0.6 for digits), graph, compatibility, or data. Truth labels enter only the five seed priors and evaluation. One-hot priors anchor those seeds. No neural model or remote computation is involved. The inspector concerns the digit experiment; the other demos keep their existing playback.

Numerical convergence means a maximum change below 1e-6 for five successive updates. Automatic playback stops there or at 500 steps. It does not equate convergence with correctness. Ties within 1e-10 have no unique prediction, use gray frames, and count separately from correct unique predictions. Strengths are not calibrated probabilities.

The comparison is nearest **labeled seed** by Euclidean pixel distance, using the identical seed set. Both accuracy counts exclude the five seeds (35 evaluation samples). Neighbor relations may involve all 40 images; this is a small transductive demonstration, not a benchmark proving superiority. Baseline distance ties choose the first seed in the displayed seed-set order.

Run `node hrl-lab/test.cjs` for reference-equivalence, support arithmetic, normalization, fixed seeds, baseline, and convergence checks. Serve the portfolio at port 8769 and run `python3 hrl-lab/browser_check.py` with Chrome and Python websocket-client available. The browser check covers all controls, digit/neighbor selection, numerical stop, and layouts at 320, 390, 720, 820, 821, and 1280 pixels. It also accepts a page URL as its first argument for live verification. Screenshots are written to `/tmp/hrl-lab-desktop.png` and `/tmp/hrl-lab-mobile.png`.
