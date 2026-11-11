# Lithium: from solvated ions to cellular regulation

Research extension of Michael Emanuel Glover's Virtual Cell framework.
Prepared with assistant research and synthesis. This note introduces mechanisms
and model requirements; it reports no new biological experiments or simulations.

## Central question

How can a small monovalent ion change neuronal dynamics and contribute to mood
stabilization? Build the explanation through solvation, transport, binding,
enzymatic rates, cellular signalling, and circuit dynamics. Molecular evidence
does not yet identify one necessary and sufficient explanation of clinical
lithium response.

## Atomic and physical description

Neutral lithium has three protons and three electrons, configuration 1s²2s¹.
Biological lithium is predominantly Li+, with two electrons (1s²). Lithium salts
supply solvated ions, not neutral metal. Its small ionic core interacts strongly
with surrounding water oxygen atoms. Hydration is dynamic; coordination depends
on environment. Quantum chemical and molecular-dynamics work supports a prevalent
four-water inner shell in dilute aqueous solution [1]. Protein binding requires
accounting for changes in this solvation environment.

Use electrochemical potential, not electrical attraction alone:

    mu_i = mu_i^0 + RT ln(a_i) + z_i F phi

Here a_i is dimensionless activity, z_i charge number, and phi electric potential.
For constant temperature, dilute ideal solution, and no solvent flow, a continuum
transport approximation is the Nernst–Planck flux:

    J_i = -D_i [grad(c_i) + (z_i F / RT) c_i grad(phi)]

J has units mol m^-2 s^-1 for c in mol m^-3 and D in m² s^-1. Membrane channels
require permeabilities or a channel model; applying bulk diffusion directly
through a lipid membrane is inappropriate. Sodium-channel-mediated Li+ entry
was demonstrated in cultured mouse neuroblastoma cells [2].

Binding selectivity reflects total free-energy differences: ion–protein
interactions, hydration loss, solvent reorganization, protein conformation and
entropy. Li+ and Mg2+ can interact with overlapping enzyme metal sites but have
different charge and coordination chemistry; radius similarity alone cannot
predict inhibition.

## Molecular targets and strength of inference

| Level | Observation | Interpretation and open question |
|---|---|---|
| Purified GSK-3 | Li+ inhibition competitive with Mg2+, not ATP or peptide substrate [3] | Direct molecular mechanism; its quantitative contribution in an intact brain depends on free ions and regulatory state. |
| IMPase kinetics | Inhibition uncompetitive with inositol-monophosphate substrate [4] | Requires enzyme-state-aware kinetics rather than treating every inhibitor as substrate-competitive. |
| IMPase structure | Three Mg2+ positions and catalytic water geometry resolved; comparison with lithium-containing structures motivates a site-2 inhibition mechanism [5] | Atomistic structural rationale, not a complete demonstration of clinical efficacy. |
| Patient-derived neurons | Hyperexcitability and lithium-dependent reduction in clinical-responder-derived neurons [6] | A cellular phenotype linked to response; cultured neurons are not a whole brain. |
| Patient-derived cellular clocks | Rhythm properties and lithium responses differ across donor cells [7,8] | Supports circadian mechanisms and heterogeneity; predictive findings require broader validation. |

IMPase catalyses the net biochemical conversion of inositol monophosphate and
water to inositol and inorganic phosphate. Inositol supplies phosphoinositide
metabolism. Phospholipase C cleaves PIP2 into IP3 and DAG; IP3 regulates calcium
release from intracellular stores. Thus an enzyme effect can propagate into
calcium signalling. Uptake, de novo synthesis, compartmentation and feedback
can compensate: IMPase inhibition does not imply a universal proportional fall
in every downstream signal.

## Minimal kinetics: useful approximations, not fitted physiology

A single mutually exclusive metal-binding-site approximation:

    E + Mg <-> E_Mg        E + Li <-> E_Li
    f_Mg = ([Mg]/Kd_Mg) / (1 + [Mg]/Kd_Mg + [Li]/Kd_Li)

Assumes rapid equilibrium, constant free-ion concentrations, one independent
site, and inactive E_Li. It is a teaching model for competition, not a complete
GSK-3 or multi-metal IMPase catalytic mechanism. Empirical Kd values are needed.

An ideal uncompetitive substrate-inhibition model for IMPase:

    alpha_prime = 1 + [Li]/Ki
    v = Vmax [S] / (Km + alpha_prime [S])

Relative to no inhibitor, v_Li/v_0 = (Km+[S])/(Km+alpha_prime[S]). Increasing
substrate does not overcome this inhibition. This is compatible with a stronger
fractional effect at high pathway demand within these assumptions. Ki and all
rates depend on assay conditions; incorporate metal states for mechanistic fits.

For a well-mixed cellular compartment, conservation requires:

    d(n_Li_inside)/dt = A J_Li_inward
    d(n_bound_Li)/dt = binding_rate - unbinding_rate

The first balance uses total intracellular lithium, including bound lithium;
free lithium has the additional opposite binding terms. A closed extracellular
plus intracellular system conserves total Li atoms. Reaction stoichiometry must
also conserve atoms and charge, including buffered protons where appropriate.

## Connection to the Person model

Add species identity, ionic charge, units, compartment volumes, free and bound
pools, reversible reaction networks, and physically constrained membrane flux.
Retain the existing molecule objects as the pedagogical layer; molecular counts
alone do not define concentrations or electrochemical potentials.

Cellular reactions follow physical kinetics. Our computational governors may
select an intervention, but chemical reactions do not require a Person's
permission or conscious decision. Separate intervention choice from state
evolution. Lithium must change measured transport or reaction parameters rather
than directly setting a person's happiness, love, or generic relaxation value.

Use molecular dynamics for hydration and coordination; use quantum chemistry or
QM/MM for bond rearrangement and catalytic energetics; use reaction kinetics
for cellular timescales; use conductance and circuit models for neural activity.
Connect scales through measured parameters and uncertainty rather than trying
to simulate an entire person atom by atom.

First proposed test: scan free Li+ and Mg2+ in the single-site approximation,
plot productive occupancy, and verify conservation in the corresponding
reversible kinetic system. Compare a subsequent IMPase model against measured
rates before adding calcium and neuronal feedback. No arbitrary parameter scan
should be labelled a prediction of treatment response.

## Primary sources

1. Rempe et al. The hydration number of Li+ in liquid water.
   https://arxiv.org/abs/physics/0001011
2. Lithium ion entry through the sodium channel of cultured mouse neuroblastoma
   cells: a biochemical study. https://pubmed.ncbi.nlm.nih.gov/860126/
3. Ryves & Harwood (2001). Lithium inhibits glycogen synthase kinase-3 by
   competition for magnesium. https://pubmed.ncbi.nlm.nih.gov/11162580/
4. Hallcher & Sherman (1980). The effects of lithium ion and other agents on
   the activity of myo-inositol-1-phosphatase from bovine brain.
   https://pubmed.ncbi.nlm.nih.gov/6253491/
5. Gill et al. (2005). High-resolution structure of myo-inositol monophosphatase,
   the putative target of lithium therapy.
   https://journals.iucr.org/d/issues/2005/05/00/tm5016/
6. Mertens et al. (2015). Differential responses to lithium in hyperexcitable
   neurons from patients with bipolar disorder.
   https://pubmed.ncbi.nlm.nih.gov/26524527/
7. Calcium channel genes associated with bipolar disorder modulate lithium's
   amplification of circadian rhythms. https://pubmed.ncbi.nlm.nih.gov/26476274/
8. Patient fibroblast circadian rhythms predict lithium sensitivity in bipolar
   disorder. https://pubmed.ncbi.nlm.nih.gov/32404948/
