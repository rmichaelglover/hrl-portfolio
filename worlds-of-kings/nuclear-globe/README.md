# Nuclear Chess Globe · Worlds of Kings

A separate, local three-player globe game. It reuses the existing Fusion game's
Natural Earth atlas, D3 projections, city/place navigation, and border-candidate
movement graph. The original Worlds of Kings, Earth atlas, Fusion, wildlife, and
small Nuclear Chess editions keep their own rules and saved state.

Start at `index.html`. Choose three countries with at least sixteen map spaces,
then pass the device between players. The match uses actual mapped provinces and
clipped ocean spaces on the rotatable 3D globe. Nearby army markers cluster at
world scale and unfold as the camera zooms in. Tap a piece, choose ordinary move
or strike, and select a highlighted destination. The piece selector and place
search provide another route to the same map positions. Queen strikes open a
map-colored forecast dialog; they do not execute immediately.

## Match rules

Kings can be captured; check and checkmate do not apply. A captured king retires
its country, while that country's remaining pieces stay on the globe as inactive
pieces. The last surviving crown wins. If every remaining king falls during the
same action and its fire, the match is a draw.

Ordinary captures send the captured non-king to the capturer's crazyhouse
reserve. Drop a reserve piece on an empty, unscorched territory instead of moving
a piece. Captured promoted pieces return as pawns. Pawns cannot drop on pole or
Antarctica promotion spaces. This edition retains its source globe's pawn compass,
polar movement, and cross-ocean promotion conventions. These irregular routes
are experimental map-based chess rules.

An armed queen can strike an enemy piece on an unobstructed queen route. She
stays in place. The target's space ignites immediately; on each of the next three
player actions, fire advances one step over the Natural Earth neighbor graph.
Older fronts own overlaps. They can cross scorched terrain. Any reached piece is
captured: enemy pieces go to the striking player's reserve; friendly losses go
to the first living rival in turn order. Captured kings are processed after all
fires in that action, so the display can report a draw when every crown falls.

Scorched provinces block moves, drops, and sliding rays; knight routes can jump
over them. The fire countdown is a map overlay, not a physical model. All living
countries must vote to accept détente. It takes no turn, disables future strikes
and extinguishes active fronts; scars and reserves remain, and ordinary moves,
captures, and drops continue. Declining dismisses the offer. It expires when a
move, capture, drop, strike, or pass ends a turn.

This game deliberately does not force a peace outcome or award a peace bonus.
Striking first can be immediately decisive. The preview makes its projected map
cost visible, and players can choose to experiment with the result.

## Position and storage

Only this edition reads and writes `worlds-of-kings-nuclear-globe-v1` in the
current browser. The stored match includes its selected country IDs, active fire
fronts, scars, reserve pieces, votes, and result. A refresh restores the match.
An undo stack covers the last 24 local actions and lives for the current page
session. No network opponent, account, or shared server is involved.

`engine.js` wraps the existing Fusion engine for geographic graph steps and
deployment. It does not modify that engine or its three-player alliance rules.
`app.js` draws the game on the same orthographic globe, with optional Mercator
and Robinson views. Four independently oriented views remain available.

## Build and verification

The atlas is fetched from `../worlds-of-kings-fusion/data/atlas.json`; D3 and
navigation assets are locally hosted. No new package, remote API, or generated
map file is required. The UI uses the preserved map source at Natural Earth
v5.1.2; see the linked source manifest and notices in the game.
