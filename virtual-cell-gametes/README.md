# Virtual cell: human gametes to zygote

Started 29 October 2026. A first executable increment toward modeling human cells.

The long-term target is a shared cell architecture with specialized cell types,
individual cell states, spatial environments, division and lineage. Starting with
sperm and egg tests specialization and fusion immediately. These are highly
specialized cells; their mechanisms cannot stand in for all somatic cells.
Development from a zygote will require maternal stores, epigenetic state and the
environment as well as DNA. Modeling every cell is a research objective, not a
capability delivered here.

## What runs tonight

`model.py` is a standard-library event-driven bookkeeping model. It starts with
a euploid human metaphase-II secondary oocyte and fusion-ready sperm already at
the egg plasma membrane. Upstream transport, capacitation, acrosome reaction,
cumulus and zona passage are outside this first executable boundary.

```sh
cd virtual-cell-gametes
python3 model.py > demonstration.json
python3 -m unittest -v
```

The demonstration supplies a normal sequence and a two-sperm sequence. No event
times, rates, probabilities, fertility outcomes or biological measurements are
invented. Events are inputs; the model checks consistency and reports consequences.
Withholding activation leaves the model pending; it does not diagnose failure.

The normal sequence is fusion → supplied activation → supplied effective block →
meiosis-II completion with second polar body → two-pronucleus endpoint.
Block establishment and meiosis completion may occur in either order after
activation. This ordering is a coarse software abstraction, not a claim about
the detailed timing of overlapping biological processes. The effective block is
one idealized gate, not a simulated cortical/zona/membrane mechanism. Before that
gate, a distinct second sperm can fuse; polyspermy is flagged. The model declines
to generate its normal two-pronucleus endpoint for that branch; abnormal
pronuclear development is not implemented. It stops before pronuclear DNA
replication and first mitosis. Pronuclei are not modeled as merging into a single
interphase nucleus.

Nuclear DNA is counted in C, where 1C is one unreplicated haploid genome.
The initial MII oocyte is 1n/2C; each sperm is 1n/1C. After completion of
meiosis II, the maternal contribution is 1n/1C and the second polar body is
1n/1C. The normal pre-replication zygote therefore contains 2C nuclear DNA
across two pronuclei, and the polar body holds the remaining 1C. The accounted
boundary begins with 2C and gains 1C for each fusion. The first polar body,
unfused sperm, mitochondrial DNA and DNA degradation are outside this ledger.
No aneuploidy, sequence variation or chromosome segregation errors are modeled.

## Reusable cell architecture to build next

Each biological cell should have an identity, type, lineage, geometry, membrane,
compartments, molecular amounts, electrical state, environment interfaces and
an evidence ledger. Compartments and organelles are parts of cells; they must
not be silently counted as additional biological cells in a recursive hierarchy.
Each variable needs units, spatial scope, initialization provenance and uncertainty.
Each interaction needs an evidence source, species, experimental context and
explicit status: measured, inferred, assumed or not implemented.

| Component | Sperm specialization | Oocyte specialization | Current implementation |
|---|---|---|---|
| Nuclear genome | Compact haploid paternal genome | MII spindle and duplicated maternal chromosomes | C accounting only |
| Membrane | Channels and recognition/fusion factors | Recognition machinery and cortical response | Supplied fusion and block events |
| Compartments | Head/acrosome, midpiece mitochondria, flagellum | Cytosol, ER, mitochondria, cortical granules | Design only |
| Energy | ATP production and flagellar demand | ATP production, pumps and maternal stores | Not implemented |
| Signaling | pH, voltage, calcium, capacitation state | PLCζ/IP3/calcium and activation | Supplied activation event only |
| Environment | Fluid mechanics and extracellular cues | Cumulus, zona, perivitelline space | Boundary conditions, not simulated |
| Lineage | Paternal contribution | Maternal contribution and polar body | Polar-body DNA accounting; no lineage tree |

Related work: the [Virtual Body dissertation](../virtual-body-cancer/) and
[HRL2026 nested-cell source](https://github.com/rmichaelglover/hrl2026).
This increment is separate and does not import the nested-cell implementation.
Their recursive categorical states are not calibrated concentrations, channel
currents or molecular reaction rates. Any future coupling needs explicit units
and a validated map between those representations.

## Evidence ledger

Sources checked 29 October 2026. These support biological design choices, not
validation of this software or its hypothetical event sequences.

| Mechanism | Evidence and scope | Modeling consequence |
|---|---|---|
| MII arrest and second polar body | [Meiosis and Fertilization, The Cell](https://www.ncbi.nlm.nih.gov/books/NBK9901/) gives textbook context; [1995 human ICSI observations](https://pubmed.ncbi.nlm.nih.gov/7580022/) report second polar-body extrusion | Distinguish chromosome sets from replicated DNA; retain expelled DNA in ledger |
| Progesterone modulation of CatSper | [Lishko et al., Nature 2011](https://www.nature.com/articles/nature09767), human sperm electrophysiology | Candidate first sperm signaling module; not yet implemented |
| IZUMO1–JUNO recognition | [Aydin et al., Nature 2016](https://www.nature.com/articles/nature18595), human protein structures; [human oocyte functional study](https://academic.oup.com/humrep/article/34/1/118/5231497) | Recognition must remain distinct from fusion; no sufficient two-protein fusion rule |
| Additional fertilization machinery | [Deneke et al., Cell 2024](https://doi.org/10.1016/j.cell.2024.09.035), conserved complex with functional evidence particularly in zebrafish | Keep species and assay provenance; do not treat fish functional results as calibrated human kinetics |
| PLCζ and calcium responses | [2012 human oocyte study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3334266/), PLCζ cRNA microinjection including failed-ICSI oocytes | Candidate egg activation module; selected/injected oocytes are not an unqualified natural-fertilization dataset |

## Next measurable milestone

Replace the supplied activation event with a compartmental calcium model of
cytosol and ER, including IP3-mediated release, SERCA uptake and membrane fluxes.
Keep concentrations separate from amounts: intracellular transfers must conserve
calcium after multiplying concentrations by compartment volumes; extracellular
exchange changes that total through recorded fluxes. Record ATP consumption when
adding active transport rather than treating pumping as free energy.

Before fitting, obtain a reusable human-oocyte calcium time-series dataset with
stimulus, sampling interval, indicator calibration or fluorescence normalization,
oocyte selection criteria, donor grouping and licensing. Fluorescence in arbitrary
units cannot be relabeled micromolar. Fit only identifiable parameters; report
remaining assumptions and uncertainty. Hold out donors where metadata permits.
Validate spike timing and amplitudes against held-out traces, compare a simple
baseline and check numerical convergence and mass balance. Until then any
oscillator would be a synthetic mechanism demonstration.

Then add sperm CatSper/pH/voltage signaling as a separately validated module,
couple fusion to PLCζ delivery, and only later add first cleavage with explicit
DNA replication and daughter-cell partitioning. Cell-type-specific models can
share interfaces without assuming identical biology.
