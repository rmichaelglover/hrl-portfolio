"""Body-position labeling from a wearable accelerometer.

A single tri-axial accelerometer worn on the torso measures the gravity vector
in the body's frame. While the body is still, that vector points at one of a
handful of canonical directions — supine, prone, on the left/right side, upright
— so *posture classification is a labeling problem*: each reading (object) is
assigned one of the canonical positions (labels).

This is the same :class:`hrl.core.RelaxationLabeler` used for motion-capture
correspondence, re-pointed by three ingredients:

* **prior = absolute fit.** How close a reading sits to each canonical gravity
  vector. This is the workhorse: it breaks the rotational symmetry of the
  canonical set (the six directions form a symmetric octahedron — pure relative
  geometry can't tell "left" from "up", so distances *alone* collapse to a tie).
* **compatibility = relative geometry + temporal smoothing.** Readings that are
  close in sensor space should land on the same posture; readings close *in
  time* should agree (you don't flip postures every second). The temporal term
  is the body-position analogue of the tracker's memory prior.
* **noise label.** Transitions — the body rolling over — produce readings that
  match no canonical direction (and whose magnitude isn't ~1 g). The noise
  label quarantines them instead of forcing a wrong posture.

Companion to the author's C++ relaxation-labeling engine, where this problem
("body_pos") is implemented over real accelerometer logs.
"""
from __future__ import annotations

import numpy as np

from .core import RelaxationLabeler, RelaxationResult
from .kernels import pairwise_distance_compatibility

__all__ = [
    "GRAVITY",
    "POSITION_NAMES",
    "canonical_positions",
    "affinity_prior",
    "session_compatibility",
    "classify_session",
    "synthetic_session",
]

GRAVITY = 9.81  # m/s^2

# The six canonical postures, each the gravity vector a torso-worn sensor reads
# while the body is still in that position. They sit on the ±axes (an octahedron).
POSITION_NAMES = ["supine", "prone", "left", "right", "upright", "inverted"]
_UNIT = np.array(
    [
        [0.0, 0.0, 1.0],   # supine   — on the back
        [0.0, 0.0, -1.0],  # prone    — face down
        [1.0, 0.0, 0.0],   # left     — left side
        [-1.0, 0.0, 0.0],  # right    — right side
        [0.0, 1.0, 0.0],   # upright  — sitting / standing
        [0.0, -1.0, 0.0],  # inverted — head down (completes the set)
    ]
)


def canonical_positions(gravity: float = GRAVITY) -> tuple[np.ndarray, list[str]]:
    """Return ``(positions[6, 3], names)`` — the canonical gravity vectors."""
    return _UNIT * gravity, list(POSITION_NAMES)


def affinity_prior(
    readings: np.ndarray,
    positions: np.ndarray,
    *,
    sigma: float | None = None,
    floor: float = 1e-3,
) -> np.ndarray:
    """Prior favoring the canonical position each reading actually points at.

    ``prior[i, j] = exp(-|reading_i - position_j|**2 / (2 sigma**2))``, floored
    so nothing is hard-excluded. This absolute fit is what lets relaxation pin
    an *absolute* posture (relative geometry alone is rotation-invariant).
    """
    readings = np.asarray(readings, dtype=float)
    positions = np.asarray(positions, dtype=float)
    if sigma is None:
        sigma = 0.3 * float(np.linalg.norm(positions[0]))  # ~0.3 g tolerance
    dist = np.linalg.norm(readings[:, None, :] - positions[None, :, :], axis=-1)
    return np.maximum(floor, np.exp(-(dist ** 2) / (2.0 * sigma ** 2)))


def session_compatibility(
    readings: np.ndarray,
    positions: np.ndarray,
    times: np.ndarray | None = None,
    *,
    sigma_spatial: float | None = None,
    tau: float = 1.0,
    temporal_strength: float = 0.0,
) -> np.ndarray:
    """Compatibility tensor: relative geometry + optional temporal smoothing.

    The geometry term (``pairwise_distance_compatibility`` with uniqueness
    *off*, since many readings legitimately share one posture) rewards readings
    that are close in sensor space taking the same posture. The temporal term
    adds, for readings close in time, a bonus on agreeing — encoding that
    posture is piecewise-constant over a night.
    """
    readings = np.asarray(readings, dtype=float)
    positions = np.asarray(positions, dtype=float)
    if sigma_spatial is None:
        sigma_spatial = 0.5 * float(np.linalg.norm(positions[0]))

    compat = pairwise_distance_compatibility(
        readings, positions, sigma=sigma_spatial,
        exclude_self=True, enforce_uniqueness=False,
    )

    if temporal_strength > 0.0 and times is not None:
        times = np.asarray(times, dtype=float)
        dt = times[:, None] - times[None, :]
        temporal = np.exp(-(dt ** 2) / (2.0 * tau ** 2))  # [n, n]
        np.fill_diagonal(temporal, 0.0)
        n_labels = positions.shape[0]
        # Reward time-adjacent readings agreeing on the *same* posture j == l.
        for j in range(n_labels):
            compat[:, j, :, j] += temporal_strength * temporal

    return compat


def classify_session(
    readings: np.ndarray,
    *,
    times: np.ndarray | None = None,
    gravity: float = GRAVITY,
    sigma_spatial: float | None = None,
    sigma_prior: float | None = None,
    tau: float = 1.0,
    temporal_strength: float = 0.6,
    prior_strength: float = 0.6,
    noise: bool = True,
    noise_gain: float = 1.2,
    max_iterations: int = 60,
    record_history: bool = False,
) -> RelaxationResult:
    """Label every accelerometer reading with a body position.

    Parameters
    ----------
    readings:
        ``[n, 3]`` accelerometer readings (the measured gravity vector).
    times:
        Optional ``[n]`` timestamps; enables temporal smoothing.
    temporal_strength:
        Weight of the "neighbors in time agree" term (0 disables it).
    prior_strength:
        How strongly the absolute-fit prior steers the labeling (see
        :class:`hrl.core.RelaxationLabeler`).

    Returns
    -------
    RelaxationResult
        ``assignments[i]`` is a posture index into :data:`POSITION_NAMES`, or
        ``-1`` for a reading sent to the noise label (a transition / movement).
    """
    readings = np.asarray(readings, dtype=float)
    positions, _ = canonical_positions(gravity)

    prior = affinity_prior(readings, positions, sigma=sigma_prior)
    compat = session_compatibility(
        readings, positions, times,
        sigma_spatial=sigma_spatial, tau=tau, temporal_strength=temporal_strength,
    )

    return RelaxationLabeler(
        compat, prior,
        noise=noise, noise_gain=noise_gain, prior_strength=prior_strength,
        max_iterations=max_iterations, record_history=record_history,
    ).run()


def synthetic_session(
    *,
    gravity: float = GRAVITY,
    schedule: list[tuple[str, int]] | None = None,
    noise: float = 0.6,
    transition_readings: int = 1,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a synthetic night: posture stretches, sensor noise, transitions.

    The body holds each posture in ``schedule`` for the given number of samples,
    with Gaussian sensor noise; between stretches it rolls over, emitting a few
    high-magnitude "movement" readings that belong to no posture.

    Returns ``(readings[n, 3], times[n], truth[n])`` where ``truth[i]`` is the
    posture index, or ``-1`` for an injected transition reading.
    """
    if schedule is None:
        schedule = [
            ("supine", 6), ("left", 5), ("supine", 4),
            ("right", 6), ("prone", 5), ("upright", 3), ("supine", 5),
        ]
    rng = np.random.default_rng(seed)
    positions, names = canonical_positions(gravity)
    name_to_idx = {n: i for i, n in enumerate(names)}

    readings: list[np.ndarray] = []
    truth: list[int] = []
    for s, (name, count) in enumerate(schedule):
        if s > 0:
            # A roll-over between postures. A still body always reads ~1 g; the
            # act of rolling adds linear acceleration, so the sensor leaves the
            # gravity sphere -- a high-magnitude spike in an arbitrary direction.
            for _ in range(transition_readings):
                direction = rng.normal(size=3)
                direction /= np.linalg.norm(direction)
                magnitude = gravity * rng.uniform(1.8, 3.3)
                readings.append(direction * magnitude)
                truth.append(-1)
        j = name_to_idx[name]
        for _ in range(count):
            readings.append(positions[j] + rng.normal(scale=noise, size=3))
            truth.append(j)

    readings_arr = np.asarray(readings)
    times = np.arange(len(readings_arr), dtype=float)
    return readings_arr, times, np.asarray(truth)
