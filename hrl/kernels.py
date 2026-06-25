"""Compatibility kernels for relaxation labeling.

A kernel builds the ``[n_objects, n_labels, n_objects, n_labels]`` compatibility
tensor consumed by :class:`hrl.core.RelaxationLabeler`. Swapping the kernel is
what re-points the same engine at a new problem domain.

``pairwise_distance_compatibility`` is the marker-correspondence kernel at the
heart of the author's motion-capture / 3-D fiducial work: assign each measured
point an identity (label) such that the *inter-point distances* agree with the
known model geometry. Because it compares only relative distances, it is
invariant to rotation and translation of the whole point set — exactly what you
want when matching a moving body to a rest-pose skeleton.
"""
from __future__ import annotations

import numpy as np

__all__ = ["pairwise_distance_compatibility"]


def pairwise_distance_compatibility(
    objects: np.ndarray,
    labels: np.ndarray,
    *,
    sigma: float = 1.0,
    exclude_self: bool = True,
    enforce_uniqueness: bool = True,
    exclusion_penalty: float = 0.0,
) -> np.ndarray:
    """Distance-invariant point correspondence kernel.

    ``compatibility[i, j, k, l] = exp(-(d_obj[i,k] - d_lab[j,l])**2 / (2 sigma**2))``

    i.e. assigning label ``j`` to point ``i`` and label ``l`` to point ``k`` is
    compatible to the degree that the measured distance ``|obj_i - obj_k|``
    matches the model distance ``|lab_j - lab_l|``.

    Parameters
    ----------
    objects:
        ``[n_objects, dim]`` measured points (e.g. detected markers this frame).
    labels:
        ``[n_labels, dim]`` model points (e.g. named skeleton markers).
    sigma:
        Tolerance on distance mismatch, in the same units as the coordinates.
        Smaller ``sigma`` is stricter.
    exclude_self:
        Zero out ``i == k`` so an object lends no support to its own labeling
        (the standard relaxation convention). Default ``True``.
    enforce_uniqueness:
        Suppress two distinct objects sharing one label (``i != k`` and
        ``j == l``). Without this the kernel would *reward* nearby points for
        taking the same marker (since the model self-distance is 0), producing
        duplicate assignments. Default ``True``.
    exclusion_penalty:
        Value written into the suppressed same-label entries. ``0.0`` removes
        the spurious reward; a negative value actively penalizes collisions.

    Returns
    -------
    np.ndarray
        ``[n_objects, n_labels, n_objects, n_labels]`` compatibility.
    """
    objects = np.asarray(objects, dtype=float)
    labels = np.asarray(labels, dtype=float)
    if objects.ndim != 2 or labels.ndim != 2 or objects.shape[1] != labels.shape[1]:
        raise ValueError("objects and labels must be [n, dim] with matching dim")

    d_obj = np.linalg.norm(objects[:, None, :] - objects[None, :, :], axis=-1)  # [no, no]
    d_lab = np.linalg.norm(labels[:, None, :] - labels[None, :, :], axis=-1)    # [nl, nl]

    # diff[i, j, k, l] = d_obj[i, k] - d_lab[j, l]
    diff = d_obj[:, None, :, None] - d_lab[None, :, None, :]
    compatibility = np.exp(-(diff ** 2) / (2.0 * sigma ** 2))

    if enforce_uniqueness:
        # same label j == l for distinct objects: a collision, not support.
        for j in range(labels.shape[0]):
            compatibility[:, j, :, j] = exclusion_penalty

    if exclude_self:
        idx = np.arange(objects.shape[0])
        compatibility[idx, :, idx, :] = 0.0

    return compatibility
