# Executed drive audit and new calculations

4 October 2026. Michael Emanuel Glover research materials, examined and calculated with Codex.

## Search coverage

Enumerated **880,934 files** in accessible `/home`, `/media`, `/mnt`, `/opt`, `/srv` and `/data` roots where present. Filename search returned 128 cancer/virtual-cell/perturbation-related candidates and 58 biomedical-format candidates. Scanned **45,884 text/code/table files**, at most 2 MB each, yielding 6,324 keyword matches, predominantly third-party medical-imaging software. There were 35 inventory traversal/stat errors and zero read errors in the selected content scan.

This is not a claim to read every byte of the physical drive. Credential stores, browser profiles, conversation stores, dependency caches and several installed-tool directories were excluded. Archives and most binary formats were not decoded. A project-referenced CRISPR dataset cache was then specifically inspected. Raw inventory paths and private physiology metadata are retained locally in `audit/`, excluded from the public source archive.

The broader scan found the HRL2026 nested virtual-cell implementation, a real cached CRISPR assay table, the associated prior prediction experiments, and a local copy of Bunne et al.'s virtual-cell perspective. The local paper is arXiv:2409.11654v2, 14 October 2024; it is a research perspective, not a dataset or an experimentally validated cure. Cancer-related terms also occur in clinical sleep-study metadata; those records are not a cancer-intervention dataset and were not used, copied or published. Third-party tumor-navigation and DICOM examples do not establish therapeutic efficacy.

## 1. Real-data CRISPR benchmark

The existing cached Doench/Azimuth table contains **5,310 assay rows**, **4,379 distinct sequences**, and **17 target genes**. The measured target is the provided `score_drug_gene_rank`, an assay rank normalized within drug/gene groups. This does not measure whole-body tumor eradication or healthy-tissue safety. Source: [Doench et al., Nature Biotechnology (2016)](https://doi.org/10.1038/nbt.3437).

Dataset SHA-256:

```
97a4fda9481985d5e4ea6b18bb52e17b1c953913fbb901f56a134ec3c31f2972
```

The previous row-random split has **271 distinct test sequences also present in training**, among 1,034 distinct test sequences. Its experiment log repeatedly uses the same test metric to decide which model to keep. Those historical metrics are exploratory, not an untouched final evaluation.

This new calculation uses fixed five-fold group splits: sequence-disjoint and gene-disjoint. Train and test sets are checked for both group overlap and identical-sequence overlap. The existing model's 25 annotation/drug/gene/stacking columns are discarded. This includes the precomputed `predictions` field, whose training provenance was not established. Sequence-only features are verified independent of annotation providers, and the portable extraction exactly matches the original on all 5,310 rows.

Baselines are a one-hot Ridge model and a Ridge model using 968 existing sequence features. The HRL extension uses eight assay-rank bins with a sequence-similarity graph, training-label anchors and held-out feature-derived priors. Feature scaling is fitted on training rows only. The feature-only graph is transductive: it includes held-out input sequences, never their assay labels. Fixed parameters were used without new hyperparameter searches. All ten HRL fits converged.

| Model | Sequence-disjoint pooled Spearman | Gene-disjoint pooled Spearman |
|---|---:|---:|
| One-hot Ridge | 0.395318 | 0.388453 |
| Existing sequence features + Ridge | 0.479858 | 0.400323 |
| Existing sequence features + HRL graph | 0.480544 | 0.403291 |

The HRL point estimates are slightly higher than the engineered Ridge baseline. These small differences do not establish statistically significant improvement. Fold scores and out-of-fold predictions are supplied. These are new exploratory evaluations of an already available dataset, not independent laboratory validation and not reproductions of the original highest-scoring boosted model.

Executed code: `benchmark_existing_crispr.py`. Outputs: `output/crispr-benchmark.json`, the two out-of-fold CSVs, and `output/crispr-benchmark.png`.

## 2. Nested virtual-cell execution and repairs

The original `Code/hrl2026/python/hrl2026/virtual_cell.py` fails on `step()` with:

```
AttributeError: 'Membrane' object has no attribute 'ish_step'
```

An isolated audited snapshot in `vendor/hrl2026_audited/` makes four explicit repairs:

1. Compute the missing entropy observation from the current categorical state; no undocumented membrane dynamics are invented.
2. Normalize nonnegative categorical weights before computing Shannon entropy; reject invalid weights.
3. Copy the old state before in-place mutation so the reported change is meaningful.
4. Give abstention its own code `-2`, distinct from the certain negative category `-1`.

A **seven-node, three-level hierarchy** ran ten recursive steps. Checks passed for child step propagation, finite nonnegative distributions, unit row mass, normalized entropy, nonzero initial state-change reporting and distinct abstention. Original project files are unchanged. These are categorical relaxation diagnostics, not simulations of physical human cells. The snapshot's nested updates do not yet implement measured intercellular signaling or bidirectional biological coupling.

Executed code: `check_nested_cells.py`. Output: `output/nested-cell-checks.json`.

## 3. Tumor-free stability calculation for the synthetic body model

For fixed systemic exposure C, the tumor-free equilibrium has E=0, O=1 and:

```
H_i* = repair / (repair + toxicity * penetration_i * C).
```

The tumor invasion Jacobian is block triangular. Its diagonal clone blocks are:

```
A_sensitive(C) = diag(growth*(1-mutation) - kill_sensitive*penetration*C)
                 + migration*L
A_resistant(C) = diag(resistant_growth - kill_resistant*penetration*C)
                 + migration*L.
```

The conversion term gives a lower off-diagonal block but does not change eigenvalues of this block-triangular system. The other state couplings do not feed back into the tumor block to first order at zero tumor population. With the model's positive repair and clearance assumptions, the non-tumor modes are stable. Local asymptotic stability therefore requires the largest eigenvalue of **both clone blocks** to be strictly negative.

Here L is symmetric. Raising C subtracts a strictly positive diagonal matrix, so the largest eigenvalue decreases strictly. Each positive-to-negative threshold is unique and calculated by a bracketed root solver. This is an analysis of the implemented equations, not a biological efficacy threshold.

At the nominal, invented parameters:

- Sensitive invasion crosses zero at C = **0.789234**.
- Resistant invasion crosses zero at C = **5.181195**.
- Retaining an assumed normalized reserve floor of 0.7 at every site allows at most C = **0.136364**.
- At the resistant threshold, the minimum equilibrium reserve is **0.057858**.

Consequently **no constant-exposure value simultaneously makes the tumor-free equilibrium locally asymptotically stable and retains that assumed reserve floor in this model**. The same intersection is empty for all 24 arbitrary parameter configurations from the earlier sensitivity study.

Root residuals, threshold crossing signs, eigenvalue monotonicity and the zero-migration analytic limit were checked. The conclusion is restricted to constant exposure, local stability and these equations. It is not a proof about arbitrary time-varying strategies, other therapies, actual patients or cancer in general. Zero tumor population is invariant mathematically; a finite-time floating-point zero is not a cure criterion.

Executed code: `analyze_extinction.py`. Outputs: `output/extinction-feasibility.json` and `output/extinction-feasibility.png`.

## What these computations establish

There is usable local algorithmic material and one measured CRISPR assay dataset. The calculation has moved beyond purely synthetic annotation examples. The nested implementation now has an executable audited snapshot. The synthetic tumor model also exposes a mathematically explicit limitation instead of implying that sufficient numerical effort will produce a cure.

No inspected artifact establishes cancer eradication with acceptable organism-level safety. The supplied evidence does not support publishing a cancer-cure claim.
