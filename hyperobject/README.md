# C — Musical Hyperobject

The primary index.html is now the first-person Projective Sound Field. Open it
in a browser and click Enable sound. It uses local field-model.js and field.js,
with no external runtime dependencies. The earlier structural interface is
preserved at structure.html. In that structural view, click Play sound.
Choose a chord or individual notes, adjust their relative weights, switch the
RGB/CMY palette, inspect all 220 trichords, or export the current state as JSON.

hyperobject.json is the machine-readable definition. It includes twelve A440
equal-tempered frequencies, the full orthogonal mode basis and coupling matrix,
the cube graph, all trichords, the seven diatonic triads, and modeling limits.

The object C is a named point with internal state, distinct from both the
empty set and the pitch class C. A normalized nonempty state occupies the
11-simplex. Empty selection is represented separately by all-zero weights.
Black/white are palette labels; they do not modify the oscillator dynamics.
Three-in-one is represented by chord membership. Undecidability is not yet
formalized. No religious mappings are included.

The cube is an organizational diagram, not a physical realization of the
general coupling matrix. The browser synthesizes that matrix's musical normal
modes directly. This is a constructed musical model, not a derivation of
fundamental string theory or evidence of dark-matter control.

To regenerate index.html and hyperobject.json after editing the sources:

    python3 build.py

Standard library only. No installation required.

## Projective Sound Field

The primary view uses a rectified stereo camera pair, with single-view mode,
rig translation/yaw, baseline, field of view, and visual slow motion. The 13
voices cover C4 through C5, including the eight diatonic octave notes. Colors
are the requested display palette; black mode changes only the two Cs.

Audio is equal-weight sine synthesis through stereo panners and a live output
analyser. Visual waves are slowed pressure traces; audio remains at the actual
frequencies. The null conductor exchanges dimensionless energy/matter tokens
with an explicit reservoir. Conversion uses c_model = 2 and preserves combined
energy-equivalent accounting. This is a toy realization of the proposed
point/wave hierarchy. The page states mathematical and physical distinctions.

Edit field-template.html for the primary page, template.html for the structural
page, then run build.py. Test the geometry and ledger with:

    node hyperobject/field-model.test.cjs
