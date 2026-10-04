"""
VirtualCell — The Minimal Living Unit Containing the Entire Theory

Tripartite Anatomy:
  1. Trititarian skeleton — Mother Nature's Comb of soft-labelled nodes (LIGHT)
  2. 2.5-itarian membrane — continuous state variables, the "ish" (THE BOUNDARY)
  3. Bititarian empirical skin — binary sensors, actuators, deep models (DARK)

The cell executes at each discrete time step:
  (i)   Base-translation cycles that open every informational closure
  (ii)  Tritwise EM update implementing E = D × U
  (iii) Projection of soft labels onto continuous fluxes and binary controls
  (iv)  Physical evolution of waste streams under solar concentration

Because the Comb never permits true closure, waste remains a substrate
rather than a terminal sink. Light-side and dark-side processes cohabit
the same material remainder.
"""

import numpy as np
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field

from .membrane import Ish, Membrane


@dataclass
class VirtualCell:
    """
    The Virtual Cell — models the entire HRL2026 theory in a single unit.

    Skeleton (light): Trititarian relaxation web — readable, communicative
    Membrane (ish): Five-fingered comb — entropy that MUST NOT leave
    Skin (dark): Bititarian deep models — crystalline, impenetrable, useful

    Cell-of-cells nesting: children contain the same tripartite structure
    ad nauseam, ad infinitum.
    """

    num_nodes: int = 1
    skeleton: np.ndarray = field(default=None)  # Soft trit distributions [N, 3]
    membrane: Membrane = field(default=None)
    dark_skin: Any = None  # Opaque handle to binary-world models (PyTorch, etc.)
    children: List['VirtualCell'] = field(default_factory=list)
    iteration: int = 0

    def __post_init__(self):
        if self.skeleton is None:
            # Initialize uniform soft trits: {p(-1), p(0), p(+1)} = {1/3, 1/3, 1/3}
            self.skeleton = np.ones((self.num_nodes, 3)) / 3.0
        if self.membrane is None:
            self.membrane = Membrane(alpha=0.5, beta=0.5)

    def tritwise_em_step(self, alpha: Optional[float] = None, beta: Optional[float] = None) -> Dict[str, float]:
        """
        E = D × U dynamics with the ish as the wetland glue.

        Implements:
            p(t+1) = (1 - α) p(t) + α μ, followed by renormalisation

        Simultaneously:
          - Calcifies (pulls toward global mean)
          - Softens (preserves local entropy via the ish)
        """
        if alpha is None:
            alpha = self.membrane.alpha
        if beta is None:
            beta = self.membrane.beta

        # Global mean soft trit
        global_mean = np.mean(self.skeleton, axis=0)

        metrics = {"calcification": 0.0, "softening": 0.0, "ish_entropy": 0.0}

        for i in range(self.num_nodes):
            p = self.skeleton[i].copy()

            # Calcification toward global mean
            calcified = (1 - alpha) * p + alpha * global_mean

            # Local diversity (Shannon entropy over trinary)
            D = -np.sum(p * np.log(p + 1e-12)) / np.log(3.0)

            # Local unity with global mean
            U = np.dot(p, global_mean)

            # The ish step — five-fingered comb mediation
            ish_val = self.membrane.ish.step(D, U)

            # Apply ish softening perturbation
            softened = calcified * (1 - ish_val) + p * ish_val
            renormalized = softened / (np.sum(softened) + 1e-12)

            self.skeleton[i] = renormalized

            metrics["calcification"] += np.linalg.norm(renormalized - p)
            metrics["softening"] += ish_val

        metrics["calcification"] /= self.num_nodes
        metrics["softening"] /= self.num_nodes
        metrics["ish_entropy"] = self.membrane.ish.entropy

        # Update membrane calcification parameter
        local_diversity_avg = np.mean([
            -np.sum(p * np.log(p + 1e-12)) / np.log(3.0) for p in self.skeleton
        ])
        self.membrane.alpha = beta * self.membrane.alpha + (1 - beta) * (1 - local_diversity_avg)

        self.iteration += 1
        return metrics

    def translate_base(self, from_base: str, to_base: str) -> np.ndarray:
        """
        Continuous digit rewrite: trinary ↔ binary ↔ unary ↔ ...

        Because the rewrite is always available, no finite truncation
        of the hierarchy is informationally closed. Entropy may be exported
        from any finite subsystem while global balance holds.
        """
        return self.membrane.translate_base(self.skeleton, from_base, to_base)

    def ish_step(self) -> float:
        """
        The entropy that MAY NOT / MUST NOT / CANNOT leave the system.

        This is the ground of being, the I AM I AM terminating condition.
        """
        # Observable categorical entropy; no undocumented membrane dynamics.
        self.membrane.ish.entropy = float(np.mean([
            self.membrane.ish.compute_entropy(row) for row in self.skeleton
        ]))
        return self.membrane.ish.entropy

    def check_terminating_condition(self, epsilon: float = 1e-10) -> bool:
        """I AM I AM terminating condition of the uncountably infinite universe."""
        return self.membrane.ish.check_terminating(epsilon)

    def spawn_child(self, num_nodes: int = 1) -> 'VirtualCell':
        """Cell-of-cells: spawn a nested virtual cell (ad nauseam)."""
        child = VirtualCell(num_nodes=num_nodes)
        self.children.append(child)
        return child

    def project_to_binary_skin(self) -> np.ndarray:
        """
        Projection of soft labels onto binary controls.

        The bititarian empirical skin — where dark crystalline models
        (deep learning, supervised/unsupervised/semi-supervised) interface.
        """
        # Argmax over trinary → binary decision
        binary_projection = np.argmax(self.skeleton, axis=1)
        # The middle state (ish) maps to uncertainty
        binary_projection = np.where(
            np.max(self.skeleton, axis=1) < 0.5,
            -2,  # uncertain: distinct from the certain negative category -1
            binary_projection - 1  # -1, 0, +1 → map 0,1,2 → -1,0,1
        )
        return binary_projection

    def integrate_dark_model(self, dark_output: np.ndarray, coupling: float = 0.3):
        """
        Integrate output from a dark crystalline model (PyTorch, TensorFlow, etc.).

        The membrane decides permeability. Deep model weights barely pass;
        predictions and support flow more easily.
        """
        if dark_output.shape != (self.num_nodes, 3):
            # Assume binary output, expand with ish ambiguity
            expanded = np.zeros((self.num_nodes, 3))
            for i, label in enumerate(dark_output):
                if label == 0:
                    expanded[i] = [0.8, 0.1, 0.1]  # hard negative
                elif label == 1:
                    expanded[i] = [0.1, 0.8, 0.1]  # ish
                else:
                    expanded[i] = [0.1, 0.1, 0.8]  # hard positive
            dark_output = expanded

        # Membrane permeability gates the integration
        perm = self.membrane.permeability("weights")
        self.skeleton = (1 - coupling * perm) * self.skeleton + coupling * perm * dark_output
        self.skeleton /= np.sum(self.skeleton, axis=1, keepdims=True) + 1e-12

    def step(self, alpha: Optional[float] = None, beta: Optional[float] = None) -> Dict[str, Any]:
        """
        Full virtual cell timestep:
          1. Tritwise EM (calcify + soften via ish)
          2. Ish entropy step
          3. Check for terminating condition
          4. Recurse into children (cell-of-cells)
        """
        metrics = self.tritwise_em_step(alpha, beta)
        entropy = self.ish_step()
        is_term = self.check_terminating_condition()

        child_metrics = []
        for child in self.children:
            child_metrics.append(child.step(alpha, beta))

        return {
            "iteration": self.iteration,
            "metrics": metrics,
            "ish_entropy": entropy,
            "is_terminating": is_term,
            "num_children": len(self.children),
            "child_metrics": child_metrics if child_metrics else None,
        }

    def __repr__(self) -> str:
        ish_state = "TERMINATING" if self.membrane.ish.is_terminating else f"ish={self.membrane.ish.value:.3f}"
        return f"VirtualCell(N={self.num_nodes}, iter={self.iteration}, {ish_state}, children={len(self.children)})"