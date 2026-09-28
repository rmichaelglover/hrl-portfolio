#!/usr/bin/env python3
"""
relax_mnist.py

RELAX on MNIST
==============

A small, interpretable experiment using the three coupled RELAX layers:

    state relaxation
    goal relaxation
    operator relaxation

For each handwritten digit, the engine considers ten candidate assignments
(0..9).  Candidate support is built from several interpretable terms:

    prototype       cosine similarity to the mean image for that class
    block_shape     similarity of a coarse 4x4 spatial representation
    mass            similarity of total ink amount
    center          similarity of center of mass
    persistence     current assignment strength for that label

During CALIBRATION, labels are known and reward is +1 / -1, so the operator
learns which support terms deserve more weight.

During TESTING, the operator is frozen and classification is performed only
from the image.

Dependencies:
    numpy

MNIST is downloaded automatically from the CVDF/Google mirror if needed.

Example:
    python3 relax_mnist.py
    python3 relax_mnist.py --prototype-count 10000 --calibrate-count 10000
    python3 relax_mnist.py --test-limit 2000
"""

from __future__ import annotations

import argparse
import gzip
import math
import struct
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np


BASE_URL = "https://storage.googleapis.com/cvdf-datasets/mnist/"
FILES = {
    "train_images": "train-images-idx3-ubyte.gz",
    "train_labels": "train-labels-idx1-ubyte.gz",
    "test_images": "t10k-images-idx3-ubyte.gz",
    "test_labels": "t10k-labels-idx1-ubyte.gz",
}


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def download_if_missing(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in FILES.values():
        path = data_dir / name
        if path.exists():
            continue
        url = BASE_URL + name
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, path)


def load_images(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as f:
        magic, n, rows, cols = struct.unpack(">IIII", f.read(16))
        if magic != 2051:
            raise ValueError(f"Bad MNIST image magic: {magic}")
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return data.reshape(n, rows, cols).astype(np.float32) / 255.0


def load_labels(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as f:
        magic, n = struct.unpack(">II", f.read(8))
        if magic != 2049:
            raise ValueError(f"Bad MNIST label magic: {magic}")
        data = np.frombuffer(f.read(), dtype=np.uint8)
    if len(data) != n:
        raise ValueError("MNIST label length mismatch")
    return data


def cosine_rows(x: np.ndarray, prototypes: np.ndarray) -> np.ndarray:
    """
    x:          (D,)
    prototypes: (10,D)
    returns:    (10,)
    """
    xn = np.linalg.norm(x) + 1e-12
    pn = np.linalg.norm(prototypes, axis=1) + 1e-12
    return (prototypes @ x) / (pn * xn)


def block_features(images: np.ndarray) -> np.ndarray:
    """
    Downsample 28x28 -> 4x4 by averaging 7x7 blocks.
    """
    n = images.shape[0]
    return images.reshape(n, 4, 7, 4, 7).mean(axis=(2, 4))


def centers_of_mass(images: np.ndarray) -> np.ndarray:
    n = images.shape[0]
    yy, xx = np.mgrid[0:28, 0:28]
    mass = images.sum(axis=(1, 2)) + 1e-12
    cx = (images * xx).sum(axis=(1, 2)) / mass
    cy = (images * yy).sum(axis=(1, 2)) / mass
    return np.stack([cx / 27.0, cy / 27.0], axis=1).astype(np.float32)


@dataclass
class Operator:
    prototype: float = 0.40
    block_shape: float = 0.25
    mass: float = 0.10
    center: float = 0.10
    persistence: float = 0.15
    exploration: float = 0.00

    def normalized(self) -> Dict[str, float]:
        vals = {
            "prototype": max(self.prototype, 1e-6),
            "block_shape": max(self.block_shape, 1e-6),
            "mass": max(self.mass, 1e-6),
            "center": max(self.center, 1e-6),
            "persistence": max(self.persistence, 1e-6),
        }
        s = sum(vals.values())
        return {k: v / s for k, v in vals.items()}

    def assign(self, w: Dict[str, float]) -> None:
        self.prototype = w["prototype"]
        self.block_shape = w["block_shape"]
        self.mass = w["mass"]
        self.center = w["center"]
        self.persistence = w["persistence"]


class RelaxMNIST:
    def __init__(
        self,
        state_lr: float = 0.45,
        goal_lr: float = 0.08,
        operator_lr: float = 0.02,
        iterations: int = 4,
        seed: int = 7,
    ):
        self.state_lr = state_lr
        self.goal_lr = goal_lr
        self.operator_lr = operator_lr
        self.iterations = iterations
        self.rng = np.random.default_rng(seed)

        # State assignment over labels. These are strengths, not required
        # to be interpreted as probabilities.
        self.state = np.ones(10, dtype=np.float64) / 10.0

        # Hierarchical goal strengths:
        # Long: classify correctly
        # Medium: shape / geometry
        # Short: classify current image
        self.goal_strengths = {
            "long_accuracy": 1.0,
            "medium_shape": 0.8,
            "medium_geometry": 0.7,
            "short_current": 1.0,
        }

        self.operator = Operator()

        # Diagnostics / "guts" history
        self.operator_history = []
        self.goal_history = []
        self.calibration_accuracy_history = []
        self.sample_trace = []

        self.prototypes = None
        self.block_prototypes = None
        self.mass_prototypes = None
        self.center_prototypes = None

    def fit_prototypes(self, images: np.ndarray, labels: np.ndarray) -> None:
        flat = images.reshape(len(images), -1)
        blocks = block_features(images).reshape(len(images), -1)
        masses = images.sum(axis=(1, 2)) / (28.0 * 28.0)
        centers = centers_of_mass(images)

        self.prototypes = np.zeros((10, 784), dtype=np.float32)
        self.block_prototypes = np.zeros((10, 16), dtype=np.float32)
        self.mass_prototypes = np.zeros(10, dtype=np.float32)
        self.center_prototypes = np.zeros((10, 2), dtype=np.float32)

        for digit in range(10):
            mask = labels == digit
            if not np.any(mask):
                raise ValueError(f"No prototype samples for digit {digit}")
            self.prototypes[digit] = flat[mask].mean(axis=0)
            self.block_prototypes[digit] = blocks[mask].mean(axis=0)
            self.mass_prototypes[digit] = masses[mask].mean()
            self.center_prototypes[digit] = centers[mask].mean(axis=0)

    def support_components(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        flat = image.reshape(-1)
        block = block_features(image[None])[0].reshape(-1)
        mass = float(image.sum() / (28.0 * 28.0))
        center = centers_of_mass(image[None])[0]

        proto = cosine_rows(flat, self.prototypes)
        block_sim = cosine_rows(block, self.block_prototypes)

        mass_scale = np.std(self.mass_prototypes) + 1e-3
        mass_sim = np.exp(-np.abs(self.mass_prototypes - mass) / mass_scale)

        center_dist = np.linalg.norm(self.center_prototypes - center[None, :], axis=1)
        center_sim = np.exp(-center_dist / 0.15)

        persistence = self.state.copy()

        return {
            "prototype": np.clip(proto, 0.0, 1.0),
            "block_shape": np.clip(block_sim, 0.0, 1.0),
            "mass": np.clip(mass_sim, 0.0, 1.0),
            "center": np.clip(center_sim, 0.0, 1.0),
            "persistence": np.clip(persistence, 0.0, 1.0),
        }

    def combined_support(self, components: Dict[str, np.ndarray]) -> np.ndarray:
        w = self.operator.normalized()

        # Goal hierarchy biases which families matter.
        shape_goal = self.goal_strengths["medium_shape"]
        geom_goal = self.goal_strengths["medium_geometry"]
        current_goal = self.goal_strengths["short_current"]

        support = (
            w["prototype"] * components["prototype"] * shape_goal
            + w["block_shape"] * components["block_shape"] * shape_goal
            + w["mass"] * components["mass"] * geom_goal
            + w["center"] * components["center"] * geom_goal
            + w["persistence"] * components["persistence"] * current_goal
        )

        if self.operator.exploration > 0:
            support += self.rng.normal(
                0.0, self.operator.exploration, size=10
            )

        return support

    def relax_state(self, support: np.ndarray) -> None:
        # Soft nonnegative support normalization.
        s = support - support.min()
        if s.sum() < 1e-12:
            target = np.ones(10) / 10.0
        else:
            target = s / s.sum()

        self.state = (1.0 - self.state_lr) * self.state + self.state_lr * target
        self.state = np.clip(self.state, 0.0, None)
        self.state /= self.state.sum() + 1e-12

    def classify(self, image: np.ndarray, reset_state=True):
        if reset_state:
            self.state[:] = 0.1

        components = None
        for _ in range(self.iterations):
            components = self.support_components(image)
            support = self.combined_support(components)
            self.relax_state(support)

        pred = int(np.argmax(self.state))
        return pred, components, self.state.copy()

    def relax_goals(self, correct: bool) -> None:
        reward01 = 1.0 if correct else 0.0

        # Fastest: current short-term goal.
        self.goal_strengths["short_current"] += self.goal_lr * (
            reward01 - self.goal_strengths["short_current"]
        )

        # Medium goals adapt more slowly.
        medium_lr = self.goal_lr * 0.4
        for key in ("medium_shape", "medium_geometry"):
            self.goal_strengths[key] += medium_lr * (
                reward01 - self.goal_strengths[key]
            )

        # Long-term goal changes very slowly.
        long_lr = self.goal_lr * 0.1
        self.goal_strengths["long_accuracy"] += long_lr * (
            reward01 - self.goal_strengths["long_accuracy"]
        )

    def relax_operator(
        self,
        components: Dict[str, np.ndarray],
        pred: int,
        truth: int,
    ) -> None:
        """
        Credit assignment over the operator.

        A component is rewarded if it scores the true label above competing
        labels, and penalized when it favors the wrong prediction.

        This is not gradient descent through a neural net. It is explicit
        operator relaxation.
        """
        current = self.operator.normalized()
        updated = dict(current)

        for name, values in components.items():
            truth_support = float(values[truth])
            competitor = float(np.max(np.delete(values, truth)))
            margin = np.clip(truth_support - competitor, -1.0, 1.0)

            updated[name] = max(
                1e-5,
                current[name] + self.operator_lr * margin
            )

        total = sum(updated.values())
        updated = {k: v / total for k, v in updated.items()}
        self.operator.assign(updated)

        if pred != truth:
            self.operator.exploration = min(
                0.08,
                self.operator.exploration + self.operator_lr * 0.02
            )
        else:
            self.operator.exploration = max(
                0.0,
                self.operator.exploration - self.operator_lr * 0.005
            )


    # ------------------------------------------------------------------
    # Diagnostics / ASCII introspection
    # ------------------------------------------------------------------

    @staticmethod
    def _ascii_bar(value: float, width: int = 36, max_value: float = 1.0) -> str:
        if max_value <= 0:
            max_value = 1.0
        frac = max(0.0, min(1.0, value / max_value))
        filled = int(round(frac * width))
        return "#" * filled + "." * (width - filled)

    @staticmethod
    def _sparkline(values, width: int = 60) -> str:
        """Unicode-free terminal sparkline using ASCII height characters."""
        if not values:
            return ""
        chars = " .:-=+*#%@"
        vals = list(values)

        if len(vals) > width:
            # Average into width buckets.
            edges = np.linspace(0, len(vals), width + 1, dtype=int)
            vals = [
                float(np.mean(vals[edges[i]:edges[i + 1]]))
                for i in range(width)
                if edges[i + 1] > edges[i]
            ]

        lo = min(vals)
        hi = max(vals)
        if abs(hi - lo) < 1e-12:
            return chars[len(chars) // 2] * len(vals)

        out = []
        for v in vals:
            q = (v - lo) / (hi - lo)
            idx = int(round(q * (len(chars) - 1)))
            out.append(chars[idx])
        return "".join(out)

    @staticmethod
    def _ascii_line_chart(series: Dict[str, list], width: int = 64, height: int = 14) -> str:
        """
        Very small multi-series ASCII line chart.
        One character per series:
          prototype=P, block_shape=B, mass=M, center=C, persistence=R
        """
        if not series:
            return "(no history)"

        char_for = {
            "prototype": "P",
            "block_shape": "B",
            "mass": "M",
            "center": "C",
            "persistence": "R",
            "accuracy": "A",
        }

        # Downsample all series to the same x positions.
        max_len = max(len(v) for v in series.values())
        if max_len == 0:
            return "(no history)"

        xcount = min(width, max_len)
        sample_idx = np.linspace(0, max_len - 1, xcount).astype(int)

        canvas = [[" " for _ in range(xcount)] for _ in range(height)]

        for name, vals in series.items():
            if not vals:
                continue
            ch = char_for.get(name, name[:1].upper())
            for xi, src_i in enumerate(sample_idx):
                src_i = min(src_i, len(vals) - 1)
                v = float(vals[src_i])
                y = int(round((1.0 - max(0.0, min(1.0, v))) * (height - 1)))
                old = canvas[y][xi]
                canvas[y][xi] = ch if old == " " or old == ch else "*"

        lines = []
        for row in range(height):
            yval = 1.0 - row / max(height - 1, 1)
            lines.append(f"{yval:4.2f} |" + "".join(canvas[row]))
        lines.append("     +" + "-" * xcount)
        lines.append("      early" + " " * max(1, xcount - 11) + "late")
        legend = "  ".join(
            f"{char_for.get(name, name[:1].upper())}={name}"
            for name in series
        )
        lines.append("      " + legend)
        return "\n".join(lines)

    def record_guts(self, running_accuracy: float | None = None) -> None:
        w = self.operator.normalized()
        self.operator_history.append(dict(w))
        self.goal_history.append(dict(self.goal_strengths))
        if running_accuracy is not None:
            self.calibration_accuracy_history.append(float(running_accuracy))

    def print_operator_guts(self) -> None:
        w = self.operator.normalized()
        print("\n" + "=" * 72)
        print("RELAX OPERATOR GUTS")
        print("=" * 72)

        print("\nCurrent evidence weighting:")
        mx = max(w.values())
        for name, value in sorted(w.items(), key=lambda kv: -kv[1]):
            bar = self._ascii_bar(value, width=40, max_value=mx)
            print(f"  {name:14s} {value:8.5f} |{bar}|")

        print(f"\n  exploration    {self.operator.exploration:.6f}")

        if self.operator_history:
            print("\nOperator-weight evolution:")
            series = {
                name: [h[name] for h in self.operator_history]
                for name in w
            }
            print(self._ascii_line_chart(series))

        print("\nInterpretation:")
        ranked = sorted(w.items(), key=lambda kv: -kv[1])
        top, second = ranked[0], ranked[1]
        print(
            f"  RELAX currently trusts '{top[0]}' most ({top[1]:.3f}), "
            f"followed by '{second[0]}' ({second[1]:.3f})."
        )
        weak = [name for name, value in ranked if value < 0.02]
        if weak:
            print("  Near-pruned terms: " + ", ".join(weak))
        else:
            print("  No support term is currently near-pruned.")

    def print_goal_guts(self) -> None:
        print("\n" + "=" * 72)
        print("GOAL-HIERARCHY GUTS")
        print("=" * 72)

        for name, value in self.goal_strengths.items():
            print(
                f"  {name:18s} {value:7.4f} "
                f"|{self._ascii_bar(value, width=40)}|"
            )

        if self.goal_history:
            print("\nGoal-strength evolution:")
            for name in self.goal_strengths:
                vals = [h[name] for h in self.goal_history]
                print(
                    f"  {name:18s} "
                    f"{self._sparkline(vals, 64)} "
                    f"[{min(vals):.3f}..{max(vals):.3f}]"
                )

    def print_confusion_guts(self, confusion: np.ndarray) -> None:
        print("\n" + "=" * 72)
        print("CONFUSION GUTS")
        print("=" * 72)

        row_totals = confusion.sum(axis=1)
        recalls = np.divide(
            np.diag(confusion),
            row_totals,
            out=np.zeros(10, dtype=float),
            where=row_totals != 0,
        )

        print("\nPer-digit recall:")
        for digit, recall in enumerate(recalls):
            print(
                f"  {digit}: {recall:7.2%} "
                f"|{self._ascii_bar(float(recall), width=40)}|"
            )

        mistakes = []
        for truth in range(10):
            for pred in range(10):
                if truth == pred:
                    continue
                n = int(confusion[truth, pred])
                if n:
                    mistakes.append((n, truth, pred))

        mistakes.sort(reverse=True)

        print("\nLargest directed confusions:")
        for n, truth, pred in mistakes[:15]:
            denom = max(1, int(row_totals[truth]))
            pct = n / denom
            print(
                f"  {truth} -> {pred}: {n:4d} "
                f"({pct:6.2%} of true {truth}s) "
                f"|{self._ascii_bar(pct, width=28, max_value=max(0.15, pct))}|"
            )

        print("\nASCII confusion heatmap")
        print("rows=true, columns=predicted")
        heat = " .:-=+*#%@"
        max_offdiag = max(
            [int(confusion[i, j]) for i in range(10) for j in range(10) if i != j]
            or [1]
        )

        print("      " + " ".join(str(i) for i in range(10)))
        for i in range(10):
            chars = []
            for j in range(10):
                if i == j:
                    chars.append("@")
                else:
                    q = confusion[i, j] / max_offdiag
                    idx = int(round(q * (len(heat) - 1)))
                    chars.append(heat[idx])
            print(f"  {i} | " + " ".join(chars))
        print("  @ on diagonal = correct classification; brighter off-diagonal = more errors")

    def print_sample_guts(
        self,
        image: np.ndarray,
        truth: int,
        pred: int,
        components: Dict[str, np.ndarray],
        state: np.ndarray,
    ) -> None:
        print("\n" + "=" * 72)
        print(f"SAMPLE GUTS  truth={truth}  prediction={pred}")
        print("=" * 72)

        # Render 28x28 MNIST digit as ASCII.
        chars = " .:-=+*#%@"
        print("\nInput digit:")
        for row in image:
            line = "".join(chars[int(round(float(v) * (len(chars) - 1)))] for v in row)
            print("  " + line)

        print("\nFinal label-assignment strengths:")
        mx = float(np.max(state)) or 1.0
        for d in np.argsort(state)[::-1]:
            print(
                f"  {int(d)}: {state[d]:.5f} "
                f"|{self._ascii_bar(float(state[d]), width=34, max_value=mx)}|"
            )

        print("\nSupport-component winners:")
        for name, values in components.items():
            order = np.argsort(values)[::-1][:3]
            top = "  ".join(f"{int(d)}={values[d]:.3f}" for d in order)
            print(f"  {name:14s}: {top}")

        w = self.operator.normalized()
        print("\nWeighted contribution to the chosen label:")
        total = 0.0
        for name, values in components.items():
            contribution = w[name] * float(values[pred])
            total += contribution
            print(
                f"  {name:14s}: weight={w[name]:.4f} "
                f"support={values[pred]:.4f} "
                f"product={contribution:.5f}"
            )
        print(f"  {'TOTAL':14s}: {total:.5f}")

    def print_calibration_guts(self) -> None:
        if not self.calibration_accuracy_history:
            return
        vals = self.calibration_accuracy_history
        print("\n" + "=" * 72)
        print("CALIBRATION LEARNING CURVE")
        print("=" * 72)
        print(
            f"  running accuracy: {self._sparkline(vals, 72)}\n"
            f"  start={vals[0]:.4f}  end={vals[-1]:.4f}  "
            f"min={min(vals):.4f}  max={max(vals):.4f}"
        )

    def calibrate(
        self,
        images: np.ndarray,
        labels: np.ndarray,
        report_every: int = 1000,
    ) -> float:
        correct = 0

        for i, (image, truth) in enumerate(zip(images, labels), start=1):
            pred, components, _ = self.classify(image, reset_state=True)
            is_correct = pred == int(truth)
            correct += int(is_correct)

            self.relax_goals(is_correct)
            self.relax_operator(
                components=components,
                pred=pred,
                truth=int(truth),
            )

            # Record internal state for later ASCII analysis.
            self.record_guts(correct / i)

            if report_every and i % report_every == 0:
                acc = correct / i
                print(
                    f"calibration {i:6d}: "
                    f"accuracy={acc:.4f} "
                    f"operator={self.operator.normalized()}"
                )
                print(
                    "  operator spark: "
                    + " | ".join(
                        f"{k[:4]} {self._ascii_bar(v, width=12)}"
                        for k, v in self.operator.normalized().items()
                    )
                )

        return correct / len(labels)

    def evaluate(
        self,
        images: np.ndarray,
        labels: np.ndarray,
    ) -> Tuple[float, np.ndarray]:
        confusion = np.zeros((10, 10), dtype=np.int64)
        correct = 0

        # Freeze operator/goals here.
        for image, truth in zip(images, labels):
            pred, _, _ = self.classify(image, reset_state=True)
            truth = int(truth)
            correct += int(pred == truth)
            confusion[truth, pred] += 1

        return correct / len(labels), confusion


def prototype_baseline(
    prototypes: np.ndarray,
    images: np.ndarray,
    labels: np.ndarray,
) -> float:
    correct = 0
    pnorm = np.linalg.norm(prototypes, axis=1) + 1e-12

    for image, truth in zip(images, labels):
        x = image.reshape(-1)
        sim = (prototypes @ x) / (
            pnorm * (np.linalg.norm(x) + 1e-12)
        )
        correct += int(np.argmax(sim) == int(truth))

    return correct / len(labels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="./mnist_data")
    ap.add_argument("--prototype-count", type=int, default=10000)
    ap.add_argument("--calibrate-count", type=int, default=5000)
    ap.add_argument("--test-limit", type=int, default=10000)
    ap.add_argument("--iterations", type=int, default=4)
    ap.add_argument("--state-lr", type=float, default=0.45)
    ap.add_argument("--goal-lr", type=float, default=0.08)
    ap.add_argument("--operator-lr", type=float, default=0.02)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument(
        "--guts-samples",
        type=int,
        default=3,
        help="Print detailed internal analysis for this many test samples",
    )
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    download_if_missing(data_dir)

    train_images = load_images(data_dir / FILES["train_images"])
    train_labels = load_labels(data_dir / FILES["train_labels"])
    test_images = load_images(data_dir / FILES["test_images"])
    test_labels = load_labels(data_dir / FILES["test_labels"])

    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(train_images))

    prototype_count = min(args.prototype_count, len(idx))
    calibrate_count = min(
        args.calibrate_count,
        len(idx) - prototype_count
    )

    proto_idx = idx[:prototype_count]
    cal_idx = idx[
        prototype_count:
        prototype_count + calibrate_count
    ]

    test_n = min(args.test_limit, len(test_images))
    test_images = test_images[:test_n]
    test_labels = test_labels[:test_n]

    engine = RelaxMNIST(
        state_lr=args.state_lr,
        goal_lr=args.goal_lr,
        operator_lr=args.operator_lr,
        iterations=args.iterations,
        seed=args.seed,
    )

    print("\nBuilding digit prototypes...")
    engine.fit_prototypes(
        train_images[proto_idx],
        train_labels[proto_idx]
    )

    print("\nBaseline: mean-image prototype cosine classifier")
    baseline = prototype_baseline(
        engine.prototypes,
        test_images,
        test_labels,
    )
    print(f"baseline test accuracy: {baseline:.4%}")

    if calibrate_count:
        print("\nRELAX calibration...")
        cal_acc = engine.calibrate(
            train_images[cal_idx],
            train_labels[cal_idx],
        )
        print(f"calibration accuracy: {cal_acc:.4%}")

    print("\nLearned operator weights:")
    for k, v in engine.operator.normalized().items():
        print(f"  {k:14s}: {v:.4f}")

    print("\nGoal strengths:")
    for k, v in engine.goal_strengths.items():
        print(f"  {k:18s}: {v:.4f}")

    engine.print_operator_guts()
    engine.print_goal_guts()
    engine.print_calibration_guts()

    print("\nFrozen RELAX test...")
    test_acc, confusion = engine.evaluate(
        test_images,
        test_labels,
    )

    print(f"RELAX test accuracy:    {test_acc:.4%}")
    print(f"baseline test accuracy: {baseline:.4%}")
    print(f"difference:             {(test_acc-baseline):+.4%}")

    print("\nConfusion matrix: rows=true, columns=predicted")
    print(confusion)

    engine.print_confusion_guts(confusion)

    n_guts = min(args.guts_samples, len(test_images))
    if n_guts > 0:
        print("\n" + "#" * 72)
        print(f"DETAILED TEST-SAMPLE GUTS ({n_guts} samples)")
        print("#" * 72)

        # Prefer a mixture of correct and incorrect examples.
        chosen_indices = []
        incorrect = []
        correct_examples = []

        for i, (image, truth) in enumerate(zip(test_images, test_labels)):
            pred, components, state = engine.classify(image, reset_state=True)
            rec = (i, int(truth), pred, components, state)
            if pred != int(truth):
                incorrect.append(rec)
            else:
                correct_examples.append(rec)
            if len(incorrect) >= n_guts and len(correct_examples) >= n_guts:
                break

        # Alternate mistakes and successes where possible.
        while len(chosen_indices) < n_guts and (incorrect or correct_examples):
            if incorrect:
                chosen_indices.append(incorrect.pop(0))
            if len(chosen_indices) < n_guts and correct_examples:
                chosen_indices.append(correct_examples.pop(0))

        for i, truth, pred, components, state in chosen_indices[:n_guts]:
            engine.print_sample_guts(
                test_images[i],
                truth,
                pred,
                components,
                state,
            )


if __name__ == "__main__":
    main()
