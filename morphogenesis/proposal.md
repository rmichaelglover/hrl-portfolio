# Morphogenesis as Hierarchical Relaxation Labeling
### A computational-level account of bioelectric pattern control, with an in-silico test of editable anatomical memory

**One-page research proposal · 2026**

## Abstract
Michael Levin's work reframes morphogenesis as **collective intelligence**: cells cooperate
to build and *homeostatically restore* a target anatomy, with the target stored as a
bioelectric **setpoint** that can be edited independently of the genome. We propose that
**hierarchical relaxation labeling (HRL)** — a probabilistic constraint-satisfaction process
with a first-class, non-decaying prior and an optional noise label — is a natural
*computational-level* (Marr) theory of this process, and we demonstrate a first result:
the two-headed planarian phenotype reproduced by editing **only** the prior.

## Background & gap
Reaction–diffusion models generate patterns but lack a stored target they error-correct
toward; they do not naturally express Levin's central phenomena — regenerative homeostasis,
and a **memory of target morphology that is editable without genomic change**. A model is
needed whose dynamics (i) converge to a stored attractor, (ii) repair toward it after
arbitrary perturbation, and (iii) expose an interpretable coupling term mappable to
gap-junctional communication.

## Mapping
cell → **object**; positional/anatomical identity → **label**; gap-junction coupling →
**compatibility kernel**; bioelectric setpoint / target-morphology memory → **persistent prior**;
anatomical homeostasis & regeneration → **convergence to the relaxation fixed-point**;
apoptosis → **noise label**; multiscale competency (cell→tissue→organ→axis) → the **hierarchy**.

## Hypothesis
The morphological outcome of a tissue is the fixed-point of an HRL process whose **prior**
encodes the bioelectric setpoint and whose **kernel** encodes gap-junctional coupling.
Therefore *editing the prior alone* (not the label set or kernel — the "genome") should
re-target regeneration, heritably across re-cuts.

## Demonstrated result (this repo)
`morphogenesis_v2.py`: a tissue amputated at the posterior regrows by relaxation. With the
**wild-type** prior it regenerates head–trunk–**tail** (one head); with a prior whose
posterior memory is flipped to **head** — *same kernel, same labels* — it regenerates
head–trunk–**head** (**two heads**). The edit lives in the prior, so it persists under
re-amputation. This mirrors Levin's bioelectric two-headed planaria.

## Predictions (falsifiable)
1. **Gap-junction blockade** (octanol/heptanol) ≈ weakening specific kernel edges → specific,
   predictable mispatternings.
2. **Apoptosis localizes** where cells settle onto the noise label (incompatible with the field).
3. **Hierarchy predicts repair order**: coarse (axis) labels stabilize before fine (organ) labels;
   perturbations that violate a higher scale are less correctable.
4. **Alternative fixed-points** of a given kernel enumerate candidate **Xenobot** morphologies.

## Methods & validation
Parametrize the kernel from gap-junction connectivity and the prior from **voltage-dye imaging**
of real setpoints (Levin-lab datasets). Compare HRL fixed-points to observed morphologies;
compare regeneration *trajectories* (with matched kinetics) to time-lapse data; quantify on
planarian head/tail statistics and induced-eye/limb assays.

## Milestones
1. ✅ Editable-memory demo (two-headed planaria, prior-edit only).
2. Relaxation on a **growing graph** (cell division/death/migration).
3. **Multi-scale** kernel (cell↔tissue↔axis) with cross-scale compatibility.
4. Data-grounded kernel/prior; quantitative validation against published phenotypes.

## Significance
If morphogenesis is well-modeled as HRL, the same interpretable engine spans neural-style
labeling, model consensus, and anatomical pattern control — and "rewriting the prior" becomes
a concrete, testable handle on regenerative and synthetic-morphology medicine.

*Caveat: this is a computational-level theory — what the system computes (constraint
satisfaction toward a stored target). Bridging to mechanism (channels, junctions) is required
to make it biology rather than analogy.*
