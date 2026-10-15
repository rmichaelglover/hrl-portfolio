# HRL terminal worlds

## Browser Matrix terminal

Visit `terminal/` on the portfolio website. The Matrix-inspired interface uses
phosphor green, scanlines, falling code, category shortcuts, numbered worlds,
one-click entry, a Back stack, and keyboard navigation. Reduced-motion settings
pause the animated background and knot automatically.

Every portfolio page opens inside the terminal. World views:

- **Read:** static page text, with scripts and styles removed.
- **Explore links:** follow local page and document links within the terminal.
- **ASCII graphics:** rasterize page images into green character cells.
- **Live scene:** run the selected world's existing engine in an offscreen,
  sandboxed frame, sample up to eight canvases into ASCII, and mirror up to
  eighty visible buttons/selectors/inputs as terminal controls. Click the
  character surface to send a pointer click to its original canvas.

Commands: `help`, `ls`, `search`, `open`, `read`, `back`, `worlds`, `links`,
`graphics`, `live`, `pause`, `clear`. `open 3` enters world 3 in the current
filtered list. Up/down chooses worlds or recalls commands; Enter opens;
`/` focuses search; Escape goes back; 1–4 switch views inside a world.

Live rendering reuses the original world engine; it does not reimplement the
simulation. WebGL buffers are preserved for character sampling. Protected
cross-origin canvases cannot be read. DOM-only games, SVG scenes, PDF pages,
audio/video and drag/continuous keyboard controls still need dedicated TUI
adapters. Static GIFs are sampled as a still image. External references do not
launch outside pages. No LLM is connected. Avoid running untrusted page engines;
this adapter is for the repository's own portfolio pages.

To preview locally, run `python3 -m http.server 8796` in the repository and
visit `http://localhost:8796/terminal/`. HTTP hosting is required.

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
