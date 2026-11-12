"""A domain-independent relaxation field over recursive span hypotheses."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Generic, Hashable, Iterable, Sequence, TypeVar

import numpy as np


Atom = TypeVar("Atom", bound=Hashable)


@dataclass(frozen=True)
class AtomStream(Generic[Atom]):
    """Ordered atoms with no domain assumptions (letters, bytes, moves, events)."""

    atoms: tuple[Atom, ...]

    @classmethod
    def from_iterable(cls, atoms: Iterable[Atom]):
        return cls(tuple(atoms))

    def __len__(self):
        return len(self.atoms)


@dataclass(frozen=True)
class Hypothesis:
    """One proposed label over an atom span at one recursive level."""

    key: str
    level: int
    start: int
    end: int
    label: str
    prior: float = 0.5
    parent: str | None = None

    def __post_init__(self):
        if self.level < 0 or self.start < 0 or self.end <= self.start:
            raise ValueError("hypothesis requires level >= 0 and a non-empty span")
        if not 0.0 <= self.prior <= 1.0:
            raise ValueError("hypothesis prior must be in [0, 1]")


@dataclass(frozen=True)
class Relation:
    """Directed compatibility support: target activation influences source."""

    source: str
    target: str
    weight: float
    kind: str = "compatibility"


@dataclass(frozen=True)
class GRRLEResult:
    hypotheses: tuple[Hypothesis, ...]
    strengths: np.ndarray
    iterations: int
    converged: bool
    history: tuple[np.ndarray, ...] | None
    prior: np.ndarray
    relation_matrix: np.ndarray

    def strength(self, key: str) -> float:
        for i, hypothesis in enumerate(self.hypotheses):
            if hypothesis.key == key:
                return float(self.strengths[i])
        raise KeyError(key)


class GRRLE:
    """Relax mutually supporting or competing recursive hypotheses.

    The update is a damped recurrent logistic field::

        s_i <- sigmoid(logit(prior_i) + gain * sum_j(w_ij * s_j))

    Positive relations reinforce; negative relations inhibit. Relations may
    connect hypotheses at the same level or cross levels in either direction,
    making the hierarchy recursive rather than a one-way parsing pipeline.
    """

    def __init__(self, hypotheses: Sequence[Hypothesis], relations: Sequence[Relation],
                 *, gain: float = 1.0, damping: float = 0.45,
                 max_iterations: int = 100, tol: float = 1e-7,
                 record_history: bool = False):
        self.hypotheses = tuple(hypotheses)
        if not self.hypotheses:
            raise ValueError("GRRLE requires at least one hypothesis")
        self.index = {hypothesis.key: i for i, hypothesis in enumerate(self.hypotheses)}
        if len(self.index) != len(self.hypotheses):
            raise ValueError("hypothesis keys must be unique")
        self.relations = tuple(relations)
        self.W = np.zeros((len(self.hypotheses), len(self.hypotheses)), dtype=float)
        for relation in self.relations:
            if relation.source not in self.index or relation.target not in self.index:
                raise ValueError(f"relation references unknown hypothesis: {relation}")
            self.W[self.index[relation.source], self.index[relation.target]] += relation.weight
        self.prior = np.array([h.prior for h in self.hypotheses], dtype=float)
        self.gain = float(gain)
        self.damping = float(np.clip(damping, 0.0, 1.0))
        self.max_iterations = int(max_iterations)
        self.tol = float(tol)
        self.record_history = bool(record_history)

    @staticmethod
    def _sigmoid(values):
        values = np.clip(values, -60.0, 60.0)
        return 1.0 / (1.0 + np.exp(-values))

    def run(self) -> GRRLEResult:
        eps = 1e-9
        clipped = np.clip(self.prior, eps, 1.0 - eps)
        logits = np.log(clipped / (1.0 - clipped))
        strengths = clipped.copy()
        history = [strengths.copy()] if self.record_history else None
        converged = False
        for iteration in range(1, self.max_iterations + 1):
            proposed = self._sigmoid(logits + self.gain * (self.W @ strengths))
            updated = self.damping * strengths + (1.0 - self.damping) * proposed
            delta = float(np.max(np.abs(updated - strengths)))
            strengths = updated
            if history is not None:
                history.append(strengths.copy())
            if delta < self.tol:
                converged = True
                break
        return GRRLEResult(
            self.hypotheses, strengths, iteration, converged,
            tuple(history) if history is not None else None,
            self.prior.copy(), self.W.copy(),
        )
