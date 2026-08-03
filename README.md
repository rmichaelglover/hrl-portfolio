# ♟️ Whimsy Chess

**Chess as an exchange of nutrients in an ecological dome — scored as music, narrated as a story, and analyzed with hierarchical relaxation labeling.**

Watch a chess game come alive: each piece is a character with a name, the board grows
rivers and mountains from the flow of the battle, the relaxation-labeling engine reads
each piece's *role* in the position, and the whole game is turned into music whose
**time signature is inferred from the moves themselves** — a quiet maneuvering game
breathes in 3/4, a wild tactical scramble lurches into 7/8.

It runs entirely in your browser from a single self-contained HTML file. No build, no
server, no dependencies. It also installs to an iPad/iPhone home screen as an app.

This repository is the canonical development home for Chess Maestro and its
supporting tools. The live, curated copy is published through
[`hrl-portfolio`](https://github.com/rmichaelglover/hrl-portfolio); reusable
Python algorithm work belongs in
[`relaxation-labeling-python`](https://github.com/rmichaelglover/relaxation-labeling-python).

> 🎥 Demos & tutorials: **[youtube.com/@mannyglover](https://www.youtube.com/@mannyglover)**

---

## Try it

**[Open the published Chess Maestro](https://rmichaelglover.github.io/hrl-portfolio/whimsy-chess/maestro.html)**
or open **`maestro.html`** locally in any modern browser. That exact
`whimsy-chess/maestro.html` path is the flagship; similarly named pages under
`lichess-emulator/` and `genesis/maestro/` are separate experiments.

- Pick a game, press **▶** to play it back *in rhythm*, or step with the arrow keys.
- **🧠 Roles** — tint each piece by the role the relaxation-labeling engine assigns it
  (attacker, defender, controller, outpost, runner, tactic, or idle "noise").
- **🏞️ Terrain** — a topographic influence field: water pools in the contested squares,
  land rises by elevation. Built with a trinary relaxation labeling over the 64 squares.
- **🔊 Music** — orchestrated Web Audio playback. **🥁 Click** adds a metronome so you can
  hear the inferred meter.
- **⬇ Export** — MIDI, WAV (upload to Suno), a Suno text prompt, or a **🌍 World JSON** that
  the included Roblox script reads to build an evolving 3D world of the game.

### Install it as an app (iPad / iPhone)
See `PWA-INSTALL.md`. Short version: host the folder over HTTPS, open `maestro.html` in
Safari, and *Share ▸ Add to Home Screen*. It runs fullscreen and offline.

---

## The idea: hierarchical relaxation labeling

Relaxation labeling (Hummel & Zucker, 1983) is an identify-by-constraints algorithm: you
have objects, a set of labels for them, and a measure of how *compatible* any two label
assignments are for any two objects. It iterates everything toward a globally consistent
labeling. This project applies it, hierarchically, in three places:

- **Roles** — pieces are objects, roles are labels; compatibility comes from how pieces
  support and threaten each other, so coherent plans emerge as label coalitions.
- **Terrain** — squares are objects labeled white / contested / black; a contested seam
  emerges, then becomes water, with land elevation rising away from it.

### HydroGRRLE terrain timeline

Every ply begins by recomputing Maestro's HRL coloration. That white/contested/black
field is the spatial prior for ChessGRRLE, not a decorative after-effect. The initial
board is nearly flat, with a small White-side height advantage representing the
first-move evaluation. Each move then raises or lowers its source, destination, and
nearby squares according to the evaluation change. Continuous water relaxes toward
the contested prior and flows downhill over several small passes; ice and sky fields
travel beside it in the World JSON. Correspondence games use a wide ecological
attention radius, while rapid and ultrabullet games emphasize the immediate tactical
neighborhood. Legacy integer `height` and `water` grids remain available to existing
Minecraft and Roblox consumers; the richer values live under each frame's `hydro`.
- **Rhythm** — each move becomes a note; its think-time (or move salience) labels its
  duration, and the game's accent pattern selects the **time signature**.

The thread tying it together: *boundaries, things, and exchange.* A chess game is a little
ecology — material is eaten, traded, regrown — and relaxation labeling is how the system
finds the meaningful structures inside that flow.

---

## What's in here

| Path | What it is |
|---|---|
| `maestro.html` | **The flagship.** Board + roles + terrain + music/rhythm + exports + PWA. |
| `pythonista/` | Pythonista host for running Maestro offline on iPhone/iPad with native PGN import. |
| `lichess.html` | Earlier clean web viewer (roles + music), preserved. |
| `index.html`, `v2.html`, `v3.html` | Early whimsical/bio viewers (the lineage). |
| `vim/` | **A Vim-native emoji chess study tool** (`chess_emoji.vim`) — 25 narrated games, stepped with `h`/`l`/arrows, board drawn in emoji, plus a self-test. |
| `worldkit.js` | One `chess-world` v1 export → **Minecraft datapack + Roblox builder**. Zero dependencies, including its own store-only zip writer. Runs in the browser *and* in Node. |
| `roblox/` | Roblox Studio scripts that read the exported World JSON into a 3D world. |
| `test/` | `bash test/run.sh` — 21 assertions over WorldKit's terrain, roles, and both exporters. |
| `tools/` | `build_games_library.py` — assemble the embedded games library. |
| `media/` | Showcase stills and an animated replay of the Kádas game. |
| `games/` | Source-game archive plus rigorous and Woodland reviews of the latest a6699–mannyfresher study chapter. |
| `novella/` | Linear tween, classroom, and advanced editions plus the optional ten-door Master Board adventure. |
| `status/` | Wide project status, current frontier, near-term polish, and preview. |
| `engine-coach/` | Future dual-overlay coach for played, study, and engine moves across exact wins and losses. |
| `hydro-computing/` | Speculative water/air/light computing habitat with thermodynamic and safety boundaries. |
| `experiments/` | Rough side sketches (some AI-assisted). |
| `*.md` | Design notes: musical mapping, the boundaries/Markov-blanket musing, PWA install. |

### The Vim study tool

```bash
vim -c 'source vim/chess_emoji.vim' -c 'ChessEmoji queendab'
```

`l` / `→` step forward, `h` / `←` back, `<` `>` jump, `t` toggles emoji vs. classic
figurines, `q` quits. Twenty-five games ship with it — `queendab`, `kadas`, `roundup`, `carr`,
`schroflag`, `horsey`, `crabblack`, `crab`, `goldsmith`, `fathersday`, `houdini`, `daisies`, `deadmove2`, `crawlnamed`, `scandi`, `stalemategambit`
— plus `ninjastalemate`, `jerryball`, `jerryballas`, `creepyharriet`, `bongcloudpilgrim`,
`bongcloudgeneral`, `creepycrown`, `kadascakes`, and `ravencliff`, each with
hand-written narration at its turning points. Verify them all with:

```bash
vim -u NONE -N -es -c 'source vim/chess_emoji.vim' \
    -c 'for l in g:ChessEmojiSelfTest() | echo l | endfor' -c 'qa!'
```

---

## License

- **Code:** [AGPL-3.0](LICENSE) — free to use, study, share, and modify; if you distribute
  it or run a modified version as a service, share your changes back. A **commercial
  license** is also available — see [`NOTICE`](NOTICE).
- **Creative assets** (the character cast, narration, musical & visual designs):
  [CC BY-SA 4.0](ART-LICENSE.md).
- Embedded chess games are public game records.

Built by **Manny Glover** (R. Michael Glover). Contributions welcome under a short CLA that
keeps the dual-license possible. If you teach with this, build on it, or want to collaborate
— please reach out.
