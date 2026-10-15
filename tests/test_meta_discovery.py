from itertools import combinations
import numpy as np
import pytest
from hrl.meta_discovery import discover,features,relax_hypotheses


def sample(seed=4,n=3000):
    rng=np.random.default_rng(seed);x=rng.normal(size=(n,6));y=.15*x.sum(axis=1)+x[:,0]*x[:,3]+.8*x[:,1]*x[:,4]+.9*np.prod(x[:,[0,1,3,4]],axis=1)+rng.normal(0,.1,n)
    return x,y


def test_discovers_unannounced_pairs_and_promotes_quartic():
    x,y=sample();result=discover(x[:2000],y[:2000],x[2000:],y[2000:])
    assert set(result.selected_interactions)=={(0,3),(1,4),(0,1,3,4)}
    assert result.relaxation_iterations>0
    assert np.mean((result.predict(x)-y)**2)<.02


def test_hidden_quartic_is_an_explicit_hierarchical_blind_spot():
    rng=np.random.default_rng(52);x=rng.normal(size=(12000,6));y=np.prod(x[:,:4],axis=1)
    result=discover(x[:9000],y[:9000],x[9000:],y[9000:])
    assert (0,1,2,3) not in result.selected_interactions


def test_no_input_mutation_deterministic_and_finite():
    x,y=sample(n=1000);before=x.copy();a=discover(x[:700],y[:700],x[700:],y[700:]);b=discover(x[:700],y[:700],x[700:],y[700:])
    assert a.terms==b.terms and a.history==b.history
    np.testing.assert_array_equal(x,before)
    assert np.isfinite(a.predict(x)).all()


def test_additive_control_does_not_require_interactions():
    rng=np.random.default_rng(9);x=rng.normal(size=(4000,5));y=.2*x.sum(axis=1)
    result=discover(x[:3000],y[:3000],x[3000:],y[3000:])
    assert not result.selected_interactions
    np.testing.assert_allclose(result.predict(x),y,atol=1e-10)


def test_relaxation_is_bounded_and_no_relaxation_is_distinct():
    gains=[.3,.2];parents={(0,1):(),(0,1,2,3):((0,1),(2,3))}
    p,it=relax_hypotheses(gains,.01,parents,[(2,3)],temperature=.2)
    raw,_=relax_hypotheses(gains,.01,parents,[],temperature=.2,enabled=False)
    assert it>0 and np.all((p>=0)&(p<=1)) and p[1]>raw[1]


@pytest.mark.parametrize('bad',[np.nan,np.inf])
def test_invalid_inputs(bad):
    x,y=sample(n=30);x[0,0]=bad
    with pytest.raises(ValueError):discover(x[:20],y[:20],x[20:],y[20:])


def test_selection_loss_decreases_and_exact_gain_is_logged():
    x,y=sample();result=discover(x[:2000],y[:2000],x[2000:],y[2000:])
    for before,after in zip(result.history,result.history[1:]):
        assert after['validation_mse']<before['validation_mse']
        assert abs(before['validation_mse']-after['validation_mse']-before['gain'])<1e-8


def test_constant_target_and_equivalent_quartic_parentages():
    x=np.ones((100,4));y=np.full(100,3.)
    result=discover(x[:70],y[:70],x[70:],y[70:])
    assert not result.selected_interactions
    np.testing.assert_allclose(result.predict(x),y)
    rng=np.random.default_rng(41);v=rng.normal(size=(40,4))
    np.testing.assert_allclose((v[:,0]*v[:,1])*(v[:,2]*v[:,3]),(v[:,0]*v[:,2])*(v[:,1]*v[:,3]))
