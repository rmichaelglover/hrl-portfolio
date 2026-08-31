"""MEGGERS — Maximally Elucidative Generic Grabby Engine, Relaxed Somewhat.

MEGGERS labels objects by one generic distinction: delimiter or delimited.
Clear delimiter evidence reads as ``vtrue``; clear delimited evidence reads as
``vfalse``; ``ish`` marks an unresolved boundary between the two. Signed
affinities then let related objects negotiate those labels by relaxation.

The engine assumes no particular geometry. A hierarchy level may be lifted
from arbitrary groups; simplicial complexes are welcome, but not required.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .consensus import ISH, TRUTH_NAMES, TRUTH_VALUES, VFALSE, VTRUE
from .core import RelaxationLabeler, RelaxationResult

__all__ = [
    "MeggersResult",
    "delimiter_prior",
    "delimitation_compatibility",
    "relax_delimitation",
    "lift_evidence",
]


@dataclass
class MeggersResult:
    """A relaxed delimiter/delimited field and its underlying HRL result."""

    labels: list[str]
    delimiter_score: np.ndarray
    hrl: RelaxationResult


def delimiter_prior(evidence: np.ndarray, *, floor: float = 0.02) -> np.ndarray:
    """Map signed evidence in ``[-1, 1]`` to ``vfalse / ish / vtrue`` priors.

    ``+1`` means clearly delimiter, ``-1`` clearly delimited, and values near
    zero reserve most prior mass for the fuzzy boundary state ``ish``.
    """
    values = np.asarray(evidence, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("evidence must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(values)) or np.any(np.abs(values) > 1):
        raise ValueError("evidence must contain finite values in [-1, 1]")
    if not 0 <= floor < 1:
        raise ValueError("floor must be in [0, 1)")

    prior = np.column_stack((
        np.maximum(-values, 0.0),
        1.0 - np.abs(values),
        np.maximum(values, 0.0),
    ))
    prior += floor
    return prior / prior.sum(axis=1, keepdims=True)


def delimitation_compatibility(affinity: np.ndarray) -> np.ndarray:
    """Convert signed object affinity to a three-label compatibility tensor.

    Positive affinity favors the same delimitation state; negative affinity
    favors opposite states. Zero leaves the pair unrelated.
    """
    links = np.asarray(affinity, dtype=float)
    if links.ndim != 2 or links.shape[0] != links.shape[1] or links.shape[0] == 0:
        raise ValueError("affinity must be a nonempty square matrix")
    if not np.all(np.isfinite(links)):
        raise ValueError("affinity must contain only finite values")

    distance = np.abs(TRUTH_VALUES[:, None] - TRUTH_VALUES[None, :]) / 2.0
    same, opposite = 1.0 - distance, distance
    n = links.shape[0]
    compatibility = np.zeros((n, 3, n, 3))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            weight = links[i, j]
            compatibility[i, :, j, :] = (
                weight * same if weight >= 0 else -weight * opposite
            )
    return compatibility


def relax_delimitation(
    evidence: np.ndarray,
    affinity: np.ndarray,
    *,
    prior_strength: float = 0.6,
    max_iterations: int = 100,
) -> MeggersResult:
    """Relax one MEGGERS hierarchy level and return Trool boundary labels."""
    prior = delimiter_prior(evidence)
    compatibility = delimitation_compatibility(affinity)
    if compatibility.shape[0] != prior.shape[0]:
        raise ValueError("evidence length must match affinity size")
    result = RelaxationLabeler(
        compatibility,
        prior,
        prior_strength=prior_strength,
        max_iterations=max_iterations,
    ).run()
    strengths = result.strengths[:, :3]
    score = strengths @ TRUTH_VALUES
    labels = [TRUTH_NAMES[index] for index in result.assignments]
    return MeggersResult(labels=labels, delimiter_score=score, hrl=result)


def lift_evidence(result: MeggersResult, groups: Iterable[Iterable[int]]) -> np.ndarray:
    """Aggregate arbitrary groups into signed evidence for the next level.

    Group structure is supplied by the caller. It may come from connected
    components, ordinary sets, learned regions, or simplicial complexes.
    """
    scores = np.asarray(result.delimiter_score)
    lifted = []
    for group in groups:
        indices = np.asarray(list(group), dtype=int)
        if indices.size == 0:
            raise ValueError("hierarchy groups must not be empty")
        if np.any(indices < 0) or np.any(indices >= scores.size):
            raise IndexError("hierarchy group index is out of range")
        lifted.append(float(scores[indices].mean()))
    if not lifted:
        raise ValueError("at least one hierarchy group is required")
    return np.asarray(lifted)
