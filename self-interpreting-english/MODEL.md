# The Self-Interpreting English Dictionary

**Michael Emanuel Glover**<br>Research model and interactive prototype · 2 November 2026

## Thesis

I propose representing English as a typed, recursively interpretable lexical graph. The graph includes the symbols used to write entries, the names and sounds of those symbols, words, senses, definitions, examples, grammatical constructions, and the rules that interpret them. The dictionary can therefore describe and interpret its own representational materials instead of treating its alphabet and parser as invisible infrastructure.

The prototype begins with the alphabet and punctuation. In `N: EN`, the key `N` denotes the grapheme U+004E. Its name is `EN`, whose written form consists of `E` and `N`; the colon is itself a grapheme, U+003A, and acts as the record separator. This small cycle is the kernel of a larger lexical system.

## Typed graph

Let the lexicon be a labeled directed multigraph

\[
G=(V,E,\tau_V,\tau_E,\alpha,\pi),
\]

where `V` is the set of nodes, `E` the set of edges, `\tau_V` and `\tau_E` assign types, `\alpha` stores node and edge attributes, and `\pi` records provenance. Node types include Unicode scalar, grapheme, letter-name, pronunciation, morpheme, word form, lexical sense, definition, example, construction, and interpreter rule. Edge types include `realizes`, `names`, `spells`, `pronounces`, `inflects`, `defines`, `exemplifies`, `selects-sense`, and `interprets`.

The typing keeps distinct facts distinct. A character is not its name; a name is not its pronunciation; a word form is not a sense; and a gloss is not the rule that parses the gloss. Relations connect these objects without collapsing them.

An entry can be represented as a record

\[
e=(k, f, s, q, m, d, x, c, p),
\]

with key `k`, written forms `f`, senses `s`, pronunciations `q`, morphology `m`, definition expressions `d`, usage examples `x`, construction links `c`, and source provenance `p`. Fields may be sets, so dialectal names and competing analyses remain explicit alternatives.

## Recursive interpretation and closure

Let `D₀` be a finite seed lexicon containing Unicode identities, the English alphabet, conventional letter names, punctuation, and a small set of grammar operators. Let `P_D` parse an expression against lexicon `D` and emit typed graph relations plus unresolved lexical hypotheses. Define the monotone expansion operator

\[
T(D)=D\cup\{\,r\mid r\text{ is a well-formed record and }P_D(r)\text{ adds a supported interpretation}\,\}.
\]

Then construct the closure sequence

\[
D_{n+1}=T(D_n), \qquad D^*=\bigcup_{n\ge0}D_n.
\]

When the seed and imported source are finite and each iteration only adds records or typed edges from a finite candidate space, the sequence stabilizes at a fixed point: `T(D*) = D*`. Open hypotheses are retained with status and provenance rather than being silently treated as resolved facts. For unbounded productive morphology or new user input, closure is computed incrementally over the affected subgraph.

Recursive definitions do not require recursive string substitution. The interpreter records references as edges, identifies strongly connected components, and evaluates each component as a graph. A cycle such as a letter name spelling itself is thus an inspectable relation. It can be grounded by character identity, pronunciation, usage, and constraints from adjacent levels. If a component has several compatible interpretations, it may retain them rather than choosing arbitrarily.

## GRRLE integration

The graph extends the existing GRRLE text frontend. For a text sequence, candidate nodes can include spans, graphemes, letter-names, word forms, parts of speech, senses, phrase structures, and definition paths. Signed directed relations encode compatibility: positive weights support joint interpretations and negative weights suppress conflicts. A generic update is

\[
s_i^{(t+1)}=\sigma\!\left(b_i+\eta\sum_j w_{ij}s_j^{(t)}\right),
\]

where `s_i` is candidate support, `b_i` is local evidence, `w_ij` is signed relational compatibility, `η` controls contextual influence, and `σ` bounds the state. Here the equation specifies an architectural interface; convergence and calibration depend on the chosen update schedule, weights, and graph. The useful consequence is that symbol identity, sound, lexical sense, syntax, and definitions can exchange evidence while their candidate identities and support traces remain inspectable.

The interpreter therefore has two layers: a deterministic typed parser that constructs admissible graph links, and a relaxation process that ranks competing admissible readings. It does not use association alone to invent a missing lexical fact. Candidate generation, provenance, and evidence remain visible.

## Bootstrap records

| Record | Typed interpretation |
|---|---|
| `N: EN` | U+004E names the letter whose conventional name is `EN`; the name spells as `E` + `N`. |
| `L: ELL` | U+004C names the letter `L`; its name spells as `E` + `L` + `L`. |
| `COLON: :` | `COLON` names punctuation U+003A, also used as the record boundary in this notation. |
| `U+003A: colon` | A code-point identifier resolves to the colon grapheme and its lexical name. |

Letter names are language conventions, not universal phonetic laws. The graph can represent variants such as `ZEE` and `ZED`, or `AITCH` and `HAITCH`, with locale, source, and pronunciation attached to each record.

## Applied research plan

1. **Validate the kernel.** Add round-trip checks for character → name → spelling → character; cover all 26 letters, punctuation, Unicode normalization, and dialect variants.
2. **Compile a licensed lexical source.** Import word forms, senses, glosses, relations, and source identifiers into typed records. Preserve original identifiers, provenance, and license metadata at record level.
3. **Ground pronunciation and use.** Add a pronunciation lexicon and corpus examples as independent evidence channels; distinguish grapheme spelling from phoneme sequence and dialect.
4. **Resolve morphology and polysemy.** Represent inflections and multiple senses as candidates, then use grammatical constructions and context to rank interpretations.
5. **Connect GRRLE.** Extend recursive span hypotheses with graph-backed character, pronunciation, sense, and definition candidates. Expose the support trace in the interface.
6. **Evaluate measurable behavior.** Measure lexical coverage, round-trip closure, sense selection, calibration, ambiguity retention, and robustness to misspelling and unfamiliar names on held-out examples.

The page’s interactive alphabet kernel is the first executable demonstration. The research contribution is the architecture: one typed graph, one compositional interpretation process, and explicit closure over the symbols and rules used by the dictionary itself.

## Codebase connection and references

The implementation direction builds on the portfolio’s GRRLE recursive span and signed-compatibility architecture, including the text frontend and its NLP roadmap:

- [GRRLE text frontend](../sandboxes/grok-relaxation-labeling/source/grrle/text.py)
- [GRRLE recursive engine](../sandboxes/grok-relaxation-labeling/source/grrle/engine.py)
- [GRRLE architecture note](../sandboxes/grok-relaxation-labeling/source/docs/GRRLE.md)
- [NLP and Lichess roadmap](../sandboxes/grok-relaxation-labeling/source/docs/ROADMAP-LICHESS-AND-NLP-GRRLE.md)

Lexical expansion can draw on established lexical resources while preserving their individual provenance and licensing:

- Fellbaum, C. (ed.). *WordNet: An Electronic Lexical Database*. MIT Press, 1998. [doi:10.7551/mitpress/7287.001.0001](https://doi.org/10.7551/mitpress/7287.001.0001).
- Princeton University. [WordNet](https://wordnet.princeton.edu/).
- Carnegie Mellon University. [CMU Pronouncing Dictionary](https://www.speech.cs.cmu.edu/cgi-bin/cmudict).
- Unicode Consortium. [The Unicode Standard](https://www.unicode.org/standard/standard.html).

The lexical sources supply organized data. The recursive self-interpretation and its integration with hierarchical relational inference are the focus of this model.
