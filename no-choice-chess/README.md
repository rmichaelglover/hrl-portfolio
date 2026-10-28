# No-Choice Chess

A calm, standard-chess trainer: exactly one legal move, no timer, score, streak, penalty, account, or automatic opponent. Choose a piece and a destination; try unlimited hints or reveal the move. A completed exercise stops when a choice returns or the game ends. If a future collection contains a longer verified forced corridor, the interface can continue one forced ply at a time.

## First collection

20 positions from the user's real Lichess games, with complete PGN witnesses. The first is a king-and-pawn position with just one legal king move. Exercises include forced king, pawn, knight, bishop, rook and queen moves. The side to move is the user's side at the extracted starting position, and the board initially faces that side. It can be flipped.

The final standard-chess scan covered 129 user games and 7,476 plies: 168 forced positions across either side, including 138 distinct starting positions on Mannyfresher's turns. The 20 selected exercises all have one forced ply followed by a branching position. No longer mutually forced corridor was found in this sample; this is not a claim that longer corridors do not exist. Earlier exploratory counts included some non-standard games and duplicate positions; the published summary uses the stricter filter.

“Only legal” is different from “only best.” No engine evaluations are needed. These exercises can come from losing positions or games decided on time. Solving the exercise means recognizing a legal move; it makes no claim about saving the game or finding an optimal plan.

## Why ordinary chess still holds

The sole extra restriction is the chosen initial position. Every offered move is generated from python-chess's complete legal move set, including king safety, captures, castling rights, en passant, and promotion rules. The generator requires a valid position, exactly one legal move, and no automatic game-over condition. It preserves source history when checking game-over and follows the forced move without inventing an opponent reply. Optional draw claims are not made automatically.

A legal promotion generally offers four promotion choices; this collection does not disguise those as one move. Likewise, when the next player has multiple legal replies, the forced exercise ends rather than silently restricting those choices.

The browser uses precomputed, verified positions and move-explanation categories. It does not contain a general-purpose chess engine or accept arbitrary FEN/PGN uploads. It only plays the stored exercises. There is no inference or neural model running per click.

## Gentle controls

- Select a piece, then a square. Wrong attempts explain a rule without losing progress.
- Hints describe the problem, identify the piece, then identify its destination.
- “Show me the move” completes the same legal step, without a penalty.
- “Start this one again,” exercise selection, previous/next, and board flipping are always available.
- Keyboard: Tab into the board, arrow keys between squares, Enter/Space to select. Standard buttons control hints and navigation. There is no sound or timed animation requirement.
- Source usernames/date/PGN/game link live in an optional disclosure; ratings and final results are not used as judgments of the learner.

## Verification and regeneration

```sh
python3 -m unittest discover -s no-choice-chess -p test_exercises.py -v
node --check no-choice-chess/app.js
```

Six tests replay the complete legal source games, verify source checksums and unique starting states, compare each stored sole move and after-position against the legal generator, verify explanatory pin/pawn-block cases, check non-mutation, and confirm the default king-and-pawn exercise. Browser QA checks incorrect attempts, hints, reveals, legal clicks, keyboard focus, flipping, navigation, reset, and mobile layout.

`python3 no-choice-chess/build_exercises.py --pgn /path/to/games.pgn` can rebuild a collection from supplied standard games involving Mannyfresher. Without arguments, it scans the local Documents/Downloads subset used in the first experiment. The generator's six-piece-type selection and two-per-game limit aim at variety rather than statistical sampling. It assumes the current user's username; other usernames would require an explicit generator option/change.

Analysis environment: Python 3.10, chess 1.10.0 (python-chess distribution 1.999). Browser: modern Chrome verified. Standard-library Python plus python-chess builds/tests the collection; the trainer itself needs no Python installation. Serve through HTTP, such as `python3 -m http.server` from the repository root. No server receives attempted moves or stores progress; reload starts fresh.

Next research: measure forced-corridor lengths in larger real-game collections, distinguish one-sided forced responses from two-sided forced sequences, and investigate longer locally legal corridors without presenting composed positions as witnessed real games.
