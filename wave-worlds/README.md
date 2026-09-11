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
