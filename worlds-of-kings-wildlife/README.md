# Worlds of Kings · Emoji Wilds

A separate local three-player game combining the playable world globe with The Lion and the Lamb's population atlas and wildlife inspiration. The preceding [classic globe](../worlds-of-kings-fusion/) and its saves remain unchanged. A hash manifest records its exact files. This edition has its own `worlds-of-kings-wildlife-v1` browser save.

## Play

The first visit automatically places 48 pieces in the checked USA / France / South Korea opening. Each army has the normal king, queen, two rooks, bishops and knights, and eight pawns. It uses connected country spaces from the existing deployment engine. Each king starts out of check and each army has legal moves. Choosing a new combination verifies these conditions and rejects an unsafe opening rather than silently beginning an illegal one. Pass the device between players; there are no remote opponents, ratings, or matchmaking.

Select pieces on the globe or use the Your piece menu, then select a highlighted legal destination. Each army character carries its country palette on its ring. A large classical Unicode figurine anchors each playing marker, with the emoji in a smaller upper-right crest. Both share one marker instead of a dangling figurine label. The checkbox hides the figurine and returns to a full-size emoji. The accessible piece menu always names the role. Kings and queens both use their country flag. Other characters keep their identity when moving; promotion to queen changes the emoji to the country flag. Figurines and menu roles reflect the current chess role.

Native-inspired residents are assigned deterministically to all mapped land spaces with a researched roster. Other spaces receive flag-colored decorative symbols. Countries with no playing pieces on their land display a flag at their mapped capital. If the source supplies no capital, the flag uses a mapped land-space anchor instead; these are decorative country markers, not extra chess pieces. Markers update as pieces move or leave the board. Background residents are scenery: they do not occupy chess cells, block moves, or count as pieces. Armies do occupy cells, and one piece can occupy Antarctica at a time. Rendering reduces overlapping background residents and caps visible residents at 900 per view; zooming reveals more of the assignments.

All gameplay rules are inherited from the previous edition: own-king safety, turn ownership, alliance consent and request caps, simultaneous round-end elimination, stalemate half-points, shared allied victories, foreign-coast promotion, and promotion on entering the single Antarctic space or North Pole ocean spaces. Every promotion can choose queen, rook, bishop, or knight.

## Animal atlas combination

The optional Animal-atlas zones checkbox loads country population averages from the Lion and the Lamb atlas and applies the same 10/300 people/km² illustrative thresholds. The globe keeps its chess province geometry; it does not replace the board with census blocks or import the atlas's entire detailed infrastructure. Tan denotes human-pressure candidates, green buffer candidates, pale green low-population candidates, and grey missing density. These are an imagined scenario, not established habitat or measured animal occupancy. The full atlas remains available through a header link.

## Wildlife sources and approximation

The first researched country rosters are USA, France, South Korea, United Kingdom, Australia, New Zealand, Brazil, China, and Antarctica. For countries without a researched roster, the engine deliberately uses decorative flag-colored symbols. This is not a complete worldwide native-species catalog.

Country-level native inspiration does not establish presence throughout every province. France's roster concerns metropolitan wildlife; overseas parts are not independently modeled. In a later ecological layer, rosters can be filtered by province and habitat. Icon assignments are artistic, not biological distributions. Do not read a seal in Antarctica's single cell as inland seal habitat.

Primary references are linked in each roster entry in `emoji-core.js`:

- [NPS Great Smoky Mountains mammal checklist](https://www.nps.gov/grsm/learn/nature/mammal-checklist.htm) and [mammals](https://www.nps.gov/grsm/learn/nature/mammals.htm): American black bear, raccoon, white-tailed deer, red squirrel.
- [MNHN red-fox research](https://isyeb.mnhn.fr/fr/actualites/chronique-ndeg40-le-renard-roux-paris-7323) and [French terrestrial mammal red list](https://inpn.mnhn.fr/docs/LR_FCE/Liste_rouge_France_Mammiferes_de_metropole_2017.pdf): French fox and roe deer inspiration.
- [Korea National Institute of Ecology water deer](https://www.nie.re.kr/nie/pgm/nature/view.do?contIdx=4&menuNo=200038) and [endangered-species listings](https://www.nie.re.kr/nie/pgm/edSearch/list.do?menuNo=200133): water deer and Eurasian otter.
- [Woodland Trust mammal guides](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/animals/mammals/): British fox, badger, roe deer, and red squirrel.
- [Australian government koala conservation](https://www.dcceew.gov.au/environment/biodiversity/threatened/action-plan/priority-mammals/koala).
- [New Zealand DOC kiwi](https://www.doc.govt.nz/kiwi) and [penguins](https://www.doc.govt.nz/penguins).
- [Brazil ICMBio big-cat conservation plan](https://www.gov.br/icmbio/pt-br/assuntos/biodiversidade/pan/pan-grandes-felinos): jaguar.
- [Chengdu Research Base](https://m.panda.org.cn/en/about/): giant panda.
- [British Antarctic Survey wildlife](https://www.bas.ac.uk/about/education-and-schools/antarctic-wildlife/): penguins and seals in Antarctic/coastal contexts.

Emoji approximations are named: the squirrel glyph may look like a chipmunk; the Korean water deer glyph has antlers although water deer do not; the jaguar uses the leopard glyph; the kiwi uses a generic bird. Emoji artwork varies by operating system. No third-party animal artwork or quoted source passages are bundled.

## Flag palettes and preservation

`data/themes.json` contains artistic palettes for all 258 mapped countries/territories. `build-themes.py` extracts broad color groups from hampusborgos/country-flags SVG reference files at commit `c09927e63705529bbf59ca6684cd9b23225dddad`, with curated overrides for common flags and neutral fallback where needed. Flag references and palettes are not official color specifications or territorial judgments. Only derived color facts and hashes are shipped, not the SVG artwork. Decorative emoji match the broad palette by design; their actual colors depend on platform rendering.

Land uses pale flag-inspired colors by default. Classic greens are available; optional population zones take priority. The checked-in map and game engine of the previous edition remain intact and are referenced/copied instead of rewritten. `data/previous-version.json` records hashes of the preserved classic globe.

## Validation

`node worlds-of-kings-wildlife/test-world.cjs` verifies preservation, legal initial placement, theme coverage, deterministic residents, source-backed roster entries, fallback symbols, a legal move, and polar-board features. Browser checks cover automatic setup, moves, role display toggles, population overlay, save/reload, four views, accessible piece selection, and desktop/mobile layout.
