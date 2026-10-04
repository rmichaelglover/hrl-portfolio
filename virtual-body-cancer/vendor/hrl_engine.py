"""Hierarchical Relaxation Labeling — the generic engine.

This is the merge of the two prior engines into one "most generic form":

* From ``hrl-portfolio/hrl/core.py`` — the **respected prior**
  (``prior**ps * strength**(1-ps)`` multiplicative base, so the prior is folded
  into *every* update instead of washing out) and the **noise / null-reject
  label** (a trailing "none of the above" class that accrues accumulated
  incompatibility with the field).

* From ``relaxation-labeling/python/core/relax.py`` — the **higher-order
  (trinity) support**, the triple product ``s[k,l] * s[m,n] * C[i,j,k,l,m,n]``.

* New here — everything is expressed as **sparse factors** over an explicit
  rule list, not a dense ``[n, L, n, L]`` tensor. A pairwise rule is an
  order-2 factor; a trinity / 2-simplex rule is an order-3 factor. Support is
  computed by message passing over the factor list, so it scales to real
  graphs (Cora's ~10k edges, not a 1.4 GB dense tensor).

The knowledge lives in the factors (the myopic, enumerable local rules) and in
the prior (seeded from however many supervised labels you have). Inference is
iterative relaxation to a consistent field. That division — many free rules,
few supervised anchors — is the whole data-efficiency thesis.

References
----------
A. Rosenfeld, R. Hummel, S. Zucker, "Scene labeling by relaxation operations,"
IEEE Trans. SMC, 1976.  R. Hummel, S. Zucker, "On the foundations of relaxation
labeling processes," IEEE Trans. PAMI, 1983.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["Factor", "pairwise_factor", "triangle_factor", "HRL", "HRLResult"]


# ---------------------------------------------------------------------------
# Factors — the sparse, myopic rules
# ---------------------------------------------------------------------------

@dataclass
class Factor:
    """A group of same-order rules that share one label-compatibility tensor.

    Attributes
    ----------
    idx:
        ``[F, order]`` integer node indices. Row ``f`` is one rule tying
        ``order`` objects together.
    C:
        ``[L] * order`` compatibility tensor (shared by all ``F`` rules).
        ``C[j, l]`` (order 2) is how much label ``j`` on the first member is
        reinforced by label ``l`` on the second; ``C[j, l, n]`` (order 3) is
        the 3-way / simplicial term. Signed values allowed (negatives suppress).
    """

    idx: np.ndarray
    C: np.ndarray

    def __post_init__(self) -> None:
        self.idx = np.asarray(self.idx, dtype=np.intp)
        self.C = np.asarray(self.C, dtype=float)
        if self.idx.ndim != 2:
            raise ValueError("Factor.idx must be [F, order]")
        self.order = self.idx.shape[1]
        if self.C.ndim != self.order:
            raise ValueError(
                f"C.ndim ({self.C.ndim}) must equal factor order ({self.order})"
            )
        if self.order not in (2, 3):
            raise ValueError("only order-2 (pairwise) and order-3 (trinity) are implemented")

    # -- support this factor contributes to each member node -----------------

    def accumulate_support(self, S: np.ndarray, support: np.ndarray) -> None:
        """Add this factor's support into ``support`` (``[n, L]``, real labels).

        ``S`` is ``[n, L]`` real-label strengths. Each rule sends every member a
        message = the compatibility tensor contracted against the *other*
        members' strengths, marginalized down to that member's label axis.
        """
        idx, C = self.idx, self.C
        if self.order == 2:
            s0, s1 = S[idx[:, 0]], S[idx[:, 1]]         # [F, L] each
            np.add.at(support, idx[:, 0], s1 @ C.T)     # member0[j] += Σ_l C[j,l] s1[l]
            np.add.at(support, idx[:, 1], s0 @ C)       # member1[l] += Σ_j C[j,l] s0[j]
        else:  # order == 3
            s0, s1, s2 = S[idx[:, 0]], S[idx[:, 1]], S[idx[:, 2]]
            np.add.at(support, idx[:, 0], np.einsum("jln,fl,fn->fj", C, s1, s2))
            np.add.at(support, idx[:, 1], np.einsum("jln,fj,fn->fl", C, s0, s2))
            np.add.at(support, idx[:, 2], np.einsum("jln,fj,fl->fn", C, s0, s1))

    # -- accumulated *incompatibility* this factor sends the noise label -----

    def accumulate_incompat(self, S: np.ndarray, incompat: np.ndarray, n_labels: int) -> None:
        """Add per-node accumulated incompatibility into ``incompat`` (``[n]``).

        Faithful to the dense C++/portfolio noise term: for a member, sum over
        the member's own ``L`` labels of ``(1 - C)`` weighted by the other
        members' strengths.  ``incompat_member = Σ_over_own_labels (1 - C) · s_others``.
        """
        idx, C, L = self.idx, self.C, n_labels
        if self.order == 2:
            w_from1 = L - C.sum(axis=0)                 # [L]; over member0's labels
            w_from0 = L - C.sum(axis=1)                 # [L]; over member1's labels
            np.add.at(incompat, idx[:, 0], S[idx[:, 1]] @ w_from1)
            np.add.at(incompat, idx[:, 1], S[idx[:, 0]] @ w_from0)
        else:  # order == 3
            s0, s1, s2 = S[idx[:, 0]], S[idx[:, 1]], S[idx[:, 2]]
            W0 = L - C.sum(axis=0)                      # [L, L] over member0's labels
            W1 = L - C.sum(axis=1)
            W2 = L - C.sum(axis=2)
            np.add.at(incompat, idx[:, 0], np.einsum("fl,fn,ln->f", s1, s2, W0))
            np.add.at(incompat, idx[:, 1], np.einsum("fj,fn,jn->f", s0, s2, W1))
            np.add.at(incompat, idx[:, 2], np.einsum("fj,fl,jl->f", s0, s1, W2))


def pairwise_factor(edges: np.ndarray, C: np.ndarray) -> Factor:
    """Order-2 factor. ``edges`` is ``[E, 2]``; each undirected edge listed once
    gives *both* endpoints support from the other. ``C`` is ``[L, L]``."""
    return Factor(np.asarray(edges), np.asarray(C))


def triangle_factor(triangles: np.ndarray, C: np.ndarray) -> Factor:
    """Order-3 (trinity / 2-simplex) factor. ``triangles`` is ``[T, 3]``;
    ``C`` is ``[L, L, L]`` (orientation-sensitive — this is what lets the
    engine see chirality that no pairwise term can)."""
    return Factor(np.asarray(triangles), np.asarray(C))


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

@dataclass
class HRLResult:
    strengths: np.ndarray       # [n, L (+1 noise)] final distribution per object
    assignments: np.ndarray     # [n] label index, or -1 for the noise label
    confidence: np.ndarray      # [n] winning strength
    iterations: int
    converged: bool
    noise_index: int | None
    history: list[np.ndarray] | None


class HRL:
    """Generic hierarchical relaxation labeler: prior + noise + sparse factors.

    Parameters
    ----------
    n_objects, n_labels:
        Field size.
    factors:
        List of :class:`Factor` (order-2 and/or order-3). The union of the
        engine's *rules*.
    prior:
        ``[n_objects, n_labels]`` non-negative prior (row-normalized), or
        ``None`` for uniform. Supervised labels enter here as sharp rows.
    noise, noise_gain:
        Enable / weight the trailing null-reject label.
    prior_strength:
        ``0.0`` classic Hummel–Zucker · ``1.0`` fully-respected Bayesian prior.
    support_factor, max_iterations, tol, record_history:
        As in the classic engine.
    """

    def __init__(
        self,
        n_objects: int,
        n_labels: int,
        factors: list[Factor],
        prior: np.ndarray | None = None,
        *,
        noise: bool = False,
        noise_gain: float = 0.15,
        prior_strength: float = 0.5,
        support_factor: float = 1.0,
        max_iterations: int = 50,
        tol: float = 1e-6,
        record_history: bool = False,
    ) -> None:
        self.n = int(n_objects)
        self.L = int(n_labels)
        self.factors = list(factors)
        for f in self.factors:
            if f.idx.max(initial=-1) >= self.n or f.idx.min(initial=0) < 0:
                raise ValueError("a factor references an out-of-range object index")
            if f.C.shape != (self.L,) * f.order:
                raise ValueError(f"a factor's C shape {f.C.shape} != {(self.L,) * f.order}")

        self.noise = bool(noise)
        self.noise_gain = float(noise_gain)
        self.noise_index = self.L if self.noise else None
        self.n_total = self.L + (1 if self.noise else 0)

        self.prior_strength = float(np.clip(prior_strength, 0.0, 1.0))
        self.support_factor = float(support_factor)
        self.max_iterations = int(max_iterations)
        self.tol = float(tol)
        self.record_history = bool(record_history)

        self._prior = self._build_prior(prior)
        self.strength = self._prior.copy()
        self.iteration = 0

    # -- setup ---------------------------------------------------------------

    def _build_prior(self, prior: np.ndarray | None) -> np.ndarray:
        if prior is None:
            real = np.full((self.n, self.L), 1.0 / self.L)
        else:
            real = np.asarray(prior, dtype=float)
            if real.shape != (self.n, self.L):
                raise ValueError(f"prior must be {(self.n, self.L)}; got {real.shape}")
            if np.any(real < 0):
                raise ValueError("prior must be non-negative")
        full = np.zeros((self.n, self.n_total))
        full[:, : self.L] = real
        if self.noise:
            full[:, self.noise_index] = real.mean(axis=1)  # noise starts on a typical footing
        return self._normalize_rows(full)

    # -- math ----------------------------------------------------------------

    @staticmethod
    def _normalize_rows(m: np.ndarray) -> np.ndarray:
        totals = m.sum(axis=1, keepdims=True)
        return m / np.where(totals > 0, totals, 1.0)

    @staticmethod
    def _minmax_rows(m: np.ndarray) -> np.ndarray:
        lo = m.min(axis=1, keepdims=True)
        hi = m.max(axis=1, keepdims=True)
        span = hi - lo
        return np.where(span > 0, (m - lo) / np.where(span > 0, span, 1.0), 0.0)

    def _support(self) -> np.ndarray:
        S = self.strength[:, : self.L]                       # real-label strengths
        support = np.zeros((self.n, self.n_total))
        real = np.zeros((self.n, self.L))
        for f in self.factors:
            f.accumulate_support(S, real)
        support[:, : self.L] = real
        if self.noise:
            incompat = np.zeros(self.n)
            for f in self.factors:
                f.accumulate_incompat(S, incompat, self.L)
            support[:, self.noise_index] = incompat * (self.noise_gain / self.L)
        return self._minmax_rows(support)

    def step(self) -> float:
        support = self._support()
        base = (self._prior ** self.prior_strength) * (self.strength ** (1.0 - self.prior_strength))
        updated = base * (1.0 + self.support_factor * support)
        new = self._normalize_rows(updated)
        delta = float(np.max(np.abs(new - self.strength)))
        self.strength = new
        self.iteration += 1
        return delta

    def run(self, verbose: bool = False) -> HRLResult:
        history: list[np.ndarray] | None = [] if self.record_history else None
        converged = False
        for _ in range(self.max_iterations):
            if history is not None:
                history.append(self.strength.copy())
            delta = self.step()
            if verbose:
                print(f"iter {self.iteration}: max Δ = {delta:.3e}")
            if delta < self.tol:
                converged = True
                break
        if history is not None:
            history.append(self.strength.copy())
        winners = np.argmax(self.strength, axis=1)
        confidence = self.strength[np.arange(self.n), winners]
        assignments = winners.copy()
        if self.noise:
            assignments[winners == self.noise_index] = -1
        return HRLResult(
            strengths=self.strength.copy(),
            assignments=assignments,
            confidence=confidence,
            iterations=self.iteration,
            converged=converged,
            noise_index=self.noise_index,
            history=history,
        )
