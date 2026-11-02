---
layout: research-paper
title: The Dual-Spin Informaton Hypothesis
permalink: /cosmic-koan-dual-spin-informaton.html
---

# The Dual-Spin Informaton Hypothesis

## A trinary monopole sector, black-hole boundary data, and a testable bridge between geometry and information

**Michael Emanuel Glover**, independent researcher<br>
**with Cypher**, AI research and writing collaborator<br>
**Working paper · 2 November 2026**

> **Status.** This paper develops a speculative hypothesis, not an established particle model or a claim of experimental discovery. We distinguish established theory, the postulates introduced here, and consequences that would have to be derived or measured before the proposal could be considered a viable physical theory.

## Abstract

We formulate a research hypothesis around one proposed physical carrier, provisionally called the **informaton**, whose state admits both a spin-0 description and a spin-2 description. The proposal takes these as potentially simultaneous descriptions of one hypothesized species, rather than silently replacing it with two unrelated particles. In representation-theoretic terms, that claim requires a reducible state space containing scalar and tensor sectors, together with a dynamical account of why both sectors belong to one species and when they can communicate. A second postulate assigns the carrier a three-valued magnetic-charge label—negative, neutral, or positive—and locates its elementary source at a quantum-gravitational, effectively zero-dimensional black-hole core. We show how exterior magnetic flux could remain a well-defined observable even when the proposed source is hidden behind a horizon; we also make clear that general relativity does not establish a physical point-like singularity.

We connect this hypothesis to dark matter, dark energy, axion physics, black-hole information, and a proposed matter–dark-sector exchange cycle. The paper does not identify dark matter with gravitons, equate Shannon information with mass, or infer dark energy from a black-hole singularity. Instead, it defines these as conjectural links and gives them operational obligations: a common spectral pole, gauge-consistent scalar–tensor dynamics, a quantized and observable magnetic flux, a cosmologically viable abundance and equation of state, and predictions distinguishable from ΛCDM, axion models, and consistent massive-spin-2 theories. We give a minimal coupled-channel parametrization, a covariant conservation framework for sector exchange, a hierarchy of logical and physical trinary structures, and a staged falsification program. The result is a mathematically organized hypothesis whose most valuable immediate contribution is to state precisely what must be true for the unification idea to become physics.

**Keywords:** graviton; axion; information; magnetic monopole; black hole; dark matter; dark energy; spin; trinary logic; effective field theory; cosmology

---

## 1. Why formulate this hypothesis?

Our point of departure is an intuition that repeatedly appears at the boundary of gravitation, quantum theory, and information: what is inaccessible to a local observer can nevertheless constrain what the observer can know and do. Black-hole horizons make that tension especially concrete. They hide interior degrees of freedom while relating area, entropy, energy, and gravitational dynamics. The holographic principle and black-hole thermodynamics make this relation precise in restricted settings; they do not, by themselves, imply that gravity is literally information or that a new particle carries all information [16–20].

We want to ask a sharper question. Could one underlying carrier have a scalar/informational face and a tensor/gravitational face, with a three-state magnetic charge, and could the black-hole interior supply a natural setting for their unified description? We call the proposed carrier an **informaton**. The name records the hypothesis; it does not assert that such a particle has been detected.

This proposal joins several intuitions from our earlier working notes:

1. **The koan as a compatibility primitive.** A primitive compatibility relation may organize which descriptions can coexist. We treat this as a mathematical/metaphysical starting point, not a measured field. Any physical version must specify its state space, observables, units, and dynamics.
2. **Four cosmological poles.** Ordinary matter, ordinary energy, dark matter, and dark energy form a useful conceptual 2×2 map. In our earlier ontology work this was a generative classification and toy-model prompt, not evidence that cosmology contains four fundamental substances. Here it motivates asking whether one hidden sector can have distinct matter-like and vacuum-like regimes.
3. **Latent information at horizons.** A prior project framed hidden content through observational equivalence: states that no admissible exterior protocol can distinguish are equivalent for that observer. We retain this as an operational notion of “latent,” while avoiding the leap from hidden information to a new particle.
4. **A dark/light exchange cycle.** The image of matter and dark matter converting into one another, while dark energy and ordinary expansion evolve, is promoted here to a covariant source-term ansatz. It is explicitly conjectural.

The goal is neither to weaken the intuition nor to report it as fact. It is to turn the intuition into a sequence of mathematical obligations. A successful model must recover known physics in its tested regimes, have internally consistent degrees of freedom, and make at least one risky prediction that competing models do not make.

## 2. Epistemic levels and notation

We use three labels throughout:

- **Established framework:** a result or formalism supported by existing theory and observation, though still subject to its ordinary scope and assumptions.
- **Postulate of this paper:** an additional assumption made to define the proposed model.
- **Open derivation/test:** a consequence not yet obtained from the postulates, or an experiment/observation needed to assess it.

This distinction matters especially for the words *spin*, *information*, *singularity*, and *dark energy*. They have precise technical meanings that do not automatically match their metaphorical or theological meanings.

We use natural units (c=\hbar=1), metric signature ((-+++)), and rationalized electromagnetic conventions unless stated otherwise. (M_{\rm Pl}=(8\pi G)^{-1/2}) denotes the reduced Planck mass. Tensor indices are raised with (g_{\mu\nu}). The symbol (X) denotes the proposed informaton sector; (a) denotes a scalar field when discussing a conventional axion-like effective theory; (h_{\mu\nu}) denotes a spin-2 perturbation.

## 3. The central postulate: one carrier with two spin descriptions

### 3.1 What “spin zero and spin two” can mean precisely

For an isolated relativistic particle in flat spacetime, Wigner’s classification labels elementary one-particle states by irreducible unitary representations of the Poincaré group [1]. A definite-mass, definite-spin particle belongs to one such irreducible sector. A scalar is spin 0; a massless graviton in perturbative general relativity has helicities (+2) and (-2) [2]. A massive spin-2 particle has five physical polarizations, conventionally described by helicities (-2,-1,0,+1,+2). Its helicity-0 polarization remains part of a spin-2 representation; it is **not** a scalar spin-0 particle.

Therefore, “one particle is spin 0 and spin 2” cannot mean that a single irreducible Poincaré representation simultaneously has two different spin labels. We make the intended claim mathematically explicit instead:

> **Dual-spin postulate.** There is one underlying species (X) whose one-particle state space contains scalar and spin-2 sectors, and whose physical states may have nonzero amplitudes in both sectors.

At the level of a reducible representation, write

\[
\mathcal H_X=\mathcal H_{0}\oplus\mathcal H_{2},\qquad
|\Psi_X\rangle=\alpha|X_0\rangle+\beta_{+}|X_{2,+2}\rangle+\beta_{-}|X_{2,-2}\rangle,
\]

with normalization (|\alpha|^2+|\beta_+|^2+|\beta_-|^2=1) for the displayed massless tensor helicities. For a massive tensor sector the sum includes all five helicity states. The label “one species” then has to be made physical: for example, both channels must share a common pole or a symmetry-protected multiplet identity, and a specified interaction must relate their preparation, propagation, or decay. A direct sum alone is mathematically allowed but does not establish that the sectors are one particle in the physically meaningful sense.

The hypothesis is thus stronger than “there is a scalar and there is a graviton,” and more precise than treating *spin* as a poetic synonym for a perspective. It proposes one carrier with experimentally distinguishable channel labels and a dynamical identity connecting those channels. Whether nature permits that construction under Lorentz invariance, locality, unitarity, and the gauge redundancies of a massless spin-2 field is an open consistency question.

### 3.2 A coupled-channel diagnostic, not yet a fundamental law

In a background where two channels can propagate coherently, a minimal phenomenological model along propagation coordinate (\ell) is

\[
i\frac{d}{d\ell}
\begin{pmatrix}A_0\\A_2\end{pmatrix}
=
\begin{pmatrix}\Delta_0&\mu_{02}\\\mu_{02}^{*}&\Delta_2\end{pmatrix}
\begin{pmatrix}A_0\\A_2\end{pmatrix}.
\]

Here (\Delta_i) are channel phase advances per unit length, and (\mu_{02}) is a mixing amplitude with units of inverse length. If the matrix is Hermitian and constant, the two-channel conversion probability is

\[
P_{0\rightarrow2}(\ell)=
\frac{4|\mu_{02}|^2}{\delta^2+4|\mu_{02}|^2}
\sin^2\!\left(\frac{\ell}{2}\sqrt{\delta^2+4|\mu_{02}|^2}\right),
\qquad \delta=\Delta_0-\Delta_2.
\]

This equation is useful because it makes a testable quantity explicit. It is **not** a derivation of the informaton. A valid theory must derive (\Delta_i) and (\mu_{02}) from a covariant action or a controlled quantum-gravity approximation, identify the background tensors that permit mixing, and show that the constraints removing unphysical spin-2 polarizations remain intact. In Lorentz-invariant vacuum, scalar and transverse-traceless tensor sectors cannot simply mix linearly without additional structure: the representation content and gauge symmetry must be respected. Curvature, a horizon, a preferred background field, or a multiplet symmetry may be relevant, but naming one does not complete the derivation.

The first quantitative target is a **common spectral signature**: a shared mass/dispersion relation and a pole structure appearing in both an appropriate scalar correlator and a gauge-invariant tensor correlator. Without that, “one carrier” remains an interpretive identification of two fields.

## 4. Trinary structure: logical value is not magnetic charge

Our working framework has used three-valued logic, (\{\mathbf T,\mathbf U,\mathbf F\}), to represent true, unresolved, and false/incompatible claims. We retain it as a way to prevent unknown evidence from being forced into a binary verdict. It is a semantic/evidential structure, not a particle charge.

Separately, we introduce a physical three-state magnetic label:

\[
\tau\in\{-1,0,+1\},\qquad g_m=\tau g_0,
\]

where (g_0>0) is a magnetic-charge unit. This is a **postulate**, not a known fundamental spectrum. The three values denote monopole, neutral, and antimonopole sectors. A model must explain whether (\tau) is a superselection label, a conserved charge, or an internal degree of freedom that can change through interactions. It must also specify how charge conservation works in pair production, black-hole accretion, and Hawking evaporation.

The two trinities can coexist without being conflated:

| Structure | Values | Role | Status here |
|---|---|---|---|
| Epistemic logic | (\mathbf T,\mathbf U,\mathbf F) | Tracks supported, unresolved, and rejected propositions | Formal modeling choice |
| Magnetic label | (-1,0,+1) | Labels magnetic charge sectors | New physical postulate |
| Scalar/tensor channels | (0,2) | Labels Poincaré spin sectors | Established representation labels; proposed common species |

One may interpret the three physical sectors as a matter–geometry–information trinity, but that is an interpretation layered over the charge assignment. It is not licensed by the word “trinary” alone.

## 5. Magnetic charge and the black-hole core

### 5.1 Define the monopole by flux

The gauge-invariant magnetic charge is defined by flux through a closed two-surface (S^2):

\[
g_m=\int_{S^2}F,
\]

where (F) is the electromagnetic field-strength two-form. In a spherically symmetric exterior, one convention gives

\[
F_{\theta\phi}=\frac{g_m}{4\pi}\sin\theta,
\qquad B^r=\frac{g_m}{4\pi r^2}.
\]

The integral can be evaluated on an exterior sphere. If no magnetic current crosses the intervening region, Stokes’ theorem makes the flux independent of the sphere’s radius. A black hole may therefore carry an exterior magnetic-charge parameter even when any microscopic source is hidden behind its horizon. Magnetically charged black-hole solutions are established solutions of suitable Einstein–Maxwell systems [4–6]. They do **not** establish that a monopole is located at a physical point singularity.

Dirac’s argument relates electric and magnetic charge through quantization. In the rationalized natural-unit convention used here, one common form is

\[
e g_m=2\pi n,\qquad n\in\mathbb Z,
\]

with factors depending on the charge normalization and gauge conventions [3]. Our trinary spectrum would have to be compatible with this condition for every allowed electric charge. It could be a subset of the Dirac lattice; it cannot simply replace quantization with a three-valued label.

### 5.2 What a “zero-dimensional singularity” does and does not assert

Classical singularity theorems establish geodesic incompleteness under specified geometric and energy conditions; they do not establish that a singularity is a tiny material object with a known internal state [7]. A coordinate point in a classical solution is not a microscope image of a quantum core. We therefore phrase the premise carefully:

> **Core postulate.** In a completed quantum-gravitational description, the informaton’s magnetic source is associated with an effectively zero-dimensional core state inside, or replacing, the classical black-hole singular region.

“Zero-dimensional” here means no resolved spatial extent in the effective description, not a demonstrated literal point of infinite density. The horizon and exterior geometry can encode the measurable charges; the core’s microscopic realization remains unspecified. This distinction protects the proposal from claiming classical general relativity can describe the interior where its own assumptions fail.

We also avoid assuming that a magnetic source can be both strictly confined behind an event horizon and independently observed as a local object. An exterior observer tests its charge through flux, motion, lensing, and interactions. Whether the core itself is observable is a separate question.

### 5.3 Existing searches

Magnetic monopoles remain hypothetical. ATLAS has searched high-ionization tracks and set model-dependent limits in proton–proton data [21]. MoEDAL has used trapping detectors and, more recently, searched for monopoles produced through the Schwinger mechanism in the strong fields of heavy-ion collisions [22]. These null results constrain production and mass ranges under assumptions about spin, charge, kinematics, and cross sections; they neither prove nonexistence at all masses nor give positive evidence for our informaton. A black-hole-bound relic could evade collider searches while still facing astrophysical, cosmological, and charge-discharge constraints.

## 6. Effective field theory: what we can write down now

A conventional scalar axion-like sector coupled to gravity and gauge fields may be represented schematically as

\[
S_{\rm EFT}=\int d^4x\sqrt{-g}\left[
\frac{M_{\rm Pl}^2}{2}R-\frac14F_{\mu\nu}F^{\mu\nu}
-\frac12(\nabla a)^2-V(a)
+\frac{c_\gamma}{4f_a}aF_{\mu\nu}\widetilde F^{\mu\nu}
+\frac{c_g}{4f_a}aR_{\mu\nu\rho\sigma}\widetilde R^{\mu\nu\rho\sigma}
\right]+S_{\rm matter}.
\]

Here (a) is a pseudoscalar, (f_a) a coupling scale, (c_\gamma,c_g) dimensionless coefficients, and tildes denote dual tensors. This is a familiar effective-field-theory pattern: axion-like fields can couple to gauge and gravitational topological densities. It supplies a plausible **scalar channel** and possible interactions with electromagnetic fields and curved spacetime. It does not, by itself, make (a) a graviton or establish one scalar–tensor particle.

In perturbative gravity, write

\[
g_{\mu\nu}=\bar g_{\mu\nu}+\kappa h_{\mu\nu},\qquad
\kappa=\sqrt{32\pi G}.
\]

The massless tensor fluctuation (h_{\mu\nu}), after gauge constraints, carries two helicities. To unify (a) and (h_{\mu\nu}) as channels of (X), the theory needs more than placing both symbols in one action. It needs:

1. a symmetry or dynamical identity explaining why the sectors are one species;
2. a common pole or controlled multiplet relation in correlation functions;
3. a covariant interaction that mixes the channels without violating diffeomorphism/gauge invariance;
4. a constraint analysis showing no negative-norm or unstable extra modes;
5. a low-energy limit reproducing general relativity, axion bounds, and tested gravitational-wave propagation.

If the tensor channel is massive, it must be treated as a massive spin-2 theory, not as the ordinary massless graviton. Generic nonlinear massive spin-2 theories carry a Boulware–Deser ghost; ghost-free constructions such as Hassan–Rosen bimetric gravity demonstrate how restrictive the consistent theory space is [9]. The scalar helicity of a massive spin-2 field is still not the scalar axion channel, so a dual-spin model must count degrees of freedom explicitly.

## 7. Dark matter, dark energy, and the proposed exchange cycle

### 7.1 Keep the observational roles distinct

Dark matter and dark energy are names for different inferred roles in cosmological models. Dark matter clusters and contributes approximately pressureless gravitating density on large scales; dark energy is smooth enough, in the standard description, to drive late-time accelerated expansion. The baseline (\Lambda\)CDM model fits a broad set of cosmological observations remarkably well [10]. That success does not reveal the microphysical identity of dark matter, nor does it prove the cosmological constant is the only possible explanation of acceleration.

Recent DESI DR2 analyses have sharpened comparisons among dark-energy histories. The 2026 Ly\(\alpha\) full-shape analysis reports constraints that can shift the significance of evolving-(w) preferences when combined with external CMB and supernova datasets; those preferences depend on the data combination and model parameterization and do not constitute a discovery of dynamical dark energy [11]. We therefore treat evolving dark energy as an empirical question, not a premise that our cycle has already answered.

The Bullet Cluster and related merging systems provide important evidence that the dominant gravitating mass can be spatially offset from collisional baryonic plasma [12]. This supports a nonluminous gravitating component in standard interpretations. It does not identify that component as gravitons, axions, monopoles, or informatons.

### 7.2 The four-pole map

Our prior ontology names four observational/interpretive poles:

| | Matter-like | Energy-like |
|---|---|---|
| Ordinary/visible sector | Baryons, leptons, radiation-coupled fields | Radiation and ordinary field energy |
| Dark/gravitationally inferred sector | Dark matter phenomenology | Dark-energy/acceleration phenomenology |

This table is a conceptual map, not a claim of four fundamental substances. In particular, “energy” is not a substance alongside matter in the same sense: in relativity, energy is a component of stress-energy and depends on the observer’s frame. The table is useful if it helps us track which observables a proposed component must reproduce.

One hypothesis is that (X) has regimes rather than four unrelated identities: a long-lived, cold, clustering state could appear matter-like, while a slowly varying coherent or vacuum-like state could contribute to acceleration. But these behaviors are sharply constrained. A component cannot act like cold dark matter at galactic and CMB epochs and like dark energy at late times without a specified mechanism, transition history, perturbation theory, and observational fit.

### 7.3 Covariant exchange as an explicit conjecture

General relativity imposes local covariant conservation of total stress-energy:

\[
\nabla_\mu T_{\rm tot}^{\mu\nu}=0.
\]

For interacting sectors, individual stress tensors may exchange energy and momentum while the sum remains conserved. A three-sector bookkeeping model can be written

\[
\nabla_\mu T_i^{\mu\nu}=Q_i^\nu,\qquad
\sum_i Q_i^\nu=0,
\]

where (i\in\{X,\mathrm{vis},\mathrm{DE}\}\). In a homogeneous FLRW background, a simple time-directed exchange ansatz is

\[
\dot\rho_X+3H(\rho_X+p_X)=-Q,\qquad
\dot\rho_{\rm vis}+3H(\rho_{\rm vis}+p_{\rm vis})=Q,
\]

with additional terms if dark energy is an independent fluid. The function (Q(t,\rho_i,H,\ldots)) is not fixed by conservation; it is new model content. It must arise from a Lagrangian or controlled open-system limit and be constrained by expansion history, structure growth, CMB anisotropies, lensing, and laboratory/astrophysical bounds.

This formalism gives mathematical shape to our “figure-eight” image of matter and dark matter exchanging states. It does **not** show that dark matter eats ordinary matter, or vice versa. Any such conversion rate must satisfy particle number/charge accounting, entropy production constraints, and existing limits on energy injection. Cosmological “total energy of the universe” also requires care in a time-dependent spacetime; local covariant conservation is the robust statement, while a globally conserved energy need not exist in a generic expanding FLRW geometry.

### 7.4 Axions, gravitons, and candidate identities

Axions were motivated by the Peccei–Quinn solution to the strong-CP problem; invisible-axion cosmology also makes axions plausible dark-matter candidates [13–15]. This establishes a serious theoretical and observational research program, not an identity between axions and gravitons. Likewise, a massless graviton mediates gravity in perturbative quantum descriptions but does not automatically behave as cold dark matter: an isotropic population of freely propagating relativistic massless quanta has radiation-like equation of state \(w=1/3\), not the clustering, pressureless behavior inferred for cold dark matter.

Massive spin-2 fields have been studied as dark-matter candidates, including gravitationally produced candidates [8,23]. Such a particle is not the standard massless graviton, and its viability depends on a consistent interaction theory, production history, lifetime, abundance, and structure constraints. A future informaton model could in principle link an axion-like scalar mode and a tensor mode; it must show how its degrees of freedom and cosmological state avoid simply relabeling two known candidate classes.

### 7.5 Conformal cycles and recurrence

Penrose’s conformal cyclic cosmology proposes a relationship between the remote future of one cosmological aeon and the Big Bang boundary of another, with strong assumptions about conformal structure and the fate of mass scales [24]. It is conceptually adjacent to our desire for a “kinder, gentler” cycle, but it does not imply a periodic interchange of dark and luminous matter, nor does it establish Nietzschean eternal recurrence as a physical law. In our proposal, cyclic language becomes physics only if a dynamical map between aeons is defined and yields observable consequences consistent with entropy, perturbation growth, and the measured expansion history.

## 8. Information, entropy, and the “ground truth” metaphor

Shannon information quantifies uncertainty in a specified probability distribution; for discrete outcomes, (H(X)=-\sum_xp(x)\log_2p(x)) bits [16]. It does not measure semantic truth, understanding, or mass-energy without a physical encoding and an operational protocol. Landauer’s principle connects logically irreversible computation to a minimum heat cost under specified thermodynamic conditions [17]. Bekenstein–Hawking entropy relates black-hole horizon area to entropy, and the holographic principle suggests bounds on information accessible to a region [18–20]. These are substantive bridges between information and physics, but none says that a graviton is a bit or that every unobserved degree of freedom is dark matter.

We can retain “ground truth” as a philosophical name for an observer-independent structure only if we keep it distinct from measurable information. A physical **informaton** must be associated with a Hilbert space, observables, state preparation, and a channel capacity or entropy accounting that can be tested. Our prior observational-equivalence idea provides one possible operational tool: two interior states (s_1,s_2) are equivalent for an exterior observer if every admissible exterior measurement protocol gives the same outcome distributions. Then the exterior theory predicts only the equivalence class ([s]), not a uniquely recoverable interior microstate. This is a precise statement about access, not evidence for an extra particle.

The present hypothesis adds a possible carrier (X) to that framework. It would be an informational degree of freedom in a physical sense only if it transports or stores a quantifiable state variable. To make that claim meaningful, we must identify:

- what system is encoded (the scalar/tensor state, magnetic sector, or black-hole microstate);
- which observer and measurement algebra define accessible information;
- how entropy and energy change under encoding, interaction, and coarse-graining;
- whether the carrier’s information is recoverable after black-hole evaporation;
- how unitarity or its replacement is realized.

“The koan is the graviton” can therefore be retained as a compact philosophical axiom within our metaphysics, while the physical theory asks whether a compatibility functional (K(\psi,\phi)) can be operationally defined and whether its excitations correspond to (X). A mathematical object becomes a physical field only after we state its domain, transformation law, coupling, and observable consequences. No appeal to mystery can substitute for those definitions.

## 9. Falsifiable consequences and a research sequence

The proposal currently has no fitted parameter set and makes no unique numerical prediction. Its immediate scientific value is to define a sequence of possible failure points.

### Test 1: one species, two channels

Derive a covariant model with scalar and tensor correlators sharing a common pole or symmetry-protected multiplet. Compute the allowed channel conversion amplitude and its dependence on curvature, magnetic flux, or black-hole spin. A null result constrains (\mu_{02}); absence of a common pole or any dynamical identity would falsify the strong “one species” version while leaving a looser two-field analogy intact.

### Test 2: degree-of-freedom and stability audit

Count propagating degrees of freedom around Minkowski, cosmological, and black-hole backgrounds. Demonstrate positive kinetic energy, hyperbolicity, causal propagation within the theory’s domain, and absence of ghosts, tachyonic instabilities, and strong-coupling breakdown below the cutoff. Failure at this step is a theoretical no-go for the proposed effective model.

### Test 3: magnetic flux and trinary charge

Specify (g_0), obey Dirac quantization, and compute the exterior field, pair-production rate, and black-hole discharge timescale. Search for the predicted flux or trapped monopole signatures. If the (\tau=\pm1) states have no distinct gauge-invariant observable, the physical trinary charge postulate has no empirical content.

### Test 4: cosmological dark matter behavior

Compute production and relic density, free-streaming length, self-interactions, decay rate, and perturbation transfer function. The model must reproduce the observed cold, clustering component and the gravitational lensing/CMB/large-scale structure data. A massless spin-2 population alone fails this requirement because its homogeneous equation of state is radiation-like.

### Test 5: dark-energy history and exchange

Derive (Q_i^\nu) and the effective equation of state (w(z)=p_{\rm DE}/\rho_{\rm DE}) from the same action. Jointly fit CMB, BAO, supernova, lensing, and growth data, reporting parameter degeneracies and priors. Compare evidence against ΛCDM and established interacting-dark-sector models. A flexible phenomenological (Q(z)) fit without a microphysical derivation is not evidence for the informaton.

### Test 6: black-hole information bookkeeping

Specify the informaton’s role in horizon entropy and evaporation. Show how generalized entropy changes and whether the outgoing state remains unitary. A claim that (X) “contains information” is incomplete until it explains what information, relative to which algebra, and how it is recovered or rendered inaccessible.

### Test 7: discriminating signal

Identify at least one measurable feature that ordinary axion-like particles, massless gravitons, massive spin-2 models, and ΛCDM do not predict in the same parameter regime. Candidate observables include correlated scalar/tensor spectral features, a characteristic gravitational-wave polarization/dispersion relation, a monopole-linked black-hole ringdown correction, or a specific redshift dependence in matter–dark-sector exchange. The signal must be computed before it is searched for, and selection effects must be modeled.

## 10. Limitations, risks, and the strongest version of the claim

Several obstacles are foundational rather than cosmetic.

1. **Representation mismatch:** spin 0 and spin 2 are different irreducible sectors. A reducible superposition is possible, but a shared species identity and conversion law need explanation.
2. **Massless spin-2 consistency:** a graviton-like tensor mode carries gauge redundancy and universal coupling constraints. Arbitrary extra interactions can violate consistency or introduce unwanted polarizations.
3. **Magnetic-source ontology:** a classical black-hole singularity is not an experimentally characterized point object. A quantum core is a postulate, and an exterior monopole charge does not locate a microscopic source.
4. **Dark-sector degeneracy:** a new field can often be tuned to imitate ΛCDM. The proposal needs a distinctive prediction, not only interpretive compatibility.
5. **Information-language ambiguity:** entropy, Shannon information, algorithmic information, semantic knowledge, and metaphysical truth are different concepts. A unified theory must state which one it uses at each step.
6. **No evidence of detection:** current searches have not established magnetic monopoles or an informaton. Cosmological observations support dark components phenomenologically, not the specific identity proposed here.

The strongest defensible claim at this stage is therefore:

> A single underlying sector with scalar and spin-2 channels, a quantized three-state magnetic charge, and a black-hole-associated source is a coherent research hypothesis only if its reducible representation, gauge-invariant dynamics, degree-of-freedom count, and phenomenology can all be made mutually consistent. The equations in this paper define useful targets; they do not yet constitute that completion.

This is not a retreat from the original idea. It specifies the work required for the idea to survive contact with mathematics and observation. A bold hypothesis becomes stronger when its failure conditions are explicit.

## 11. Conclusion

We have formulated the proposed informaton as one hypothesized carrier whose state can be described through scalar and tensor channels, and whose magnetic sector is assigned three possible charge values. A black-hole core is proposed as the source or organizing locus, but the operational observable is exterior flux and the quantum structure remains unknown. We have placed the idea beside axion theory, graviton physics, dark-sector cosmology, black-hole thermodynamics, and information theory without conflating their established results.

The key mathematical move is to read “spin zero and spin two simultaneously” as a claim about one species represented in a reducible state space, rather than as a claim that one irreducible particle representation has two incompatible spin labels. The key physical move is to require a shared pole and derived mixing law. The key cosmological move is to express matter–dark-sector exchange through conserved stress-energy source terms and demand a joint data fit. The key epistemic move is to distinguish a fruitful metaphysical axiom from a measured physical law.

Our proposal is ambitious because it tries to connect geometry, information, magnetic charge, and cosmic evolution in one framework. Its next productive step is not another layer of analogy: it is a minimal covariant model with a declared field content, a complete constraint analysis, and one quantitative prediction. If such a model exists, the informaton hypothesis can earn its place in physics. If it does not, the formalization will show us exactly which part of the vision remains philosophical, which part can be retained as an effective description, and which part must be revised.

## Author contributions and provenance

**Michael Emanuel Glover** originated the central proposal that spin 0 and spin 2 may be simultaneous descriptions of one hypothesized particle; the magnetic-monopole-at-a-black-hole-core picture; the trinary framing; and the broader intuitions linking information, dark matter, dark energy, cyclical exchange, and cosmological recurrence. He supplied the prior conceptual framework and research direction.

**Cypher (AI research and writing collaborator)** organized the proposal against established representation theory, field theory, black-hole physics, and cosmology; made the dual-spin claim explicit as a reducible state-space hypothesis; derived the illustrative two-channel probability and covariant exchange bookkeeping; separated epistemic trivalence from magnetic charge; and drafted the consistency tests and literature synthesis. These contributions are analytical and editorial, not experimental, and do not imply independent authorship claims beyond this collaboration.

## Declarations

**Competing interests:** None declared.<br>
**Funding:** No external funding is declared for this working-paper draft.<br>
**Data/code:** No new experimental dataset or numerical simulation is presented.<br>
**Publication status:** Working paper; not peer reviewed. Claims and references should be checked by domain specialists before journal submission.

## References

1. E. P. Wigner, “On Unitary Representations of the Inhomogeneous Lorentz Group,” *Annals of Mathematics* **40** (1939), 149–204. [https://doi.org/10.2307/1968551](https://doi.org/10.2307/1968551).
2. S. Weinberg, “Photons and Gravitons in S-Matrix Theory: Derivation of Maxwell’s and Einstein’s Field Equations,” *Physical Review* **135** (1964), B1049–B1056. [https://doi.org/10.1103/PhysRev.135.B1049](https://doi.org/10.1103/PhysRev.135.B1049).
3. P. A. M. Dirac, “Quantised Singularities in the Electromagnetic Field,” *Proceedings of the Royal Society A* **133** (1931), 60–72. [https://doi.org/10.1098/rspa.1931.0130](https://doi.org/10.1098/rspa.1931.0130).
4. H. Reissner, “Über die Eigengravitation des elektrischen Feldes nach der Einsteinschen Theorie,” *Annalen der Physik* **355** (1916), 106–120. [https://doi.org/10.1002/andp.19163550905](https://doi.org/10.1002/andp.19163550905).
5. E. Newman, E. Couch, K. Chinnapared, A. Exton, A. Prakash, and R. Torrence, “Metric of a Rotating, Charged Mass,” *Journal of Mathematical Physics* **6** (1965), 918–919. [https://doi.org/10.1063/1.1704351](https://doi.org/10.1063/1.1704351).
6. K. Lee, V. P. Nair, and E. J. Weinberg, “Black Holes in Magnetic Monopoles,” *Physical Review D* **45** (1992), 2751–2761. [https://doi.org/10.1103/PhysRevD.45.2751](https://doi.org/10.1103/PhysRevD.45.2751); [arXiv:hep-th/9112008](https://arxiv.org/abs/hep-th/9112008).
7. S. W. Hawking and R. Penrose, “The Singularities of Gravitational Collapse and Cosmology,” *Proceedings of the Royal Society A* **314** (1970), 529–548. [https://doi.org/10.1098/rspa.1970.0021](https://doi.org/10.1098/rspa.1970.0021).
8. C. Cai, C. Cacciapaglia, and H.-H. Zhang, “Massive Gravitons as Feebly Interacting Dark Matter Candidates,” *Physical Review Letters* **128** (2022), 081806. [https://doi.org/10.1103/PhysRevLett.128.081806](https://doi.org/10.1103/PhysRevLett.128.081806).
9. S. F. Hassan and R. A. Rosen, “Bimetric Gravity from Ghost-free Massive Gravity,” *Journal of High Energy Physics* **02** (2012), 126. [https://doi.org/10.1007/JHEP02(2012)126](https://doi.org/10.1007/JHEP02(2012)126); [arXiv:1109.3515](https://arxiv.org/abs/1109.3515).
10. Planck Collaboration, N. Aghanim et al., “Planck 2018 Results. VI. Cosmological Parameters,” *Astronomy & Astrophysics* **641** (2020), A6. [https://doi.org/10.1051/0004-6361/201833910](https://doi.org/10.1051/0004-6361/201833910); [arXiv:1807.06209](https://arxiv.org/abs/1807.06209).
11. DESI Collaboration, “DESI DR2 Results IV: Alcock–Paczynski Measurements from the Lyman Alpha Forest and Cosmological Constraints,” arXiv:2607.27410 (2026). [https://arxiv.org/abs/2607.27410](https://arxiv.org/abs/2607.27410). See also [DESI DR2 publication collection](https://data.desi.lbl.gov/doc/papers/dr2/). Results are data-combination and model dependent.
12. D. Clowe, M. Bradac, A. H. Gonzalez, M. Markevitch, S. W. Randall, C. Jones, and D. Zaritsky, “A Direct Empirical Proof of the Existence of Dark Matter,” *Astrophysical Journal Letters* **648** (2006), L109–L113. [https://doi.org/10.1086/508162](https://doi.org/10.1086/508162); [arXiv:astro-ph/0608407](https://arxiv.org/abs/astro-ph/0608407).
13. R. D. Peccei and H. R. Quinn, “CP Conservation in the Presence of Pseudoparticles,” *Physical Review Letters* **38** (1977), 1440–1443. [https://doi.org/10.1103/PhysRevLett.38.1440](https://doi.org/10.1103/PhysRevLett.38.1440).
14. S. Weinberg, “A New Light Boson?” *Physical Review Letters* **40** (1978), 223–226. [https://doi.org/10.1103/PhysRevLett.40.223](https://doi.org/10.1103/PhysRevLett.40.223).
15. J. Preskill, M. B. Wise, and F. Wilczek, “Cosmology of the Invisible Axion,” *Physics Letters B* **120** (1983), 127–132. [https://doi.org/10.1016/0370-2693(83)90637-8](https://doi.org/10.1016/0370-2693(83)90637-8).
16. C. E. Shannon, “A Mathematical Theory of Communication,” *Bell System Technical Journal* **27** (1948), 379–423, 623–656. [https://doi.org/10.1002/j.1538-7305.1948.tb01338.x](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x).
17. R. Landauer, “Irreversibility and Heat Generation in the Computing Process,” *IBM Journal of Research and Development* **5** (1961), 183–191. [https://doi.org/10.1147/rd.53.0183](https://doi.org/10.1147/rd.53.0183).
18. J. D. Bekenstein, “Black Holes and Entropy,” *Physical Review D* **7** (1973), 2333–2346. [https://doi.org/10.1103/PhysRevD.7.2333](https://doi.org/10.1103/PhysRevD.7.2333).
19. S. W. Hawking, “Particle Creation by Black Holes,” *Communications in Mathematical Physics* **43** (1975), 199–220. [https://doi.org/10.1007/BF02345020](https://doi.org/10.1007/BF02345020).
20. R. Bousso, “The Holographic Principle,” *Reviews of Modern Physics* **74** (2002), 825–874. [https://doi.org/10.1103/RevModPhys.74.825](https://doi.org/10.1103/RevModPhys.74.825); [arXiv:hep-th/0203101](https://arxiv.org/abs/hep-th/0203101).
21. ATLAS Collaboration, “Search for Magnetic Monopoles and Stable Particles with High Electric Charges in \(\sqrt{s}=13\) TeV pp Collisions with the ATLAS Detector,” *Journal of High Energy Physics* **11** (2023), 112. [https://doi.org/10.1007/JHEP11(2023)112](https://doi.org/10.1007/JHEP11(2023)112).
22. B. Acharya et al. (MoEDAL Collaboration), “MoEDAL Search in the CMS Beam Pipe for Magnetic Monopoles Produced via the Schwinger Effect,” *Physical Review Letters* **133** (2024), 071803. [https://doi.org/10.1103/PhysRevLett.133.071803](https://doi.org/10.1103/PhysRevLett.133.071803); [arXiv:2402.15682](https://arxiv.org/abs/2402.15682).
23. E. Verner et al., “Gravitational Production of Massive Spin-2 Particles During Reheating,” *Physical Review D* **113** (2026), 123503. [https://doi.org/10.1103/3st2-jhx5](https://doi.org/10.1103/3st2-jhx5); [arXiv:2512.19041](https://arxiv.org/abs/2512.19041). Model-dependent theoretical study.
24. R. Penrose, “Before the Big Bang: An Outrageous New Perspective and Its Implications for Particle Physics,” *Proceedings of the EPAC 2006* (2006), 2759–2762; see also *Cycles of Time: An Extraordinary New View of the Universe* (Bodley Head, 2010). [arXiv:hep-th/0609447](https://arxiv.org/abs/hep-th/0609447).
25. J. D. Bekenstein, “Universal Upper Bound on the Entropy-to-Energy Ratio for Bounded Systems,” *Physical Review D* **23** (1981), 287–298. [https://doi.org/10.1103/PhysRevD.23.287](https://doi.org/10.1103/PhysRevD.23.287).
26. J. A. Wheeler, “Information, Physics, Quantum: The Search for Links,” in W. H. Zurek (ed.), *Complexity, Entropy, and the Physics of Information* (Addison-Wesley, 1990), 3–28. Conceptual perspective, not evidence for a specific particle.
27. D. Deutsch, “Constructor Theory of Information,” *Proceedings of the Royal Society A* **471** (2015), 20140540. [https://doi.org/10.1098/rspa.2014.0540](https://doi.org/10.1098/rspa.2014.0540).

## Selected prior working notes

These are internal conceptual predecessors, not peer-reviewed evidence and not independent scientific citations:

- Michael Emanuel Glover, [*Framework: Compatibility, Relaxation, and the Koan*](FRAMEWORK.md).
- Michael Emanuel Glover, [*Projective Horizon: Observational Equivalence and Latent Information*](attack-on-christendom/projective-horizon/paper-01.md).
- Glover portfolio, [*Genesis ontology builder*](genesis/build_ontology.py) and associated ordinary/dark matter-energy “four poles” visualization.
- Glover portfolio, [*Light / self-gravitating light concept study*](genesis/light/index.html).
- Glover portfolio, [*Energy: diversity and unity*](genesis/energy/index.html).
