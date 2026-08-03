# Game Archive and Latest-Game Review

This directory preserves source records separately from their adaptations. PGN tags,
moves, comments, clocks, variations, and results are evidence; narration may interpret
them but must not silently alter them.

## Archive status

- `2026-08-03-ninja-ultrabullet.pgn` is the newest unique-game archive: mannyfresher–
  Androsov_andrey, Lichess `VeWkDqu1`, won on time in a `15+0` arena.
- `2026-08-03-checkers-study.pgn` is the newest full-study archive before that game.
  Its latest chapter is a6699–mannyfresher, Lichess `Iti1c13V`.
- `2026-08-03-coachz-crossing.pgn` preserves the earlier CoachZ game used by the
  optional Master Board adventure.
- `creepy-harriet-study.pgn` is the broader annotated source used to build the current
  teaching shelf.
- `2026-06-30-kadas-tschucksl.md` preserves an earlier game as a documented narrative.

Duplicate full studies and chapter exports must be collapsed by Lichess game ID and
normalized moves before future catalogue expansion.

## VeWkDqu1 — the one-second king walk

The new chapter appears in six public studies, but it is one game and therefore has one
canonical archive file here. White began with fifteen seconds; Black's first recorded
clock is eight seconds, consistent with an arena berserk, though the PGN does not carry
an explicit berserk tag. The result was `1-0` by time, not checkmate.

White used a Mieses/Creepy-Crawly shell, then walked the king through `e2`, `f3`, `g4`,
back through `f3`, `e2`, `e1`, and `d1`, and onward to `d2`, `c3`, and `c4`. The walk
captured Black's bishop on g4 but surrendered normal king safety and development. Black
won White's queen with `14...Qxd1+` and gathered more material, yet the clock fell to
zero after `18...Nd4`; White still had one second after `19.Kc4`.

The rigorous lesson is format-specific: the clock decided the recorded game, while the
position itself should not be presented as a model of sound classical king play. In
ultrabullet, legal continuity, forced replies, and clock pressure can outweigh an
ordinary material narrative. “Won the game” and “had the preferable position” are
different claims, and this PGN proves only the former.

## a6699–mannyfresher — rigorous examination

### Record and scope

- Date and format: August 3, 2026; rated rapid tournament, `600+0`
- White: a6699, 1902
- Black: mannyfresher, 828
- Opening: St. George Defense
- Recorded result: `1-0`, normal termination by checkmate after `40.Qcg4#`
- Rating difference: 1074 points

The rating difference supplies context, not causation. This review follows Black's
decisions because **Avoid the Inaccuracy** is meant to teach the learner's chosen side.
All numerical evaluations and suggested variations below come from the annotations
embedded in the exported Lichess study.

### The first and best intervention point

After `1.e4 a6 2.Bc4 h6 3.Qf3`, White attacks f7 with queen and bishop. Black played
`3...f6??`, blocking the knight, weakening the king, and failing to answer the threat.
The study marks mate in two:

`4.Qh5+ g6 5.Qxg6#`

The recommended move is `3...e6`, which closes the bishop's diagonal and prepares
ordinary development. This is the earliest decisive Black-side checkpoint and therefore
the default place for the coach to pause. The lesson is more exact than “do not play
flank pawns”: before every move, inspect the opponent's checks, captures, and threats.

White instead played `4.e5??`, losing the forced mate. Black immediately received a
second chance to play `4...e6`, but chose `4...d6??` and again allowed a large advantage.
This repetition makes the chapter pedagogically valuable: a missed punishment does not
erase the underlying threat.

### The wandering-king phase

After `5.Qh5+ Kd7 6.e6+ Kc6`, Black's king began a long walk. White's `8.Bb3??` reduced
the advantage and made `8...Bxe6` Black's best defensive chance; `8...b5?` missed it.
Later `10...Kxb5??` stepped toward the attack when `10...Kb7` was safer. At move eleven,
`11...Bd7??` again permitted a forced mating sequence; `11...Kb6` resisted longer.

These positions teach a coherent defensive rule: when the king is exposed, reduce
forcing lines and complete escape squares before seeking material or development that
does not answer the immediate attack.

### A real fight after the opening

The game did not proceed in a straight line. White repeatedly let the advantage shrink,
while Black found active moves and material. After `16...Nxa5 17.Rxa5`, the struggle
continued. Black's `18...c5??` reopened White's advantage; `18...Ne7` was sounder.
`22...Kd6?` then allowed the evaluation to rise sharply, whereas `22...Qc8` directly
addressed White's queen and passed c-pawn.

White still gave Black practical chances. `28.Qd3??` and `29.Nec3??` reduced a large
advantage to near equality. At move twenty-nine Black could play `29...Rxc7`, removing
the dangerous passer, but `29...Bc5??` returned the advantage to White.

### The queen on a6

The final phase is the most memorable synthesis. White's `31.Qa6+??` changed a winning
position into a Black advantage because Black could answer `31...Qxa6`. Instead Black
played `31...Kh5??`, allowing a forced mate.

Then the same defensive resource kept returning:

- after `32.h3??`, Black again had `32...Qxa6`, but played `32...g4??`;
- after `34.Nxh7??`, Black again had `34...Qxa6`, but played `34...f4??`.

White finally removed the defender with `35.Qxc8`, and the attack became decisive:

`35...e3 36.Qxg8 exf2+ 37.Kh1 gxh3 38.gxh3 Kxh3 39.c8=Q+ Kh4 40.Qcg4#`.

The repeated `...Qxa6` opportunity is ideal for spaced practice. The coach can revisit
the same tactical idea at three positions and ask whether the learner now recognizes it.

### Logical synthesis

1. `3...f6??` is the earliest decisive Black-side inaccuracy; `3...e6` answers the
   queen-and-bishop battery.
2. White's missed mate gives Black a new decision, not retroactive safety.
3. With an exposed king, immediate forcing threats outrank routine plans.
4. The passed c-pawn makes `29...Rxc7` urgent.
5. `...Qxa6` appears repeatedly as the late defensive resource; pattern recognition
   should improve on the second and third encounter.
6. The exact loss is valuable because both sides missed wins. Engine evaluation swung,
   but legal opportunities remained until the final mating sequence.

Engine labels describe positions under particular settings. They do not measure either
player's intelligence, courage, or worth.

## The Three Chances at Queen A6 — Woodland narration

The Master Board opened onto Checkers Wood, where paths crossed like red and black
squares on an old picnic blanket. Across the clearing stood a6699, carrying 1902 rating
stones. Manny carried 828 and a very experimental map.

On the third Black move, a small pawn stepped to f6 and accidentally propped open the
castle gate. Ella's feathers rose. White could ring the bell on h5 and finish the visit
almost at once—but the bell went unrung. Black had another chance to close the diagonal
with `...e6`. That chance also wandered away.

So did the king. He crossed d7, c6, b5, b6, and b7 while bishops, knights, rooks, and
pawns rearranged the forest behind him. The position looked decided, then less decided,
then nearly balanced, then wild again. Nobody was allowed to say “it was over all along.”
The board kept offering real choices.

Near the end, White's queen landed on a6 like a bright kite snagged in a tree. Three
times Black could simply take it. Three times another move looked more urgent. The
Woodland spectators began whispering the square together: “A-six. A-six. A-six.”

At last the queen escaped to c8, the c-pawn became a second queen, and two white queens
closed the final net with `40.Qcg4#`.

Ella saved three bookmarks, all shaped like the same leaf. “The first bookmark teaches
the tactic,” she said. “The second tests whether we remember. The third proves why we
practice patterns.”

Manny recorded the loss exactly. No secret victory, no rewritten trail—just a marvelous
game in which the best future move became easier to see because the same chance knocked
three times.

## Second-newest glance — mannyfresher–chejov0353

The second-newest unique chapter is Lichess `8FILwQjX`, also played August 3, 2026:
mannyfresher (833)–chejov0353 (1824), `0-1` by `43...Rh3#`. It is newer than CoachZ
Crossing and appears immediately before the a6699 chapter in the newest Checkers study.

Its first decisive checkpoint is `5.Nxe4??`. Black's d5-pawn answers `5...dxe4`, so
after `6.dxe4` White has exchanged a knight for a pawn. The study recommends `5.Nh3`,
simply saving the attacked knight. `8.Bxh6?! Rxh6` then gives up the remaining bishop
on that wing and makes the material deficit much harder to repair.

Black converted with active knights and rook checks. A quicker finish existed at
`27...Ncd4 28.Bf1 Nc6#`; the played `27...Rh8?!` missed it without surrendering the
large advantage. The eventual rook mate on h3 demonstrates patient conversion after
a missed shortcut.

Woodland version: a knight reached for a berry on e4 without noticing the d5 branch
bending above it. The branch swept the knight from the trail. Much later Black missed
the shortest path to the cabin, took the longer moonlit route, and arrived safely with
`...Rh3#`. Ella's bedtime note was peaceful: count every defender before gathering a
berry, and when one route disappears, calmly look for the next sound road.
