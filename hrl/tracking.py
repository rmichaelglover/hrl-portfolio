"""Marker tracking — relaxation labeling across time.

Single-frame correspondence (:func:`hrl.kernels.pairwise_distance_compatibility`)
decides *which measured point is which marker* from geometry alone. To *track*
markers through a sequence we add one thing: **memory**, expressed as a prior.

Each frame, the previous frame's labeled positions predict where every marker
should be now; that prediction becomes the per-detection prior for this frame.
Geometry (compatibility) keeps the constellation self-consistent; memory (the
prior) keeps identities stable through noise, shuffled detection order, and
dropouts — while the noise label quarantines ghost detections.

This is the same `RelaxationLabeler`; tracking is just correspondence with a
temporal prior.
"""
from __future__ import annotations

import numpy as np

from .core import RelaxationLabeler
from .kernels import pairwise_distance_compatibility

__all__ = ["temporal_prior", "track_sequence", "synthetic_sequence"]


def temporal_prior(
    detections: np.ndarray,
    predicted: np.ndarray,
    *,
    sigma: float = 0.5,
    floor: float = 1e-3,
) -> np.ndarray:
    """Prior favoring detections near where each marker was last seen.

    ``prior[i, m] = exp(-|detection_i - predicted_m|**2 / (2 sigma**2))``,
    floored so nothing is hard-excluded. Markers with unknown position
    (``nan`` row in ``predicted``) contribute only the floor.
    """
    detections = np.asarray(detections, dtype=float)
    n_det = detections.shape[0]
    n_markers = predicted.shape[0]
    prior = np.full((n_det, n_markers), floor)
    for m in range(n_markers):
        p = predicted[m]
        if np.any(np.isnan(p)):
            continue
        dist = np.linalg.norm(detections - p, axis=1)
        prior[:, m] = np.maximum(floor, np.exp(-(dist ** 2) / (2.0 * sigma ** 2)))
    return prior


def track_sequence(
    frames: list[np.ndarray],
    model: np.ndarray,
    *,
    sigma_spatial: float = 0.1,
    sigma_temporal: float = 0.6,
    prior_strength: float = 0.4,
    noise: bool = True,
    noise_gain: float = 0.3,
    motion_gate: float | None = None,
    max_iterations: int = 80,
) -> list[np.ndarray]:
    """Assign a marker identity to every detection in every frame.

    Parameters
    ----------
    frames:
        List of ``[n_detections_t, dim]`` arrays — detections per frame, in
        arbitrary order, possibly with dropouts (missing markers) or ghosts
        (spurious points).
    model:
        ``[n_markers, dim]`` canonical marker geometry (the rest-pose labels).
    sigma_spatial, sigma_temporal:
        Tolerances for the geometry kernel and the temporal-memory prior.
    prior_strength:
        How strongly memory steers the labeling (see ``RelaxationLabeler``).

    Returns
    -------
    list[np.ndarray]
        Per frame, ``[n_detections_t]`` marker indices (``-1`` = ghost/noise).
    """
    model = np.asarray(model, dtype=float)
    n_markers, dim = model.shape
    last_known = np.full((n_markers, dim), np.nan)
    seen_any = False
    assignments: list[np.ndarray] = []

    for detections in frames:
        detections = np.asarray(detections, dtype=float)
        compat = pairwise_distance_compatibility(detections, model, sigma=sigma_spatial)
        prior = temporal_prior(detections, last_known, sigma=sigma_temporal) if seen_any else None

        result = RelaxationLabeler(
            compat,
            prior,
            noise=noise,
            noise_gain=noise_gain,
            prior_strength=prior_strength,
            max_iterations=max_iterations,
        ).run()

        a = result.assignments
        assignments.append(a)
        for i, m in enumerate(a):
            if m < 0:
                continue
            # Memory gate: reject an update that implies an implausible jump,
            # so a mislabeled ghost can't hijack a marker's remembered position.
            if (motion_gate is not None and not np.any(np.isnan(last_known[m]))
                    and np.linalg.norm(detections[i] - last_known[m]) > motion_gate):
                continue
            last_known[m] = detections[i]  # remember where each marker went
        seen_any = True

    return assignments


def synthetic_sequence(
    model: np.ndarray,
    n_frames: int = 30,
    *,
    noise: float = 0.02,
    rotate_deg_per_frame: float = 4.0,
    drift: tuple[float, float] = (0.15, 0.05),
    ghost_every: int = 0,
    drop_every: int = 0,
    seed: int = 0,
):
    """Generate a rigidly-moving marker set: rotate + drift + noise, then
    shuffle detection order each frame and optionally inject ghosts/dropouts.

    Returns ``(frames, truth)`` where ``truth[t][i]`` is the true marker index
    of detection ``i`` in frame ``t`` (``-1`` for an injected ghost).
    """
    model = np.asarray(model, dtype=float)
    rng = np.random.default_rng(seed)
    n_markers = model.shape[0]
    center = model.mean(axis=0)
    frames: list[np.ndarray] = []
    truth: list[np.ndarray] = []

    for t in range(n_frames):
        theta = np.radians(rotate_deg_per_frame * t)
        rot = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta), np.cos(theta)]])
        pos = (model - center) @ rot.T + center + np.asarray(drift) * t
        pos = pos + rng.normal(scale=noise, size=pos.shape)

        points = list(pos)
        ids = list(range(n_markers))
        if drop_every and t > 0 and t % drop_every == 0:
            d = int(rng.integers(len(points)))
            del points[d]
            del ids[d]
        if ghost_every and t > 0 and t % ghost_every == 0:
            ghost = center + np.asarray(drift) * t + rng.normal(scale=3.0, size=2)
            points.append(ghost)
            ids.append(-1)

        order = rng.permutation(len(points))
        frames.append(np.asarray(points)[order])
        truth.append(np.asarray(ids)[order])

    return frames, truth
