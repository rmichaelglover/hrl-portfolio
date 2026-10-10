# Front-page world access audit

155 public entry pages are now directly linked from the landing page. The directory includes independent worlds, individual Genesis biomes, study and game modes, laboratories, reading tools, and research portals. Archive notices, test harnesses, and alternate obsolete renderers are excluded.

Six featured world cards sit above the directory. The landing-page discovery column also features the Stalemate Gambit study and direct access to the Tiny Creek and Worlds of Kings families.

Run `python3 tools/build_world_directory.py` when adding an entry page. It scans public `index.html` pages, adds selected standalone experiences, validates destinations, and regenerates the static HTML and JSON inventory. Search and category controls progressively enhance those native links.

## Directory coverage

- Worlds & Nature: 47 entries.
- Chess & Games: 28 entries.
- Music & Art: 8 entries.
- Science & Tools: 24 entries.
- Words & Faith: 12 entries.
- Writing & Research: 28 entries.
- Community: 8 entries.

Every inventory destination exists on disk. Live publication and browser interactions are checked separately.
