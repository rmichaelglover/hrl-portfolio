"""Mutual support winners and early assignment finalization for correspondence.

This is an opt-in heuristic scheduler over the public dense core's update, not
a replacement for its convergence definition. Locked *soft rows* still supply
support. Their contributions are cached, and their target rows are skipped.
Audits can reopen locks. Neither persistence nor auditing guarantees agreement
with an unfrozen run. Use for one-to-one identity matching, not posture/classes.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
import numpy as np

from .core import RelaxationLabeler


@dataclass(frozen=True)
class FinalizationPolicy:
    mode: str = "audited"  # off: same update without freezing; permanent: no mid-run audits
    patience: int = 3
    min_strength: float = 0.45
    min_strength_margin: float = 0.05
    min_label_support_margin: float = 0.05
    min_object_support_margin: float = 0.05
    max_row_change: float = 0.03
    audit_every: int = 6
    release_change: float = 0.06
    tie_tolerance: float = 1e-12

    @classmethod
    def aggressive(cls, *, mode="audited"):
        """Lower confidence gates for an explicit measured risk/speed tradeoff.

        Retains three fresh mutual wins, strict tie rejection, and support
        margins. Not a calibrated correctness guarantee or guaranteed speedup.
        """
        return cls(mode=mode, min_strength=0., min_strength_margin=.01,
                   min_label_support_margin=.03, min_object_support_margin=.03,
                   max_row_change=.05, audit_every=8, release_change=.10)

    def __post_init__(self):
        if self.mode not in {"off", "audited", "permanent"}:
            raise ValueError("mode must be off, audited, or permanent")
        if isinstance(self.patience, bool) or not isinstance(self.patience, int) or self.patience < 1:
            raise ValueError("patience must be a positive integer")
        if isinstance(self.audit_every, bool) or not isinstance(self.audit_every, int) or self.audit_every < 1:
            raise ValueError("audit_every must be a positive integer")
        for name in ["min_strength", "min_strength_margin", "min_label_support_margin",
                     "min_object_support_margin", "max_row_change", "release_change", "tie_tolerance"]:
            value = getattr(self, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if self.min_strength > 1 or self.min_strength_margin > 1:
            raise ValueError("strength thresholds must not exceed one")


@dataclass
class FinalizationResult:
    strengths: np.ndarray
    assignments: np.ndarray
    confidence: np.ndarray
    finalized: np.ndarray
    finalized_at: np.ndarray
    iterations: int
    converged: bool
    assignment_converged: bool
    stop_reason: str
    full_update_residual: float
    history: list[np.ndarray] | None
    audit_log: list[dict]
    trace: list[dict]
    statistics: dict
    noise_index: int | None


class MutualBestLabeler(RelaxationLabeler):
    """Early finalization in explicitly declared one-to-one correspondence.

    Row and column winners use *raw support*, not row-minmax scores. A candidate
    must also win in updated strength, have strength and normalized support
    margins, and change by at most max_row_change. Three consecutive fresh
    eligible sweeps are required by default. Every broken condition resets
    persistence. Noise never locks or reserves a label.

    Frozen source distributions are retained, not rounded to one-hot vectors.
    Active competitors may still choose a reserved label provisionally, but
    cannot finalize it. No assignment optimality or correctness is certified.
    Input compatibility is copied and read-only because cache validity requires
    a fixed problem. Construct a new instance for a new frame/evidence.
    """
    def __init__(self, compatibility, prior=None, *, one_to_one: bool,
                 policy: FinalizationPolicy | None = None, **kwargs):
        if one_to_one is not True:
            raise ValueError("MutualBestLabeler requires explicit one_to_one=True")
        if kwargs.get("max_iterations", 50) < 1:
            raise ValueError("max_iterations must be positive")
        if not 0 <= kwargs.get("support_factor", 1.0) or not np.isfinite(kwargs.get("support_factor", 1.0)):
            raise ValueError("support_factor must be finite and nonnegative")
        if not np.isfinite(kwargs.get("tol", 1e-6)) or kwargs.get("tol", 1e-6) < 0:
            raise ValueError("tol must be finite and nonnegative")
        if not np.isfinite(kwargs.get("noise_gain", .15)) or kwargs.get("noise_gain", .15) < 0:
            raise ValueError("noise_gain must be finite and nonnegative")
        if not np.isfinite(kwargs.get("prior_strength", .5)):
            raise ValueError("prior_strength must be finite")
        super().__init__(np.array(compatibility, dtype=float, copy=True), prior, **kwargs)
        self.compatibility.setflags(write=False)
        self.policy = FinalizationPolicy() if policy is None else policy
        if not isinstance(self.policy, FinalizationPolicy):
            raise TypeError("policy must be a FinalizationPolicy")
        self._matrix = self.compatibility.reshape(self.n_objects*self.n_labels, -1)
        # Exactly the legacy core's global noise expression, not the newer local-noise model.
        self._noise_matrix = ((self.n_labels - self.compatibility.sum(axis=1))
                              * (self.noise_gain / self.n_labels)).reshape(self.n_objects, -1) if self.noise else None
        self.finalized = np.zeros(self.n_objects, dtype=bool)
        self.finalized_at = np.full(self.n_objects, -1, dtype=int)
        self._locked_label = np.full(self.n_objects, -1, dtype=int)
        self._streak_label = np.full(self.n_objects, -1, dtype=int)
        self._streak = np.zeros(self.n_objects, dtype=int)
        self._fixed = np.zeros((self.n_objects, self.n_labels))
        self._fixed_noise = np.zeros(self.n_objects)
        self._active = np.arange(self.n_objects)
        self._kernel = self._matrix
        self._noise_kernel = self._noise_matrix
        self.audit_log = []
        self.trace = []
        self.stats = {"support_multiply_adds": 0, "cache_rebuilds": 0,
                      "finalizations": 0, "reopenings": 0, "full_checks": 0}
        self._ran = False

    def step(self):
        raise RuntimeError("Use run(); isolated legacy steps would invalidate the finalization cache")

    def _columns(self, rows):
        return (np.asarray(rows)[:, None]*self.n_labels + np.arange(self.n_labels)).ravel()

    def _rebuild(self):
        """Stream fixed-source support once; pack the smaller active operator.

        Full contiguous BLAS products deliberately do more arithmetic than a
        gathered-column product, but avoid a large strided temporary. Count
        those full products honestly. No cache is built if all rows lock.
        """
        self.stats["cache_rebuilds"] += 1
        self._active = np.flatnonzero(~self.finalized)
        if not len(self._active):
            self._kernel = np.empty((0, 0))
            self._noise_kernel = np.empty((0, 0)) if self.noise else None
            return
        if self.finalized.any():
            fixed = np.zeros((self.n_objects, self.n_labels))
            fixed[self.finalized] = self.strength[self.finalized, :self.n_labels]
            vector = fixed.ravel()
            self._fixed[:] = (self._matrix @ vector).reshape(self.n_objects, self.n_labels)
            self.stats["support_multiply_adds"] += self._matrix.size
            if self.noise:
                self._fixed_noise[:] = self._noise_matrix @ vector
                self.stats["support_multiply_adds"] += self._noise_matrix.size
        else:
            self._fixed.fill(0); self._fixed_noise.fill(0)
        cols = self._columns(self._active)
        if len(self._active) == self.n_objects:
            self._kernel = self._matrix
            self._noise_kernel = self._noise_matrix
        else:
            self._kernel = self._matrix[np.ix_(cols, cols)]
            self._noise_kernel = self._noise_matrix[np.ix_(self._active, cols)] if self.noise else None

    def _raw(self, all_rows=False):
        active = self._active
        rows = np.arange(self.n_objects) if all_rows else active
        raw = np.zeros((len(rows), self.n_total))
        if not len(rows):
            return raw
        if all_rows:
            self.stats["full_checks"] += 1
            # A full audit streams the original operator. Packing a large
            # all-target/active-source slice at every audit costs more than
            # the multiplication it saves, and also needs temporary memory.
            kernel, nk = self._matrix, self._noise_matrix
            vec = self.strength[:, :self.n_labels].ravel()
            fixed = np.zeros((len(rows), self.n_labels))
            fixed_noise = np.zeros(len(rows))
        else:
            kernel, nk = self._kernel, self._noise_kernel
            vec = self.strength[active, :self.n_labels].ravel()
            fixed, fixed_noise = self._fixed[rows], self._fixed_noise[rows]
        raw[:, :self.n_labels] = (kernel @ vec).reshape(len(rows), self.n_labels) + fixed
        self.stats["support_multiply_adds"] += kernel.shape[0]*kernel.shape[1]
        if self.noise:
            raw[:, self.noise_index] = nk @ vec + fixed_noise
            self.stats["support_multiply_adds"] += nk.shape[0]*nk.shape[1]
        return raw

    def _proposal(self, rows, raw):
        support = self._minmax_rows(raw)
        base = self._prior[rows]**self.prior_strength * self.strength[rows]**(1-self.prior_strength)
        return self._normalize_rows(base * (1+self.support_factor*support))

    def _eligible(self, rows, raw, proposed, change, *, respect_reservations=True):
        """Return a unique mutual-best label, or -1; ties are never broken by index."""
        if not len(rows):
            return np.empty(0, dtype=int)
        p = self.policy
        winner = np.argmax(raw, axis=1)
        sorted_raw = np.partition(raw, -2, axis=1) if self.n_total > 1 else raw
        row_gap = sorted_raw[:, -1] - sorted_raw[:, -2] if self.n_total > 1 else np.full(len(rows), np.inf)
        row_scale = np.maximum(np.max(np.abs(raw), axis=1), np.finfo(float).eps)
        real = raw[:, :self.n_labels]
        column_owner = np.argmax(real, axis=0)
        column_sorted = np.partition(real, -2, axis=0) if len(rows) > 1 else real
        col_gap = column_sorted[-1] - column_sorted[-2] if len(rows) > 1 else np.full(self.n_labels, np.inf)
        col_scale = np.maximum(np.max(np.abs(real), axis=0), np.finfo(float).eps)
        sorder = np.partition(proposed, -2, axis=1) if self.n_total > 1 else proposed
        sgap = sorder[:, -1]-sorder[:, -2] if self.n_total > 1 else np.ones(len(rows))
        out = np.full(len(rows), -1, dtype=int)
        # Vectorized eligibility matters when support contracts to a small field:
        # a Python loop over every remaining object can cost more than its BLAS work.
        label = np.minimum(winner, self.n_labels-1)
        eligible = ((winner < self.n_labels)
                    & (column_owner[label] == np.arange(len(rows)))
                    & (row_gap > p.tie_tolerance) & (col_gap[label] > p.tie_tolerance)
                    & (row_gap/row_scale >= p.min_label_support_margin)
                    & (col_gap[label]/col_scale[label] >= p.min_object_support_margin)
                    & (np.argmax(proposed, axis=1) == winner)
                    & (proposed[np.arange(len(rows)), label] >= p.min_strength)
                    & (sgap > p.tie_tolerance) & (sgap >= p.min_strength_margin)
                    & (change <= p.max_row_change))
        if respect_reservations and self.finalized.any():
            eligible &= ~np.isin(winner, self._locked_label[self.finalized])
        out[eligible] = winner[eligible]
        return out

    def _audit(self, *, final=False):
        rows = np.arange(self.n_objects)
        raw = self._raw(all_rows=True)
        proposed = self._proposal(rows, raw)
        delta = np.max(np.abs(proposed-self.strength), axis=1)
        # All objects compete on a full fresh sweep; never audit stale cached rankings.
        candidates = self._eligible(rows, raw, proposed, np.zeros(self.n_objects), respect_reservations=False)
        release = np.flatnonzero(self.finalized & ((candidates != self._locked_label) | (delta > self.policy.release_change)))
        self.audit_log.append({"iteration": self.iteration, "final": final,
                               "full_update_residual": float(delta.max()), "reopened": release.tolist()})
        if len(release):
            self.audit_log[-1]["released_pairs"] = [
                {"object": int(i), "label": int(self._locked_label[i]),
                 "raw_winner": int(np.argmax(raw[i])), "strength_winner": int(np.argmax(proposed[i])),
                 "one_step_change": float(delta[i])} for i in release]
            self.finalized[release] = False
            self.finalized_at[release] = -1
            self._locked_label[release] = -1
            self._streak[release] = 0
            self._streak_label[release] = -1
            self.stats["reopenings"] += len(release)
            self._rebuild()
        return float(delta.max()), len(release)

    def run(self, verbose=False):
        if self._ran:
            raise RuntimeError("Create a fresh labeler for each run/problem")
        self._ran = True
        start = time.perf_counter()
        history = [self.strength.copy()] if self.record_history else None
        reason = "iteration_limit"
        for _ in range(self.max_iterations):
            rows = self._active.copy()
            raw = self._raw()
            proposed = self._proposal(rows, raw)
            change = np.max(np.abs(proposed-self.strength[rows]), axis=1)
            self.strength[rows] = proposed
            self.iteration += 1
            new = []
            if self.policy.mode != "off":
                eligible = self._eligible(rows, raw, proposed, change)
                same = eligible == self._streak_label[rows]
                self._streak[rows] = np.where(eligible < 0, 0, np.where(same, self._streak[rows]+1, 1))
                self._streak_label[rows] = eligible
                new = rows[(eligible >= 0) & (self._streak[rows] >= self.policy.patience)]
                if len(new):
                    self.finalized[new] = True
                    self.finalized_at[new] = self.iteration
                    self._locked_label[new] = self._streak_label[new]
                    self.stats["finalizations"] += len(new)
                    self._rebuild()
            delta = float(change.max())
            audit_due = self.policy.mode == "audited" and self.iteration % self.policy.audit_every == 0
            need_stop_check = not len(self._active) or delta < self.tol or self.iteration == self.max_iterations
            residual = None
            reopened = 0
            if audit_due or need_stop_check:
                if self.policy.mode == "audited":
                    residual, reopened = self._audit(final=need_stop_check)
                else:
                    residual = float(np.max(np.abs(self._proposal(np.arange(self.n_objects), self._raw(all_rows=True))-self.strength)))
            self.trace.append({"iteration": self.iteration, "active": int(len(self._active)),
                               "new_finalizations": np.asarray(new, dtype=int).tolist(), "reopened": reopened,
                               "new_pairs": [{"object": int(i), "label": int(self._streak_label[i])} for i in new],
                               "active_delta": delta, "full_residual": residual})
            if history is not None:
                history.append(self.strength.copy())
            if verbose:
                print(self.trace[-1])
            if residual is not None and residual < self.tol:
                reason = "numerical_fixed_point"
                break
            if delta < self.tol and self.finalized.any() and not reopened:
                reason = "active_fixed_point_with_finalized_assignments"
                break
            if not len(self._active) and not reopened:
                reason = "all_assignments_finalized"
                break
        # Always report a full unfrozen one-step residual, even for permanent mode.
        raw = self._raw(all_rows=True)
        residual = float(np.max(np.abs(self._proposal(np.arange(self.n_objects), raw)-self.strength)))
        assignments, confidence = self._decide()
        self.stats["inference_seconds"] = time.perf_counter()-start
        self.stats["policy"] = dict(self.policy.__dict__)
        if self.n_total > 1:
            top = np.partition(self.strength, -2, axis=1)
            self.stats["tied_strength_rows"] = int(np.sum(top[:, -1]-top[:, -2] <= self.policy.tie_tolerance))
        else:
            self.stats["tied_strength_rows"] = 0
        self.stats["full_sweep_equivalents"] = self.stats["support_multiply_adds"] / (self.n_objects*self.n_total*self.n_objects*self.n_labels)
        return FinalizationResult(self.strength.copy(), assignments, confidence,
                                  self.finalized.copy(), self.finalized_at.copy(), self.iteration,
                                  residual < self.tol, bool(self.finalized.all()), reason, residual,
                                  history, list(self.audit_log), list(self.trace), dict(self.stats), self.noise_index)
