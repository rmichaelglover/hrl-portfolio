# GRRLE Strong / HyperObject

This page packages `grrle_strong.zip` from the user's Downloads directory as a reviewable portfolio exhibit. Archive SHA-256: `9a8fdab4bc95e072f27eec4259c5297f163b66eaf7f629c6fe843ee1a2f36dbf`.

The archive contained a self-contained Python implementation, a header-only C++ implementation, a C++ demo, and a README. The Python code was copied into `python/grrle.py`; the C++ code into `cpp/`. The source correction is in Python `deepen_and_check()`: `extra_depth` is validated and now controls repeated promotion passes. `python/test_grrle.py` was added for structural, boundedness, duality, depth, and validation checks.

## Verification

The original Python demo ran successfully and built 20 nodes across depths -2…2. The original C++ demo compiled with `g++ -std=c++17 -O2 -Wall -Wextra -pedantic` and ran successfully. The added Python tests pass. The default demo reaches the projection boundary quickly; its numerical convergence therefore means the chosen projected dynamics stopped changing, not that the system found physical truth.

The Python and C++ versions share the architecture but are not bit-for-bit equivalent: random generators, defaults, and update details differ. A future cross-language fixture suite should compare serialized initial trees, support values, and observables before treating them as interchangeable.

## Interpretation boundary

This is a computational substrate for recursive relaxation labeling. It does not derive a new physical law or validate the HyperStar of David as a physical object. Physics-facing work would need explicit dimensional compatibility, an emergent target, units, real measurements, held-out predictions, uncertainty calibration, and comparisons with established models. `strength()` is a perturbation diagnostic; it is not a probability of truth.

The recursive page uses a finite visualization and explains one sufficient decay condition for a hypothetical infinite extension. Infinite depth, convergent total influence, and physical infinite structure remain distinct claims.

