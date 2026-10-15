"""GRRLE-inspired finite recurrent hierarchy for reciprocal representations.

Observation leaves -> thing/name representations -> reciprocal relations ->
bounded representation updates. No hidden correspondence labels enter fitting.
Validation observations select a checkpoint, never supply update gradients.
"""
from dataclasses import dataclass
import numpy as np
from .reciprocal import relax_view, accept_reciprocal


@dataclass
class RecursiveConfig:
    rounds: int = 24
    damping: float = .45
    cross_weight: float = .25
    self_weight: float = 1.
    drift_cap: float = .8
    patience: int = 4
    minimum_improvement: float = 1e-5
    gate: float = .4
    margin: float = .06
    select_validation: bool = True
    bounded: bool = True
    require_persistence: bool = True


@dataclass
class RecursiveResult:
    things: tuple
    names: tuple
    selected_round: int
    history: list
    stop_reason: str
    coupled: bool


def _observations(value, name):
    a = np.array(value, dtype=float, copy=True)
    if a.ndim != 3 or min(a.shape) < 1 or not np.isfinite(a).all():
        raise ValueError(f'{name} requires finite [entities, observations, dimensions]')
    return a


def relations(x):
    distance = np.sum((x[:, None] - x[None, :])**2, axis=2)
    graph = np.exp(-distance / 10.)
    np.fill_diagonal(graph, 0)
    return graph


def evidence(x, w, *, temperature=.65, unknown=-4.):
    if not np.isfinite(temperature) or temperature <= 0 or not np.isfinite(unknown):
        raise ValueError('invalid evidence parameters')
    distance = np.sum((x[:, None] - w[None, :])**2, axis=2)
    return np.column_stack((-distance / (2*temperature**2), np.full(len(x), unknown)))


def infer(things, names):
    """Two directions in separate sensor spaces; the final column is unknown."""
    x1, x2 = things
    w1, w2 = names
    forward = relax_view(evidence(x1, w1), relations(x1), relations(w1)).strengths
    reverse = relax_view(evidence(w2, x2), relations(w2), relations(x2)).strengths
    return forward, reverse


def _loss(xs, ws, vx, vw):
    # Compare coordinates to independent measurements of the SAME identities.
    # No thing-to-name correspondence labels are available to this objective.
    return float(np.mean([np.mean((x[:, None]-v)**2) for x,v in zip(xs,vx)])
                 + np.mean([np.mean((w[:, None]-v)**2) for w,v in zip(ws,vw)]))


def _proposal(current, origin, partner, weights, config):
    mass = weights.sum(axis=1, keepdims=True)
    numerator = config.self_weight*origin + config.cross_weight*(weights @ partner)
    denominator = config.self_weight + config.cross_weight*mass
    target = np.divide(numerator, denominator, out=origin.copy(), where=denominator > 0)
    candidate = current + config.damping*(target-current)
    if config.bounded:
        displacement = candidate-origin
        norm = np.linalg.norm(displacement, axis=1, keepdims=True)
        candidate = origin + displacement*np.minimum(1., config.drift_cap/np.maximum(norm, 1e-12))
    return candidate


def recursive_refine(thing_observations, name_observations,
                     validation_things, validation_names, *, config=None):
    """Return the best observation-validated representation checkpoint.

    All arguments are pairs of sensor-view arrays. Validation data affect only
    checkpoint selection and stopping, not proposal coordinates or pair gates.
    Input arrays are copied. The initial checkpoint is always eligible.
    Names/thing IDs retain their identity; no geometric or semantic truth claim
    follows from a smaller validation coordinate loss.
    """
    c = config or RecursiveConfig()
    if not isinstance(c.rounds, int) or c.rounds < 0 or not isinstance(c.patience, int) or c.patience < 1:
        raise ValueError('invalid recursion budget')
    if not 0 < c.damping <= 1 or not np.isfinite(c.cross_weight) or c.cross_weight < 0:
        raise ValueError('invalid damping or cross weight')
    if not np.isfinite(c.self_weight) or c.self_weight < 0 or not np.isfinite(c.drift_cap) or c.drift_cap <= 0:
        raise ValueError('invalid identity regularization or drift cap')
    if not np.isfinite(c.minimum_improvement) or c.minimum_improvement < 0:
        raise ValueError('invalid stopping tolerance')
    if not 0 <= c.gate <= 1 or not 0 <= c.margin <= 1:
        raise ValueError('invalid pairing gates')
    groups=[]
    for values, name in [(thing_observations,'things'),(name_observations,'names'),
                         (validation_things,'validation things'),(validation_names,'validation names')]:
        if len(values) != 2:
            raise ValueError('exactly two views required')
        groups.append(tuple(_observations(v,name) for v in values))
    tx,tw,vx,vw=groups
    n,m,d=tx[0].shape[0],tw[0].shape[0],tx[0].shape[2]
    for group,count in [(tx,n),(tw,m),(vx,n),(vw,m)]:
        if any(a.shape[0]!=count or a.shape[2]!=d for a in group):
            raise ValueError('entity counts and dimensions must agree across views')
    ox=tuple(np.median(a,axis=1) for a in tx)
    ow=tuple(np.median(a,axis=1) for a in tw)
    xs=tuple(a[:,0].copy() for a in tx)
    ws=tuple(a[:,0].copy() for a in tw)
    best_loss=_loss(xs,ws,vx,vw)
    best=(tuple(a.copy() for a in xs),tuple(a.copy() for a in ws),0)
    history=[];stale=0;stop='round budget';coupled=False
    def record(round_index, accepted=0):
        identity=float(np.mean([np.mean((x-o)**2) for x,o in zip(xs,ox)]) + np.mean([np.mean((w-o)**2) for w,o in zip(ws,ow)]))
        history.append({'round':round_index,'validation_loss':_loss(xs,ws,vx,vw),
                        'identity_loss':identity,'accepted_relations':int(accepted),
                        'max_drift':float(max(np.linalg.norm(x-o,axis=1).max() for x,o in list(zip(xs,ox))+list(zip(ws,ow))))})
    record(0)
    previous_pairs = np.full(n, -1)
    for depth in range(1,c.rounds+1):
        f,r=infer(xs,ws)
        pairs=accept_reciprocal(f,r,threshold=c.gate,margin=c.margin)
        weights=np.zeros((n,m))
        persistent = pairs.labels >= 0
        if c.require_persistence:
            persistent &= pairs.labels == previous_pairs
        for i in np.flatnonzero(persistent):
            weights[i,pairs.labels[i]]=pairs.score[i]
        previous_pairs = pairs.labels.copy()
        coupled |= bool(np.any(weights) and c.cross_weight>0)
        next_x=tuple(_proposal(x,o,w,weights,c) for x,o,w in zip(xs,ox,ws))
        next_w=tuple(_proposal(w,o,x,weights.T,c) for w,o,x in zip(ws,ow,xs))
        xs,ws=next_x,next_w
        record(depth,np.count_nonzero(weights))
        loss=history[-1]['validation_loss']
        if loss < best_loss-c.minimum_improvement:
            best_loss=loss;best=(tuple(a.copy() for a in xs),tuple(a.copy() for a in ws),depth);stale=0
        else:
            stale+=1
        if c.select_validation and stale>=c.patience:
            stop='validation patience';break
    if c.select_validation:
        xs,ws,selected=best
    else:
        selected=len(history)-1
    return RecursiveResult(xs,ws,selected,history,stop,coupled)
