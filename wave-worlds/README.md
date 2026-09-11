# Wave Worlds

A first-person comparison of air, water, and a flat air-water interface.
Open index.html in a browser; audio requires Enable sound. Dependencies are
local JavaScript only, including the existing musical note palette.

Select any subset of the three worlds. All share one visual clock; switching
worlds does not reset it. Emitters control physical input. Listening controls
mute air/water probe channels without changing the simulated fields. Hidden
worlds do not contribute to audio. Master sound and visual time are independent.

model.js implements linear, lossless, normal-incidence plane-wave paths,
reflection/transmission coefficients, and energy-normalized pressure signals.
The mixed field includes both directions and coherent superposition. Web Audio
uses per-path delays and signed gains to retain reflection phase. Material
constants, coordinates, approximation limits, and display scaling are stated
on the page. No surface-wave or full fluid simulation is claimed.

Tests:

    node wave-worlds/model.test.cjs
    node wave-worlds/app.test.cjs

Browser verification also covers real audio samples, separate monitor mutes,
both sources off, all worlds hidden, and the mobile layout.

## Movable box

Enable Add box, then choose a closed shell, a five-face shell with a selectable
opening, or one square face. XYZ and size sliders share a pose across worlds.
Each note occupies an axial lane at x = (note_index - 6) * 0.35 m, y = -0.35 m.
Both rendering and audio sample obstaclePaths at that lane. Ideal rigid faces
reflect pressure with gain +1 and transmit nothing. The ray tracer follows up
to four wall/interface encounters, retaining mixed-medium gains and delays.
It is not a 3D wave solver: parallel faces do not scatter, diffraction and late
reverberation are omitted, and the box does not contain a different fluid.
Paths are cached until geometry changes. Audio keeps fixed path slots and
smooths gains/delays during edits. Geometry changes preserve visual time.
