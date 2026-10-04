"""
HRL2026 — Hierarchical Relaxation Labeling 2026

Virtual Cell Architecture: Trititarian relaxation labeling (light)
bridged to binary deep models (dark) via the five-fingered "ish" membrane.

Two worlds. One comb. Five fingers.

By Manny Glover
"""

from .membrane import Ish, Membrane
from .virtual_cell import VirtualCell

__version__ = "2026.0.1"
__author__ = "Manny Glover"

__all__ = ["Ish", "Membrane", "VirtualCell"]