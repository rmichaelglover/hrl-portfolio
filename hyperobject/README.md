# C — Musical Hyperobject

Open index.html in a browser. Everything is local and self-contained; no server,
network dependency, or account is required. Click Play sound to enable audio.
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
