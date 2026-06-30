# Simplicial Complexes → the HRL Hierarchy (roadmap)

The virtual body, until now, was a **graph** — 0-simplices (cells) and 1-simplices (gap
junctions), pairwise coupling, one scale. Lifting it to a **simplicial complex** gives us the
higher dimensions, and each dimension *is* a scale of Levin's multiscale competency.

## The dimensional hierarchy
| simplex | biology | HRL role |
|---|---|---|
| 0 (vertex) | cell | object — anatomical label |
| 1 (edge) | gap junction | pairwise compatibility (current engine) |
| 2 (triangle) | tissue patch | **higher-order** coherence — 3 cells jointly agree |
| 3 (tetrahedron) | tissue volume | organ-scale constraint |

## What this page demonstrates (the analysis layer)
- **Homology as morphological integrity.** χ = V−E+F; b₀ = connected pieces; b₁ = holes.
  A healthy body is a disk (b₁=0); an interior wound is a **hole** (b₁=1). Topology *detects
  and quantifies* the injury — a rigorous, label-free health signature.
- **The anatomical seams are a sub-complex.** The 1-simplices whose two cells carry different
  labels (head|trunk, trunk|tail) form the boundary sub-complex — the morphological seams as
  a topological object.

## The roadmap to Milestone 3 (higher-order relaxation)
1. **Relabel across dimensions.** Run relaxation not only on vertices but with compatibility
   *between* dimensions: a cell's label must cohere with its incident **faces** (tissue patches),
   not just its neighbours. Faces act as the tissue-scale agent; the complex's nested face
   structure is the hierarchy.
2. **Higher-order compatibility kernels.** A 2-simplex rewards its 3 vertices for jointly
   forming a valid tissue triple — constraints pairwise edges cannot express.
3. **Topology as a target.** Give the morphogenesis a *target homology* (e.g. simply-connected),
   and let the relaxation drive both labelling and shape toward it — homeostasis of topology,
   not just identity. Track b₀/b₁ through growth, injury, and remodelling as a convergence metric.
4. **Persistent homology** of the bioelectric/label field as a multi-scale descriptor for
   data-grounding against real imaging.

This page is the substrate. The next build runs the engine *on* it.
