import numpy as np
import pytest
from hrl.recursive_grounding import RecursiveConfig, recursive_refine


def sample():
    rng=np.random.default_rng(81)
    latent=rng.normal(size=(5,3))
    things=tuple(latent[:,None]+rng.normal(0,.5,(5,5,3)) for _ in range(2))
    names=tuple(latent[:,None]+rng.normal(0,.5,(5,5,3)) for _ in range(2))
    valid_x=tuple(latent[:,None]+rng.normal(0,.5,(5,3,3)) for _ in range(2))
    valid_w=tuple(latent[:,None]+rng.normal(0,.5,(5,3,3)) for _ in range(2))
    return things,names,valid_x,valid_w


def test_inputs_not_mutated_and_repeatable():
    args=sample();copies=[[a.copy() for a in group] for group in args]
    a=recursive_refine(*args);b=recursive_refine(*args)
    assert a.history==b.history and a.selected_round==b.selected_round
    for x,y in zip(a.things,b.things):np.testing.assert_array_equal(x,y)
    for group,before in zip(args,copies):
        for x,y in zip(group,before):np.testing.assert_array_equal(x,y)


def test_finite_normalized_bounded_and_checkpoint_not_worse_than_initial():
    from hrl.recursive_grounding import infer
    result=recursive_refine(*sample(),config=RecursiveConfig(drift_cap=.2))
    assert result.selected_round<=24
    chosen=result.history[result.selected_round]
    assert chosen['validation_loss']<=result.history[0]['validation_loss']
    assert all(r['max_drift']<=.2+1e-10 for r in result.history[1:])
    for p in infer(result.things,result.names):
        assert np.isfinite(p).all();np.testing.assert_allclose(p.sum(axis=1),1)


def test_zero_rounds_and_no_cross_self_only():
    args=sample();result=recursive_refine(*args,config=RecursiveConfig(rounds=0))
    assert result.selected_round==0 and not result.coupled
    self_only=recursive_refine(*args,config=RecursiveConfig(cross_weight=0))
    assert not self_only.coupled
    assert self_only.history[-1]['identity_loss'] < self_only.history[0]['identity_loss']


def test_validation_does_not_change_proposal_path_without_early_stop():
    args=sample();config=RecursiveConfig(rounds=3,patience=20)
    a=recursive_refine(*args,config=config)
    vx=tuple(v+100 for v in args[2]);vw=tuple(v+100 for v in args[3])
    b=recursive_refine(args[0],args[1],vx,vw,config=config)
    assert [r['identity_loss'] for r in a.history]==[r['identity_loss'] for r in b.history]
    assert [r['accepted_relations'] for r in a.history]==[r['accepted_relations'] for r in b.history]


@pytest.mark.parametrize('config',[RecursiveConfig(rounds=-1),RecursiveConfig(damping=0),RecursiveConfig(self_weight=-1),RecursiveConfig(drift_cap=np.inf)])
def test_invalid_configuration(config):
    with pytest.raises(ValueError):recursive_refine(*sample(),config=config)


def test_transient_first_round_relations_do_not_feed_back():
    result=recursive_refine(*sample())
    assert result.history[1]['accepted_relations']==0
