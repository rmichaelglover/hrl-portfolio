# Tiny Creek World

One planet. Many small welcomes.

An original, peaceful, browser-playable whole-world friendship and garden prototype by Manny Glover and Cypher. Its starting idea grew out of our Worlds of Kings emoji globe and Lion and Lamb animal atlas: what if the same Earth became a place to make friends instead of contesting territory?

## Play

Search a country or province, click a globe character, or choose a destination shortcut. Select **Visit this place** to travel. Say hello to neighbors, gather one story material per place per story day, craft decorations, and either place them or give them away. One hello adds one heart; a crafted gift adds two. Three hearts unlock an invitation to your home garden. Your first garden is in Georgia; another visited land place can become home. Choose a traveler avatar and name in the workshop. Day/night changes the native neighbor roster; **A new day** renews greetings and gathering.

This first version supports local single-player progress, not online multiplayer, free walking, or user accounts. Progress is saved under its own `tiny-creek-world-v1` localStorage key. Other chess and atlas editions remain separate and unchanged. Gardens in each visited place retain their decorations. Invited friends appear as explicitly fictional home visitors, never as new native-range observations.

## Distribution model

The generated atlas has 4,602 land spaces and 198 sampled ocean coves, covering 258 Natural Earth country/territory/disputed-area entries. Antarctica retains the earlier globe’s single land space; its wildlife anchor is near its derived coast rather than the South Pole. Map count does not imply a count of sovereign states.

`world-core.js` contains a curated catalog of 28 named or explicitly broad animal-group entries. Eligibility uses country lists, coarse longitude/latitude boxes, approximate habitat classes, coastal hints, ocean/land separation, and selected day/night activity. A deterministic hash chooses up to three neighbors per place, prioritizing researched named wildlife over generic groups. Hash order is a game population generator, **not a biological abundance model**. Named species boxes overinclude some unsuitable areas and omit many real populations. Country-average human population data is retained from the animal atlas but does not pretend to estimate wildlife abundance.

Koalas use a broad eastern mainland Australia box; kiwi use the main New Zealand box, excluding remote tropical territories. Orangutans are limited to Sumatra/Borneo sketches, excluding peninsular Malaysia and Java. Southern penguin and seal groups require an approximate coastal anchor. Raccoons use a native Americas sketch rather than introduced European populations. The simple model does not distinguish all penguin/seal/kangaroo/elephant species. Generic groups are labeled as groups. A leopard emoji stands in for jaguar, a bird for kiwi, a whale for orca, and an antlered deer for antlerless water deer.

Habitats are rough latitude/continent rules and a few regional overrides, not surveyed land-cover layers. Shore anchors derive from adjacency to ocean cells in the predecessor’s simplified geography; they are not exact coastlines. Ocean coves are sampled gameplay spaces, not observed animal locations. Some places intentionally have no wildlife character. Cottage gardens, creeks, trees, gathering items, and travel invitations are fictional set dressing. There are no real-world feeding or animal handling mechanics.

## Sources and provenance

Base geography: [Natural Earth](https://www.naturalearthdata.com/), v5.1.2, through the preserved [Fusion atlas](../worlds-of-kings-fusion/data/atlas.json); country density comes from the [Lion and Lamb world](../lion-and-the-lamb/world/). `data/globe.json` records the predecessor atlas SHA256 and generation notes. Natural Earth geography is public domain. Vendor D3 scripts are reused from the existing real-globe edition under their existing licenses. No third-party franchise characters or artwork are included.

Primary wildlife references guiding the deliberately approximate roster:

- [National Park Service mammal checklist](https://www.nps.gov/grsm/learn/nature/mammal-checklist.htm): southeastern US inspiration for deer and black bear.
- [University of Michigan Animal Diversity Web: red fox](https://animaldiversity.org/accounts/Vulpes_vulpes/).
- [Raccoon range research](https://onlinelibrary.wiley.com/doi/full/10.1111/mam.12249).
- [Koala distribution research](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0162207).
- [Woodland Trust mammals](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/animals/mammals/).
- [New Zealand DOC: kiwi](https://www.doc.govt.nz/kiwi) and [kākā](https://www.doc.govt.nz/kaka).
- [British Antarctic Survey wildlife](https://www.bas.ac.uk/about/education-and-schools/antarctic-wildlife/): Antarctic/subantarctic coastal inspiration, not support for every southern national range.
- [Chengdu panda research base](https://m.panda.org.cn/en/about/).
- [US Fish and Wildlife Service: jaguar](https://www.fws.gov/species/jaguar-panthera-onca).
- WWF species accounts: [elephants](https://www.worldwildlife.org/species/elephant/), [tigers](https://www.worldwildlife.org/species/tiger/), [orangutans](https://www.worldwildlife.org/species/orangutan/).
- [NOAA: killer whale](https://www.fisheries.noaa.gov/species/killer-whale).
- [Australia DCCEEW native wildlife](https://www.dcceew.gov.au/environment/wildlife-trade/natives).
- [Korea National Institute of Ecology: water deer](https://www.nie.re.kr/nie/pgm/nature/view.do?contIdx=4&menuNo=200038).

The cited sources inform general range choices; numeric bounds and regional selections are our own coarse game approximations. Generic animals are educational story groups and do not assert specific species presence.

## Responsiveness and validation

The first map load is about 4.2 MB of uncompressed JSON. Whole-world rendering uses country outlines; province borders appear after zooming. Resident rosters and emoji sprites are cached, and map characters are collision-filtered. Globe, Robinson, and Mercator views share the same game state. Search, destination buttons, and keyboard globe controls provide alternatives to pointer selection.

Run `node tiny-creek-world/test-world.cjs` from the portfolio root. Tests cover geographic exclusions, coastal and marine restrictions, day/night availability, friendship thresholds, craft costs, daily limits, visit requirements, and deterministic eligible characters across every place. Browser checks exercise a complete friendship/gift/invitation/decorating loop, reload persistence, projections, and desktop/mobile overflow checks.

Rebuild geography with `python3 tiny-creek-world/build.py` (Python + Shapely). No C++/WASM or backend is required for this version; the heavy simplified base geometry is reused from the earlier preprocessing pipeline.

Future directions: researched species range polygons, better land-cover layers, city-scale gardens, walking, richer conversations, and shared visits. These are not implemented features.
