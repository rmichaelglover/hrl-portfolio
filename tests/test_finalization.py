import numpy as np
import pytest

from hrl import RelaxationLabeler, MutualBestLabeler, FinalizationPolicy


def constant_support(scores):
    scores = np.asarray(scores, dtype=float)
    n, labels = scores.shape
    return np.broadcast_to(scores[:, :, None, None]/n, (n, labels, n, labels)).copy()


def delayed_swap():
    """Two early reciprocal winners swap after a weak driver gains strength."""
    score = np.zeros((4, 4))
    score[0, 0] = score[2, 2] = 1.1
    score[0, 2] = score[2, 0] = .05
    score[1, 1] = score[3, 3] = 1.
    c = constant_support(score)
    c[0, 0, 1, 1] -= 1.
    c[2, 2, 1, 1] -= 1.
    c[0, 2, 1, 1] += 1.3
    c[2, 0, 1, 1] += 1.3
    prior = np.full((4, 4), .1)
    prior[0] = [.7, .1, .1, .1]
    prior[1] = [.499, .001, .25, .25]
    prior[2] = [.1, .1, .7, .1]
    prior[3] = [.05, .05, .05, .85]
    return c, prior


@pytest.mark.parametrize("noise", [False, True])
def test_off_matches_reference_entire_trajectory(noise):
    rng = np.random.default_rng(11)
    c = rng.uniform(-.6, 1, (5, 3, 5, 3))
    prior = rng.uniform(.1, 1, (5, 3))
    args = dict(noise=noise, prior_strength=.35, max_iterations=12, tol=0, record_history=True)
    a = RelaxationLabeler(c, prior, **args).run()
    b = MutualBestLabeler(c, prior, one_to_one=True, policy=FinalizationPolicy(mode="off"), **args).run()
    np.testing.assert_allclose(a.history, b.history, atol=2e-14, rtol=2e-14)
    assert not b.finalized.any()


def test_three_fresh_sweeps_soft_lock_and_not_false_numerical_convergence():
    c = constant_support(np.eye(3))
    prior = .7*np.eye(3)+.15*(1-np.eye(3))
    p = FinalizationPolicy(max_row_change=1)
    result = MutualBestLabeler(c, prior, one_to_one=True, policy=p, max_iterations=50, tol=1e-12).run()
    assert result.finalized.all()
    assert np.all(result.finalized_at == 3)
    assert result.stop_reason == "all_assignments_finalized"
    assert not result.converged
    assert result.full_update_residual > 1e-12
    assert np.all(result.strengths > 0)
    assert np.all(result.confidence < 1)
    # Two sweeps cannot establish the configured three-sweep persistence.
    short = MutualBestLabeler(c, prior, one_to_one=True, policy=p, max_iterations=2, tol=0).run()
    assert not short.finalized.any()


@pytest.mark.parametrize("scores", [np.ones((2, 2)), [[1, 0], [1, 0]]])
def test_row_or_column_ties_never_finalize(scores):
    p = FinalizationPolicy(min_strength=0, min_strength_margin=0,
                           min_label_support_margin=0, min_object_support_margin=0, max_row_change=1)
    result = MutualBestLabeler(constant_support(scores), one_to_one=True, policy=p, max_iterations=8, tol=0).run()
    assert not result.finalized.any()


def test_column_competition_uses_raw_support_not_row_minmax():
    p = FinalizationPolicy(mode="permanent", min_strength=.1, min_strength_margin=0,
                           min_label_support_margin=0, min_object_support_margin=0, max_row_change=1)
    result = MutualBestLabeler(constant_support([[2, 1], [100, 99]]), one_to_one=True,
                               policy=p, max_iterations=4, tol=0).run()
    assert not result.finalized[0]
    assert result.finalized[1]


def test_noise_is_never_reserved_or_finalized():
    c = -np.ones((3, 2, 3, 2))
    result = MutualBestLabeler(c, one_to_one=True, noise=True, max_iterations=20).run()
    assert not result.finalized.any()
    assert np.all(result.assignments == -1)


def test_delayed_support_change_reopens_wrong_locks():
    c, prior = delayed_swap()
    args = dict(one_to_one=True, max_iterations=100, prior_strength=0, tol=1e-9, record_history=True)
    reference = MutualBestLabeler(c, prior, policy=FinalizationPolicy(mode="off"), **args).run()
    permanent = MutualBestLabeler(c, prior, policy=FinalizationPolicy(mode="permanent"), **args).run()
    audited = MutualBestLabeler(c, prior, policy=FinalizationPolicy(), **args).run()
    assert reference.assignments.tolist() == [2, 1, 0, 3]
    assert permanent.assignments.tolist() != reference.assignments.tolist()
    assert audited.statistics["reopenings"] >= 2
    np.testing.assert_array_equal(audited.assignments, reference.assignments)
    assert any(a["reopened"] for a in audited.audit_log)


def test_cached_frozen_sources_equal_direct_support_and_are_still_present():
    c, prior = delayed_swap()
    model = MutualBestLabeler(c, prior, one_to_one=True, max_iterations=100, prior_strength=0)
    model.run()
    direct = np.einsum('iajb,jb->ia', c, model.strength[:, :model.n_labels])
    np.testing.assert_allclose(model._raw(all_rows=True), direct, atol=2e-14)
    assert np.any(model._fixed)


def test_frozen_noise_and_active_support_cache_are_exact():
    score=np.eye(3)
    c=constant_support(score)
    prior=.7*np.eye(3)+.15*(1-np.eye(3))
    model=MutualBestLabeler(c,prior,one_to_one=True,noise=True,noise_gain=.01,
                          policy=FinalizationPolicy(max_row_change=1),max_iterations=10)
    result=model.run()
    assert result.finalized.all()
    # Reopen one row to exercise a mixed active/frozen contraction with noise.
    model.finalized[0]=False
    model._rebuild()
    real=model.strength[:,:3]
    direct=np.einsum('iajb,jb->ia',c,real)
    noise=np.einsum('iajb,jb->i',1-c,real)*(.01/3)
    expected=np.column_stack([direct,noise])
    np.testing.assert_allclose(model._raw(),expected[[0]],atol=2e-14)
    np.testing.assert_allclose(model._raw(all_rows=True),expected,atol=2e-14)


def test_reserved_labels_only_finalize_once_and_ambiguous_tail_stops_honestly():
    c=constant_support([[5,0],[4,0],[0,5]])
    p=FinalizationPolicy(mode="permanent",max_row_change=1)
    result=MutualBestLabeler(c,one_to_one=True,policy=p,max_iterations=100,tol=1e-7).run()
    assert not result.finalized[1]
    assert result.finalized.sum()==2
    assert len(set(result.assignments[result.finalized]))==2
    assert result.stop_reason=="active_fixed_point_with_finalized_assignments"
    assert not result.converged


def test_aggressive_preset_keeps_three_observations_and_rejects_ties():
    p=FinalizationPolicy.aggressive()
    assert p.patience==3 and p.mode=="audited"
    result=MutualBestLabeler(constant_support(np.ones((3,3))),one_to_one=True,policy=p,max_iterations=4,tol=0).run()
    assert not result.finalized.any()


def test_input_snapshot_and_explicit_correspondence_contract():
    c = constant_support(np.eye(2)); saved = c.copy()
    model = MutualBestLabeler(c, one_to_one=True)
    c.fill(900)
    np.testing.assert_array_equal(model.compatibility, saved)
    with pytest.raises(ValueError): MutualBestLabeler(saved, one_to_one=False)
    with pytest.raises(ValueError): FinalizationPolicy(patience=0)
    with pytest.raises(ValueError): FinalizationPolicy(min_strength=np.nan)
    with pytest.raises(RuntimeError): model.step()
    model.run()
    with pytest.raises(RuntimeError): model.run()
