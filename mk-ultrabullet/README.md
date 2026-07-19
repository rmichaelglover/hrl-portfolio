# MK Ultrabullet

**Musical Kernel Ultrabullet** turns the pulse and tactical punctuation of
ultrafast chess into gentle, resolving music. It does not model personalities,
rank players, or reproduce games. Player identifiers are discarded.

Lichess monthly database exports are published under CC0. Download a monthly
standard-rated PGN archive from <https://database.lichess.org/>, then extract a
small anonymous feature file:

```bash
python3 prepare_lichess_ultrabullet.py lichess_db_standard_rated_YYYY-MM.pgn.zst ultrabullet.json --limit 5000
```

Load `ultrabullet.json` in the browser page. Processing stays local. Large PGN
archives and generated datasets are intentionally not committed.

The extractor retains only time control, ply count, per-move time spent,
tactical-event indices, and result. It filters for zero-increment games with an
initial clock of 30 seconds or less. The music engine maps cadence to rhythm,
captures/checks to restrained harmonic color, and every phrase toward a stable
tonic resolution.
