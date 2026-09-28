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

            if report_every and i % report_every == 0:
                acc = correct / i
                print(
                    f"calibration {i:6d}: "
                    f"accuracy={acc:.4f} "
                    f"operator={self.operator.normalized()}"
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


if __name__ == "__main__":
    main()
