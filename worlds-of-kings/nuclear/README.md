# Nuclear Chess · Worlds of Kings

A separate, buildless, local game from Manny Glover's concept. Open `index.html` through the published site or a static server. No dependencies, account, matchmaking, or remote game state. Its files and `worlds-of-kings-nuclear-v1` local-storage key are independent of the original, Earth, Fusion, and wildlife editions.

## Rules contract

This is a **royal-capture crazyhouse variant**, not orthodox crazyhouse or standard atomic chess. Capture the enemy king to win; no check/checkmate, castling, or en passant. Otherwise familiar movement, including an unmoved home-rank pawn's double step and four promotion choices. Dropped pawns cannot double-step or drop on either end rank. All ordinary captured non-king pieces change color into the capturer's reserve; captured promoted pieces become pawns.

A queen can instead strike an enemy-occupied square on an available queen ray. She stays where she is; the target is captured and its square ignites immediately. Every later action advances each existing fire front by one Manhattan-distance ring, to distance three. A new strike is added after advancing the older fronts, so it starts its first outer ring on the following action. Fronts can overlap and cross existing scorched territory. A piece is captured only once: a caught non-king piece, of either color, enters the opposite color's reserve. Both kings' presence is assessed after all existing fronts resolve; loss of both kings within that turn draws. Missing legal actions, including drops, also draws.

Squares glow for a short visual countdown, then remain scorched and blocked until a new game. Sliders cannot cross ruins; knights can jump over them. The wave overlay shows the next actual ring, not all future rings. The strike dialog shows all three future rings **against the current position**; it cannot predict later movement, captures, new strikes, or an accepted détente. Its ordinary-capture button makes the queen move and creates no fire.

Détente offers consume no turn, expire on the next move, and require the other hotseat player's acceptance. Acceptance permanently disables both sides' strikes and cancels active fire and its glow, while preserving ruins and reserves. Capture and drop play continues. The simple computer always accepts a détente offer. No lecture, forced agreement, or automatic shared victory is attached to this mechanic.

## Play modes and storage

White can play a simple one-ply heuristic computer, or two humans can pass the same device. This is not an engine-strength opponent. It prefers immediate king capture, ordinary material gains, escape from imminent fire, and king safety; strike collateral is scored against it. Three setups: standard armies, extra pocket pieces, and a small queen-choice scenario. Board flipping, keyboard square navigation, promotion selection, strike previews, turn undo, and local save/reload are included. Undo versus the computer normally returns both plies. Détente changes are also undoable.

The 8×8 board uses invented square territories, not a real-world map or physical weapon model. The cost of a strike is expressed through lost pieces, enemy reserves, and blocked playing space. Ordinary capture can achieve the same win condition while preserving the board.

## Verification

Run `node worlds-of-kings/nuclear/test-engine.cjs` from the portfolio root. Tests cover legal action ownership, captures and reserves, queen-only ray strikes, all three fire waves, overlapping fronts, friendly captures, terrain and drops, promotions and pawn reversion, direct and simultaneous king capture, détente, offer expiry, and no-action draws. Browser verification exercises play modes, bot replies, drops, strike/capture alternatives, agreed détente, save/reload, undo, and mobile/desktop layout.
