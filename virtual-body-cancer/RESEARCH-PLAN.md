# The virtual body: cells, niches, organs, organism

Michael Emanuel Glover's research programme, developed with Codex. 4 October 2026.

The ambition is to help discover cancer treatments that control malignant populations while preserving the person. This first deliverable is an executable, synthetic feasibility model. It does not establish a cure, a safe intervention, a calibrated patient simulator, or superiority over other methods.

## What exists and what it can contribute

The local audit reviewed the generic sparse HRL engine and its documentation, the recursive GRRLE interface, the Relaxfish experiment documentation, and the portfolio's morphogenesis demonstration. It did not read every file on the drive. The targeted code/document search found no cancer dataset in those inspected project paths. Medical imaging and physiology project directories also exist; their relevance, permissions and data provenance require a separate audit before scientific reuse.

- **Sparse HRL:** imported verbatim from `Code/relaxation-labeling/python/hrl_generic/engine.py`; pairwise and three-way compatibility factors, persistent priors, explicit rejection option. The copy is in `vendor/hrl_engine.py`. The underlying repository lacks a top-level license file in the inspected location; no new redistribution license is inferred.
- **GRRLE:** supplies a pattern for competing hypotheses and cross-level relations. It is architectural inspiration here, not an integrated biology backend.
- **Relaxfish:** supplies the discipline of baselines, ablations and claims limited to measured evidence. Chess evaluation is not a biological efficacy score.
- **Morphogenesis:** supplies an inspectable visualization precedent. Its simulated anatomical identities are not evidence of cancer reprogramming.
- **Manuelian knowledge states:** separate an unavailable measurement, an unresolved hypothesis, a conflicting result and a validated relationship in a future evidence ledger. These are epistemic metadata, not extra physical substances.

Anatomical levels form interacting systems: molecular networks within cells, cells in spatial niches, niches in tissues, tissues in organs, and organs linked through circulation and immune traffic. This is a hierarchy of organization; tissues and organs are not literally cells inside cells. Feedback must travel both up and down the hierarchy.

## Implemented model

There are three abstract sites, each with sensitive tumor population S, resistant population R, immune activity E, resource O and healthy reserve H. A shared systemic exposure C connects sites. Sites are not named organs and the resource is not a validated oxygen concentration. All variables and time are dimensionless. Treatment inputs are fictional control signals, not drug doses.

For site i, N_i=S_i+R_i and c_i=p_i C, with assumed penetration p=(1,0.65,0.4):

```
dS_i/dt = r_s O_i S_i (1-N_i/K) - m r_s O_i S_i
          - (k_s c_i + k_e E_i) S_i + migration*(L S)_i
dR_i/dt = r_r O_i R_i (1-N_i/K) + m r_s O_i S_i
          - (k_r c_i + k_e E_i) R_i + migration*(L R)_i
dE_i/dt = recruitment*N_i/(0.1+N_i) - decay*E_i - immune_toxicity*c_i*E_i
dO_i/dt = supply*H_i*(1-O_i) - consumption*N_i*O_i
dH_i/dt = repair*(1-H_i) - toxicity*c_i*H_i
dC/dt   = input - clearance*C
```

L has nonnegative off-diagonal entries and zero column sums, so intersite transport conserves each tumor clone in the absence of other processes. Clone conversion cancels in the total tumor balance. At zero population the corresponding vector field is nonnegative. At O,H=0 the derivatives point inward, and at O,H=1 they are nonpositive. These structural properties do not guarantee accuracy of a finite numerical step. RK4 uses held input per step; explicit checks reject negative states or resource/reserve excursions. Repeating at half the step size checks numerical sensitivity.

The model has aggregate clone populations rather than individual cells. It has no molecular dynamics, spatial mechanics, explicit vasculature, liver/kidney pharmacokinetics, clinically validated resistance mechanism or toxicity mapping. The three-site transport is a placeholder, not a validated metastasis process. It is a starting interface for replacing crude components with measured submodels, not a complete virtual human.

## Experiments implemented

Four fixed fictional controls: no input, continuous input, a periodic pulse, and a burden/reserve feedback rule. The feedback threshold values are arbitrary. They were not optimized, and no best clinical schedule is inferred.

Twenty-four reproducibly sampled parameter configurations are run with shared draws across policies. Their uniform ranges are arbitrary engineering sensitivity ranges, not a posterior, confidence interval or population distribution. Outputs include final tumor burden, integrated burden, minimum reserve, resistant fraction and integrated input. A scatter plot shows tradeoffs without collapsing them into an unjustified clinical utility score.

A separate HRL ablation uses 120 synthetic cells, four classes, noisy priors, within-patch edges and within-patch triangles. It compares prior-only, pairwise and pairwise-plus-triple factors, and demonstrates the rejection option. Patch homophily is true by construction. This toy task cannot establish accuracy on human cell annotations; normalized strengths are not calibrated biological probabilities. The inference demo does not drive the dynamical simulator. Connecting them requires an identified observation model and learned state-to-rate mapping.

## An evidence-backed path to a useful virtual cell

1. Select a cancer subtype and a specific prediction: for example, predicting a measured perturbation's effect on a resistant subpopulation. Agree on measured endpoints before fitting.
2. Version one public dataset with sample IDs, assay, donor/line, tissue, perturbation, units, license/access terms, missingness and checksum. Pair it with a compatible untreated/control dataset. Keep controlled-access patient data outside public artifacts.
3. Define an observation likelihood connecting latent cell state to RNA, protein, imaging or viability. Learn observation priors on training donors only. Use assay and batch covariates; do not encode label answers into the test graph.
4. Build cell-neighborhood factors from measured spatial contacts and molecular evidence. Cell neighborhoods can be heterotypic; tumor/immune boundaries must not be treated as same-label links. Include positive and negative effects and evaluate their empirical validity.
5. Fit identifiable kinetic parameters with replicates and longitudinal perturbations. RNA counts alone generally do not identify growth, death, migration, drug clearance and immune killing. Distinguish structural from practical identifiability.
6. Couple intracellular mechanisms to tissue models and validated exposure/toxicity components. Test pooling and projection operators to avoid counting a signal twice across scales. Benchmark against established simulators, including PhysiCell/PhysiBoSS where appropriate.
7. Hold out donors, laboratories, perturbations and time points as appropriate. Compare independent classifier, pairwise graph model, full HRL and mechanistic baselines using identical splits and compute budgets. Report accuracy, abstention coverage/risk, calibration, forecast error and intervention-response uncertainty. Include failed predictions.
8. Use prospective predictions to choose informative laboratory experiments with qualified collaborators. A successful retrospective fit does not establish causal intervention validity. External experimental replication and the clinical research process are needed before claims about treatment benefit.

## Candidate public resources (not downloaded or fitted here)

- NCI Cancer Systems Biology Consortium: https://www.cancer.gov/about-nci/organization/dcb/research-programs/csbc — multiscale cancer-ecosystem research.
- Human Tumor Atlas Network: https://docs.humantumoratlas.org/data_access/introduction/ — spatial and molecular tumor context; metadata open, assay access varies.
- Broad DepMap: https://depmap.org/portal/data_page/ — cancer dependency and perturbation resources; select and record a specific release rather than silently using latest.
- PhysiCell: https://physicell.org/ — established multicellular simulation framework; integration is proposed, not present.
- Bunne et al., *How to build the virtual cell with artificial intelligence: Priorities and opportunities*, Cell (2024), DOI https://doi.org/10.1016/j.cell.2024.11.015 — perspective on the virtual-cell research programme, not proof that a complete human model exists.

Sources were located/checked on 4 October 2026. Source pages inform the research direction; they do not supply this prototype's numerical parameters. No patient data, clinical endpoint or experimentally established cancer intervention was used in its execution.

## The next decisive milestone

A versioned, independently held-out perturbation benchmark in one defined cancer context. Demonstrate whether measured spatial and higher-order factors improve response prediction beyond simpler baselines while exposing failures and uncertainty. Only then expand the hierarchy. The goal is a useful, falsifiable model that earns each added level through evidence.
