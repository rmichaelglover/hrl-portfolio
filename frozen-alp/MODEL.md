# Spatial-Stiffness ALP: an operational frozenness model

Michael Emanuel Glover's proposal developed with AI assistance · 28 October 2026 · v0.1

**Status:** a newly specified phenomenological effective model, analytical derivation and reproducible benchmark. Not an observational detection, cosmological fit, established novel discovery, or UV-complete theory. No assertion of priority for higher-spatial-derivative scalar theories.

## 1. Choice and meaning

Choose a **generic ultralight axion-like particle (ALP)** with rest energy `m = 10^-20 eV`, not a QCD axion. The QCD mass/decay-constant relation is not imposed. Work near a harmonic potential minimum and neglect self-interactions, particle-number-changing processes and observable photon portals for this benchmark.

Define operational **frozenness** as *positive energetic stiffness against fine spatial variation*. Independent spatial modes remain; their dispersion changes. The term does not mean motionlessness, universal phase coherence, inaccessible information, or elimination of the field's local degrees of freedom. The present model changes the original manuscript rather than proving its literal no-spatial-modes assertion.

The explicit extra assumption is a preferred cosmological foliation. This is a Newtonian/subhorizon cosmological EFT, not a demonstration of a generally covariant completion. A complete dynamical preferred-frame sector, radiative stability, and experimental constraints remain to be supplied.

## 2. Candidate field dynamics

Let `s(t)` denote scale factor and `phi` the real ALP, avoiding the original use of `a` for both field and scale. Set hbar=c=1. On the specified background take

    S_phi = integral dt d^3x s^3 [
        phi_dot^2/2 - |grad phi|^2/(2s^2) - m^2 phi^2/2
        - (laplacian phi)^2/(2 M^2 s^4)
    ].

`M > 0` is a physical crossover momentum, not automatically an EFT ultraviolet cutoff. This equation specifies the free-sector benchmark; gravity in the following nonrelativistic action is the weak Newtonian interaction. For physical momentum p=k/s the local free dispersion is

    omega^2 = m^2 + p^2 + p^4/M^2.

All terms are positive, so the specified free scalar has no gradient instability. It is second order in time and introduces no extra time-derivative degree of freedom at this level. These statements do not prove stability of an unspecified fully relativistic gravity/frame completion.

If `(p^2+p^4/M^2)/m^2 << 1` and `H << m`, its positive-frequency envelope has

    epsilon(p) = omega-m approximately p^2/(2m) [1+p^2/M^2].

The omitted relativistic correction is of relative order `(p^2+p^4/M^2)/m^2`. Higher spatial operators are an open modeling issue: near p~M the leading modification is not small. We explicitly postulate this dispersion over the benchmark band; it must not be defended as a generic controlled truncation solely because p is below m. A distinct higher cutoff or completion with sufficiently small omitted operators is required.

A fundamental scale-dependent frozen-sector construction would have to explain this operator and its coefficient. Here it is a declared hypothesis.

## 3. Explicit Newtonian envelope action and normalization

Use a comoving complex envelope `psi`; physical number density is `|psi|^2/s^3`, and background comoving density is `n0`. A defined effective weak-gravity model is

    S = integral dt d^3x [
        (i/2)(psi* psi_dot - psi psi*_dot)
        - |grad psi|^2/(2 m s^2)
        - |laplacian psi|^2/(2 m M^2 s^4)
        - m Phi (|psi|^2-n0)
        - s |grad Phi|^2/(8 pi G)
    ].

The subtraction is the ordinary cosmological removal of the homogeneous Newtonian source. Variation gives

    i psi_dot = [-laplacian/(2ms^2) + laplacian^2/(2mM^2s^4) + m Phi] psi,
    laplacian Phi / s^2 = 4 pi G rho_bar delta,
    rho_bar = m n0/s^3.

The free spatial Hamiltonian is Hermitian and positive for standard periodic/decaying boundary conditions. This envelope model conserves comoving particle number under its U(1) symmetry. For a real ALP this is an effective approximate number conservation, not an exact fundamental ALP charge. Newtonian gravitational instability is allowed and is not a free-field gradient pathology.

The same mass and mean density define the **standard baseline**, obtained by M -> infinity. Background density dilutes as s^-3 in both models to the adopted approximation.

## 4. Derive the density perturbation equation

Write, to first order,

    psi = sqrt(n0) [1 + delta/2 + i theta].

For a Fourier mode let

    F = 1+p^2/M^2,
    epsilon = p^2 F/(2m).

The real and imaginary equations give

    delta_dot = 2 epsilon theta,
    theta_dot = -epsilon delta/2 - m Phi,
    Phi = -(4 pi G rho_bar/p^2) delta.

Eliminating theta gives

    delta_ddot - (epsilon_dot/epsilon) delta_dot
        + [epsilon^2 - F*4 pi G rho_bar] delta = 0.

Because M is constant in physical units and p=k/s,

    -epsilon_dot/epsilon = 2H [1+2y]/[1+y],  y=p^2/M^2.

Hence

    delta_ddot + 2H(1+2y)/(1+y) delta_dot
        + [(p^4/(4m^2))(1+y)^2 - (1+y)4 pi G rho_bar] delta = 0.

**Important consistency point:** it would be incorrect simply to change the pressure term while retaining standard `2H` damping and the unmodified gravitational coefficient. The modified dispersion also changes the density/phase relation, producing the displayed factors. The independent implementations in model.py verify this elimination numerically.

At M -> infinity this reduces to the usual nonrelativistic ALP Schrödinger–Poisson perturbation equation:

    delta_ddot + 2H delta_dot + [p^4/(4m^2)-4 pi G rho_bar]delta = 0.

This standard baseline and its validity conditions are discussed by Marsh (2015/2016) and Passaglia & Hu (2022). The new coefficient and subsequent predictions are consequences of the explicitly postulated modification, not claims from those sources.

## 5. One quantitative prediction: shifted instantaneous Jeans boundary

Define the instantaneous Jeans momentum by zero of the bracket in the density equation. This is a gravitational stability diagnostic, not the complete transfer-function cutoff or a direct halo-count prediction.

The standard result is

    pJ0^4 = 16 pi G rho_bar m^2.

The modified result is

    pJ^4 [1+pJ^2/M^2] = pJ0^4.

Let x=pJ/pJ0 and y0=(pJ0/M)^2. Then

    x^4 (1+y0*x^2) = 1.

For y0>0 the positive root is unique and smaller than 1: the left side is strictly increasing for x>0. Consequently, the instantaneous Jeans length increases. At y0=0 the exact standard result x=1 is recovered.

**Benchmark chosen before numerical integration:**

- m = 10^-20 eV.
- rho_bar,0 = 0.265 * 3 H0^2/(8 pi G), with H0=67.4 km/s/Mpc used only as a density normalization.
- s_ref=0.01, or z_ref=99.
- M = pJ0(z_ref), equivalently M = 1.34643949e-25 eV.
- Homogeneous ALP-only matter-dominated benchmark. Baryons, radiation, self-interactions and Lambda are omitted. This is not the full measured cosmology.

Then

    x^4(1+x^2)=1,
    x = 0.8688369618327093.

| Quantity at z=99 | Standard ALP | Spatial-stiffness ALP |
|---|---:|---:|
| Comoving instantaneous kJ (Mpc^-1) | 210.5479 | 182.9318 |
| Jeans-associated mass, solar masses | 464,898.69 | 708,832.23 |

Thus **kJ decreases by 13.1163%** and the Jeans-associated mass increases by **52.4703%**. The mass convention is `(4pi/3) rho_bar (pi/qJ)^3`, with qJ the physical wave number in inverse metres. Its ratio is x^-3. These numbers are conditional benchmark predictions, not fitted measurements. The percentages follow from deliberately selecting the crossover M=pJ0 at the reference epoch; the benchmark itself is not evidence for that parameter value.

## 6. Distinction from merely changing the standard ALP mass

At a single epoch a different standard ALP mass can mimic the Jeans scale. A stronger discriminator is the redshift dependence at fixed constant parameters.

Since rho_bar scales as s^-3:

- Standard: physical pJ0 scales as rho_bar^(1/4), so comoving kJ0=s*pJ0 scales as s^(1/4).
- Strong-stiffness limit pJ>>M: pJ^6/M^2 approximately 16piG rho_bar m^2, so comoving kJ scales as s^(1/2).

A single constant standard ALP mass cannot reproduce both limiting exponents. Finite parameter intervals can still be approximately degenerate with other cosmological or astrophysical changes; observational distinguishability has not been demonstrated.

At z=9 the chosen benchmark has kJ/kJ0 approximately 0.992363, compared with 0.868837 at z=99. At z=999 the instantaneous benchmark ratio is approximately 0.553200. All of these use the same M and mass. They should not be interpreted as a full radiation-era calculation.

## 7. Numerical evolution: defined common initial conditions

To demonstrate dynamics, integrate only the ALP-only matter era from z=99 to z=9, with the same initial delta=1 and ddelta/dln(s)=1 in each model. Linearity allows an arbitrarily small common amplitude to replace 1; the plotted variables are normalized linear-response solutions, not order-one nonlinear perturbations.

These are matched initial conditions at a chosen finite redshift, not a radiation-era primordial transfer calculation. The initial phases required to realize the same density growth differ according to each model's epsilon.

Writing N=ln(s/s_ref), r=exp(-N) and X=k/kJ0,ref, the code uses

    F = 1+X^2*r^2,
    epsilon/H = sqrt(3/2) X^2 sqrt(r) F,
    delta_NN + [1/2+2(F-1)/F]delta_N
       + [(epsilon/H)^2 - (3/2)F]delta = 0.

For X=0.9, the endpoint normalized density amplitudes are approximately 7.03818 (standard) and 5.60975 (modified), a ratio of 0.797046. This does not establish a 20% suppression in an observed primordial density field. Oscillatory solutions, initial phases, and different start epochs matter.

The figure shows the scale dependence rather than asserting uniform suppression at every k or time. A Jeans-associated mass is not a calibrated minimum halo mass.

## 8. Checks completed

Running `python3 model.py` checks:

1. Standard Jeans limit at zero modification.
2. Positive-root residuals across six stiffness ratios.
3. Independent first-order density/phase integration against the derived second-order density equation at five wave numbers.
4. Numerical tolerance refinement at the same wave numbers.
5. Long-wavelength recovery of the matter-era dust growing mode.
6. Positive free kinetic dispersion over a test grid, supplementing the analytical positivity argument.
7. Agreement of the density/phase matrix determinant with the Jeans condition.

Independent evolution implementations agree to approximately 2e-9 relative error or better; root residuals are below 5e-14. These checks support the internal numerical implementation, not the empirical truth or fundamental consistency of the proposed EFT.

At the reference Jeans scale p/m is approximately 1.35e-5, supporting the nonrelativistic expansion. A proposed band p<=10M still gives local group speed approximately <=0.0271c and small rest-energy corrections for these parameters. No claim is made that this dispersion remains causal or physically valid at arbitrarily high momentum. Behavior of an actual ultraviolet completion is unresolved.

## 9. What this accomplishes and what remains

Accomplished: a precise replacement for the original ambiguous frozenness condition, an explicit effective action, a baseline-matched linear derivation, an analytic parameter-dependent discriminant, and reproducible computations.

Remaining: physical origin of M and the preferred frame; higher-operator control; relativistic completion; abundance and production history; coupled radiation/baryon evolution; CMB and Lyman-alpha likelihoods; halo evolution; parameter inference; and a demonstration that an observable feature survives degeneracies. Dark energy is separate in v0.1. The earlier master-mediator and entanglement claims are not assumed or proved here.

A falsifiable use of this benchmark is to fix m, M, abundance and initial conditions, compute full transfer functions and predictions for a specified dataset, and compare the likelihood against the same baseline without retuning. Negative results would constrain or reject that parameter choice. The unmodified limit M->infinity remains nested, so ruling out every finite effect requires specifying a finite parameter region or sensitivity target.

## References

- Marsh, *Non-linear hydrodynamics of axion dark matter: relative velocity effects and quantum forces* (2015): https://arxiv.org/abs/1504.00308
- Marsh, *Axion Cosmology* (2016): https://arxiv.org/abs/1510.07633
- Passaglia & Hu, *Accurate effective fluid approximation for ultralight axions* (2022): https://background.uchicago.edu/~whu/Papers/PasHu22.pdf
- Rubio et al., *Well-posed evolution of field theories with anisotropic scaling: the Lifshitz scalar field in a black hole space-time* (2023): https://arxiv.org/abs/2307.13041 — context for higher spatial derivatives and preferred-frame field theories, not a validation of this particular model.

## Reproduction and artifacts

    python3 model.py --output results

Dependencies: Python 3, NumPy, SciPy, Matplotlib. Exact tested package versions are in `environment.json`. Outputs are `results/results.json`, `results/jeans-scales.csv`, `results/matched-evolution.csv`, and the standalone figure `results/prediction.png` / `.pdf`.
