"""Reciprocal selective grounding with independently supplied views.

Scores are normalized strengths, not calibrated probabilities of correctness.
This module never treats a transpose of one view as independent evidence.
"""
from dataclasses import dataclass
import numpy as np


def _matrix(value, name, *, square=False):
    a = np.array(value, dtype=float, copy=True)
    if a.ndim != 2 or min(a.shape) < 1 or not np.isfinite(a).all():
        raise ValueError(f'{name} must be a nonempty finite matrix')
    if square and a.shape[0] != a.shape[1]:
        raise ValueError(f'{name} must be square')
    return a


def _normalize(a):
    scale = a.max(axis=1, keepdims=True)
    scaled = np.divide(a, scale, out=np.zeros_like(a), where=scale > 0)
    total = scaled.sum(axis=1, keepdims=True)
    return np.divide(scaled, total, out=np.zeros_like(a), where=total > 0)


def softmax(logits):
    a = _matrix(logits, 'logits')
    a = np.exp(a - a.max(axis=1, keepdims=True))
    return _normalize(a)


@dataclass
class ViewResult:
    strengths: np.ndarray
    deltas: list
    converged: bool


def relax_view(logits, object_graph, label_graph, *, gain=2., damping=.5,
               max_iterations=80, tolerance=1e-7):
    """Damped, prior-respecting graph relaxation; last logit is unknown.

    P_next = (1-d) P + d softmax(L + g [A P_real B.T, 0]).
    Nonnegative graphs are copied, stripped of self edges, and row normalized.
    The null label receives no relational support, but retains its prior.
    No convergence or correctness guarantee is asserted for arbitrary graphs.
    """
    l = _matrix(logits, 'logits')
    n, total = l.shape
    if total < 2:
        raise ValueError('at least one real label and an unknown label required')
    a = _matrix(object_graph, 'object_graph', square=True)
    b = _matrix(label_graph, 'label_graph', square=True)
    if a.shape != (n,n) or b.shape != (total-1,total-1):
        raise ValueError('graph dimensions do not match logits')
    if (a < 0).any() or (b < 0).any():
        raise ValueError('graphs must be nonnegative')
    if not np.isfinite(gain) or gain < 0 or not 0 < damping <= 1:
        raise ValueError('invalid gain or damping')
    if not isinstance(max_iterations, int) or max_iterations < 1 or not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('invalid iteration controls')
    np.fill_diagonal(a, 0); np.fill_diagonal(b, 0)
    a, b = _normalize(a), _normalize(b)
    p = softmax(l); deltas = []
    for _ in range(max_iterations):
        support = np.zeros_like(p)
        support[:,:-1] = a @ p[:,:-1] @ b.T
        updated = (1-damping)*p + damping*softmax(l + gain*support)
        delta = float(np.abs(updated-p).max()); deltas.append(delta); p=updated
        if delta < tolerance:
            break
    return ViewResult(p, deltas, deltas[-1] < tolerance)


@dataclass
class ReciprocalResult:
    labels: np.ndarray
    score: np.ndarray
    eligible: np.ndarray
    stability: np.ndarray


def _strengths(value, name):
    a = _matrix(value, name)
    if (a<0).any() or (a>1).any() or not np.allclose(a.sum(axis=1),1,atol=1e-7):
        raise ValueError(f'{name} must contain row-normalized strengths')
    return a


def accept_reciprocal(forward, reverse, *, threshold=.6, margin=.08,
                      perturbations=(), minimum_stability=1.):
    """Mutual unique winners; threshold and margin in BOTH directions.

    F shape n x (m+1), R shape m x (n+1). Last columns are unknown.
    Perturbations are additional (F,R) pairs with the same dimensions.
    Stability is the fraction whose mutual winners preserve the base pair;
    it does not measure independent truth. Abstentions have label -1.
    No one-to-one matching is imposed on input strengths, but mutual unique
    winner acceptance can accept at most one thing per word: this conservative
    instance-matching contract does not implement polysemy or class labeling.
    """
    f = _strengths(forward, 'forward'); r = _strengths(reverse, 'reverse')
    n,m=f.shape[0],f.shape[1]-1
    if m<1 or r.shape!=(m,n+1):
        raise ValueError('reverse must have shape m x (n+1)')
    if not 0<=threshold<=1 or not 0<=margin<=1 or not 0<=minimum_stability<=1:
        raise ValueError('thresholds must lie in [0,1]')
    fw=f.argmax(axis=1); rw=r.argmax(axis=1); rows=np.arange(n); chosen=np.minimum(fw,m-1)
    fmargin=np.sort(f,axis=1)[:,-1]-np.sort(f,axis=1)[:,-2]
    rmargin=np.sort(r,axis=1)[:,-1]-np.sort(r,axis=1)[:,-2]
    score=np.sqrt(f[rows,chosen]*r[chosen,rows])
    eligible=(fw<m)&(rw[chosen]==rows)&(fmargin>margin)&(rmargin[chosen]>margin)
    eligible&=(f[rows,chosen]>=threshold)&(r[chosen,rows]>=threshold)
    counts=np.zeros(n); runs=0
    for pf,pr in perturbations:
        pf=_strengths(pf,'perturbed forward');pr=_strengths(pr,'perturbed reverse')
        if pf.shape!=f.shape or pr.shape!=r.shape:
            raise ValueError('perturbation dimensions differ')
        pfw=pf.argmax(axis=1);prw=pr.argmax(axis=1)
        counts+=(pfw==fw)&(pfw<m)&(prw[chosen]==rows)
        runs+=1
    stability=counts/runs if runs else np.ones(n)
    accepted=eligible&(stability>=minimum_stability)
    return ReciprocalResult(np.where(accepted,fw,-1),score,eligible,stability)


def audit_anchors(result, verifier, *, previous=None, provenance='unspecified'):
    """Separate audit gate. A fresh verifier may reject previously accepted pairs.

    Returns provenance records for candidates and revocations, not immutable
    truths. Calling code must keep verifier evidence separate from view fitting.
    No automatic pseudo-label feedback is performed here.
    """
    records=[]; current={}
    for thing,word in enumerate(result.labels):
        if word<0: continue
        verified=bool(verifier(thing,int(word)))
        record={'thing':thing,'word':int(word),'status':'provisional' if verified else 'rejected',
                'score':float(result.score[thing]),'stability':float(result.stability[thing]),'provenance':str(provenance)}
        records.append(record)
        if verified:current[thing]=int(word)
    for thing,word in (previous or {}).items():
        if current.get(thing)!=word:
            records.append({'thing':int(thing),'word':int(word),'status':'revoked','provenance':str(provenance)})
    return records


def anchor_logits(forward_logits, reverse_logits, records, *, bonus=.5, max_bonus=1.):
    """Apply a bounded, revocable anchor bias to freshly supplied base evidence.

    Only the final ledger status of each pair matters. Start every round from
    fresh base logits, not a previously biased result. A provisional ledger
    status assumes the caller's separate audit; this function cannot establish
    evidence independence. Once anchors are shared, views are no longer wholly
    separate, so later agreement is not a new independent confirmation.
    """
    f = _matrix(forward_logits, 'forward_logits')
    r = _matrix(reverse_logits, 'reverse_logits')
    n, m = f.shape[0], f.shape[1] - 1
    if m < 1 or r.shape != (m, n + 1):
        raise ValueError('reverse dimensions do not match forward logits')
    if not np.isfinite(bonus) or not np.isfinite(max_bonus) or not 0 <= bonus <= max_bonus <= 1:
        raise ValueError('require 0 <= bonus <= max_bonus <= 1')
    latest = {}
    for record in records:
        thing, word = record['thing'], record['word']
        if not isinstance(thing, (int, np.integer)) or not isinstance(word, (int, np.integer)):
            raise ValueError('anchor indices must be integers')
        if not 0 <= thing < n or not 0 <= word < m:
            raise ValueError('anchor index outside logits')
        if record['status'] not in {'provisional', 'rejected', 'revoked'}:
            raise ValueError('unsupported anchor status')
        latest[thing, word] = record['status']
    used_things, used_words = set(), set()
    for (thing, word), status in latest.items():
        if status != 'provisional':
            continue
        if thing in used_things or word in used_words:
            raise ValueError('conflicting one-to-one anchors')
        used_things.add(thing)
        used_words.add(word)
        f[thing, word] += bonus
        r[word, thing] += bonus
    return f, r
