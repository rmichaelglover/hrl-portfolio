"""MEGGERS: generic delimiter, delimited, fuzzy-boundary, and hierarchy behavior."""
import numpy as np

from hrl.meggers import delimiter_prior, lift_evidence, relax_delimitation


def test_clear_and_fuzzy_evidence_have_expected_trool_labels():
    evidence = np.array([1.0, -1.0, 0.0])
    result = relax_delimitation(evidence, np.zeros((3, 3)))

    assert result.labels == ["vtrue", "vfalse", "ish"]
    assert result.delimiter_score[0] > 0
    assert result.delimiter_score[1] < 0
    assert abs(result.delimiter_score[2]) < 1e-12


def test_compatible_neighbor_clarifies_a_fuzzy_boundary():
    evidence = np.array([1.0, 0.15])
    affinity = np.array([[0.0, 1.0], [1.0, 0.0]])

    result = relax_delimitation(evidence, affinity, prior_strength=0.1)

    assert result.labels == ["vtrue", "vtrue"]


def test_hierarchy_lift_is_geometry_agnostic():
    evidence = np.array([1.0, 0.8, -0.8, -1.0])
    result = relax_delimitation(evidence, np.zeros((4, 4)))

    lifted = lift_evidence(result, [{0, 1}, (2, 3)])

    assert lifted[0] > 0
    assert lifted[1] < 0
