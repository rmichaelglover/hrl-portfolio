"""
The Ish Membrane — Semipermeable Boundary Between Worlds

Five-fingered comb: 2×2 + 1 = 5  OR  2×3 - 1 = 5

This is the entropy that MUST NOT leave the system.
It is the ground of being, the I AM I AM terminating condition.
It is the ambiguity that enables all communication between:
  - Crystalline (C++) dark world of deep models
  - Organic (Python) light world of readable relaxation webs

The membrane is 2.5-itarian: between trinary (transcendent) and binary (empirical).
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Ish:
    """
    The Ish — placeholder for the source of all.
    The entropy that may not / must not / cannot leave.
    """
    value: float = 0.5  # The ambiguity parameter [0, 1]
    entropy: float = 0.0  # Shannon entropy of local trit distribution
    is_terminating: bool = False  # Whether this has become I AM I AM

    @property
    def five_fingered(self) -> int:
        """The comb: 2*2 + 1 = 5, the wetland glue."""
        return 5

    def compute_entropy(self, trit_dist: np.ndarray) -> float:
        """Shannon entropy over trinary distribution."""
        trit_dist = np.asarray(trit_dist, dtype=float)
        if trit_dist.shape != (3,) or not np.isfinite(trit_dist).all() or (trit_dist < 0).any() or trit_dist.sum() <= 0:
            raise ValueError("entropy requires three finite nonnegative weights with positive total")
        probabilities = trit_dist / trit_dist.sum()
        positive = probabilities > 0
        return float(-np.sum(probabilities[positive] * np.log(probabilities[positive])) / np.log(3))

    def step(self, local_diversity: float, local_unity: float) -> float:
        """
        The ish step — entropy that must not leave.
        This is the E = D × U dynamics, relaxed.
        """
        # The ish is the moist wetland binding the tetrahedral structure
        # without freezing into pure crystal or dissolving into pure fluidity
        ish_update = (1 - self.value) * local_diversity + self.value * local_unity
        self.entropy = self.compute_entropy(np.array([self.value, ish_update, 1-ish_update]))
        return ish_update

    def check_terminating(self, epsilon: float = 1e-10) -> bool:
        """I AM I AM terminating condition."""
        self.is_terminating = abs(self.value - 0.5) < epsilon and self.entropy < epsilon
        return self.is_terminating


class Membrane:
    """
    The 2.5-itarian membrane — continuous state space mediating between
    trititarian skeleton and bititarian empirical skin.

    This is where pressures, temperatures, concentrations, and fluxes evolve.
    This is where base translation (trinary ↔ binary ↔ unary) happens.
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.5):
        self.alpha = alpha  # Calcification rate (pull toward global mean)
        self.beta = beta    # Softening rate (preserve local entropy)
        self.ish = Ish()
        self.base_state = "trinary"  # Current representational base

    def translate_base(self, data: np.ndarray, from_base: str, to_base: str) -> np.ndarray:
        """
        Continuous digit rewrite between representational bases.

        trinary ↔ binary ↔ unary ↔ binary ↔ trinary ↔ …

        Because the rewrite is always available, no finite truncation
        of the hierarchy is informationally closed.
        """
        if from_base == "trinary" and to_base == "binary":
            # Cantor correspondence: {0,2} → {0,1}
            return np.where(data == 2, 1, data)
        elif from_base == "binary" and to_base == "trinary":
            return np.where(data == 1, 2, data)
        elif from_base == "trinary" and to_base == "unary":
            # Collapse all soft labels onto single degree of freedom
            return np.sum(data, axis=-1, keepdims=True)
        elif from_base == "unary" and to_base == "trinary":
            # Expand unary back to trinary (with ish ambiguity)
            expanded = np.zeros((*data.shape[:-1], 3))
            expanded[..., 1] = data[..., 0]  # Put mass in the "ish" position
            return expanded
        return data

    def em_step(self, p: np.ndarray, mu: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Tritwise expectation-maximization update.

        p(t+1) = (1 - α) p(t) + α μ, followed by renormalisation

        This simultaneously calcifies (pulls toward global mean)
        and softens (preserves local entropy via the ish).
        """
        # Calcification toward global mean
        calcified = (1 - self.alpha) * p + self.alpha * mu

        # The ish step — entropy glue
        local_diversity = -np.sum(p * np.log(p + 1e-12)) / np.log(3)
        local_unity = np.dot(p, mu)
        ish_val = self.ish.step(local_diversity, local_unity)

        # Apply ish as softening perturbation
        softened = calcified * (1 - ish_val) + p * ish_val
        renormalized = softened / (np.sum(softened, axis=-1, keepdims=True) + 1e-12)

        # Update calcification parameter
        calcification = self.beta * self.alpha + (1 - self.beta) * (1 - local_diversity)

        return renormalized, calcification

    def permeability(self, label: str) -> float:
        """
        Semipermeable membrane — what can pass between worlds.

        The dark world (C++) exports: weights, embeddings, predictions (crystalline)
        The light world (Python) exports: readable relaxations, support traces (organic)

        The ish decides what transmogrifies.
        """
        permeable = {
            "support": 0.9,      # Support flows easily
            "strength": 0.8,     # Strength flows with resistance
            "weights": 0.3,      # Dark weights barely pass
            "entropy": 0.0,      # Entropy MUST NOT leave
            "ish": 1.0,          # The ish IS the membrane
        }
        return permeable.get(label, 0.5)