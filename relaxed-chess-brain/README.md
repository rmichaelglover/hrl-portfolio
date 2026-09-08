# Relaxed Chess Brain

A corpus-trained, browser-visible hierarchical relaxation-labeling network.

Build its memory from every PGN beneath the home directory:

```bash
python3 build_brain.py --pgn-root /home/rmichaelglover
```

Then serve the portfolio and open `/relaxed-chess-brain/`. The generated
`brain.json` is committed so the presentation works as a static site. Exact
duplicate games are learned once even when the same PGN occurs in several
folders.
