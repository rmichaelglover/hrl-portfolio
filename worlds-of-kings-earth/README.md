# Worlds of Kings — the real globe, atlas workbench

This is the first real-world foundation of Manny’s chess–geography–diplomacy game. It is **an interactive atlas and movement workbench, not yet a full world match**. The original [three-country edition](../worlds-of-kings/) remains playable and unchanged, with its own save key and a byte-hash reference in `data/prototype-reference.json`.

## Implemented

- Real country and province geometry from a pinned Natural Earth v5.1.2 snapshot: 258 mapped countries and territories, 4,596 source province features, plus seven explicitly labeled country fallbacks where no province feature is available.
- Province borders retain their actual shape, simplified at 0.012 degrees for browser rendering. No square approximation replaces them.
- 1,778 distinct water components from a 12-degree longitude–latitude ocean grid clipped against the mapped country land union. Water parts separated by land are separate spaces. Small residual inland water can remain because this is not a dedicated ocean dataset.
- 7,342 city names, supplied local names, capitals, source population estimates, country names, and province names. Names appear according to zoom and collision avoidance. Search works across countries, provinces, and cities. Population estimates are source-vintage values, not live census rankings.
- One globe view by default, up to four independently rotated/zoomed views sharing selections and the exploration token. Each supports orthographic 3D globe, Mercator, and Robinson. Projection libraries are bundled locally; there is no runtime CDN.
- An inspectable candidate movement compass, piece lenses, an exploration token, a local travel ledger, and accumulated spherical distances. Keyboard-accessible search and destination controls accompany map clicking.
- Local honorary hometown crowns. Atlanta starts as an optional jewel; any supplied city can be crowned. No crown implies geographic superiority, authority, ownership, or a gameplay advantage.

## Candidate movement is not a legal-move claim

A graph connects border candidates within 0.02 degrees, accommodating simplification seams. Connections are reciprocal. Cardinal sectors select up to three edge-connected candidates within 50 degrees of the heading. Diagonal candidates come from corner contacts or two graph edges, selecting one candidate per sector. Sliders trace the first candidate of each applicable direction until a missing connection or a repeated region. Knights preview two cardinal steps and a perpendicular cardinal step. Pawn lenses distinguish forward candidates from two capture-direction candidates.

This approximation needs validation: sectors can be empty, narrow geography can produce awkward choices, and diagonal steps can skip regions. The compass and missing connections are visible. The workbench performs no occupancy, capture, king-safety, checkmate, alliance, or scoring adjudication. An exploration token is not an army or an opponent. Its travel distance is trivia along anchor-to-anchor routes, not an exact geographic transit itinerary.

Date-line ocean links are declared explicitly. North-pole ocean links connect opposite longitudes and reverse north/south direction in route preview. The Antarctic continent is mapped, but its final traversable game subdivisions and south-pole direction rules are not yet defined. Switching panes can inspect either pole. Mercator clips the polar display; globe and Robinson preserve access to the pole views.

## Coverage and interpretation

Natural Earth includes dependencies, territories, disputed areas, and heterogeneous administrative levels and generally maps de facto boundaries. The count is map coverage, not a count of sovereign states recognized by every government. This pinned source is an educational cartographic snapshot, not an authoritative current boundary service.

Missing province data is labeled as a country fallback. Real-world city-based supplemental spaces have **not** been invented or silently substituted. Countries with fewer than sixteen mapped spaces are flagged as requiring that design before full-army deployment. Existing province names and country codes remain inspectable.

## Next milestones

1. Validate reciprocal cardinal routes and visual diagonal conventions on actual province borders, coastlines, islands, date-line transitions, and both poles.
2. Design geographic city-area spaces for countries with fewer than sixteen usable deployment spaces, labeling game-created geometry separately from administrative boundaries.
3. Adapt and test the original full-match engine on the validated atlas: timed deployment, pawn departure and ocean promotion, global turns, per-rival alliance requests, stalemate half-points, and simultaneous disappearing armies.
4. Add country claiming/origin preference with first-come availability and random fallback, then persistent online rooms and explicit recipient consent.
5. Expand geography layers and source coverage; benchmark performance, rating design, and multiplayer balance.

## Rebuild and verify

Sources and raw SHA-256 values are listed in `data/manifest.json`. Cache the three original GeoJSON downloads outside the repository, then run:

```
python3 build-atlas.py --source-dir /path/to/natural-earth-cache
node test-atlas.cjs
```

The builder requires Shapely. Source data is public domain; D3 libraries keep their licenses in `vendor/`. Browser fetches the static atlas. The local `worlds-of-kings-earth-v1` record stores selected space, token, crowns, and travel ledger without sending them to a server. Clearing this journey affects only this atlas save; the original game remains separate.
