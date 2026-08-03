# Engine & Study Coach

Status: **future chess subapp; specification only, not yet implemented.**

## Purpose

Teach exact archived games—wins and/or losses, with draws where instructive—by
comparing three things at a chosen position:

1. the move actually played;
2. the study author's default suggested move or main-line continuation;
3. the engine's top move under visible analysis settings.

This is a comparison lesson, not an autoplay oracle. The learner should be able to
think first, reveal hints gradually, and understand why two reasonable sources agree
or disagree.

The primary exercise is **Avoid the Inaccuracy**. The learner chooses White or Black
in the current study chapter. The subapp follows that side's recorded moves, stops
immediately before its first meaningful inaccuracy, and asks the learner to find a
better move without revealing the answer. Later inaccuracies can become additional
checkpoints after the first one is understood.

## Board overlay

- **Gold arrow — Study move:** the authored main-line or explicitly marked suggestion.
- **Cyan arrow — Engine move:** the engine's current principal-variation first move.
- **Gold-and-cyan arrow — Agreement:** one move satisfies both sources.
- **White outline — Played move:** the move from the exact archived game, when different.

The interface must also state the moves in text and symbols; color alone cannot carry
meaning. If a study has no authored suggestion, say **No study move recorded**. If an
engine is unavailable or still searching, say so rather than inventing a move.

## Teaching sequence

1. Load the current study chapter and choose the learner's side.
2. Analyze only that side's recorded decisions for the exercise and locate the first
   meaningful inaccuracy under the declared engine settings.
3. Replay the chapter to the position immediately before that move, then pause.
4. Hide every hint and ask the learner to choose a legal move that avoids the inaccuracy.
5. Reveal the played move, study move, or engine move one at a time.
6. Ask what each candidate changes: checks, captures, threats, king safety, development,
   pawn structure, space, time, and tactical consequences.
7. Show a short principal variation and a plain-language explanation.
8. Continue through the recorded game and disclose its real result: win, loss, or draw.
9. Offer a retry or advance to the next inaccuracy on that side without rewriting the
   historical score.

An **inaccuracy** is a configurable evaluation loss, not merely the presence of `?!`
in imported text. The interface should show the threshold and distinguish a small
engine preference from a mistake or blunder. If no move on the chosen side crosses
the threshold, the chapter passes that exercise honestly: **No qualifying inaccuracy
found at these settings.**

## Outcome-balanced library

The default lesson shelf must include exact wins **and** exact losses. Draws are useful
for stalemate, repetition, fortress, and practical-defense lessons. Filters may select
`Wins`, `Losses`, `Draws`, or `All`, but the general course should not imply that only
victories deserve study.

The result badge describes the complete recorded game. It must never claim that the
displayed engine move guarantees that result or that one disagreement caused the loss.
Use language such as **the game was won** or **the game was lost**, not **this person is
a winner** or **this person is a loser**.

## Analysis contract

Every engine suggestion records enough context to reproduce or qualify it:

- engine name and version;
- depth, nodes, or time limit;
- evaluation and side to move;
- MultiPV setting and principal variation;
- position FEN and PGN game identifier;
- whether the result came from ordinary search or an exact endgame tablebase.

Evaluations belong to positions under particular settings; they are not timeless facts
about people. A deeper search may change the top move. For supported small endgames,
tablebase win/draw/loss truth should be labeled separately from heuristic evaluation.

## Study-data rules

- Prefer an explicitly authored main line or marked recommendation.
- Do not mistake the next historical move for a recommendation unless the interface
  labels it **Played move**.
- Preserve variations, comments, glyphs, clock data, and game result when importing PGN.
- Deduplicate chapter and full-study exports by Lichess game ID plus normalized moves.
- Keep private studies local unless the owner intentionally publishes or exports them.

## Worked checkpoint — a6699–mannyfresher

The latest study chapter supplies the reference exercise. Choose Black and replay to
the position after `3.Qf3`. Hide all arrows and ask for Black's move.

- Played move: `3...f6??`
- Study/engine suggestion: `3...e6`
- Threat to discover: `Qh5+`, followed by `Qxg6#` if Black answers `...g6`
- Exact game result: Black lost by checkmate on move forty; the result describes the
  full game, not a guaranteed consequence of one candidate move

The later course supplies spaced repetition. After `31.Qa6+??`, `32.h3??`, and
`34.Nxh7??`, Black repeatedly has the defensive resource `...Qxa6`. A lesson can revisit
the pattern until the learner recognizes when to remove the attacking queen.

This chapter tests the goal precisely: recognize the earliest meaningful inaccuracy by
the learner's side, then recognize repeated later opportunities to avoid the loss.

## Possible implementation path

1. Reuse Maestro's board, PGN parser, move stepping, narration hooks, and game metadata.
2. Add a web-worker engine adapter so analysis never freezes playback.
3. Represent played, study, and engine candidates as separate typed annotations.
4. Add reveal controls, accessibility labels, filters, and outcome-balanced lesson sets.
5. Add side selection, configurable evaluation-loss thresholds, and first/next
   inaccuracy navigation within the current chapter.
6. Cache analysis by FEN plus engine settings; invalidate it when those settings change.
7. Test agreement, disagreement, absent-study-move, no-qualifying-inaccuracy,
   engine-unavailable, and exact-result cases.

## Not in scope yet

Google Sheets Chess, multiplayer synchronization, automatic cloud analysis, and private
study fetching are separate future projects. This README records the coach clearly so
the idea survives without expanding the present polishing pass.
