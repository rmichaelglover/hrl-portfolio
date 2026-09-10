# Cellular Complexes

Open `index.html` in a browser. No build step or external JavaScript dependencies.

`engine.js` constructs conforming meshes and synchronous, shared-facet cellular
automata. `app.js` renders the paired fields and controls. States live only on
maximal cells; lower-dimensional faces define adjacency.

Run the engine verification with:

```sh
node cellular-complexes/engine.test.cjs
```

Checks cover cell counts, boundary-facet counts, adjacency symmetry, connectivity,
tetrahedron volumes, deterministic and matched parent-block seeding, the
square/rectangle evolution invariant, and explicit synchronous-update fixtures.

The page documents open boundaries, rule definitions, geometric construction,
unequal discretization, and the limitations of the depth-sorted 3D display.
