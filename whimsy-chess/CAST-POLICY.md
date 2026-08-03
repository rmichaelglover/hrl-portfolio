# Default cast policy

The default presentation follows the player, not the board color:

- `mannyfresher` is the Woodland cast whether playing White or Black.
- Every opponent begins as classical chess figurines.
- `pappymagee` begins as Woodland after a win or draw and as classical figurines
  after a loss, reflecting his retirement-era preference for the positive chapters.
- Users may deliberately select another set after load. Alternate-history football,
  Gooblets/Zappies, voxel, Atari-era, and export themes remain opt-in visualizations;
  they do not redefine the default identity policy.
- An uploaded PGN uses the side selected as “your side” as Woodland and the other
  side as classical unless the user changes the selectors.

## Coverage audit — 2026-08-03

- `maestro.html`: enforced per side on initial load, game change, supplied-position
  games, and PGN upload; tested for Manny White/Black and Pappymagee win/loss/draw.
- `lichess.html`: Story default renders the hero side as Woodland and the opponent
  with classical figurines.
- `index.html` and `v2.html`: their fixed Manny-as-White chronicle renders White as
  Woodland and Black as classical.
- `v3.html`: its fixed Manny-as-Black Goldsmith replay renders Black as Woodland and
  White as classical.
- Portfolio, PWA, Minecraft, and Roblox outputs derive from `maestro.html`; the
  portfolio mirror is updated with the same producer and tests.

Early experiments are retained as development artifacts. When they intentionally
show a named alternate cast, that is a selected theme rather than the default Chess
Worlds presentation.
