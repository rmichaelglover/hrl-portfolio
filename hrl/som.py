"""Self-organizing map — a competitive-learning cousin of relaxation labeling.

A Kohonen SOM and relaxation labeling share a soul: both settle a field by
**local neighborhood coherence**. Relaxation labeling pulls neighboring objects
toward compatible *labels*; a SOM pulls neighboring grid nodes toward nearby
*data*. Here the SOM is pointed, self-referentially, at the relaxation engine's
own output — it learns the 2-D topology of the **truth-assignment space** (where
the engine places each claim), so vtrue / ish / vfalse regions emerge as
contiguous territory and the undecidable claims cluster at the manifold's peak.

numpy-only; imports nothing heavy.
"""
from __future__ import annotations

import numpy as np

__all__ = ["SelfOrganizingMap"]


class SelfOrganizingMap:
    """A rectangular Kohonen self-organizing map.

    Parameters
    ----------
    grid:
        ``(width, height)`` of the node lattice.
    dim:
        Dimensionality of the weight/data vectors.
    seed:
        RNG seed for reproducible initialization + training order.
    """

    def __init__(self, grid: tuple[int, int] = (6, 6), dim: int = 2, seed: int = 0) -> None:
        self.gw, self.gh = grid
        self.dim = dim
        self._rng = np.random.default_rng(seed)
        self.weights = self._rng.normal(0.0, 0.05, size=(self.gw, self.gh, dim))
        gx, gy = np.meshgrid(np.arange(self.gw), np.arange(self.gh), indexing="ij")
        self._coords = np.stack([gx, gy], axis=-1).astype(float)   # node lattice coords

    def bmu(self, x: np.ndarray) -> tuple[int, int]:
        """Best matching unit (grid index) for input vector ``x``."""
        d = np.sum((self.weights - x) ** 2, axis=-1)
        return tuple(int(v) for v in np.unravel_index(np.argmin(d), d.shape))

    def quantization_error(self, data: np.ndarray) -> float:
        """Mean distance from each data point to its best matching unit."""
        data = np.asarray(data, dtype=float)
        flat = self.weights.reshape(-1, self.dim)
        return float(np.mean([np.sqrt(np.min(np.sum((flat - x) ** 2, axis=-1))) for x in data]))

    def train(self, data, epochs: int = 40, lr0: float = 0.5,
              sigma0: float | None = None, record: bool = False):
        """Train on ``data`` with decaying learning rate + neighborhood radius.

        Returns a list of weight snapshots (one per epoch) when ``record=True``.
        """
        data = np.asarray(data, dtype=float)
        n = len(data)
        sigma0 = sigma0 if sigma0 is not None else max(self.gw, self.gh) / 2.0
        total = epochs * n
        history = []
        t = 0
        for _ in range(epochs):
            if record:
                history.append(self.weights.copy())
            for x in data[self._rng.permutation(n)]:
                decay = np.exp(-t / total)
                lr, sigma = lr0 * decay, max(sigma0 * decay, 0.4)
                bx, by = self.bmu(x)
                dist2 = np.sum((self._coords - np.array([bx, by])) ** 2, axis=-1)
                influence = np.exp(-dist2 / (2.0 * sigma ** 2))[..., None]
                self.weights += lr * influence * (x - self.weights)
                t += 1
        if record:
            history.append(self.weights.copy())
        return history
