# Simplicial Relax

**Simplicial Relax** is the umbrella name for the information-processing
engines built from hierarchical relaxation labeling.  An engine receives
objects, labels, priors, and local compatibility rules; it repeatedly passes
support through a graph or simplicial complex until the field reaches a
mutually coherent labeling.

The name distinguishes the general architecture from any one application:
motion capture, dark-matter residuals, chess, biological form, language, and
interactive worlds are different surfaces over the same relaxation process.

## Trinitarian architecture

| Role | Computational responsibility | Representation |
| --- | --- | --- |
| **Father — architecture / word giver** | declares objects, labels, priors, factors, and stopping rules | schema and configuration |
| **Mother God / Holy Spirit — relationship** | carries compatibility support among objects and across simplex dimensions | compatibility matrices/tensors, factor graph, message passing |
| **Son / Sun — embodiment / word deliverer** | makes the relaxed field observable and usable | assignments, confidence, history, TUI, GUI, exports |

The three roles form one 2-simplex rather than a one-way pipeline.  Schema
constrains relationship; relationship revises the embodied result; observable
results expose where the schema and relationships must be refined.

## Mathematical layers

- **0-simplices:** objects and their label-strength distributions.
- **1-simplices:** pairwise compatibility factors.
- **2-simplices:** order-3 or trinity factors capable of representing
  constraints, such as chirality, that pairwise terms cannot see.
- **Noise/null label:** an honest rejection state for observations that the
  current known labels cannot coherently explain.  A domain may interpret a
  stable, independently validated coherent residual more specifically (for
  example, as an nhoton candidate), but unknown is not automatically dark
  matter.

The active generic implementation lives in
`../relaxation-labeling/python/hrl_generic/`.  It combines sparse factors,
respected priors, a null/noise label, and order-3 support.  The tested `hrl/`
package in this repository remains the stable public pairwise engine while the
generic implementation is prepared for promotion.

## Surfaces

### TUI

The terminal surface should expose:

1. the object/label schema;
2. the factor graph and its 2-simplices;
3. live iteration, convergence, and confidence;
4. inspection of ordinary noise versus coherent residuals; and
5. export of a reproducible run record.

FTXUI is the preferred C++ terminal framework.  Diagon can optionally render
mathematics and small relationship diagrams.  Both are MIT-licensed; retain
their license and upstream attribution when code is distributed.

### GUI

The existing browser-based HRL Lab is the first GUI surface.  It should consume
the same serialized engine state as the TUI so both views describe one run,
not two implementations.  A future native Qt surface must be written from
licensed dependencies or clean-room interfaces.

## MrMocap adoption boundary

Repository metadata reviewed 18 July 2026:

| Repository | Status | Simplicial Relax use |
| --- | --- | --- |
| `mr-mocap/Diagon` | MIT | optional TUI/GUI diagram rendering, with attribution |
| `mr-mocap/FTXUI` | MIT fork | TUI framework; preserve upstream and fork provenance |
| `mr-mocap/general-processor-emulator` | GPL-3.0 | separate process or GPL-compatible program only |
| `mr-mocap/MathLib` | no published license | no copying or redistribution; request permission or clean-room implementation from public mathematics |
| `mr-mocap/dual_quaternion_interpolator` | no published license | inspiration/interop only until permission is granted |
| MrMocap Qt examples | no published license | do not copy; implement the GUI independently |

“Public on GitHub” does not itself grant reuse rights.  This boundary lets the
project honor David Harrison's influence without silently assuming ownership
of his source.

## Initial integration sequence

1. Promote `hrl_generic` into the tested public package under the
   `simplicial_relax` namespace.
2. Define one versioned JSON run format shared by TUI and GUI.
3. Build a dependency-light terminal reference surface, followed by an FTXUI
   renderer.
4. Adapt HRL Lab to load the same run format.
5. Add motion/pose transforms through a licensed dependency or a clean-room
   quaternion module with mathematical citations and MrMocap inspiration
   credit.
6. Validate pairwise equivalence, trinity/chirality behavior, noise rejection,
   and identical TUI/GUI run summaries before the first release.

