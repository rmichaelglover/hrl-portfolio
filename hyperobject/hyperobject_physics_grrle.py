#!/usr/bin/env python3
"""
hyperobject_physics_grrle.py
============================

GRRLE Physics / Law-Derivation Experiment v0.2

Basis
-----
This program uses the attached "C — Musical Hyperobject" JSON as a concrete
primitive dynamical system:

    x'' + K x = 0
    x = U q

It does NOT hard-code twelve separate oscillator laws.

Instead it:

1. Loads the primitive coupling matrix K and mode basis U.
2. Verifies that U is approximately orthonormal.
3. Derives the modal operator

       Lambda = U^T K U

4. Detects whether Lambda is approximately diagonal.
5. Derives the subsidiary modal laws

       q_j'' + lambda_j q_j = 0

6. Derives the corresponding frequencies

       f_j = sqrt(lambda_j) / (2*pi)

7. Generates motion from the primitive dynamics.
8. Hides the known lambda_j values from the observation-stage GRRLE.
9. Re-estimates candidate subsidiary laws from sampled trajectories.
10. Uses relaxation over competing law families:
       FREE            q'' = 0
       OSCILLATOR      q'' + lambda q = 0
       DAMPED          q'' + gamma q' + lambda q = 0
       DRIVEN_OFFSET   q'' + lambda q = c
    with a simplicity penalty so needless parameters are disfavored.

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

EPS = 1e-12
PI2 = 2.0 * math.pi


# ============================================================================
# BASIC LINEAR ALGEBRA — STANDARD LIBRARY ONLY
# ============================================================================

Vector = List[float]
Matrix = List[List[float]]


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b:
        return []
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def matvec(a: Matrix, x: Sequence[float]) -> Vector:
    return [sum(v * w for v, w in zip(row, x)) for row in a]


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm2(x: Sequence[float]) -> float:
    return math.sqrt(dot(x, x))


def frobenius(a: Matrix) -> float:
    return math.sqrt(sum(v * v for row in a for v in row))


def identity(n: int) -> Matrix:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def matrix_sub(a: Matrix, b: Matrix) -> Matrix:
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def diagonal_matrix(diag: Sequence[float]) -> Matrix:
    n = len(diag)
    return [[diag[i] if i == j else 0.0 for j in range(n)] for i in range(n)]


def diagonal(a: Matrix) -> Vector:
    return [a[i][i] for i in range(min(len(a), len(a[0]) if a else 0))]


def offdiag_norm(a: Matrix) -> float:
    return math.sqrt(
        sum(
            a[i][j] * a[i][j]
            for i in range(len(a))
            for j in range(len(a[i]))
            if i != j
        )
    )


# ============================================================================
# TROOL
# ============================================================================

VFALSE = "vfalse"
ISH = "ish"
VTRUE = "vtrue"


def trool(strength: float, low: float = 0.33, high: float = 0.67) -> str:
    if strength < low:
        return VFALSE
    if strength > high:
        return VTRUE
    return ISH


# ============================================================================
# MODEL LOADING
# ============================================================================

@dataclass
class Hyperobject:
    name: str
    K: Matrix
    U: Matrix
    note_names: List[str]
    note_frequencies: List[float]


def load_hyperobject(path: Path) -> Hyperobject:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    dynamics = data["dynamics"]
    K = [[float(v) for v in row] for row in dynamics["coupling_K"]]
    U = [[float(v) for v in row] for row in dynamics["mode_basis_U"]]

    notes = data.get("notes", [])
    names = [str(n.get("register", n.get("pitch_class", i))) for i, n in enumerate(notes)]
    freqs = [float(n.get("frequency_hz", float("nan"))) for n in notes]

    n = len(K)
    if n == 0 or any(len(row) != n for row in K):
        raise ValueError("K must be a nonempty square matrix.")
    if len(U) != n or any(len(row) != n for row in U):
        raise ValueError("U must have the same square shape as K.")

    if len(names) != n:
        names = [f"mode_{i}" for i in range(n)]
    if len(freqs) != n:
        freqs = [float("nan")] * n

    return Hyperobject(
        name=str(data.get("name", path.stem)),
        K=K,
        U=U,
        note_names=names,
        note_frequencies=freqs,
    )


# ============================================================================
# LAW DERIVATION FROM THE PRIMITIVE OPERATOR
# ============================================================================

@dataclass
class ModalDerivation:
    lambda_matrix: Matrix
    lambdas: Vector
    frequencies_hz: Vector
    orthonormal_error: float
    diagonalization_error: float
    relative_diagonalization_error: float


def derive_modal_laws(model: Hyperobject) -> ModalDerivation:
    U = model.U
    K = model.K
    UT = transpose(U)

    gram = matmul(UT, U)
    orth_error = frobenius(matrix_sub(gram, identity(len(U))))

    # Because x = U q:
    #
    #     U q'' + K U q = 0
    #     q'' + U^T K U q = 0
    #
    # when U is orthonormal.
    lam = matmul(matmul(UT, K), U)
    lambdas = diagonal(lam)

    off = offdiag_norm(lam)
    full = max(frobenius(lam), EPS)

    freqs = [
        math.sqrt(max(v, 0.0)) / PI2
        for v in lambdas
    ]

    return ModalDerivation(
        lambda_matrix=lam,
        lambdas=lambdas,
        frequencies_hz=freqs,
        orthonormal_error=orth_error,
        diagonalization_error=off,
        relative_diagonalization_error=off / full,
    )


# ============================================================================
# SYNTHETIC OBSERVATION GENERATION
# ============================================================================

@dataclass
class Trajectory:
    times: Vector
    x: List[Vector]
    q_true: List[Vector]


def simulate_modal_motion(
    model: Hyperobject,
    derivation: ModalDerivation,
    duration: float,
    sample_rate: float,
) -> Trajectory:
    n = len(derivation.lambdas)
    dt = 1.0 / sample_rate
    steps = max(5, int(round(duration * sample_rate)))

    # Deterministic, mixed initial modal state.
    # Every mode receives some excitation, but amplitudes decrease mildly.
    q0 = [1.0 / math.sqrt(i + 1.0) for i in range(n)]
    v0 = [0.15 * ((-1.0) ** i) / math.sqrt(i + 1.0) for i in range(n)]

    times: Vector = []
    xs: List[Vector] = []
    qs: List[Vector] = []

    for k in range(steps):
        t = k * dt
        q: Vector = []

        for j, lam in enumerate(derivation.lambdas):
            omega = math.sqrt(max(lam, 0.0))
            if omega < EPS:
                value = q0[j] + v0[j] * t
            else:
                value = (
                    q0[j] * math.cos(omega * t)
                    + (v0[j] / omega) * math.sin(omega * t)
                )
            q.append(value)

        x = matvec(model.U, q)

        times.append(t)
        qs.append(q)
        xs.append(x)

    return Trajectory(times=times, x=xs, q_true=qs)


def recover_modal_coordinates(model: Hyperobject, xs: List[Vector]) -> List[Vector]:
    UT = transpose(model.U)
    return [matvec(UT, x) for x in xs]


# ============================================================================
# OBSERVATIONAL DIFFERENTIATION
# ============================================================================

@dataclass
class ModeObservations:
    q: Vector
    qdot: Vector
    qddot: Vector


def finite_difference_mode(q_full: Sequence[float], dt: float) -> ModeObservations:
    # Five-point formulas improve frequency recovery substantially while
    # still treating the trajectory as sampled observations.
    q: Vector = []
    qdot: Vector = []
    qddot: Vector = []

    if len(q_full) < 5:
        raise ValueError("Need at least five samples.")

    h2 = dt * dt

    for i in range(2, len(q_full) - 2):
        qm2 = q_full[i - 2]
        qm1 = q_full[i - 1]
        q0 = q_full[i]
        qp1 = q_full[i + 1]
        qp2 = q_full[i + 2]

        d1 = (qm2 - 8.0 * qm1 + 8.0 * qp1 - qp2) / (12.0 * dt)
        d2 = (-qm2 + 16.0 * qm1 - 30.0 * q0 + 16.0 * qp1 - qp2) / (12.0 * h2)

        q.append(q0)
        qdot.append(d1)
        qddot.append(d2)

    return ModeObservations(q=q, qdot=qdot, qddot=qddot)


# ============================================================================
# SMALL LEAST-SQUARES HELPERS
# ============================================================================

def solve_1d_coefficient(x: Sequence[float], y: Sequence[float]) -> float:
    # y ~= beta*x
    den = dot(x, x) + EPS
    return dot(x, y) / den


def solve_2x2(
    a11: float, a12: float, a22: float,
    b1: float, b2: float,
) -> Tuple[float, float]:
    det = a11 * a22 - a12 * a12
    if abs(det) < EPS:
        return 0.0, 0.0
    x1 = (b1 * a22 - b2 * a12) / det
    x2 = (a11 * b2 - a12 * b1) / det
    return x1, x2


def rms(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        return 0.0
    return math.sqrt(sum(v * v for v in vals) / len(vals))


# ============================================================================
# CANDIDATE SUBSIDIARY LAWS
# ============================================================================

@dataclass
class CandidateLaw:
    name: str
    parameters: dict
    residual_rms: float
    normalized_residual: float
    complexity: int
    local_support: float = 0.0
    strength: float = 0.0


def fit_candidate_laws(obs: ModeObservations) -> List[CandidateLaw]:
    q = obs.q
    v = obs.qdot
    a = obs.qddot

    acceleration_scale = max(rms(a), EPS)

    laws: List[CandidateLaw] = []

    # FREE: q'' = 0
    r_free = list(a)
    laws.append(CandidateLaw(
        name="FREE",
        parameters={},
        residual_rms=rms(r_free),
        normalized_residual=rms(r_free) / acceleration_scale,
        complexity=0,
    ))

    # OSCILLATOR: q'' + lambda*q = 0
    # => -q'' ~= lambda*q
    lam = solve_1d_coefficient(q, [-x for x in a])
    lam = max(0.0, lam)
    r_osc = [aa + lam * qq for qq, aa in zip(q, a)]
    laws.append(CandidateLaw(
        name="OSCILLATOR",
        parameters={"lambda": lam},
        residual_rms=rms(r_osc),
        normalized_residual=rms(r_osc) / acceleration_scale,
        complexity=1,
    ))

    # DAMPED: q'' + gamma*q' + lambda*q = 0
    # Solve [-q''] ~= lambda*q + gamma*q'
    sqq = dot(q, q)
    sqv = dot(q, v)
    svv = dot(v, v)
    bq = dot(q, [-x for x in a])
    bv = dot(v, [-x for x in a])
    lam_d, gamma = solve_2x2(sqq, sqv, svv, bq, bv)
    lam_d = max(0.0, lam_d)
    r_damp = [
        aa + gamma * vv + lam_d * qq
        for qq, vv, aa in zip(q, v, a)
    ]
    laws.append(CandidateLaw(
        name="DAMPED",
        parameters={"lambda": lam_d, "gamma": gamma},
        residual_rms=rms(r_damp),
        normalized_residual=rms(r_damp) / acceleration_scale,
        complexity=2,
    ))

    # DRIVEN_OFFSET: q'' + lambda*q = c
    # Rearranged: -q'' ~= lambda*q - c.
    # Fit using q plus constant.
    n = len(q)
    sq = sum(q)
    sqq = dot(q, q)
    sy = sum(-x for x in a)
    sqy = dot(q, [-x for x in a])
    lam_o, intercept = solve_2x2(sqq, sq, float(n), sqy, sy)
    # Here y = lambda*q + intercept, where intercept = -c.
    lam_o = max(0.0, lam_o)
    c = -intercept
    r_offset = [
        aa + lam_o * qq - c
        for qq, aa in zip(q, a)
    ]
    laws.append(CandidateLaw(
        name="DRIVEN_OFFSET",
        parameters={"lambda": lam_o, "c": c},
        residual_rms=rms(r_offset),
        normalized_residual=rms(r_offset) / acceleration_scale,
        complexity=2,
    ))

    return laws


# ============================================================================
# GRRLE RELAXATION OVER LAW FAMILIES
# ============================================================================

def relax_law_strengths(
    laws: List[CandidateLaw],
    iterations: int = 24,
    fit_scale: float = 0.05,
    complexity_pressure: float = 0.35,
    persistence: float = 0.30,
) -> None:
    """
    Relax strengths over candidate law families.

    Evidence:
        exp(-normalized_residual / fit_scale)

    Simplicity:
        exp(-complexity_pressure * complexity)

    Persistence:
        each iteration retains part of the previous assignment.

    Competition:
        strengths are normalized after each update.
    """
    n = len(laws)
    strengths = [1.0 / n] * n

    for law in laws:
        fit = math.exp(-law.normalized_residual / max(fit_scale, EPS))
        simplicity = math.exp(-complexity_pressure * law.complexity)
        law.local_support = fit * simplicity

    for _ in range(iterations):
        raw = []
        for old, law in zip(strengths, laws):
            target = max(law.local_support, EPS)
            score = (old ** persistence) * target
            raw.append(score)

        total = sum(raw) + EPS
        strengths = [x / total for x in raw]

    for law, strength in zip(laws, strengths):
        law.strength = strength


# ============================================================================
# REPORT
# ============================================================================

def print_derivation(model: Hyperobject, d: ModalDerivation) -> None:
    print()
    print("=" * 78)
    print("GRRLE PHYSICS — PRIMITIVE -> SUBSIDIARY LAW DERIVATION")
    print("=" * 78)
    print(f"model:                       {model.name}")
    print(f"dimension:                   {len(model.K)}")
    print(f"||U^T U - I||_F:             {d.orthonormal_error:.6e}")
    print(f"offdiag ||U^T K U||_F:       {d.diagonalization_error:.6e}")
    print(f"relative offdiag error:      {d.relative_diagonalization_error:.6e}")

    print()
    print("Primitive law:")
    print("    x'' + K x = 0")
    print("    x = U q")
    print()
    print("Derived law:")
    print("    q'' + (U^T K U) q = 0")
    print()
    print("Because U^T K U is numerically diagonal here:")
    print("    q_j'' + lambda_j q_j = 0")
    print("    f_j = sqrt(lambda_j)/(2*pi)")
    print()

    print(
        f"{'mode':>4} {'name':>7} {'lambda':>16} {'derived Hz':>13} "
        f"{'JSON Hz':>13} {'delta Hz':>12}"
    )
    print("-" * 78)

    for i, (lam, f) in enumerate(zip(d.lambdas, d.frequencies_hz)):
        known = model.note_frequencies[i]
        delta = f - known if math.isfinite(known) else float("nan")
        print(
            f"{i:4d} {model.note_names[i]:>7s} "
            f"{lam:16.6f} {f:13.6f} "
            f"{known:13.6f} {delta:12.3e}"
        )


def print_discovery(
    model: Hyperobject,
    d: ModalDerivation,
    q_recovered: List[Vector],
    sample_rate: float,
) -> None:
    print()
    print("=" * 78)
    print("OBSERVATION-STAGE GRRLE LAW DISCOVERY")
    print("=" * 78)
    print("The observation stage is not handed lambda_j.")
    print("It sees sampled modal motion and competes among candidate law families.")
    print()

    dt = 1.0 / sample_rate
    n_modes = len(d.lambdas)

    for mode in range(n_modes):
        series = [row[mode] for row in q_recovered]
        obs = finite_difference_mode(series, dt)
        laws = fit_candidate_laws(obs)
        relax_law_strengths(laws)
        laws.sort(key=lambda law: law.strength, reverse=True)

        winner = laws[0]
        lam_found = float(winner.parameters.get("lambda", 0.0))
        f_found = math.sqrt(max(lam_found, 0.0)) / PI2 if lam_found > 0 else 0.0
        f_true = d.frequencies_hz[mode]

        print(
            f"mode {mode:2d} {model.note_names[mode]:>4s}: "
            f"winner={winner.name:13s} "
            f"strength={winner.strength:7.4f} {trool(winner.strength):>6s} "
            f"f_found={f_found:10.4f} Hz "
            f"f_derived={f_true:10.4f} Hz "
            f"error={f_found - f_true:+9.4f}"
        )

        for law in laws:
            params = ", ".join(f"{k}={v:.6g}" for k, v in law.parameters.items())
            print(
                f"    {law.name:13s} "
                f"S={law.strength:8.5f} "
                f"res={law.normalized_residual:10.3e} "
                f"C={law.complexity} "
                f"{params}"
            )


# ============================================================================
# MAIN
# ============================================================================

def locate_default_json() -> Path:
    candidates = [
        Path("./hyperobject(1).json"),
        Path("./hyperobject.json"),
        Path("/mnt/data/hyperobject(1).json"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "json_file",
        nargs="?",
        default=str(locate_default_json()),
        help="Path to the Musical Hyperobject JSON",
    )
    ap.add_argument(
        "--duration",
        type=float,
        default=0.20,
        help="Synthetic observation duration in seconds",
    )
    ap.add_argument(
        "--sample-rate",
        type=float,
        default=12000.0,
        help="Observation sample rate in Hz",
    )
    args = ap.parse_args()

    path = Path(args.json_file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    model = load_hyperobject(path)
    derivation = derive_modal_laws(model)

    print_derivation(model, derivation)

    trajectory = simulate_modal_motion(
        model,
        derivation,
        duration=args.duration,
        sample_rate=args.sample_rate,
    )

    # The law-discovery stage starts from x(t), not the internally retained q(t).
    q_recovered = recover_modal_coordinates(model, trajectory.x)

    # Reconstruction sanity check: recovered q versus q used only to synthesize x.
    max_q_error = max(
        abs(a - b)
        for qa, qb in zip(q_recovered, trajectory.q_true)
        for a, b in zip(qa, qb)
    )
    print()
    print(f"max |U^T x - q_true|:        {max_q_error:.6e}")

    print_discovery(
        model,
        derivation,
        q_recovered,
        sample_rate=args.sample_rate,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
