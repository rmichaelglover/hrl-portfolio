# ecc+++ — first experimental fragment

A deterministic, browser-only English compiler and interpretation lab. No learned model, external API, or relaxation labeling is involved at runtime. No measured energy-efficiency claim is made.

## Semantics

“Every A is B” compiles to a universal implication from unary predicate A to unary predicate B. “Every A is not B” has an explicitly negative conclusion. “N is A” supplies a positive fact; “N is not A” supplies a negative fact. Names and predicates are normalized to lowercase and matched literally. Articles, plural morphology, synonym resolution, quantifier nesting, and arbitrary natural-language syntax are not supported. The parser accepts one statement per line, with optional trailing period or exclamation mark.

The finite forward-chaining engine applies rules only to positive facts, retaining an individual’s name. Each new fact records the rule’s source line and the supporting fact’s step number. Duplicate facts are suppressed. Since no new names or predicate strings are introduced by inference, the set of possible facts is finite and the loop terminates. Cyclic rules do not cause an infinite derivation.

A query can be supported, opposed, unresolved, or both. Both is a conflict, not a resolved truth value. This is a signed forward-rule system, not a complete classical or paraconsistent first-order calculus. It does not use explosion or contraposition. Unsupported source lines are excluded and reported; conclusions are explicitly restricted to accepted lines. Premises are assumptions, not verified claims about reality.

## Meaning and record

The English–Turkish glossary is a small stipulated set of candidate senses, not an exhaustive dictionary. A sense-dependent translation is not a claim that two words are interchangeable in every context.

Records preserve original wording, source/context, optional interpretation, and recording time. Persistence is device-local browser storage, not a collaborative shared server. Storage failure is disclosed; JSON export works without persistence. Content is rendered through textContent, not evaluated as HTML or code.

## Scope and next research

The word is treated as the semantic atom. Candidate interpretations and proofs are distinct. Historical dictionary and scripture collections are now included through a separate source explorer. A public shared commons, interpretation ranking, and contextual compilation are not implemented. Study those requirements before extending the grammar. This project makes no claim to be the first English compiler.

Run the meaningful inference checks with `node test-engine.cjs`. Open index.html through a static web server or the published portfolio.


## Six-source library

- Old Testament: KJV English, Project Gutenberg #10; 39 books and 23,145 verse records.
- New Testament: the same edition; 27 books and 7,957 verse records.
- Qur’an: J. M. Rodwell’s historical English translation, Project Gutenberg #2800. All 114 surahs; 6,285 edition paragraphs. These paragraph labels are not modern ayah numbering. Surahs are displayed in standard numerical order even though Rodwell arranges them differently. Separated translator notes and introductions are excluded from scripture search; inline note markers remain.
- Old English: J. R. Clark Hall’s A Concise Anglo-Saxon Dictionary, second edition (1916), Project Gutenberg #31543; 29,342 extracted entry groups.
- Middle English: Mayhew and Skeat’s A Concise Dictionary of Middle English (1888), Project Gutenberg #10625; 10,954 extracted entry groups.
- Early Modern English: Cawdrey’s A Table Alphabeticall (1604), CrossWire SWORD module 1.0; all 2,516 module records. Module grouping is not claimed to reproduce a printed headword count.

Old and Middle English name language periods; the selected dictionaries were compiled later. Scripture here is in English translation, not original Hebrew, Aramaic, Greek, or Arabic. No one-entry/one-sense assumption is made.

The corpus explorer fetches source data only on selection or explicit comparison, caches it for the session, and performs searching and indexing in a web worker. Word indices are constructed only when the word-string view is requested. It makes no energy benchmark claim. No source data is sent to an external model. JSON download provides the actual data used in the interface.

Words are sequences of Unicode letters and combining marks, with internal apostrophes and hyphens retained. Exact forms—including case and historical diacritics—remain separate primitive word-strings. Case-insensitive search is labeled and does not merge the original forms. Phrase/full-entry search uses substring matching; clicking a word-string uses exact token occurrence matching. Dictionary headword search matches the recorded headwords, not inferred synonyms. Comparisons do not prove senses are identical. The word-string index of a dictionary includes its English glosses and cited material, not just its historical headwords.

`build-corpora.py` imports the chosen editions, records source hashes and output hashes, and saves a manifest with coverage and source URLs. Pass a directory of cached source downloads for an offline rebuild; otherwise it downloads the specified URLs. HTML whitespace is normalized. The importer preserves Bible paragraph continuations and separates multiple verse labels within a paragraph. Dictionary senses are retained together as source entries rather than automatically interpreted.

The source texts have their own rights notices in `corpora/SOURCE-LICENSES.txt`: Project Gutenberg identifies its editions as public domain in the USA and includes its redistribution terms; the Cawdrey SWORD module declares public-domain distribution. These third-party texts are not relicensed under the portfolio’s code license.

Run `node test-corpora.cjs` to check hashes, counts, reference identities, coverage, tokenization, and query behavior. Run the original `node test-engine.cjs` to verify that the controlled-English inference fragment is unchanged.
