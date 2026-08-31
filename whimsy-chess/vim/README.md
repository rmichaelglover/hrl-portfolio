# Chess Maestro in Vim — terminal study mode

An interactive chess board that lives in a Vim buffer. This first version is
**Study mode**: load an annotated game and step through it move by move, with the
board and narration updating in a single Vim window. Its terminal-native Maestro
layer adds identity-tracked story characters, a live tactical role/plan field,
Rage Comic reactions, recent score, hero-relative orientation, and autoplay.

It runs in stock Vim 8+ on Ubuntu (tested on Vim 8.2). No plugins, no Python — a
single legacy-Vimscript file.

## Run it

```sh
cd whimsy-chess/vim
chmod +x chess-study          # first time only
./chess-study                 # the Crab game (mannyfresher, White)
./chess-study goldsmith       # the Goldsmith Defense game (mannyfresher, Black)
```

Or from inside Vim:

```vim
:source /full/path/to/chess.vim
:ChessStudy crab
:ChessStudy goldsmith
```

(To always have it available, add the `:source` line to your `~/.vimrc`.)

## Controls (inside the board)

| key | action |
|-----|--------|
| `l` &nbsp; `→` &nbsp; `Space` | next move |
| `h` &nbsp; `←` | previous move |
| `<` | jump to the start |
| `>` | jump to the end |
| `p` | toggle timed autoplay |
| `t` | toggle emoji cast / classic pieces |
| `m` | toggle the Maestro role and plan panel |
| `r` | toggle Rage Comic reactions |
| `f` | flip the board |
| `q` | quit the board |

The panel below the board names the move and tells the story (with hand-written
notes at each game's turning points). The board normally places Manny's side at
the bottom; `f` temporarily reverses that orientation.

The Maestro panel assigns the living Woodland pieces practical roles such as
Tactician, Attacker, Controller, Defender, Runner, and Outpost from the current
position. This is intentionally a compact terminal reading of the position; the
browser Maestro remains the home of music synthesis, terrain, QCD, and 3D views.

Set `g:chess_emoji_tempo` before opening a board to change autoplay speed in
milliseconds (the default is 900).

## How the board is represented

The buffer holds the position as plain **FEN letters**, one per square, separated
by `|`:

```
 8 |r|n|b|q|k|b|n|r|
 7 |p|p|p|p|p|p|p|p|
 ...
 1 |R|N|B|Q|K|B|N|R|
    a b c d e f g h
```

- **UPPERCASE = White**, **lowercase = Black**, space = empty square.
- Vim's `:conceal` feature *displays* those letters as chess figurines
  (♔♕♖♗♘♙ / ♚♛♜♝♞♟), white pieces outlined-light and black pieces filled-dark,
  so the two sides are clearly distinct.
- The rank your cursor sits on can reveal the raw letters for editing — which is
  the foundation for the next modes.

Storing letters (not emoji) is deliberate: letters are single-byte, trivial to
parse, and trivial to edit with `r` — which is what makes the planned **Play** and
**Puzzle** modes possible.

## What's next (engine is already in place)

The move engine (legal-move generation, SAN parsing, captures, castling, en
passant, promotion, check/mate) is fully built and tested — it's what drives
Study mode. The remaining modes reuse it:

- **Play**: edit the board letters to make your move, then `:w` validates that the
  buffer differs from the last committed position by *exactly one legal move* for
  the side to move — committing it if so, or reverting and explaining if not.
- **Puzzles**: a start position plus a known solution; your move is checked for
  both legality and correctness.
- **Narration split**: move list + running commentary in a second window.

## Self-test

```sh
vim -es -u NONE -N -c 'source chess.vim' \
  -c 'call writefile(g:ChessSelfTestLines(), "/dev/stdout")' -c 'qa!'
```

Builds both games through the engine and checks ply counts, the mating move, and
king positions.
