"""Hierarchical relaxation labeling — the core engine.

A clean, numpy-only implementation of probabilistic relaxation labeling
(Rosenfeld–Hummel–Zucker), generalized with two features that the classic
formulation lacks:

* **A first-class, persistently-respected prior.** Instead of using the prior
  only as an initial condition (where it washes out after a few iterations and
  every object can collapse onto a single popular label), the prior is folded
  back into the multiplicative base of *every* update. ``prior_strength``
  interpolates between classic Hummel–Zucker (``0.0``) and a Bayesian-style
  "posterior ∝ prior × field-evidence" update (``1.0``).

* **An optional noise label.** A trailing "none of the above" class that
  accrues strength for objects which are incompatible with the rest of the
  field. It absorbs outliers / spurious detections and acts as a regularizer
  against over-confident labelings.

The same engine labels chess pieces by role, 3-D points by marker identity
(motion capture), and observations by best-fitting theory — only the
``compatibility`` kernel and the ``prior`` change.

References
----------
A. Rosenfeld, R. Hummel, S. Zucker, "Scene labeling by relaxation
operations," IEEE Trans. SMC, 1976.
R. Hummel, S. Zucker, "On the foundations of relaxation labeling
processes," IEEE Trans. PAMI, 1983.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["RelaxationLabeler", "RelaxationResult"]


@dataclass
class RelaxationResult:
    """Outcome of a relaxation run.

    Attributes
    ----------
    strengths:
        ``[n_objects, n_labels (+1 if noise)]`` final label-strength
        distribution per object (each row sums to 1). The trailing column is
        the noise label when ``noise=True``.
    assignments:
        ``[n_objects]`` integer label index per object, or ``-1`` where the
        object was assigned to the noise label (or fell below ``min_strength``).
    confidence:
        ``[n_objects]`` the winning strength for each object.
    iterations:
        Number of iterations actually run.
    converged:
        Whether the run stopped because it reached ``tol`` (vs. ``max_iterations``).
    history:
        Optional list of per-iteration strength snapshots (for plotting), or
        ``None`` when ``record_history=False``.
    noise_index:
        Column index of the noise label, or ``None`` when noise is disabled.
    """

    strengths: np.ndarray
    assignments: np.ndarray
    confidence: np.ndarray
    iterations: int
    converged: bool
    history: list[np.ndarray] | None
    noise_index: int | None


class RelaxationLabeler:
    """Relaxation labeling with a respected prior and an optional noise label.

    Parameters
    ----------
    compatibility:
        ``[n_objects, n_labels, n_objects, n_labels]`` array. ``compatibility
        [i, j, k, l]`` is how much assigning label ``j`` to object ``i`` is
        reinforced by assigning label ``l`` to object ``k`` (typically in
        ``[0, 1]``, but signed values are allowed — negatives suppress).
    prior:
        ``[n_objects, n_labels]`` non-negative prior strength per object/label.
        Rows are re-normalized internally. ``None`` (default) uses a uniform
        prior, in which case the prior has no steering effect.
    noise:
        Enable the trailing noise label. Default ``False``.
    noise_gain:
        How strongly accumulated incompatibility pulls an object toward the
        noise label. Default ``0.15`` (the value tuned in the original C++
        engine).
    prior_strength:
        ``0.0`` → classic Hummel–Zucker (prior only seeds iteration 0).
        ``1.0`` → the prior is the full multiplicative base every iteration
        (Bayesian-style, maximally respected). Default ``0.5``.
    support_factor:
        Gain on the support term in the multiplicative update. Default ``1.0``.
    max_iterations, tol:
        Stop after ``max_iterations`` or when the largest per-cell change in
        strength drops below ``tol``.
    record_history:
        Keep a per-iteration snapshot of the strength matrix for plotting.
    """

    def __init__(
        self,
        compatibility: np.ndarray,
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
        compatibility = np.asarray(compatibility, dtype=float)
        if compatibility.ndim != 4 or compatibility.shape[0] != compatibility.shape[2] \
                or compatibility.shape[1] != compatibility.shape[3]:
            raise ValueError(
                "compatibility must have shape "
                "[n_objects, n_labels, n_objects, n_labels]; got "
                f"{compatibility.shape}"
            )
        self.compatibility = compatibility
        self.n_objects = compatibility.shape[0]
        self.n_labels = compatibility.shape[1]

        self.noise = bool(noise)
        self.noise_gain = float(noise_gain)
        self.noise_index = self.n_labels if self.noise else None
        self.n_total = self.n_labels + (1 if self.noise else 0)

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
            real = np.full((self.n_objects, self.n_labels), 1.0 / self.n_labels)
        else:
            real = np.asarray(prior, dtype=float)
            if real.shape != (self.n_objects, self.n_labels):
                raise ValueError(
                    f"prior must have shape {(self.n_objects, self.n_labels)}; "
                    f"got {real.shape}"
                )
            if np.any(real < 0):
                raise ValueError("prior must be non-negative")
        full = np.zeros((self.n_objects, self.n_total))
        full[:, : self.n_labels] = real
        if self.noise:
            # Neutral starting belief for the noise label: the object's own
            # mean prior, so it begins on equal footing with a typical label.
            full[:, self.noise_index] = real.mean(axis=1)
        return self._normalize_rows(full)

    # -- math ----------------------------------------------------------------

    @staticmethod
    def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
        """Make each row a distribution (sum to 1); leave all-zero rows alone."""
        totals = matrix.sum(axis=1, keepdims=True)
        safe = np.where(totals > 0, totals, 1.0)
        return matrix / safe

    @staticmethod
    def _minmax_rows(matrix: np.ndarray) -> np.ndarray:
        """Per-row min–max to ``[0, 1]``; constant rows map to 0 (neutral)."""
        lo = matrix.min(axis=1, keepdims=True)
        hi = matrix.max(axis=1, keepdims=True)
        span = hi - lo
        return np.where(span > 0, (matrix - lo) / np.where(span > 0, span, 1.0), 0.0)

    def _support(self) -> np.ndarray:
        """Compute (and per-row normalize) support for the current strengths."""
        real_strength = self.strength[:, : self.n_labels]  # [n_objects, n_labels]
        support = np.zeros((self.n_objects, self.n_total))

        # support[i, j] = sum_{k, l} compatibility[i, j, k, l] * strength[k, l]
        support[:, : self.n_labels] = np.einsum(
            "ijkl,kl->ij", self.compatibility, real_strength
        )

        if self.noise:
            # Accumulated incompatibility with the whole field pulls object i
            # toward the noise label:
            #   support[i, noise] = noise_gain/n_labels
            #                       * sum_{j,k,l} (1 - compat[i,j,k,l]) * strength[k,l]
            incompat = 1.0 - self.compatibility
            support[:, self.noise_index] = (
                np.einsum("ijkl,kl->i", incompat, real_strength)
                * (self.noise_gain / self.n_labels)
            )

        return self._minmax_rows(support)

    def step(self) -> float:
        """Run one relaxation iteration; return the largest per-cell change."""
        support = self._support()

        # Multiplicative base interpolates between the prior (Bayesian) and the
        # evolving strength (classic Hummel–Zucker), so the prior stays
        # respected instead of washing out.
        base = (self._prior ** self.prior_strength) * (
            self.strength ** (1.0 - self.prior_strength)
        )
        updated = base * (1.0 + self.support_factor * support)
        new_strength = self._normalize_rows(updated)

        delta = float(np.max(np.abs(new_strength - self.strength)))
        self.strength = new_strength
        self.iteration += 1
        return delta

    def run(self, verbose: bool = False) -> RelaxationResult:
        """Iterate to convergence (or ``max_iterations``) and return the result."""
        history: list[np.ndarray] | None = [] if self.record_history else None
        converged = False
        for _ in range(self.max_iterations):
            if history is not None:
                history.append(self.strength.copy())
            delta = self.step()
            if verbose:
                print(f"iteration {self.iteration}: max Δ = {delta:.3e}")
            if delta < self.tol:
                converged = True
                break
        if history is not None:
            history.append(self.strength.copy())

        assignments, confidence = self._decide()
        return RelaxationResult(
            strengths=self.strength.copy(),
            assignments=assignments,
            confidence=confidence,
            iterations=self.iteration,
            converged=converged,
            history=history,
            noise_index=self.noise_index,
        )

    # -- readout -------------------------------------------------------------

    def _decide(self, min_strength: float | None = None):
        winners = np.argmax(self.strength, axis=1)
        confidence = self.strength[np.arange(self.n_objects), winners]
        assignments = winners.copy()
        if self.noise:
            assignments[winners == self.noise_index] = -1
        if min_strength is not None:
            assignments[confidence < min_strength] = -1
        return assignments, confidence

    def assignments(self, min_strength: float | None = None) -> np.ndarray:
        """Object → label index (``-1`` = noise / below ``min_strength``)."""
        return self._decide(min_strength)[0]
