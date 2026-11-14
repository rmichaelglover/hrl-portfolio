# Controlled Provocation — Michael Emanuel Glover's recent studies

Start with `GAME-SUMMARIES.md`: concise reviews of every chapter in all six PGNs.
Open `index.html` for the full searchable review, filters, all recorded mainlines,
and links to the public study chapters. The complete detailed text is also in
`CONTROLLED-PROVOCATION-REVIEW.md`.

Coverage: 77 chapters, 76 unique games, 4,856 unique recorded plies. One duplicated
loss is indexed in both studies but counted once overall. Seventy-five games use
standard chess rules; one uses Crazyhouse. Two standard-rule records start from
supplied positions. All records identify Michael's side explicitly.

`game-index.csv` is the spreadsheet index. `games.json` retains move-level scores,
PV lines, queen-pressure events and the deeper checks. `summary.json` holds the
aggregate counts. `metadata.json` records the six source hashes and engine settings.
The exact original PGN bytes are copied into `inputs/`; original Documents files
were not modified.

Framework, originating theory, playing style, games and studies: Michael Emanuel
Glover. Assistant: implementation of the audit, legal replay, engine evaluation,
aggregation and writing. Stockfish is credited separately in the engine metadata.

Analysis scripts are included. Their source filenames refer to the original
Documents downloads; the identical inputs are bundled here for inspection.
Engine settings: Stockfish 14.1; one thread; 64 MB hash; 20,000-node screening
positions, with selected 200,000-node before/after rechecks. Crazyhouse is legally
replayed without a standard-chess score. Interpretations separate board evidence,
practical results and the hypothesis of psychological underestimation.
