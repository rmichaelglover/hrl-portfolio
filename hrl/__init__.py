"""Hierarchical relaxation labeling — one engine, many worlds.

``RelaxationLabeler`` settles a field of objects onto labels by iteratively
reinforcing mutually-compatible assignments. With a respected prior and an
optional noise label, the same engine handles motion-capture marker
correspondence, chess-piece roles, and weighted-consensus model selection —
only the compatibility kernel and prior change.
"""
from .core import RelaxationLabeler, RelaxationResult
from .kernels import pairwise_distance_compatibility
from .tracking import temporal_prior, track_sequence, synthetic_sequence
from .consensus import (
    relax_truth, agreement_to_compatibility, anchor_prior, truth_report,
    lexical_agreement, extract_claims, TRUTH_NAMES, VFALSE, ISH, VTRUE,
)
from .nli import NLIAgreement          # transformers/torch imported lazily on use
from .llm_judge import LLMAgreement, extract_claims_llm  # anthropic imported lazily

__all__ = [
    "RelaxationLabeler",
    "RelaxationResult",
    "pairwise_distance_compatibility",
    "temporal_prior",
    "track_sequence",
    "synthetic_sequence",
    "relax_truth",
    "agreement_to_compatibility",
    "anchor_prior",
    "truth_report",
    "lexical_agreement",
    "extract_claims",
    "NLIAgreement",
    "LLMAgreement",
    "extract_claims_llm",
    "TRUTH_NAMES",
    "VFALSE",
    "ISH",
    "VTRUE",
]

__version__ = "0.1.0"
