# Before You Take — working tutor 0.1

A focused classical-AI teaching prototype for roughly 850–1250 Lichess players.
It teaches a bounded habit: inspect the immediate consequence of a capture.

Run from the portfolio root:

```sh
python3 -m http.server 8765
```

Open http://localhost:8765/capture-tutor/ . Opening index.html directly also
works in browsers that permit its local scripts; persistence may be restricted.
The runtime uses local files only, with no installation, model, engine, account,
analytics, external fonts, or API calls. It has no service worker/offline cache.

## What is implemented

- Three authored concepts: immediate replies, abandoned defenses, material count.
- Six positions: three constructions and their color-mirrored counterparts.
- Decide, predict, replay, explain, then suggest another exercise.
- Hints, board flipping, coordinate labels, keyboard-accessible answer buttons,
  a textual board description for assistive technology, and mobile layout.
- Browser-local first-attempt records, with graceful storage failure.
- Explicit relaxation-labeling inference drives next-exercise selection.

This is not an arbitrary-position tutor, engine replacement, rating estimator,
or validated instructional product. Mirrored positions test the same motif;
finishing them does not establish transfer to independent positions or games.
The safe-capture example verifies absence of an immediate check or capture,
not every possible tactical continuation.

## Architecture and relation to existing work

`relax.js` is domain-neutral sparse pairwise relaxation labeling. It adapts the
respected-prior update from the existing local
`Code/relaxation-labeling/python/hrl_generic/engine.py`. It is a limited JS
implementation, not a full port of GRRLE: no order-3 factors, automatic object
construction, learned weights, or incompatibility-driven null channel yet.
Its objects have explicit label priors, factors encode compatibility, and
fixed evidence objects send support through repeated synchronous updates.

ASCII update:

```text
support[i,a] = sum(factor[i,j,a,b] * strength[j,b])
base[i,a] = prior[i,a]^0.85 * strength[i,a]^0.15
next[i,a] = normalize(base[i,a] * (1 + row_minmax(support[i,a])))
```

`tutor.js` is the chess curriculum adapter. Skills have practice/steady/unknown
labels and initial strengths [0.2, 0.2, 0.6]. The unknown label is an ordinary
label, not the generic engine's rejection mechanism. Each completed first
attempt supplies a fixed evidence node:

- Both answers correct, no hint: [0.05, 0.90, 0.05].
- Both correct with a hint: [0.40, 0.40, 0.20].
- Either incorrect: [0.90, 0.05, 0.05].

Identity compatibility links evidence to its skill. A weaker identity factor
connects reply-checking and defense-checking. Unseen exercises are ranked by
`practice_strength + 0.5 * unknown_strength`, breaking ties by authored order.
These heuristic strengths are not calibrated probabilities. They do not claim
knowledge of an opponent's intent or infer player Elo.

`app.js` owns the teaching sequence, display and storage. The board displays
preverified frames; it does not generate arbitrary legal moves. Feedback is
authored. GRRLE guides curriculum inference, not tactical truth checking.

`build_lessons.py` uses the locally installed python-chess only at build/test
time to verify initial validity, all line moves, alternative reply legality,
checkmates, material deltas, and the absence of immediate forcing replies in
the safe examples. It generates `lessons.js`, committed alongside its source.

## Validation

```sh
python3 capture-tutor/build_lessons.py
node capture-tutor/test.cjs
```

Tests cover generic propagation, fixed anchors, normalization, recommendation,
full interaction flow, replay boundaries, hint accounting, storage denial,
reload, clearing progress, and preservation of first attempts on replay.
Browser verification additionally checks rendering at desktop/mobile sizes.
With Chrome and Python websocket-client installed, serve the repository at
127.0.0.1:8766 and run `python3 capture-tutor/browser_check.py`. The test uses
an isolated browser profile under /tmp, not your normal browsing profile.

## Data and licensing

No real players' games or personal data are included. Progress consists only
of exercise IDs, skill IDs and three answer/hint booleans. The first completed
attempt per ID is retained until explicitly cleared. Abandoned attempts are
not saved. Recommendation is rebuilt on load.

This directory inherits the repository's MIRL-1.0 source-available license.
It is not being represented as an OSI-approved open-source release. A future
license choice is a product decision for the owner, not changed by this work.

Board geometry is measured for every cell across 216 combinations: six viewport
widths (320, 390, 720, 721, 850, 1280), six lessons, two orientations and three
replay frames. Width/height differences must stay below one CSS pixel. Run
`python3 capture-tutor/browser_check.py --share-card` to also regenerate the
1200x630 sharing card.
