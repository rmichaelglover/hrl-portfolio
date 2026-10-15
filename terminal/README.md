# HRL terminal worlds

## Browser terminal

Visit `terminal/` on the portfolio website for the browser explorer. It shares
`world-directory.json` with the native CLI and provides search, keyboard
navigation, static page reading, full-page links, a 3D character animation, and
a command prompt (`help`, `ls`, `search`, `read`, `open`, `worlds`, `pause`,
`clear`). Up/down at the prompt recalls command history. It runs entirely in
the browser and supports mobile screens and reduced-motion preferences.

To preview locally, run `python3 -m http.server 8796` in the repository and
visit `http://localhost:8796/terminal/`. It needs HTTP hosting, not `file://`.

## Native terminal

Run from the portfolio checkout with Python 3.9+ on Linux or macOS. No packages,
API keys, or network access are needed for browsing and rendering.

```sh
python3 terminal/hrl.py tui
python3 terminal/hrl.py list chess
python3 terminal/hrl.py list --json
python3 terminal/hrl.py read "Oort Cloud"
python3 terminal/hrl.py render --frames 200
python3 terminal/hrl.py open "Oort Cloud"
```

The TUI searches the existing `world-directory.json`, reads local HTML without
scripts or styles, and shows a rotating, depth-buffered 3D trefoil. Use arrows,
Enter to read, Escape to return, `/` to filter, space to pause, and `q` to quit.
`o` launches the selected live page in your browser. It needs a terminal at least
60 columns by 12 rows. Windows needs a curses implementation or WSL.

This first surface covers the shared directory, not every file in the repository.
Page reading extracts static text; browser games, canvas, WebGL, audio, and
JavaScript-generated text still run in the browser. The trefoil is an original
terminal scene, not an exact reproduction of the OpenAI logo or existing site
graphics. There is no LLM connected yet.

## Toward RelaxGPT / HRLGPT

Keep the terminal and website as views over shared tools and data:

1. Export existing graphics as scene state (points, edges, colors, camera,
   iteration) and render that state with terminal characters or terminal image
   protocols. Image-capable terminals can display raster frames; ordinary
   terminals need ASCII, Braille, or half-block adapters. Browser screenshots
   offer visual fidelity but do not make browser interactions terminal-native.
2. Connect the existing relaxation engine to both surfaces. Show priors,
   compatibility factors, confidence, null labels, convergence, and a
   reproducible run record using the same serialized state described in
   `SIMPLICIAL_RELAX.md`.
3. Add an LLM provider behind an explicit configuration boundary. Give it
   catalog search, document retrieval, scene controls, and validated solver
   tools. Keep credentials outside the repository. The model proposes candidate
   interpretations; Relax evaluates their consistency under declared factors.
4. Expose evidence and uncertainty. Consistency is not proof of truth, and an
   inference wrapper is not a newly trained foundation model. Evaluate the
   combined system against the underlying LLM and solver independently.

This Python prototype is a small entry point. The preferred richer engine TUI
in the architecture document remains FTXUI; the catalog and future state format
can be shared with it.
