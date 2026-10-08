# Tiny Creek Chess

One Earth. Many kind moves.

A child-friendly geographic chess learning edition of Manny Glover and Cypher’s Tiny Creek World. Each of three participating nature councils starts with **exactly sixteen pieces in sixteen distinct places**: eight pawns, two bishops, two knights, two rooks, one king, and one queen. All 258 mapped country/territory entries have enough learning spaces to participate.

Animal emojis and classical Unicode chess figurines appear side by side. Figurines use 92% of the common marker size and emojis 95%, making their roles readable without covering the animals. Team colors identify the councils. Marker size remains shared within the current view; deep master zoom, country focus, geographic search, and globe/Mercator/Robinson views are retained.

## Learn and play

**Teamwork practice** is the default. Everyone is allied, any player’s piece can be selected, and friends block one another’s paths. Choose a piece, read its role card, inspect the legal destinations, then move using the green map dots or the destination menu. Moving each of the six piece types earns a lesson badge. Practice has no automatic eliminations or forced turns.

**Friendly council game** starts new teams, uses sequential country turns, protects kings from check, and permits chess captures. Captured characters are preserved on the **friendship bench**. They are resting story characters, never injured or killed. A council that finishes through checkmate/stalemate keeps its remaining characters on the same bench. Active plus resting characters always total 48. Promotion changes a role without creating or deleting a character.

Negotiation is explicit: send an alliance offer to another active council, pass the shared screen to that player, then accept or politely decline. Joining includes both existing alliances. There are at most three offers per ordered rival pair. When every active council belongs to one alliance, the council game finishes with shared peace and one point for each active council. Practice is already cooperative and remains open for exploration.

This is local shared-screen play. No online reservation, account system, remote opponent, or chat service is connected. Chess progress uses `tiny-creek-chess-v1`; the attached gardens use `tiny-creek-chess-garden-v1`. The original [Tiny Creek World](../tiny-creek-world/) and all earlier chess worlds remain separate.

## Geographic movement, not orthodox square-board chess

The map uses the preserved Fusion atlas’s compass route model, extended with learning-space links. Rooks follow cardinal routes, bishops diagonal routes, queens either, kings one mapped step, and knights two mapped steps plus a perpendicular step. Knights must traverse three actual, distinct routing steps; missing links cannot collapse a knight into a one-step move. Slider routes stop at occupied locations; a knight may jump over intervening places. Pawns take one forward mapped step and capture a rival diagonally; they do not have orthodox chess’s initial two-step move. Castling and en passant are absent.

Geographic polygons and ocean cells are irregular. Compass rays can curve or terminate, and bishops are not constrained to the ordinary board’s square colors. These rules must not be presented as a complete orthodox-chess implementation. The role cards teach movement ideas, and the page names the geographic differences explicitly.

The inherited promotion rules allow a pawn to learn a queen/rook/bishop/knight role at Antarctica, at a northern-polar ocean space, or on an eligible ocean approach to another coast after leaving its original country. Those are geographic variant rules, not orthodox rank-eight promotion.

## Provinces, cities, and imaginary gardens

The base atlas contains 4,602 land spaces and 1,778 ocean spaces. Large councils deploy to sixteen existing province/region spaces. For countries with fewer than sixteen spaces, `build.py` adds recorded Natural Earth city points, then clearly named **story gardens** inside the mapped country if the city records are insufficient. The current build adds 443 city spaces and 1,118 story gardens, for 7,941 total spaces. These additions are learning locations, not new administrative boundaries. Tiny circular city/garden outlines are schematic footprints.

Existing province geometry is reused. Learning spaces connect to nearby same-country spaces and a gateway to nearby external map spaces. If an enclosed territory has no inherited exterior neighbor, nearest external spaces supply its gateway. The route graph is approximate; it is not a transportation network or a physical travel model. Every country has a verified playable practice start with two companion councils.

Initial placement is deterministic from a seed and searches for an arrangement with all kings initially safe and at least one legal move per council. Country choices must be distinct. Rejected choices do not replace the existing game. Starting fresh councils explicitly restarts chess progress; your separate garden memories remain.

## Naturalist layers

Ambient animals retain Tiny Creek World’s approximate geographic and habitat filters. Chess characters are wildlife-inspired **story ambassadors**, chosen from their starting place or broader council roster. Their animal identities remain stable as they travel. A chess animal visiting another region does not assert that its species lives there. See the [cozy-world model and wildlife bibliography](../tiny-creek-world/README.md).

The geographic layer, wildlife layer, and chess-role layer describe different things at the same location. A promotion updates a role; it does not change an actual animal or a real-world jurisdiction.

## Sources and checks

Natural Earth v5.1.2 via the [preserved Fusion atlas](../worlds-of-kings-fusion/data/atlas.json); geography is public domain. `data/atlas.json` records the baseline SHA256. Existing D3 vendor files and the local geographic engine are reused; no third-party franchise characters or art are included.

Run `python3 tiny-creek-chess/build.py` (Python/Shapely) and `node tiny-creek-chess/test-lesson.cjs` from the portfolio root. Checks cover all map entries’ minimum space counts, exact stocks and unique deployment, safe starting positions, legal moves, small-country additions, bench conservation, whole-alliance agreements, shared peace, and preservation of the source atlas. Browser validation covers practice movement, lesson persistence, accepting/declining alliances, all three countries sharing peace, Singapore/Monaco/Luxembourg placement, and desktop/mobile layouts.

## Whole-world initialization (October 8 update)

The default **Whole-world teamwork** lesson now initializes all 258 mapped countries and territories simultaneously, with exactly sixteen pieces each (4,128 in total). All councils are allied in this cooperative practice mode. USA, Panama, and South Korea are the featured family councils. The opening globe is centered on Atlanta/Georgia and the southeastern United States; the sixteen USA deployment spaces are chosen near Georgia, with roles shuffled among them. Other countries use randomized distinct home-country spaces. A fresh world uses a new stored seed.

Explore any country using the council selector above the sixteen-piece picker. This avoids an unwieldy 4,128-option menu. Visiting a featured family council selects its pieces and frames its deployment. The optional friendly council game still uses the three selected featured countries and its sequential negotiation rules.

The world save uses `tiny-creek-chess-v2`; previous three-country lesson saves remain under the old key. New whole-world saves persist piece positions, featured countries, selection, and lesson progress. The separate garden save remains independent.

Kings and queens display three symbols: their animal ambassador, classical chess figurine, and their council’s country flag. The flag stays with the council as the piece travels and also appears for promoted queens. Atlas entries without a usable country-flag code use a neutral white flag.

Flag visibility fix: the map and role card use locally bundled Twemoji SVG flag artwork rather than operating-system emoji fonts. Royal badges are repainted above neighboring pieces and are prioritized for selection. Attribution and the CC BY 4.0 graphics license are in `flags/`. Pixel checks verify colored flag artwork while the test deliberately omits emoji-font drawing; desktop/mobile screenshots confirm visibility.
