# Serve: a proposed generic English compiler primitive

“Purposes must be served or they’re only dreams.” — Michael Emanuel Glover

`serve` connects a capability to a recipient or purpose. Hosting a network server
is one contextual implementation, alongside providing a meal, helping a community,
and serving as evidence. It is a proposed computational abstraction, not a proven
indefinable semantic atom.

Proposed intermediate representation:

```text
serve(provider, offering, recipient, purpose, manner, constraints)
```

| Utterance | Offering | Recipient / purpose | Interpretation |
| --- | --- | --- | --- |
| Serve toast for supper. | toast | diners / supper | provide food |
| Serve the forum on port 8787. | forum service | clients / conversation | start a listener |
| Serve the community kindly. | assistance | community | act in service; preserve “kindly” |
| This log serves as evidence. | log | an argument | describe evidential function; no network action |
| She served a sentence. | time under a legal sentence | a legal obligation | distinct sense, not food or hosting |

Nouns, adjectives, and adverbs remain typed arguments and modifiers. Context
selects a sense and implementation. Unresolved senses remain unresolved; no
network service, shell command, or other external effect follows from word
association alone. Authorization belongs to the selected action.

The current ECC+ engine supports unary facts and universal implications. This
document does **not** claim that ECC+ executes this new grammar. The forum runtime
does implement the concrete command `python3 backend/server.py serve`.

## Dictionary-graph exploration: research plan

Use sense-level nodes, dictionary-definition dependencies, and typed lexical
relations. Keep each source and its license, context, spelling, part of speech,
definition, and sense identifier. The existing ECC+ corpora are a starting point;
they do not constitute every English meaning.

Compare strongly connected components, grounding-kernel reductions, and several
candidate cycle-breaking vocabularies before training a recursive graph neural
network. A cycle is not itself a semantic primitive. A missing definition is
missing data, not evidence of an irreducible word. Different minimal grounding
sets can exist.

The proposed learned component would rank candidate foundations by context and
test how well retained senses reconstruct or discriminate held-out definitions.
Message-passing depth alone does not establish irreducibility. Compare with
non-neural graph baselines and test on a separately constructed dictionary;
avoid evaluating on definitions already used to construct the test features.

For “serve,” compare its senses with “do,” “give,” “help,” “use,” “want,” and
“purpose.” Report stability across sources, reconstruction error, cycle
membership, and contextual usefulness. Do not label network centrality as proof
that a concept exists independently of human language or experience.

Earlier work to consult before new research code:

- [WordNet: senses and typed lexical relations](https://wordnet.princeton.edu/).
- [How Is Meaning Grounded in Dictionary Definitions?](https://arxiv.org/abs/0806.3710).
- [The Latent Structure of Dictionaries](https://arxiv.org/abs/1411.0129).
- [NSM semantic-prime chart](https://intranet.secure.griffith.edu.au/__data/assets/pdf_file/0019/346033/NSM_Chart_ENGLISH_v19_April_12_2017_Greyscale.pdf).

No GNN has been trained or new semantic-prime discovery established by this
forum implementation. These are a sourced research direction and a compiler
design proposal.
