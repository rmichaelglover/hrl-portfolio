import json
import math
import numpy as np
import pytest
from cypher_robot_mind.authorization import CommandGate, PresencePolicy, sign, permitted
from cypher_robot_mind.model import Attention, BeliefMap, KalmanTrack, center, plan, relax_scene
from cypher_robot_mind.voice import OfflineVoice


def test_bayesian_mapping_and_max_range():
    b=BeliefMap()
    b.scan([1.25,1.25],[1.],0.,1.,4.)
    assert b.occupancy[2,4]>.5
    assert b.occupancy[2,2]<.5
    assert b.occupancy[10,10]==.5
    b.scan([1.25,1.25],[4.],math.pi/2,1.,4.)
    assert np.max(b.occupancy[:,2])<=.5
    for _ in range(100):b.scan([1.25,1.25],[1.],0.,1.,4.)
    assert np.isfinite(b.occupancy).all()
    assert np.max(b.log_odds)<=5


def test_kalman_tracks_motion_and_covariance():
    k=KalmanTrack([0,0]); rng=np.random.default_rng(3)
    errors=[]
    for i in range(1,80):
        k.predict(.1); target=np.array([i*.1,i*.05]); measured=target+rng.normal(0,.1,2)
        k.correct(measured,.01); errors.append(np.linalg.norm(k.position-target))
        assert all(np.linalg.eigvalsh(p).min()>=-1e-12 for p in k.p)
    assert np.mean(errors[-30:])<.12
    assert np.linalg.norm(k.future()-np.array([8.9,4.45]))<.3
    before=k.p[:,0,0].copy();k.predict(2.);assert np.all(k.p[:,0,0]>before)


def test_hrl_hierarchy_and_unknown():
    b=BeliefMap(); scene=relax_scene(b,np.array([2.25,2.25]),np.array([8.25,8.25]))
    assert len(scene['regions'])==9
    assert len(scene['cells'])==25
    assert np.allclose(np.sum(scene['strengths'],axis=1),1)
    assert all(np.argmax(s)==3 for s in scene['strengths'])
    b.observations[:]=10;b.log_odds[:]=-4
    b.log_odds[5,5]=4
    changed=relax_scene(b,np.array([2.25,2.25]),np.array([8.25,8.25]))
    assert changed['strengths'][changed['cells'].index((5,5))][1]>.5
    assert changed['regions']!=scene['regions']


def test_planning_uses_beliefs_and_detours():
    b=BeliefMap();b.observations[:]=10;b.log_odds[:]=-4
    b.log_odds[1:14,8]=5
    route=plan(b,np.array([1.25,1.25]),np.array([8.25,8.25]))
    assert route[0]==(2,2) and route[-1]==(16,16)
    assert all(not (x==8 and 1<=y<14) for x,y in route)
    assert all(abs(a[0]-bb[0])+abs(a[1]-bb[1])==1 for a,bb in zip(route,route[1:]))
    hazard=center(route[5]); rerouted=plan(b,np.array([1.25,1.25]),np.array([8.25,8.25]),hazard)
    assert rerouted and all(np.linalg.norm(center(p)-hazard)>=.8 for p in rerouted[1:])


def test_attention_is_bounded_and_changes_with_surprise():
    a=Attention();quiet=a.update(0,4);active=a.update(1,4)
    assert active['active_regions']>quiet['active_regions']
    for _ in range(300):state=a.update(100,4)
    assert .25<=state['gain']<=1.5
    assert len(state['history'])==80
    assert all(0<=v<=1 for v in state['activity'])


def test_role_permissions_public_stop_and_admin_mission():
    for role in ['public','basic','admin']:
        assert permitted(role,'stop') and permitted(role,'shutdown')
    assert not permitted('public','wake')
    assert permitted('basic','wake') and permitted('basic','present')
    assert not permitted('basic','start') and not permitted('basic','reset')
    assert permitted('admin','start')
    assert not permitted('admin','invented')


def test_signed_commands_expire_reject_replay_and_tampering():
    secret='a'*64; gate=CommandGate(secret); message=sign(secret,'start',100.)
    assert gate.verify(message,101.)=='start'
    assert gate.verify(message,101.) is None
    assert CommandGate(secret).verify(message,106.) is None
    assert CommandGate('b'*64).verify(message,101.) is None
    obj=json.loads(message);obj['payload']['action']='reset'
    assert gate.verify(json.dumps(obj),101.) is None
    assert gate.verify('bad json',101.) is None


def test_presence_loss_cancels_task_sleep_then_hibernates():
    p=PresencePolicy(0)
    assert p.mode=='WAITING'
    p.apply('start',1);assert p.tick(29)=='RUNNING'
    assert p.tick(32)=='SLEEPING' and p.mission_until==0
    assert p.tick(931)=='SLEEPING'
    assert p.tick(932)=='HIBERNATING'
    p.apply('wake',933);assert p.mode=='WAITING' and p.mission_until==0
    p.apply('present',934);assert p.mode=='WAITING'
    p.apply('start',935);assert p.mode=='RUNNING'
    p.apply('stop',936);assert p.mode=='SLEEPING' and p.mission_until==0
    p.apply('shutdown',937);assert p.mode=='HIBERNATING'


def test_presence_renewal_does_not_extend_mission_authority():
    p=PresencePolicy(0);p.apply('start',1)
    for now in [25,50,75,90]:p.apply('present',now);p.tick(now)
    assert p.tick(92)=='WAITING' and p.mission_until==0


def test_offline_voice_rejects_silence():
    v=OfflineVoice()
    try:
        assert v.decode(bytes(32000),'blue seven red one')==(None,'')
        with pytest.raises(ValueError):v.decode(bytes(20),'blue seven red one')
    finally:v.close()


def test_spoken_challenge_matches_actual_decoded_words(tmp_path):
    import audioop
    import shutil
    import subprocess
    import wave
    if not shutil.which('espeak'):pytest.skip('Optional generated speech fixture requires espeak')
    wav=tmp_path/'voice.wav'
    subprocess.run(['espeak','-v','en-us','-s','130','-w',str(wav),'robot go one two three four'],check=True)
    with wave.open(str(wav)) as w:
        pcm=audioop.ratecv(w.readframes(w.getnframes()),2,1,w.getframerate(),16000,None)[0]
    v=OfflineVoice()
    try:
        assert v.decode(pcm,'one two three four','start')[0]=='start'
        assert v.decode(pcm,'one two three five','start')[0] is None
    finally:v.close()
