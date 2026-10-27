# Rotated ellipse detector: measured improvement

The source notebook’s four-stage grid search is reproduced exactly on the original seed-42 scene. Its fitted center is (45.2, 68.0), versus the true (50, 50); it expands the semi-axes to (42.5, 29.8), versus (32, 14). Its algebraic tolerance varies in physical width, and its single-candidate refinement can lock onto clutter. The algorithm is a shrinking grid search; it has no relaxation-labeling updates or Cantor middle-third construction.

## Evaluation

30 synthetic scenes: six conditions × five seeds (42, 7, 19, 83, 101). Conditions: original (150 clutter, noise σ=0.8, rotation 30°), horizontal (0°), near-wrap (177°), noisier (σ=1.6, 60°), more-clutter (300 clutter, σ=0.8, 110°), and stress (500 clutter, σ=1.6, 145°). Every scene has 70 target samples. Ground truth labels enter evaluation and plots only, never fitting.

Boundary RMSE is the root-mean-square nearest-boundary distance from 720 points on the true noiseless ellipse to the fitted ellipse, in scene units. This one-direction metric is accompanied by center, axis, angle, precision, and recall measurements in results.json. A successful fit is defined here as boundary RMSE < 2 units.

| Method | Median boundary RMSE | Worst RMSE | Successes / 30 | Median precision | Median recall |
|---|---:|---:|---:|---:|---:|
| original_grid | 11.880 | 16.531 | 0 | 0.607 | 0.414 |
| all_points | 14.852 | 17.138 | 0 | 0.014 | 0.007 |
| ransac | 0.523 | 12.532 | 22 | 0.819 | 0.979 |
| refined | 0.257 | 12.597 | 22 | 0.833 | 1.000 |

## Methods and assumptions

- Original grid: supplied score, bounds, samples, tie order, and refinement schedule, vectorized for speed.
- All points: direct scikit-image EllipseModel fit without outlier rejection.
- RANSAC: standard five-point random ellipse hypotheses, up to 2,000 trials, using fast Sampson (first-order distance) residuals for hypothesis scoring and a fixed 2.4-unit threshold. This approximation is not exact Euclidean distance, especially far from the boundary.
- Refined: robust local least-squares fitting on consensus points. Each proposed update is accepted only when the sum of exact nearest-boundary squared distances, truncated at 2.4², improves. Exact distances also determine evaluation precision and recall.

The threshold is calibrated to three times the original 0.8-unit noise and held fixed across scenes, including noisier conditions. Model bounds assume the scene’s 0–100 coordinate scale, axes between 4 and 90, centers between −20 and 120, and aspect ratio below 8. RANSAC seeds are fixed for reproduction. The fitters receive no target center, axis lengths, rotation, or point labels. The fixed scene bounds are prior knowledge.

## What improved, and what remains

The improved method recovers the original example and succeeds on 22 of 30 scenes. The local refinement lowers median error but does not rescue any failed scene under the two-unit criterion. RANSAC supplies the main improvement; these results do not demonstrate an HRL-specific or Cantor-specific advantage.

Failures remain concentrated in heavier clutter and higher noise. With few target points relative to clutter, 2,000 random five-point samples may miss a good hypothesis; accidental clutter-supported ellipses can also win the consensus score. A useful next experiment is hypothesis-budget sensitivity and spatial/angular support scoring, followed by partial arcs and structured distractors.

Uniform random clutter is not organic or fractal structure. This benchmark contains one complete ellipse at a known scene scale. It does not validate multiple ellipses, real photographs, partial arcs, circles, extreme aspect ratios, or automatic noise estimation. The original inclusive angle sampling duplicates the noiseless endpoint, and is preserved for comparability.

## Reproduce

```bash
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python3 study.py
python3 -m unittest -v
```

The script regenerates results.json and comparison.png. The report summarizes that recorded run. Four tests cover equivalent ellipse parameterizations, noise-free rotated recovery, source scene reproduction, and recovery amid the original clutter. Exact-distance checks allow a 1e-5 numerical tolerance. The original grid output was additionally compared directly with source notebook cells and matched to 1e-12.

Original notebooks remain unchanged. improved_detector.ipynb is a separate demonstration importing the shared module. The browser explorer displays recorded results; it does not rerun the detector.
