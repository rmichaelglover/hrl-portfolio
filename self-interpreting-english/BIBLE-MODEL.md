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

The checked-in `kjv/` directory contains one compact JSON file per book and a manifest with book order, testament, chapter counts, verse counts, source URL, and source archive SHA-256. The included compiler, `tools/build_kjv_self_interpreting.py`, converts the source USFM into verse text plus occurrence-indexed annotations. It preserves KJV-added-word markup as a separate list and records Strong’s identifiers at their source word ordinals. Footnote and cross-reference apparatus are excluded from the verse string; the source USFM remains the reproducible input.

Source archive SHA-256:

```text
ce1f526c64c2376f407308c2c23cb2d2fb58efaf5296327d2d8e408c3700650d
```

James 1:19 is the first worked passage. In this source its word sequence includes `swift` at a token occurrence indexed by `G5036`, `hear` by `G0191`, `slow` by `G1021`, `speak` by `G2980`, and `wrath` by `G3709`. These are the supplied edition’s lexical links; the reader keeps the English verse and source-language lookup as distinct graph nodes.

## The dictionary layer

The English dictionary path has two complementary roles:

1. **A recursive English lexical graph** supplies spelling, letter identity, headwords, grammatical forms, multiple senses, definitions, examples, and usage relations. Its definitions are parsed with the same typed English resources as ordinary text.
2. **Webster’s 1828 American Dictionary** is a historical aid for the English register represented by the KJV. The reader links selected surface forms to their historical headwords and gives authored plain-English glosses for central James terms. As the lexicon grows, each local gloss can resolve to a source-cited Webster record and one or more modern English senses.

The Greek and Hebrew layer is separate. A Strong’s number is a stable lookup index in the source edition, not itself a lexical definition or an interpretive verdict. Where available, it connects the English occurrence to a source-language headword, morphology, pronunciation, and lexicon gloss. Translation choices can then be compared across occurrences and contexts.

For example, selecting `swift` in James 1:19 yields this path:

```text
Jas 1:19 / KJV-1769 / token 8
  → surface “swift”
  → English headword “swift”
  → historical English dictionary entry
  → source index G5036
  → Greek lemma ταχύς (tachys)
```

The reader presents the English headword, a concise contextual gloss, the exact verse address, and outbound dictionary/lexicon references. Unrecognized forms still remain selectable and can be looked up; they are marked as unresolved rather than being assigned an invented sense.

The first archaic-term records include `naughtiness`, `filthiness`, `superfluity`, and `engrafted` from James 1:21. For `naughtiness`, the reader records Webster’s historical primary sense—badness, wickedness, or evil purpose—alongside the occurrence’s Greek index `G2549` (`κακία`, *kakia*), whose range includes badness, wickedness, and, in some contexts, malice. The verse note connects the term to James’s instruction to put it away and to the contrast with receiving the word in meekness. This keeps the historical English sense, Greek lexical range, and local contextual reading distinct but connected.

## Self-interpretation and closure

The graph includes the characters used in scripture references and lexicon entries; the words in the verses; the English entries used to interpret those words; and the dictionary grammar used to read the entries. If `D_n` is the lexicon after iteration `n`, define

\[
D_{n+1}=D_n\cup\{r:\operatorname{parse}_{D_n}(r)\text{ constructs supported typed links}\}.
\]

Closure is reached when `D_{n+1}=D_n` over a finite imported record set. Cyclic definitions remain graph components, not endlessly expanded strings. A token can point to several candidate senses; grammar, local context, parallel usage, and source provenance provide relational support for resolving them. The passage text is invariant while interpretation gains structure.

This operational definition is deliberately useful: it can be checked by verifying reference identity, token alignment, dictionary coverage, cycle handling, and preservation of the source text. It also allows an interpretive claim to show its path through the graph rather than appearing as an unsupported gloss.

## James-first, whole-canon build path

1. **James reader:** navigate all five chapters; select any word; expose its surface form, token index, source Strong’s tags, Webster link, and local contextual glosses for key terms.
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
- Blue Letter Bible, [Greek lexicon G5036](https://www.blueletterbible.org/lexicon/g5036/kjv/tr/), linked from the example occurrence `swift` in James 1:19.
- Blue Letter Bible, [Greek lexicon G2549](https://www.blueletterbible.org/lexicon/g2549/kjv/tr/), linked from `naughtiness` in James 1:21.

The complete Bible corpus and reader are this project’s working implementation. The contribution is the translation-bound, word-occurrence graph and the design that lets scripture, English lexicography, and source-language lookup be interpreted through one recursively extensible lexical system.
