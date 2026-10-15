import numpy as np
import pytest
from hrl.reciprocal import relax_view, accept_reciprocal, audit_anchors


def test_no_relation_leaves_prior_unchanged_and_does_not_mutate():
    logits=np.array([[3.,0.,-2.],[0.,3.,-2.]])
    graph=np.eye(2); before=graph.copy()
    out=relax_view(logits,graph,graph)
    expected=np.exp(logits-logits.max(axis=1,keepdims=True));expected/=expected.sum(axis=1,keepdims=True)
    np.testing.assert_allclose(out.strengths,expected)
    np.testing.assert_array_equal(graph,before)
    assert out.converged


def test_mutual_match_unknown_ties_and_asymmetry():
    f=np.array([[.9,.05,.05],[.04,.91,.05],[.1,.1,.8]])
    r=np.array([[.9,.03,.02,.05],[.02,.9,.03,.05]])
    result=accept_reciprocal(f,r)
    assert result.labels.tolist()==[0,1,-1]
    r[1]=[.9,.02,.03,.05]
    assert accept_reciprocal(f,r).labels.tolist()==[0,-1,-1]
    assert accept_reciprocal([[.5,.5,0]],[[1,0],[1,0]],threshold=.4,margin=0).labels.tolist()==[-1]


def test_perturbation_disagreement_rejects():
    f=np.array([[.95,.05]]);r=np.array([[.95,.05]])
    bad=np.array([[.05,.95]])
    assert accept_reciprocal(f,r,perturbations=[(bad,r)]).labels[0]==-1


def test_shared_wrong_permutation_is_not_detected_by_agreement():
    f=np.array([[.01,.98,.01],[.98,.01,.01]])
    r=f.copy()
    result=accept_reciprocal(f,r)
    assert result.labels.tolist()==[1,0] # confidently wrong if truth is [0,1]
    records=audit_anchors(result,lambda i,j:i==j,previous={0:1},provenance='held-out')
    assert [r['status'] for r in records]==['rejected','rejected','revoked']


@pytest.mark.parametrize('bad',[[[np.nan,0]],[[np.inf,0]],[[-1,2]],[[.1,.1]]])
def test_invalid_strengths_rejected(bad):
    with pytest.raises(ValueError):accept_reciprocal(bad,[[.9,.1]])


def test_relational_support_changes_an_ambiguous_assignment():
    # Neighboring things ought to have neighboring (different) labels.
    graph=np.array([[0,1],[1,0]])
    out=relax_view([[5,0,-5],[.1,0,-5]],graph,graph,gain=4)
    assert out.strengths.argmax(axis=1).tolist()==[0,1]
    np.testing.assert_allclose(out.strengths.sum(axis=1),1)


def test_bad_graphs_and_controls():
    with pytest.raises(ValueError):relax_view([[1,0]],[[0]],[[np.nan]])
    with pytest.raises(ValueError):relax_view([[1,0]],[[0]],[[0]],damping=0)
    with pytest.raises(ValueError):accept_reciprocal([[.9,.1]],[[.8,.1,.1]])


def test_large_finite_graph_weights_normalize_without_overflow():
    graph=np.full((3,3),1e308)
    result=relax_view(np.zeros((3,4)),graph,graph)
    assert np.isfinite(result.strengths).all()
    np.testing.assert_allclose(result.strengths.sum(axis=1),1)


def test_abstention_never_becomes_an_anchor():
    result=accept_reciprocal([[.1,.9]],[[.9,.1]])
    assert audit_anchors(result,lambda i,j:True)==[]


def test_anchor_bias_is_bounded_reversible_and_does_not_modify_evidence():
    from hrl.reciprocal import anchor_logits
    f=np.zeros((2,3));r=f.copy()
    ledger=[{'thing':0,'word':1,'status':'provisional'}]
    pf,pr=anchor_logits(f,r,ledger,bonus=.5)
    assert pf[0,1]==.5 and pr[1,0]==.5
    assert np.all(f==0) and np.all(r==0)
    ledger.append({'thing':0,'word':1,'status':'revoked'})
    pf,pr=anchor_logits(f,r,ledger)
    np.testing.assert_array_equal(pf,f)
    with pytest.raises(ValueError):anchor_logits(f,r,[],bonus=1.1)
    with pytest.raises(ValueError):anchor_logits(f,r,[{'thing':0,'word':0,'status':'provisional'},{'thing':1,'word':0,'status':'provisional'}])
