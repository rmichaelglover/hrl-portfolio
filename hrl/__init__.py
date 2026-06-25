"""Hierarchical relaxation labeling — one engine, many worlds.

``RelaxationLabeler`` settles a field of objects onto labels by iteratively
reinforcing mutually-compatible assignments. With a respected prior and an
optional noise label, the same engine handles motion-capture marker
correspondence, chess-piece roles, and weighted-consensus model selection —
only the compatibility kernel and prior change.
"""
from .core import RelaxationLabeler, RelaxationResult
from .kernels import pairwise_distance_compatibility

__all__ = [
    "RelaxationLabeler",
    "RelaxationResult",
    "pairwise_distance_compatibility",
]

__version__ = "0.1.0"
