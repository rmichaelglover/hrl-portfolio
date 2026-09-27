"""
GRRLE / HyperObject — Strong Reference Implementation
=====================================================
Action-governed, multi-scale recursive relaxation labeling
with object↔label duality, cross-scale support, and robustness diagnostics.

Design goals
------------
- ActionFunctional sits above Compatibility (the inversion you wanted)
- Finite but arbitrarily extendable recursive depth
- Promote / Decompose operators for object↔label duality
- State- and context-dependent CompatibilitySuperFn
- Cross-scale consistency terms
- Strength as genuine persistence under perturbation + scale change
- Observable stability under depth increase (computational infinity)
- Clean, extensible architecture suitable for further research

This is intentionally more than a toy.  It is meant to be a solid
starting point for the stronger versions you have built over the years.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple
from enum import Enum, auto
import logging
from copy import deepcopy

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("grrle")


# ---------------------------------------------------------------------------
# Core data structures
# ---------------------------------------------------------------------------

class Role(Enum):
    OBJECT = auto()
    LABEL  = auto()


@dataclass
class Node:
    """A node that can act as object or label depending on recursive context."""
    uid: int
    depth: int
    tau: np.ndarray                     # state in [-1, 1]^L
    role: Role = Role.OBJECT
    parent_uid: Optional[int] = None
    children_uids: List[int] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)

    @property
    def n_labels(self) -> int:
        return len(self.tau)

    def copy(self) -> "Node":
        return Node(
            uid=self.uid,
            depth=self.depth,
            tau=self.tau.copy(),
            role=self.role,
            parent_uid=self.parent_uid,
            children_uids=list(self.children_uids),
            meta=dict(self.meta),
        )


# ---------------------------------------------------------------------------
# Compatibility Super-Function (context-aware)
# ---------------------------------------------------------------------------

class CompatibilitySuperFn:
    """
    C(n_i, a, n_j, b | context) → real

    Default implementation is deliberately richer than the earlier toy:
    - label agreement
    - depth / scale proximity
    - state magnitude (confidence) modulation
    - mild repulsive term for over-crowding the same label
    - optional user-supplied extra term
    """

    def __init__(
        self,
        agreement: float = 1.0,
        depth_scale: float = 0.35,
        confidence_mod: float = 0.25,
        repulsion: float = 0.15,
        extra: Optional[Callable] = None,
    ):
        self.agreement = agreement
        self.depth_scale = depth_scale
        self.confidence_mod = confidence_mod
        self.repulsion = repulsion
        self.extra = extra

    def __call__(
        self,
        ni: Node,
        a: int,
        nj: Node,
        b: int,
        tree: Optional["RelaxSuperTree"] = None,
    ) -> float:
        # 1. Base agreement
        score = self.agreement if a == b else -0.45 * self.agreement

        # 2. Scale proximity (prefer nearby depths)
        dd = abs(ni.depth - nj.depth)
        score += self.depth_scale * np.exp(-0.6 * dd)

        # 3. Confidence modulation (stronger influence when both |τ| are large)
        conf = abs(ni.tau[a]) * abs(nj.tau[b])
        score += self.confidence_mod * (2.0 * conf - 1.0)

        # 4. Soft repulsion if many nodes already strongly claim the same label
        if tree is not None and a == b:
            crowd = sum(1 for n in tree.nodes if n.uid != ni.uid and n.tau[a] > 0.6)
            score -= self.repulsion * np.log1p(crowd)

        # 5. Optional user extension
        if self.extra is not None:
            score += self.extra(ni, a, nj, b, tree)

        return float(score)


# ---------------------------------------------------------------------------
# Action Functional (the governing object)
# ---------------------------------------------------------------------------

class ActionFunctional:
    """
    Discrete action over the current finite tree.

    A ≈ Σ ½ m ||Δτ||²  -  S_total

    where S_total = within-scale support + cross-scale support.

    Stationarity of A drives the relaxation.
    """

    def __init__(
        self,
        compat: CompatibilitySuperFn,
        mass: float = 1.0,
        cross_scale_weight: float = 0.55,
        within_scale_weight: float = 1.0,
    ):
        self.compat = compat
        self.mass = mass
        self.w_cross = cross_scale_weight
        self.w_within = within_scale_weight

    def local_support(self, node: Node, tree: "RelaxSuperTree") -> np.ndarray:
        Q = np.zeros(node.n_labels, dtype=float)
        for other in tree.nodes:
            if other.uid == node.uid:
                continue
            for a in range(node.n_labels):
                for b in range(other.n_labels):
                    c = self.compat(node, a, other, b, tree)
                    Q[a] += c * other.tau[b]
        return Q

    def cross_scale_support(self, node: Node, tree: "RelaxSuperTree") -> np.ndarray:
        """Support coming from parent and children (object↔label duality)."""
        Q = np.zeros(node.n_labels, dtype=float)

        # From parent (top-down constraint)
        if node.parent_uid is not None:
            parent = tree.by_uid.get(node.parent_uid)
            if parent is not None:
                for a in range(node.n_labels):
                    for b in range(parent.n_labels):
                        # Parent acting as higher-level object
                        c = self.compat(node, a, parent, b, tree)
                        Q[a] += 0.7 * c * parent.tau[b]

        # From children (bottom-up constitution)
        for cuid in node.children_uids:
            child = tree.by_uid.get(cuid)
            if child is None:
                continue
            for a in range(node.n_labels):
                for b in range(child.n_labels):
                    c = self.compat(node, a, child, b, tree)
                    Q[a] += 0.5 * c * child.tau[b]

        return Q

    def total_support(self, node: Node, tree: "RelaxSuperTree") -> np.ndarray:
        return (
            self.w_within * self.local_support(node, tree)
            + self.w_cross * self.cross_scale_support(node, tree)
        )

    def tree_support_scalar(self, tree: "RelaxSuperTree") -> float:
        """Scalar potential used inside the action."""
        total = 0.0
        for n in tree.nodes:
            Q = self.total_support(n, tree)
            total += float(np.dot(Q, n.tau))
        return total

    def action_value(self, tree: "RelaxSuperTree", prev_taus: Optional[Dict[int, np.ndarray]] = None) -> float:
        """Approximate discrete action."""
        kinetic = 0.0
        if prev_taus is not None:
            for n in tree.nodes:
                if n.uid in prev_taus:
                    dtau = n.tau - prev_taus[n.uid]
                    kinetic += 0.5 * self.mass * float(np.dot(dtau, dtau))
        potential = -self.tree_support_scalar(tree)
        return kinetic + potential

    def gradient(self, node: Node, tree: "RelaxSuperTree") -> np.ndarray:
        """∇_τ of the potential part (drives the dynamics)."""
        return self.total_support(node, tree)


# ---------------------------------------------------------------------------
# Hierarchical Tree with Promote / Decompose
# ---------------------------------------------------------------------------

class RelaxSuperTree:
    def __init__(
        self,
        depth_range: Sequence[int],
        n_labels: int = 4,
        nodes_per_depth: int = 3,
        compat: Optional[CompatibilitySuperFn] = None,
        action: Optional[ActionFunctional] = None,
        seed: int = 42,
    ):
        self.rng = np.random.default_rng(seed)
        self.n_labels = n_labels
        self.nodes: List[Node] = []
        self.by_uid: Dict[int, Node] = {}
        self.compat = compat or CompatibilitySuperFn()
        self.action = action or ActionFunctional(self.compat)
        self._uid_counter = 0

        self._build_initial_hierarchy(depth_range, nodes_per_depth)

    def _next_uid(self) -> int:
        uid = self._uid_counter
        self._uid_counter += 1
        return uid

    def _build_initial_hierarchy(self, depth_range: Sequence[int], nodes_per_depth: int):
        """Create a simple parent–child hierarchy across depths."""
        depths = sorted(depth_range)
        depth_to_nodes: Dict[int, List[Node]] = {d: [] for d in depths}

        for d in depths:
            for _ in range(nodes_per_depth):
                tau = self.rng.uniform(-0.4, 0.4, self.n_labels)
                node = Node(uid=self._next_uid(), depth=d, tau=tau, role=Role.OBJECT)
                self.nodes.append(node)
                self.by_uid[node.uid] = node
                depth_to_nodes[d].append(node)

        # Wire parent–child relations (nearest higher depth becomes parent)
        for i, d in enumerate(depths[:-1]):
            parents = depth_to_nodes[depths[i + 1]]
            children = depth_to_nodes[d]
            for idx, child in enumerate(children):
                parent = parents[idx % len(parents)]
                child.parent_uid = parent.uid
                parent.children_uids.append(child.uid)
                # At the boundary the child can also be viewed as a label
                child.role = Role.LABEL

        log.info(f"Built tree: {len(self.nodes)} nodes, depths {depths[0]}…{depths[-1]}")

    # ----- Promote / Decompose (object↔label duality) -----

    def promote(self, node: Node) -> Node:
        """Turn a resolved (object, label) pair into a higher-level object."""
        new_tau = node.tau.copy()
        # Simple aggregation: slightly sharpen
        new_tau = np.tanh(1.4 * new_tau)
        new_node = Node(
            uid=self._next_uid(),
            depth=node.depth + 1,
            tau=new_tau,
            role=Role.OBJECT,
            meta={"promoted_from": node.uid},
        )
        self.nodes.append(new_node)
        self.by_uid[new_node.uid] = new_node
        node.parent_uid = new_node.uid
        new_node.children_uids.append(node.uid)
        return new_node

    def decompose(self, node: Node, n_children: int = 2) -> List[Node]:
        """Split a higher object into constituent lower-level nodes."""
        children = []
        for k in range(n_children):
            # Small random perturbation around the parent state
            noise = self.rng.normal(0, 0.15, self.n_labels)
            tau = np.clip(node.tau + noise, -1.0, 1.0)
            child = Node(
                uid=self._next_uid(),
                depth=node.depth - 1,
                tau=tau,
                role=Role.LABEL,
                parent_uid=node.uid,
                meta={"decomposed_from": node.uid},
            )
            self.nodes.append(child)
            self.by_uid[child.uid] = child
            node.children_uids.append(child.uid)
            children.append(child)
        return children

    # ----- Dynamics -----

    def relax(
        self,
        steps: int = 80,
        eta: float = 0.12,
        momentum: float = 0.82,
        proj: str = "clip",
        tol: float = 1e-5,
        log_every: int = 20,
    ) -> List[float]:
        """
        Projected momentum gradient ascent on total support
        (equivalently descent on the potential part of the action).
        """
        velocity = {n.uid: np.zeros_like(n.tau) for n in self.nodes}
        action_history = []
        prev_taus = {n.uid: n.tau.copy() for n in self.nodes}

        for step in range(steps):
            grads = {}
            for n in self.nodes:
                grads[n.uid] = self.action.gradient(n, self)

            max_change = 0.0
            for n in self.nodes:
                g = grads[n.uid]
                velocity[n.uid] = momentum * velocity[n.uid] + eta * g
                new_tau = n.tau + velocity[n.uid]

                if proj == "clip":
                    new_tau = np.clip(new_tau, -1.0, 1.0)
                elif proj == "tanh":
                    new_tau = np.tanh(new_tau)

                change = float(np.linalg.norm(new_tau - n.tau))
                max_change = max(max_change, change)
                n.tau = new_tau

            a_val = self.action.action_value(self, prev_taus)
            action_history.append(a_val)
            prev_taus = {n.uid: n.tau.copy() for n in self.nodes}

            if step % log_every == 0 or step == steps - 1:
                S = self.action.tree_support_scalar(self)
                log.info(f"step {step:3d} | action={a_val:9.4f} | support={S:9.4f} | Δ={max_change:.2e}")

            if max_change < tol:
                log.info(f"Converged at step {step}")
                break

        return action_history

    # ----- Strength / Robustness -----

    def strength(self, node: Node, eps: float = 3e-3, n_trials: int = 5) -> float:
        """
        Robustness = -average change in support under small state perturbations.
        Higher (less negative / closer to zero) ⇒ more robust.
        """
        base_Q = self.action.total_support(node, self)
        changes = []
        original = node.tau.copy()
        for _ in range(n_trials):
            node.tau = original + self.rng.normal(0, eps, size=original.shape)
            node.tau = np.clip(node.tau, -1.0, 1.0)
            new_Q = self.action.total_support(node, self)
            changes.append(np.linalg.norm(new_Q - base_Q))
        node.tau = original
        return -float(np.mean(changes))

    def hierarchy_strength(self) -> Dict[int, float]:
        return {n.uid: self.strength(n) for n in self.nodes}

    # ----- Observable stability under depth increase -----

    def observables(self) -> Dict[str, float]:
        """Simple macroscopic observables used for fixed-point checking."""
        all_tau = np.concatenate([n.tau for n in self.nodes])
        return {
            "mean_abs_tau": float(np.mean(np.abs(all_tau))),
            "std_tau": float(np.std(all_tau)),
            "total_support": self.action.tree_support_scalar(self),
            "n_nodes": float(len(self.nodes)),
        }

    def deepen_and_check(self, extra_depth: int = 1, relax_steps: int = 40) -> Dict:
        """
        Increase recursive horizon, re-relax, and measure how much
        observables moved.  This is the operational definition of
        'infinity' in the framework.
        """
        if not isinstance(extra_depth, int) or extra_depth < 0:
            raise ValueError("extra_depth must be a non-negative integer")
        if relax_steps < 0:
            raise ValueError("relax_steps must be non-negative")
        before = self.observables()
        # Promote a small frontier repeatedly.  Each pass adds a genuine
        # scale, so the parameter measures the depth increase it promises.
        top = [n for n in self.nodes if n.depth == max(n.depth for n in self.nodes)]
        for _ in range(extra_depth):
            top = [self.promote(n) for n in top[:2]]
        self.relax(steps=relax_steps, log_every=999)
        after = self.observables()
        delta = {k: after[k] - before[k] for k in before}
        return {"before": before, "after": after, "delta": delta}


# ---------------------------------------------------------------------------
# Convenience factory & demonstration
# ---------------------------------------------------------------------------

def build_strong_demo(seed: int = 42) -> RelaxSuperTree:
    compat = CompatibilitySuperFn(
        agreement=1.15,
        depth_scale=0.40,
        confidence_mod=0.30,
        repulsion=0.12,
    )
    action = ActionFunctional(
        compat,
        mass=1.0,
        cross_scale_weight=0.60,
        within_scale_weight=1.0,
    )
    tree = RelaxSuperTree(
        depth_range=range(-2, 3),
        n_labels=5,
        nodes_per_depth=4,
        compat=compat,
        action=action,
        seed=seed,
    )
    return tree


if __name__ == "__main__":
    print("=" * 60)
    print("GRRLE Strong Reference Implementation — Demo")
    print("=" * 60)

    tree = build_strong_demo()
    print(f"\nInitial observables: {tree.observables()}")

    history = tree.relax(steps=100, eta=0.10, momentum=0.85, log_every=25)

    print(f"\nFinal observables: {tree.observables()}")
    strengths = tree.hierarchy_strength()
    print(f"Mean strength: {np.mean(list(strengths.values())):.4f}")

    print("\n--- Deepening test (computational infinity) ---")
    result = tree.deepen_and_check(extra_depth=1, relax_steps=50)
    print(f"Observable deltas after deepening: {result['delta']}")
    print("\nDone.")
