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

The word is treated as the semantic atom. Candidate interpretations and proofs are distinct. Historical dictionaries, corpus imports, a public commons, interpretation ranking, and contextual compilation are not implemented. Study those requirements before extending the grammar. This project makes no claim to be the first English compiler.

Run the meaningful inference checks with `node test-engine.cjs`. Open index.html through a static web server or the published portfolio.
