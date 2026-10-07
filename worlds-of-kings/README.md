# Worlds of Kings — little-world prototype

A local, pass-the-device implementation of Manny Glover’s chess–geography–diplomacy variant. Open `index.html` through the portfolio or a local static server. No dependencies, remote game service, or weapons functionality.

## Implemented

Three fictional countries, each with sixteen province spaces, share a 24-column × 14-row spherical movement atlas. Each gets one king, one queen, two rooks, two bishops, two knights, and eight pawns. Ready-made deployment is playable immediately; optional manual deployment gives each country 45 seconds and randomly fills the remaining spaces on expiry. A browser refresh preserves the match and absolute deployment deadline locally.

Country borders are deliberately fictional, mildly perturbed province polygons; shared vertices match. They demonstrate province-shaped spaces rather than claim to reproduce real borders. Ocean cells use longitude–latitude spacing and checker colors. Space counts determine moves. Haversine distances between successive route centers accumulate as travel trivia, including knight jumps; they are not simulated ship speeds or exact coast-to-coast navigation distances.

The default single canvas renders an orthographic 3D globe. Rotate by dragging; zoom with scroll or buttons. Up to four independently oriented panes share selection, moves, and game state. Each supports globe, Mercator, or Robinson (standard coefficient tables with linear interpolation). Mercator clips at 85 degrees; the globe shows full polar routes. This is a canvas globe, not a terrain or photorealistic Earth renderer. Label toggles show fictional countries and coordinate guides; hover reveals province names and coordinates.

## Movement atlas

Edges advance cardinal directions, corners advance diagonals. Longitude wraps. At the north/south boundary, a route reaches the opposite longitude’s polar-row cell and reverses its north/south component. The transition is a declared game convention. Each elementary step reverses correctly; slider rays follow carried direction and stop at occupancy or a repeated cell. Knights travel two edge steps and one perpendicular step, jumping intervening pieces. Routes and destinations are drawn on selection.

Pawns carry their forward orientation, move into empty forward spaces, and capture on two forward diagonals. At marked ocean junctions (rows 1 and 12, columns divisible by six), the two diagonals additionally allow noncapturing advances, producing three forward choices without adding capture directions. Crossing a pole reverses the pawn’s forward direction. There is no initial double-step, en passant, or castling.

Departure from an owned coast is recorded when a pawn enters an ocean cell from its own land. On reaching an ocean space with a forward/capture route into foreign land, it promotes immediately to the piece selected in the sidebar. Allied foreign coasts qualify; own coasts do not. This prototype defines the arrival approach geometrically rather than requiring an announced destination. Arrival space must still be legal and the king safe.

## Turns, check, elimination, and alliances

Turn order is Ember Reach → Azure Isles → Moss Coast, skipping eliminated players. A move must leave its own king safe. Kings are not capturable. Allied pieces block but cannot be captured; allied attacks do not give check. A player without a legal move passes pending review.

**Prototype adjudication convention:** after a complete global round, all living players with no legal moves are assessed from the same position, then all eliminated armies disappear together. Checkmate scores zero; stalemate scores half. Reassess in simultaneous batches until no further eliminations arise. This timing allows intervening players to change threats before the round review; it differs from immediate orthodox checkmate and from reviewing only the player whose turn begins. This is a visible experimental rule, not an implicit claim that those conventions are equivalent.

Each requester can initiate three requests **per rival**, independently in each direction. Declines count. Accepting merges both complete alliances; no unanimity or breakup in the base prototype. Pass the device to the recipient before accepting. No move is consumed. A pending offer pauses board input until accepted or declined. On refresh, pending offers are withdrawn but their request counts remain. Once all living players belong to one alliance, they win together with one point each. A sole survivor gets one point. No survivors means no victory. Scores are local points, not Elo.

## Not yet implemented

Real province datasets; the complete country catalog; origin preference and first-come assignment; supplemental city spaces for countries with fewer than sixteen spaces; online accounts, remote consent, matchmaking, or ratings; actual river/terrain influences; named real landmarks; Model UN unanimous-merger and Sharp Bois breakup expansions. The fictional three-country world exists to test movement, geography display, diplomacy, and elimination before adding real political boundaries.

Local browser state uses `worlds-of-kings-v1`; no personal data or external network actions are collected. Reset replaces that local match. The [authority and restraint charter](../white-hat-hackers/authority.html) applies to future consequential features; game actions confer no authority over real people or systems.

## Verification

`node worlds-of-kings/test-engine.cjs`

Tests cover full-army deployment, opening mobility, reversible geographic steps, longitude/polar transitions, ray blocking/capture, turn ownership, own-king safety, exceptional pawn routes, coast promotion, alliance acceptance and per-rival request limits, stalemate scoring, army removal, and shared victory. Browser checks exercise multiple synchronized map views, projections, a legal move, timed deployment, alliance acceptance, persistence, and mobile/desktop layout.
