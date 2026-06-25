"""Syncretistic consensus — relax a web of claims to vtrue / ish / vfalse.

Every model is a simplification of the world, so the "true" picture is a
weighted reconciliation of many models against each other and against the
observations we trust most. This module casts that as relaxation labeling:

* **objects** = claims (sentences extracted from papers, theory statements…),
* **labels**  = the three Trool truth values ``vfalse (-1)``, ``ish (0)``,
  ``vtrue (+1)``,
* **compatibility** = an *agreement matrix*: claims that entail each other want
  the same truth value; claims that contradict want opposite ones,
* **prior** = how true a claim has already proven — a few trusted observations
  *anchor* the field and break the global sign symmetry,
* **noise label** (optional) = a claim that fits no consensus — a spurious model.

Relaxation then settles every claim onto a truth value consistent with the web,
and a claim pulled equally toward truth and falsehood lands, correctly, on
``ish``. The agreement matrix is the only NLP-dependent part and is fully
swappable: hand-authored, the lexical heuristic here, or a real NLI / embedding
/ LLM-judge front-end.
"""
from __future__ import annotations

import re

import numpy as np

from .core import RelaxationLabeler

__all__ = [
    "VFALSE", "ISH", "VTRUE", "TRUTH_NAMES", "TRUTH_VALUES",
    "agreement_to_compatibility", "anchor_prior", "relax_truth",
    "truth_report", "lexical_agreement",
]

VFALSE, ISH, VTRUE = 0, 1, 2
TRUTH_NAMES = ["vfalse", "ish", "vtrue"]
TRUTH_VALUES = np.array([-1.0, 0.0, 1.0])  # signed truth per label


def agreement_to_compatibility(agreement: np.ndarray, *, neutral: float = 0.0) -> np.ndarray:
    """Turn an ``[n, n]`` agreement matrix into an ``[n, 3, n, 3]`` kernel.

    ``agreement[i, k] > 0`` (claims agree/entail) rewards i and k sharing a
    truth value; ``< 0`` (contradict) rewards opposite truth values; ``0`` is
    neutral. The magnitude scales the strength of the coupling.
    """
    A = np.asarray(agreement, dtype=float)
    n = A.shape[0]
    va, vb = TRUTH_VALUES[:, None], TRUTH_VALUES[None, :]
    same = 1.0 - np.abs(va - vb) / 2.0   # [3,3]: equal->1, opposite->0
    opposite = np.abs(va - vb) / 2.0     # [3,3]: opposite->1, equal->0

    compat = np.zeros((n, 3, n, 3))
    for i in range(n):
        for k in range(n):
            if i == k:
                continue
            a = A[i, k]
            if a > 0:
                compat[i, :, k, :] = a * same
            elif a < 0:
                compat[i, :, k, :] = (-a) * opposite
            else:
                compat[i, :, k, :] = neutral
    return compat


def anchor_prior(n: int, anchors: dict[int, int], *, strength: float = 0.9) -> np.ndarray:
    """Prior that pins ``anchors`` (claim index -> truth label) and leaves the
    rest uniform. The anchors are trusted observations that break the
    truth/falsehood sign symmetry of a pure contradiction web."""
    prior = np.full((n, 3), 1.0 / 3.0)
    for i, truth in anchors.items():
        row = np.full(3, (1.0 - strength) / 2.0)
        row[truth] = strength
        prior[i] = row
    return prior


def relax_truth(
    agreement: np.ndarray,
    prior: np.ndarray | None = None,
    *,
    noise: bool = False,
    prior_strength: float = 0.5,
    max_iterations: int = 200,
    **kwargs,
):
    """Relax a claim web to truth values. Returns a ``RelaxationResult``."""
    compat = agreement_to_compatibility(agreement)
    return RelaxationLabeler(
        compat, prior, noise=noise, prior_strength=prior_strength,
        max_iterations=max_iterations, **kwargs,
    ).run()


def truth_report(result) -> list[dict]:
    """Per-claim ``{truth, score, confidence}``; ``score`` is the expected truth
    value in ``[-1, +1]`` (``-1`` false … ``+1`` true)."""
    out = []
    for row in result.strengths:
        s = row[:3]
        total = s.sum()
        norm = s / total if total > 0 else s
        out.append({
            "truth": TRUTH_NAMES[int(np.argmax(s))],
            "score": float(np.dot(norm, TRUTH_VALUES)),
            "confidence": float(np.max(norm)),
        })
    return out


# --- swappable NLP front-end (placeholder for a real NLI / embedding model) ---

_NEGATIONS = {"not", "no", "never", "cannot", "without", "neither", "nor",
              "false", "wrong", "incorrect", "fails", "refutes"}


def lexical_agreement(texts: list[str], *, threshold: float = 0.2) -> np.ndarray:
    """A crude, offline agreement estimate: bag-of-words cosine for topical
    overlap, flipped to *contradiction* when two similar sentences differ in
    negation polarity. Good enough to demo the text → web seam; replace with a
    real natural-language-inference model for serious use.
    """
    def tokens(s: str) -> list[str]:
        return re.findall(r"[a-z']+", s.lower())

    vocab = sorted({w for s in texts for w in tokens(s) if w not in _NEGATIONS})
    index = {w: i for i, w in enumerate(vocab)}
    vectors, polarity = [], []
    for s in texts:
        toks = tokens(s)
        vec = np.zeros(len(vocab))
        for w in toks:
            if w in index:
                vec[index[w]] += 1.0
        neg = sum(1 for w in toks if w in _NEGATIONS or w.endswith("n't")) % 2
        norm = np.linalg.norm(vec)
        vectors.append(vec / norm if norm > 0 else vec)
        polarity.append(neg)

    V = np.array(vectors)
    sim = V @ V.T
    n = len(texts)
    agreement = np.zeros((n, n))
    for i in range(n):
        for k in range(n):
            if i == k or sim[i, k] < threshold:
                continue
            agreement[i, k] = sim[i, k] if polarity[i] == polarity[k] else -sim[i, k]
    return agreement
