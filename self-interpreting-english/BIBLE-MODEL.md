# The Self-Interpreting Bible: KJV Corpus and James-First Reader

**Michael Emanuel Glover** · Research model, corpus compiler, and interactive reader · 2 November 2026

## The project

I am extending the self-interpreting English lexicon into a Bible reader bound to a named, stable translation. The first corpus is the standardized 1769 King James Version (KJV), distributed by eBible.org as `eng-kjv2006` USFM with the protocanon: 39 Old Testament books and 27 New Testament books. The interface opens on James 1 and navigates the full 66-book corpus.

The translation is the textual anchor. Dictionary records, grammatical analysis, Strong’s references, cross-references, and interpretive notes are linked data around the verse. They do not silently rewrite its words. This lets a reader move from a familiar translation into the word’s spelling, lexical candidates, historical English usage, source-language index, chapter, and book while preserving the exact reference.

## Data model

Let a Bible collection be a graph

\[
\mathcal B=(V,E,\tau,\alpha,\pi),
\]

where `V` contains typed nodes, `E` contains typed relations, `\tau` gives node and edge types, `\alpha` stores attributes, and `\pi` stores provenance. Core node types are `Translation`, `Book`, `Chapter`, `Verse`, `TokenOccurrence`, `UnicodeCharacter`, `EnglishLexeme`, `EnglishSense`, `Definition`, `StrongIndex`, and `SourceLanguageLexeme`.

A token occurrence is identified by

\[
o=(t,b,c,v,i),
\]

where `t` is the translation-edition ID, `b` the book ID, `c` the chapter number, `v` the printed verse label, and `i` the token ordinal within that verse. This makes repeated words different occurrence nodes while allowing them to point to the same English lexeme or original-language index.

Representative relations are:

```text
Verse --contains--> TokenOccurrence
TokenOccurrence --has-surface-form--> EnglishWordForm
EnglishWordForm --spells--> UnicodeCharacter*
EnglishWordForm --candidate-lemma--> EnglishLexeme
EnglishLexeme --has-sense--> EnglishSense
EnglishSense --has-definition--> Definition
TokenOccurrence --has-source-index--> StrongIndex
StrongIndex --indexes--> SourceLanguageLexeme
Verse --next-to / cross-references--> Verse
```

The asterisk denotes a sequence of character links, not an unordered set. Part of speech, morphology, dialect, sense, and source remain fields or edges so an interpretation can preserve alternatives.

## Fixed edition and corpus

The reader uses the eBible.org `eng-kjv2006` USFM distribution. The source identifies it as the KJV with the standardized 1769 text, Strong’s numbers, and the 66-book protocanon. Its text package credits CrossWire Bible Society and eBible.org. In the United States the KJV text is public domain; the source page records the Crown-patent printing exception for the United Kingdom.

The checked-in `kjv/` directory contains one compact JSON file per book and a manifest with book order, testament, chapter counts, verse counts, source URL, and source archive SHA-256. The included compiler, `tools/build_kjv_self_interpreting.py`, converts the source USFM into verse text plus occurrence-indexed annotations. It preserves KJV-added-word markup as a separate list and records Strong’s identifiers at their source word ordinals. Some supplied verse strings also contain inline `|strong="…"` markers. The browser reader strips this source syntax before display, attaches each inline tag to its preceding word, and remaps later annotation indices; tags without a matching displayed token remain visible as linked verse notes instead of disappearing. Footnote and cross-reference apparatus are excluded from the verse string; the source USFM remains the reproducible input.

Source archive SHA-256:

```text
ce1f526c64c2376f407308c2c23cb2d2fb58efaf5296327d2d8e408c3700650d
```

James 1:19 is the first worked passage. In this source its word sequence includes `swift` at a token occurrence indexed by `G5036`, `hear` by `G0191`, `slow` by `G1021`, `speak` by `G2980`, and `wrath` by `G3709`. These are the supplied edition’s lexical links; the reader keeps the English verse and source-language lookup as distinct graph nodes.

## The dictionary layer

The English dictionary path combines three complementary sources:

1. **A recursive English lexical graph** supplies spelling, letter identity, headwords, grammatical forms, multiple senses, definitions, examples, and usage relations. Its definitions are parsed with the same typed English resources as ordinary text.
2. **Princeton WordNet 3.0** supplies a local, broad English candidate-sense layer for KJV forms. `lexicon/wordnet-3.0.json` is a generated subset containing senses and morphology links reachable from the corpus. Every candidate retains its WordNet sense ID, part of speech, lexicographer file, gloss, examples, and provenance. The reader exposes all listed candidates rather than choosing a contextual sense automatically.
3. **Webster’s 1828 American Dictionary** is a historical aid for the English register represented by the KJV. Selected records link to historical headwords; the interface distinguishes paraphrased historical senses from project-authored glosses and links each candidate sense to its provenance.

The project-curated records now live in `lexicon/lexicon.json`, versioned as `hrl.self-interpreting-lexicon/v1`. Each English lexeme has a stable ID, headword, part of speech, candidate senses, and optional verse notes and source-language links. `surfaceForms` records explicit links from inflected forms to lexemes, with project provenance for the morphological analysis. The separately generated WordNet file has its own source and license metadata; `tools/build_wordnet_subset.py` rebuilds it from Princeton WordNet 3.0 data and the checked-in KJV corpus. The top-level provenance registry describes the KJV corpus, Webster 1828, Strong’s Greek lexicon, and project-authored glosses, morphology, and contextual notes. Source-language records have their own IDs, lemmas, transliterations, glosses, citations, and provenance. Phrase-level links retain cases where the source tags a multiword English expression at one token. This replaces the former page-local gloss, inflection, source-gloss, and context-note maps.

The Greek and Hebrew layer is separate. A Strong’s number is a stable lookup index in the source edition, not itself a lexical definition or an interpretive verdict. Where available, it connects the English occurrence to a source-language headword, morphology, pronunciation, and lexicon gloss. The interpreter canonicalizes zero-padded corpus tags for record lookup while preserving the original tag in the displayed occurrence path; for example, `G0182` resolves to the local `G182` record. If a source-language record has not yet been imported, the occurrence still receives a language-appropriate outbound lexicon link.

For example, selecting `swift` in James 1:19 yields this path:

```text
Jas 1:19 / KJV-1769 / token 8
  → surface “swift”
  → English headword “swift”
  → historical English dictionary entry
  → source index G5036
  → Greek lemma ταχύς (tachys)
```

The reader follows the selected occurrence through the registered project form or WordNet surface-form link, English lexeme and candidate senses, occurrence-level Strong’s tag, and any imported source-language lexeme. It displays that sequence as an interpretation path, alongside the sense-by-sense provenance and any note matched to the exact verse. This path is deterministic link traversal: it exposes which records were followed and which links are absent; it does not silently select one sense as the only reading. A visible status reports whether the local WordNet file loaded. Forms with no local record remain selectable, use an external Webster search link, and are marked as having no local headword rather than being assigned an invented sense.

The first archaic-term records include `naughtiness`, `filthiness`, `superfluity`, and `engrafted` from James 1:21. For `naughtiness`, the reader records Webster’s historical primary sense—badness, wickedness, or evil purpose—alongside the occurrence’s Greek index `G2549` (`κακία`, *kakia*), whose range includes badness, wickedness, and, in some contexts, malice. The verse note connects the term to James’s instruction to put it away and to the contrast with receiving the word in meekness. This keeps the historical English sense, Greek lexical range, and local contextual reading distinct but connected.

The James seed also includes everyday and theological vocabulary such as `servant`, `patience`, `temptation`, `wisdom`, `righteousness`, `faith`, `liberty`, and `rejoice`. In James 1:1, `servant` links to Webster’s English entry and to Greek `G1401`, *doulos*. The lexical note preserves both the KJV’s “servant” and the Greek term’s broader range, including “slave” or “bondservant”; the verse context shows James’s self-description as belonging to God and the Lord Jesus Christ. James 1:8 `unstable` resolves its padded occurrence tag `G0182` to Greek `G182`, *akatastatos* (ἀκατάστατος), with the sourced lexical range “unstable, inconstant, or restless.” In James 2:13, `rejoiceth` resolves through its project-curated archaic-inflection link to Webster’s `rejoice` entry. Its token has no direct Strong’s tag; a phrase link connects “mercy rejoiceth against” to `G2620`, which the KJV source places on the word `against`. The reader shows both the exact token annotation and the phrase-level lexical relation so readers can inspect how the English expression and source tag align.

The whole-canon audit in `lexicon/coverage-audit.json` and `lexicon/coverage-audit.csv` covers all 790,453 displayed word occurrences and 12,676 distinct case-folded forms. The curated project layer contains 41 English lexemes and 25 registered forms, directly resolving 9,987 occurrences. The generated WordNet 3.0 subset links 8,001 forms to 6,344 headwords and 25,815 candidate senses. Together, curated and WordNet data provide local dictionary records for 8,011 distinct forms and 464,000 occurrences (58.701%). The remaining 4,665 forms and 326,453 occurrences are explicitly marked as external-lookup fallback; a fallback link is not counted as a local definition. Run `python3 self-interpreting-english/tools/audit_kjv_lexicon.py` to regenerate the form-by-form CSV, JSON summary, and unaligned annotation inventory. The audit also records that the reader removed 35,489 inline Strong’s markers from 7,857 verses and exposes the 48 source annotation keys that have no matching displayed token in a separate linked inventory.

## Self-interpretation and closure

The graph includes the characters used in scripture references and lexicon entries; the words in the verses; the English entries used to interpret those words; and the dictionary grammar used to read the entries. If `D_n` is the lexicon after iteration `n`, define

\[
D_{n+1}=D_n\cup\{r:\operatorname{parse}_{D_n}(r)\text{ constructs supported typed links}\}.
\]

Closure is reached when `D_{n+1}=D_n` over a finite imported record set. Cyclic definitions remain graph components, not endlessly expanded strings. A token can point to several candidate senses; grammar, local context, parallel usage, and source provenance provide relational support for resolving them. The passage text is invariant while interpretation gains structure.

This operational definition is deliberately useful: it can be checked by verifying reference identity, token alignment, dictionary coverage, cycle handling, and preservation of the source text. It also allows an interpretive claim to show its path through the graph rather than appearing as an unsupported gloss.

## James-first, whole-canon build path

1. **James reader:** navigate all five chapters; select any word; expose its surface form, zero-based token index, traversed lexicon links, candidate senses with provenance, source Strong’s tags, Webster link, and verse-specific notes for key terms.
2. **English lexicon:** add licensed or public-domain headword, inflection, definition, and example records with source and edition metadata.
3. **Original-language records:** import a compatible Hebrew and Greek lexicon, morphology, and transliteration source; retain that source’s license and record IDs.
4. **Whole-canon navigation:** load any of the 66 books and chapters from the same edition-bound schema; add search, concordance, and linked occurrences.
5. **Context relations:** add source-linked cross-references and parallel wording, then use hierarchical relaxation labeling to keep competing senses visible and score context-compatible paths.
6. **Canon and edition extensions:** register other textual canons, Apocrypha collections, or translations as distinct collections with their own edition IDs, reference maps, and provenance rather than merging their wording into this KJV corpus.

## Sources

- eBible.org, [King James (Authorized) Version, `eng-kjv2006`](https://ebible.org/bible/details.php?all=1&id=eng-kjv2006), including edition description, source credits, license statement, and developer downloads.
- eBible.org, [USFM source archive](https://ebible.org/Scriptures/eng-kjv2006_usfm.zip). Source package used for the checked-in corpus and Strong’s word tags.
- CrossWire Bible Society, [KJV module notes](https://wiki.crosswire.org/CrossWire_KJV), describing the 1769 Oxford basis and source lineage of its Strong’s annotations.
- Noah Webster, *An American Dictionary of the English Language* (1828); [digitized edition notes and source attribution](https://1828dictionary.com/about/).
- Webster 1828, [“Naughtiness”](https://webstersdictionary1828.com/Dictionary/naughtiness), whose primary noun sense is badness, wickedness, or evil purpose.
- Webster 1828, [“Servant”](https://webstersdictionary1828.com/Dictionary/servant).
- Blue Letter Bible, [Greek lexicon G5036](https://www.blueletterbible.org/lexicon/g5036/kjv/tr/), linked from the example occurrence `swift` in James 1:19.
- Blue Letter Bible, [Greek lexicon G2549](https://www.blueletterbible.org/lexicon/g2549/kjv/tr/), linked from `naughtiness` in James 1:21.
- Blue Letter Bible, [Greek lexicon G1401](https://www.blueletterbible.org/lexicon/g1401/kjv/tr/), linked from `servant` in James 1:1.
- Blue Letter Bible, [Greek lexicon G4045](https://www.blueletterbible.org/lexicon/g4045/kjv/tr/), linked to the KJV phrase “fall into” in James 1:2; the source annotation is on “into.”
- Princeton University, Cognitive Science Laboratory, [WordNet 3.0](https://wordnet.princeton.edu/), with the applicable license and attribution in `lexicon/WORDNET-LICENSE.txt`; the local subset is generated by `tools/build_wordnet_subset.py`.
- Webster 1828, [“Fall”](https://webstersdictionary1828.com/Dictionary/fall), historical English senses and usage examples for `fall`.
- Blue Letter Bible, [Greek lexicon G182](https://www.blueletterbible.org/lexicon/g182/kjv/tr/), linked from `unstable` in James 1:8.
- Blue Letter Bible, [Greek lexicon G2620](https://www.blueletterbible.org/lexicon/g2620/kjv/tr/), linked at phrase level from “mercy rejoiceth against” in James 2:13.
- Webster 1828, [“Rejoice”](https://webstersdictionary1828.com/Dictionary/rejoice), linked from `rejoiceth` in James 2:13.

The complete Bible corpus and reader are this project’s working implementation. The contribution is the translation-bound, word-occurrence graph and the design that lets scripture, English lexicography, and source-language lookup be interpreted through one recursively extensible lexical system.
