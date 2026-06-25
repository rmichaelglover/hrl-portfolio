"""Morphogenesis as relaxation labeling — a body that heals itself.

Michael Levin's picture of regeneration, cast as the same engine: **cells are
objects**, their **anatomical region is the label**, and **bioelectric
gap-junction coupling is the compatibility kernel** (adjacent cells want to share
an identity). A coarse *pattern memory* — the blurred target morphology — is the
respected prior (Levin's bioelectric setpoint). Wound a region, stripping its
cells of identity, and relaxation propagates identity inward from the intact
boundary, guided by the coarse memory, until the form grows back.

numpy-only; uses the core ``RelaxationLabeler`` unchanged.
"""
from __future__ import annotations

import numpy as np

from .core import RelaxationLabeler

__all__ = ["body_plan", "LABELS", "COLORS", "bioelectric_compatibility",
           "pattern_memory_prior", "regenerate"]

LABELS = ["background", "head", "trunk", "tail"]
COLORS = ["#0d0f16", "#ff8c42", "#3ddc84", "#5b8cff"]   # for visualization


def body_plan(h: int = 24, w: int = 24) -> np.ndarray:
    """A simple banded creature: an ellipse body labeled head / trunk / tail."""
    target = np.zeros((h, w), dtype=int)
    cy, cx, ry, rx = h / 2.0, w / 2.0, h * 0.44, w * 0.30
    for y in range(h):
        for x in range(w):
            if ((y - cy) / ry) ** 2 + ((x - cx) / rx) ** 2 <= 1.0:
                frac = y / h
                target[y, x] = 1 if frac < 0.34 else 2 if frac < 0.66 else 3
    return target


def bioelectric_compatibility(h: int, w: int, k: int, same: float = 1.0) -> np.ndarray:
    """Gap-junction coupling: 4-neighbor cells are rewarded for sharing a label.

    Returns the ``[N, k, N, k]`` compatibility tensor (N = h*w) the core consumes.
    """
    n = h * w
    compat = np.zeros((n, k, n, k))
    diag = same * np.eye(k)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    compat[i, :, ny * w + nx, :] = diag
    return compat


def _one_hot(target: np.ndarray, k: int) -> np.ndarray:
    h, w = target.shape
    oh = np.zeros((h, w, k))
    for c in range(k):
        oh[..., c] = (target == c)
    return oh


def _blur(field: np.ndarray, iterations: int) -> np.ndarray:
    f = field.astype(float)
    for _ in range(iterations):
        acc = 4 * f.copy()
        acc[1:] += f[:-1]; acc[:-1] += f[1:]
        acc[:, 1:] += f[:, :-1]; acc[:, :-1] += f[:, 1:]
        f = acc / acc.sum(axis=-1, keepdims=True)
    return f


def pattern_memory_prior(target: np.ndarray, wound: np.ndarray, k: int,
                         anchor: float = 0.9, blur_iterations: int = 12) -> np.ndarray:
    """Prior = bioelectric pattern memory. Intact cells hold their identity
    strongly; wounded cells keep only the *coarse* (blurred) memory of the form,
    which relaxation + coupling then sharpen back into crisp anatomy."""
    h, w = target.shape
    oh = _one_hot(target, k)
    coarse = _blur(oh, blur_iterations)
    uniform = np.full(k, 1.0 / k)
    prior = (1 - anchor) * uniform + anchor * oh        # intact: strong memory
    prior[wound] = coarse[wound]                        # wound: coarse memory only
    return prior.reshape(h * w, k)


def regenerate(target: np.ndarray, wound: np.ndarray, *, anchor: float = 0.9,
               prior_strength: float = 0.55, iterations: int = 60):
    """Heal a wounded body back to ``target``. Returns (label-grid history, result)."""
    h, w = target.shape
    k = len(LABELS)
    compat = bioelectric_compatibility(h, w, k)
    prior = pattern_memory_prior(target, wound, k, anchor=anchor)
    res = RelaxationLabeler(compat, prior, prior_strength=prior_strength,
                            max_iterations=iterations, record_history=True).run()
    grids = [s[:, :k].argmax(axis=1).reshape(h, w) for s in res.history]
    return grids, res
