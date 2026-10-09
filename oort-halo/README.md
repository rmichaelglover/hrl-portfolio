# Oort Cloud and Galactic Halo: first model comparison

This experiment compares geometry and gravitational response. It does not fit
Milky Way observations, measure the Oort Cloud, identify dark matter, or assess
modified gravity. Both examples assume Newtonian gravity and exact spherical
symmetry. The central component is a point mass; a real galaxy has a disk, bulge,
bar and other structure. Circular speed is a diagnostic, not an assumption that
comets follow circular orbits.

## The three models

Use units G = M₀ = r₀ = 1. All models have a central point mass M₀.

1. Central mass alone.
2. Central mass plus a uniform-density thick shell, from 2r₀ to 10r₀.
3. Central mass plus a cored extended halo, with density
   ρ(r) = ρ₀ / [1 + (r/a)²], core a = 0.3r₀, truncated at 10r₀.

Models 2 and 3 have the same total extra mass: 4M₀. This intentionally large
mass makes their different radial distributions visible. It is not an Oort
Cloud mass claim and is not a fitted Milky Way halo.

For the thick shell, enclosed extra mass is zero below its inner radius; within
the shell it is Mₛ(r³−rᵢ³)/(rₒ³−rᵢ³); outside, it is Mₛ.

For the cored halo, enclosed mass before truncation is
4πρ₀a³[r/a−arctan(r/a)]. Choose ρ₀ to obtain the specified mass at rₒ.

In both cases, the shell theorem gives inward gravitational acceleration
|g(r)| = G[M₀+Mextra(<r)]/r² and circular speed
v_c(r) = sqrt(G[M₀+Mextra(<r)]/r).

## What the comparison establishes

- Inside the shell cavity, the shell adds exactly zero net force. Its individual
  gravitational pulls cancel under spherical symmetry; gravity is not screened.
  Its gravitational potential inside the cavity is a nonzero constant when
  referenced to zero at infinity. It can therefore alter escape energy even
  though it does not alter local acceleration or circular speed there.
- The extended halo contains mass inside the tracer's radius and therefore adds
  inward acceleration there. Its influence is small deep inside the core.
- A roughly flat circular-speed curve requires approximately M(<r) ∝ r over
  that interval. In a spherical model, that corresponds to ρ ∝ r⁻².
- Our cored halo approaches that density slope outside its core. A flat total
  speed is approached only where the halo dominates and before truncation;
  central gravity and the finite extent prevent exact flatness everywhere.
- Outside 10r₀, both extended models have identical enclosed total mass, so
  both return to the same Keplerian decline, v ∝ r⁻¹ᐟ².
- Shape alone cannot reveal composition. Ordinary matter and hypothetical dark
  matter with the same mass distribution have the same Newtonian field.

## Solar-scale illustration

`solar-shell.png` uses a Sun of one solar mass and an **assumed** cloud mass of
10 Earth masses in a uniform spherical shell from 2,000 to 100,000 AU. The
range is illustrative, within the broad ranges discussed by NASA; it is not a
measured cloud boundary. The 10-Earth-mass choice is a demonstration parameter,
not a mass estimate or confidence interval.

The extra cloud force is exactly zero in the model's cavity. Beyond all of it,
the maximum force increase relative to the Sun alone is approximately 30 ppm
(0.003%). Circular speed increases by approximately half that fraction.
Even at the outer edge, this assumed cloud does not dominate the Sun's gravity.

A real Oort population is discrete and need not be perfectly spherical. Local
perturbations, planetary gravity, Galactic tides and passing stars are omitted.
The ambient Galactic dark-matter distribution is not modeled as a shell centered
on the Sun; a Sun-centered dense dark-matter halo is not assumed here.

## Reproduce and inspect

Run `python3 model.py` with NumPy and Matplotlib installed. Outputs:

- `three-models.png` and `.pdf`: dimensionless speed, acceleration and mass plots.
- `solar-shell.png` and `.pdf`: illustrative Sun/cloud speed and force comparison.
- `three-models.csv`: numerical curves, 800 radii per model.
- `results.json`: parameters, sample values and verification summary.

Checks include an independent numerical integral of the cored density and an
independent vector-force integration over a thin shell, verifying cancellation
inside it and point-mass behavior outside it. Mass normalization, monotonicity,
truncation, and the circular-force relation are also checked.

## Observational context and next step

NASA describes the Oort Cloud as an inferred population of icy bodies with
uncertain dimensions. ESA describes the Milky Way halo as inferred from the
gravitational effect of unseen matter on stellar motions.

- NASA Oort Cloud facts: https://science.nasa.gov/solar-system/oort-cloud/facts/
- ESA galaxy overview: https://www.esa.int/Science_Exploration/Space_Science/Gaia/Guide_to_our_galaxy
- Planetary-ephemeris constraints on unseen Solar System mass:
  https://arxiv.org/abs/1306.5534

Next: replace the galaxy's point-mass component with a disk-and-bulge model,
compare against a source-backed Milky Way rotation-curve dataset with errors,
and examine how conclusions change with baryonic-model and dynamical assumptions.
