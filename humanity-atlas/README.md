# Humanity Atlas — first edition

A small PG learning site about food, hospitality, material evidence and symbols.
Eight curated cards are a starting sample, not a representative census of humanity.

## Sources and interpretation

Each card in data.js links its source. Summaries are original paraphrases, checked
2026-09-26 using museum, community, government, literary-edition and UNESCO records.
UNESCO and some museum full pages blocked automated retrieval; their indexed record
summaries supported the narrow facts used. No full texts, images, or restricted
community records were imported. Flags and the Aboriginal flag diagram are labeled;
modern flags are not retrospectively assigned to ancient peoples. The wampum emoji
is explicitly a cue, not an official representation. No community endorsement is implied.

Sources include the Haudenosaunee Confederacy, New York State Museum, Queensland
Parks, National Museum of Australia, UNESCO, The Met, Genesis 18:1–8 (KJV), and
Homer's Odyssey Book 6 (A. T. Murray, Perseus). Living practices and textual accounts
are explicitly distinguished. Card content is the complete curated corpus for v0.1;
this is not the earlier proposed 24-excerpt research benchmark.

## Model

Objects: eight source-linked cards. Labels: food, welcome, land. Each is an
independent channel, so memberships overlap. The object graph is generated from
editor-authored shared themes. A three-way welcome comparison connects couscous,
kimjang and bunya; all its edges exist in the graph, satisfying face closure for
this displayed 2-simplex. Hierarchy pools cards into three theme hubs. The label
complex is the themes and their observed co-occurrences, rather than a duplicate
of the object complex; the theme selector operationalizes a label becoming the
focus of inquiry. Full dynamic schema induction is future work.

The prior-respecting logistic update follows the design of the existing
/home/rmichaelglover/triadic-unity-research/contractive.py, extended here with bounded
neighbor, hub and product-of-two triple messages. For each independent channel,
q_new = sigmoid(logit(prior) + 0.6 * mean(messages)). Seeds are 0.85 for an authored
connection and 0.15 otherwise. The UI reports numerical residual convergence.
No claim is made that the old theorem automatically transfers to this extension.
Affinities are editorial, not calibrated truth probabilities or cultural rankings.
Switching the triangle off gives a real pairwise-plus-hierarchy ablation.

The evidence exercise uses supported / unresolved / contradicted judgments on
explicit claims. No model judges the worth of people, infers private ancestry,
or treats a shared story as proof of historical identity. Historical dates are
not inferred from thematic affinity. Distinct cause, descent and exchange relations
will require a larger independently reviewed dataset before implementation.

## Design and resource budget

Cyan / lilac / mint label themes; shapes label evidence types; all have text
alternatives. Unicode modern flags carry country names in text. Aboriginal flag
colors are retained as a specific symbol, independent of the site's theme palette.
Responsive CSS, native buttons, focus outlines, skip link and reduced-motion support.
No external fonts, libraries, analytics, accounts or network requests on page load.
A tiny static corpus and bounded local solver keep resource use small.

## Validation and next work

Run `node humanity-atlas/test.cjs`. Browser checks cover filtering, no-result states,
map selection, theme changes, triangle ablation, quiz feedback and small screens.
Next research phase: community review, more specific regional voices, per-claim
source lineages, revision/removal workflow, independent annotation, and held-out
comparisons before making any accuracy claim. The current prototype is a public
learning demonstration, not a validated historical inference system.
