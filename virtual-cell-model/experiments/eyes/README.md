# A pair of Eyes, an observer, and a reusable concept

Originating framework and project direction: **Michael Emanuel Glover**. The
attended-integration and concept-retirement interpretations develop Michael's
proposals. The assistant contributed literature retrieval, C++ implementation,
verification, analysis and documentation.

This increment adds two value-owned Eyes to Alex's existing Body. Each contains
an Organ with three effective retinal cells. A physical optical window couples
the external scene to a rod-like cascade; retinal ganglion output reaches the
existing Brain through delayed connections. Alex's observer estimates source
rather than receiving the simulator's source labels.

## Ownership and the first C++ lesson

```
PersonModel
  HomoSapiens Alex
    Will
    Body
      Brain, Heart, Lungs, Skin, Mouth
      optional<array<Eye, 2>>
        Eye -> Organ -> Tissue -> receptor, ON bipolar, ganglion cells
      NervousSystem -> body-local cell IDs and queued events
  BoundaryObserver, AttendedSelfModel, percept records
```

The Body has seven organ/region components and sixteen electrical cells in this
example. Eye cells participate in the same electrical stepping and routing as
the existing body cells; they are not separately owned copies in the graph.
Ordinary values, `std::array`, `std::optional` and containers manage lifetimes.
There is no manual initialization/shutdown or new model-level owning pointer.
The older cognitive-memory implementation retains its existing ownership design.

```cpp
auto model = virtual_cell::vision::make_seeing_alex();
auto& body = model.alex.human().body();

body.eye(0).window().set_open(false); // close the left optical window
body.eye(1).window().set_open(true);  // keep the right one open
```

The optical scene is outside Alex, within our simulated environment. Photons
travel from its emitters into an eye's aperture. The model does not require an
undefined region outside the simulated environment itself.

## Physical light and the reference frame

Each emitter is an isotropic point source with position in metres, radiant power
in watts and wavelength in nanometres. Each optical window owns a classical
position/orientation reference frame and a finite forward field of view.

```
photon_energy = h*c/wavelength
incident_rate = (power/photon_energy) * pupil_area*cos(angle)/(4*pi*distance^2)
```

This is a small-aperture far-field approximation; sources closer than ten pupil
diameters are rejected. A forward-field and aperture test can reject the source.
Pupil area is pi*d^2/4. Closing the window admits zero external photons.
Photons incident over an interval are Poisson sampled. Transmission and
photoisomerization are separate binomial thinning stages. Counts obey
`photoevents <= transmitted <= incident`; the audit retains incident energy.
The source is a stationary radiance reservoir, with Poisson emission statistics,
not a finite inventory of individually traced rays.

The example uses a 3 mm pupil, 0.8 transmission and peak conversion probability
0.5. An illustrative Gaussian sensitivity is centred at 500 nm with width 70 nm.
Left and right pupil origins are at x=-0.032 and +0.032 m, facing +z. These are
chosen model parameters. The current retina pools light into one rod-like
channel per eye. It does not form images, resolve colours, infer stereo depth,
reconstruct refraction or simulate human development. Lens/cornea throughput is
represented by transmission, rather than separate unimplemented anatomical
classes. Additional retinal channels and calibrated optics can extend this.

## Conserved vertebrate organization, with explicit reductions

The architecture preserves photopigment conversion, graded receptor voltage,
an ON-pathway sign inversion, spiking ganglion output and a Brain connection.
We use this conserved functional organization as a natural-history guide, not
as a simulation of evolution, embryogenesis, or an assertion that development
recapitulates an ancestral sequence.

[Baylor, Lamb & Yau (1979)](https://doi.org/10.1113/jphysiol.1979.sp012716)
measured quantal responses in toad rods. [Baylor, Nunn & Schnapf (1984)](https://doi.org/10.1113/jphysiol.1984.sp015518)
measured primate rod photocurrent, noise and wavelength sensitivity, including
photon-like endogenous events. These motivate event statistics and the need to
separate receptor activation from an inference about its cause. The 0.006/s
endogenous-event starting value is primate-inspired, not a fitted human rate.

[Fesenko, Kolesnikov & Lyubarsky (1985)](https://doi.org/10.1038/313310a0)
demonstrated cGMP-dependent cationic conductance in excised rod membrane patches,
providing primary evidence for the conductance link represented here.

The reduced cascade is:

```
photoisomerization or endogenous activation -> active opsin -> PDE
PDE increases normalized cGMP hydrolysis
lower cGMP -> lower CNG conductance -> receptor hyperpolarization
ON bipolar graded response -> ganglion spikes -> delayed Brain input
```

The active-opsin, PDE and normalized-cGMP states use decay/recovery constants of
50, 50 and 100 ms; PDE gain is 0.03/ms. The equations use interval-average opsin
and locally frozen PDE in a sequential exponential update. They are reduced,
unfitted kinetics, not a calibrated rhodopsin/transducin/PDE6 biochemical network.
The spectral curve, response gain and effective cell parameters are illustrative.
Cones, OFF pathways, horizontal/amacrine cells, rods' full adaptation feedback,
bleaching, retinoid recycling, and molecular stoichiometry remain future layers.

At dark equilibrium, the receptor has a 2 nS conductance reversing at -70 mV and
1.5 nS CNG conductance reversing at 0 mV. Their weighted electrical equilibrium
is -40 mV. Light closes CNG conductance, so the same current-balance law drives
voltage toward more negative values. Reduced ON-bipolar and ganglion current
couplings have gains of 10 and 5 pA/mV; these stand in for graded synaptic
chemistry. A photosensitive cell does not directly fire a photon-triggered spike.

## Internal and external: inference without an origin oracle

`retinal_observation()` supplies visual ganglion-event counts over a specified
interval, alongside a supplied interoceptive-event count. Interoceptive encoding
is an observation interface here; the model does not yet generate a calibrated
heartbeat or visceral afferent signal. Optical photon/endogenous audit counters
are for experiment logging and are excluded from the inference function's input.
This is an explicit software interface, not a security barrier around the Body.

`BoundaryObserver` compares two illustrative hypotheses with independent Poisson
likelihoods. External-dominant expectations are 12 visual and 2 interoceptive
events/s; internal-dominant expectations are 2 and 8 events/s. Its starting prior
is 0.5. It scales expectations to the observation duration and returns a posterior.
These are chosen hypotheses, not learned human likelihoods or accuracy claims.
Identical observed features give identical attribution regardless of their
simulator origin. Photon-like internal events can therefore be misattributed.
Machine probabilities near zero/one can round to those values; they are not
proofs of causal certainty.

The endogenous-control experiment triggers twenty receptor activations with
closed windows and no external photons. This is a deliberate research
perturbation, not a normal dark-noise frequency or a psychiatric diagnosis.

## Quantum reference frames: the intended connection

[Fields, Glazebrook & Levin (2022), *Neurons as hierarchies of quantum reference frames*](https://arxiv.org/abs/2201.00921)
proposes a quantum-information framework relating hierarchical physical
measurement systems, inference and memory. We borrow the design questions about
physical measurement frames and observer-relative representations. Our frames,
Poisson optics, Bayesian observer and integration rule are classical. We have
not implemented that paper's quantum states, coherence assumptions, operators
or reference-frame transformations. The C++ model does not establish or test
those quantum claims.

## Will and “what one beholds, one gradually becomes”

Michael's proposed principle has a limited operational implementation:

```
feature_next = feature + eta*attention*(perceived_evidence - feature)
```

Perceived evidence is the external-source posterior times a normalized visual
count `n/(1+n)`. The default eta is 0.1. `Will` holds a chosen attention weight in
[0,1] and a Permit/Decline integration policy. This is an explicit hypothesis
about updating an attended self-representation, not a law that exposure changes
someone into the external object. An attended feature is a representation, not
an intrinsic value or a complete identity.

Declining integration leaves that feature unchanged while photons, receptor
chemistry, retinal spikes, source inference and the percept record continue.
No claim is made that voluntary refusal prevents implicit learning or all
physiological changes. A future motor policy may choose gaze or eyelid state;
the current Will is an attention/integration interface.

| Domain | Possible future mechanism | Relation to the current Will |
|---|---|---|
| Attending or declining a representation | Explicit attention and integration policy | Implemented at the representational level |
| Tool/prosthesis incorporation into a body model | Sensorimotor agreement and adaptive body schema | Needs additional measurements and state |
| Graft or implant immune rejection | Immune recognition, inflammation and tissue compatibility | A distinct biological controller |
| Medication response or rejection | Receptor action, tolerability, aversion and/or a personal decision | Distinct processes requiring distinct models |

The shared word “rejection” does not merge these mechanisms or imply that a
person chooses an immune response or an adverse drug effect.

## Concept retirement and reuse

Michael's computational interpretation of deconstruction distinguishes an
active representation's lifetime from the continued availability of its concept.
`retire_representation()` removes an active feature value and retains its named
definition. A later permitted observation can instantiate a fresh value from that
retained vocabulary. It does not resurrect the same C++ object or silently restore
its previous state. This is an operational analogy, not a historical claim about
Derrida or a general theorem of language.

## Reproduce and inspect

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
./build/vision_demo light
./build/vision_demo one-eye
./build/vision_demo closed
./build/vision_demo endogenous
./build/vision_demo decline
python3 experiments/eyes/analyze.py
```

[Four-panel report](EYES_OBSERVER_REPORT.pdf) · [Figure](eyes-observer.png) ·
[Summary](summary.json) · [Gradual C++ lesson](TUTORIAL.md)

Nine CTest suites include the previous work plus optical units and inverse-square
scaling, reference-frame orientation, Poisson means, event ledgers, receptor
polarity/recovery, paired ownership and copied states, optic routing, endogenous
ambiguity, posterior evidence direction, Will gating, and concept retirement/reuse.
The analysis verifies that permitting/declining integration produces exactly the
same physical trajectories and source estimates, with different representation
updates. The five empirical IMPase Python checks remain separate and available.

Each Eye owns independent optical and endogenous random streams. Closing one
window leaves the other eye’s optical realization unchanged under matched seeds.
Random distributions follow the standard-library implementation; a seed is
recorded for reproduction on the same toolchain. Different standard libraries
need not produce bit-identical stochastic traces.
