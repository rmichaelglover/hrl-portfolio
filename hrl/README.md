# 🧬 `hrl/` — the engine

One `RelaxationLabeler`. Change `(labels, compatibility, prior)` and the same
machine labels a different world.

```
        objects ─┐
                 ├──▶  RelaxationLabeler  ──▶  strengths ──▶ assignments
   compatibility ┤        (Hummel–Zucker          │
          prior ─┘         + respected prior       └─▶ noise label  (−1)
                            + noise label)
```

| Module | What it is |
|---|---|
| `core.py` | `RelaxationLabeler` — the prior-respecting, noise-aware relaxation engine |
| `kernels.py` | `pairwise_distance_compatibility` — rotation/translation-invariant point correspondence |
| `tracking.py` | `temporal_prior` + `track_sequence` — correspondence across time (the prior is memory) |
| `consensus.py` | `relax_truth` — claims → `vtrue`/`ish`/`vfalse` over an agreement web |
| `nli.py` | `NLIAgreement` — a DeBERTa-v3 NLI model builds the agreement web from text |
| `llm_judge.py` | `LLMAgreement` + `extract_claims_llm` — Claude backend (opt-in) |

## What makes the core different 🧠

* **Respected prior** — folded into the multiplicative base of *every* update
  (`prior_strength` slides from classic Hummel–Zucker to Bayesian), so
  informative priors don't wash out and the field can't collapse onto one label.
* **Noise label** — a trailing "none of the above" class that absorbs outliers /
  spurious detections and regularizes against over-confident labelings.

Watch it converge — each point's winning-label strength climbing to a stable,
confident assignment, and the final strength matrix lighting up the correct
(permuted) marker for every point:

![core](../assets/core_convergence.png)

## Real NLP, lazily loaded 🔌

`import hrl` stays **numpy-only** — `transformers`/`torch` (for `nli.py`) and
`anthropic` (for `llm_judge.py`) are imported only when you actually use those
backends. Here's the real NLI model's agreement matrix on raw prose:

![nli](../assets/nli_agreement.png)

➡️ Full gallery: [`../assets/`](../assets/README.md)
