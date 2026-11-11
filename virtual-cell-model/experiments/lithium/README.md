# Lithium: a conserved biochemical extension

Michael Emanuel Glover originated the Virtual Cell / Person framework and the
direction of this lithium extension. The assistant implemented this prototype,
tests, research synthesis and plots in collaboration with him.

The new `bio::LithiumPhysiology` is a small deterministic compartment model.
Concentrations and individual responses arise from state evolution rather than
from a rule saying that lithium improves a person. A `mind::PersonModel` may own
an optional physiology, which evolves independently of its behavioral governor.

## Reproduce

From the project root:

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
./build/lithium_demo
python3 experiments/lithium/plot.py
```

The plot script requires Matplotlib and writes raw CSV, a JSON summary, and PNG
and vector PDF figures beside this README. The CSV includes a comment identifying
synthetic parameters, then 488 observations: 2 coupling profiles × 4 initial
external concentrations × 61 sample times. Both profiles have identical chemistry
for the same preparation; only the downstream observation differs.

## What is physically constrained

- Species carry formula, charge and amounts. Volumes are in picolitres,
  concentrations in millimolar, times in seconds, amounts in femtomoles.
  `mM × pL = fmol`. The enzyme site is an abstract conserved moiety, not a protein
  sequence or a complete GSK-3 atomic structure.
- Reactions must conserve every tracked atom, site moiety and charge. Invalid
  stoichiometry or insufficient reactants are rejected before mutation.
- A closed extracellular / intracellular system exchanges LiCl reversibly.
  Pair flux is `g * (cLi_out*cCl_out - cLi_in*cCl_in)`, with `g` in
  pL/(mM s). This follows the ideal salt chemical-potential difference and
  preserves compartment charges. It is an effective pair-transport model, not
  a claim that neuronal sodium channels cotransport lithium and chloride.
- Binding follows `E + Li <-> E:Li` and `E + Mg <-> E:Mg`, with concentration-
  based mass action. Free pools are finite and bound ions stay in the ledger.
  The Mg-bound fraction is a productive-site proxy motivated by GSK-3 metal
  competition, not a complete kinase catalytic cycle.
- Hydrolysis follows balanced `C6H11O9P(2-) + H2O -> C6H12O6 + HPO4(2-)`.
  Its effective rate is `Vmax*S / (Km + (1 + free_Li/Ki)*S)`, an ideal
  uncompetitive-substrate inhibition model motivated by IMPase kinetics.
  Fixed protonation and forward-only hydrolysis omit pH dynamics and reverse
  chemistry. The finite substrate eventually depletes; this is not sustained
  inositol recycling or a PIP2/IP3/calcium cycle.

The synthetic starting cell contains 1 mM free Mg, 2 mM chloride, 0.4 mM
nontransported sodium counterion, 0.01 mM sites, 0.2 mM inositol monophosphate,
0.05 mM inositol and 55,500 mM water. It is electrically neutral. The external
volume is 10 pL and cell volume 1 pL. Adding external LiCl changes the preparation;
there is no kidney, dosage calculation, water transport or osmotic volume model.

## What is an explicit modelling hypothesis

The downstream dimensionless response relaxes toward

```
target = basal_drive + kinase_gain * productive_fraction
         + inositol_gain * inositol / (inositol_half + inositol)
d(response)/dt = (target - response) / response_time
```

This transfer function is a synthetic observation model. It does not simulate
neuronal firing or represent happiness, sedation, mania, or clinical outcome.
All parameter values and timescales in the demonstration are illustrative;
the molecular papers motivate mechanisms but do not fit these values.

The `coupled` profile has both gains set to 1. The `uncoupled` profile has both
set to 0, so lithium still enters and changes molecular states while the
downstream response does not change. This null case is constructed to verify
the separation of mechanisms and observation, not an explanation of clinical
nonresponse. A zero transport conductance provides a separate no-entry case.

A decrease of the response is not intrinsically beneficial: whether it brings
a synthetic person closer to a specified operating range depends on that range
and their initial state. No objective score or behavioral choice is silently
modified by the physiology. Later empirical mappings can connect observables to
specific decision features with provenance and uncertainty.

`bio::OperatingRange` measures distance from an explicitly supplied proxy range.
For the coupled 60-second demonstration, 1 mM initial external lithium moves the
proxy from about 1.479 to 1.403 relative to zero exposure. This approaches the
declared range [1.35, 1.42] and departs from [1.45, 1.50]. These two ranges are
deliberately chosen examples of evaluation dependence, not measured human norms
or independently discovered beneficial/adverse responses. The JSON records both.

## Numerics and tests

Backward Euler is solved by 80 bisection iterations on feasible reaction or
transport extent. Sequential transport, Mg binding, Li binding and hydrolysis
are first-order operator splitting. The downstream relaxation uses its exact
update for a target held fixed during that substep. Default maximum step is
0.01 s. Step size is numerical resolution, not a biological time constant.

The biochemical suite checks analytic binding equilibrium; salt equilibrium;
decrease of ideal mixing free energy under passive salt exchange; transport
against a Li gradient when salt chemical potential requires it; unit conversion;
atom, site and charge conservation; nonnegative pools; stiff binding; the
uncompetitive inhibition ratio at equal substrate; zero exposure; zero entry;
uncoupled response; invalid inputs; 0.01 versus 0.005 s refinement; and Person
integration without changes to behavioral budgets, permissions or experiences.

The published manuscript and its frozen reproduction model remain a versioned
record of the preceding experiments. This extension is not included in its
reported results. See `../../LITHIUM_RESEARCH.md` for primary references and
the next empirical steps.
