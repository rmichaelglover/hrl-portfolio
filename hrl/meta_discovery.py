"""Finite hierarchical feature discovery with active/inactive relaxation labels.

The learner receives observations and targets, never generating supports or
coefficients. Candidate grammar: linear leaves -> all pairs -> products of
selected disjoint pairs. This is a specialized GRRLE-inspired learner.
"""
from dataclasses import dataclass
from itertools import combinations
import numpy as np


def _data(x,y,name):
    x=np.array(x,dtype=float,copy=True);y=np.array(y,dtype=float,copy=True)
    if x.ndim!=2 or min(x.shape)<1 or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError(f'{name} requires finite X[n,d] and y[n]')
    return x,y


def features(x,terms):
    x=np.asarray(x,dtype=float)
    return np.column_stack([np.ones(len(x))]+[np.prod(x[:,term],axis=1) for term in terms])


def fit_linear(x,y,terms):
    design=features(x,terms)
    return np.linalg.lstsq(design,y,rcond=None)[0]


@dataclass
class DiscoveryResult:
    terms: list
    coefficients: np.ndarray
    history: list
    selected_interactions: list
    relaxation_iterations: int
    stop_reason: str

    def predict(self,x):
        x=np.asarray(x,dtype=float)
        if x.ndim!=2 or not np.isfinite(x).all():
            raise ValueError('prediction data must be a finite matrix')
        if self.terms and x.shape[1]<=max(max(t) for t in self.terms):
            raise ValueError('prediction data has too few components')
        return features(x,self.terms)@self.coefficients


def relax_hypotheses(gains,cost,parents,selected,*,temperature,enabled=True):
    """Label hypotheses inactive/active with fixed gain evidence and support.

    Selected parents give bounded positive support to promoted hypotheses.
    Unselected parent/child hypotheses exchange support if both are present.
    Support cannot make a candidate pass the independent positive-gain gate.
    """
    gains=np.asarray(gains,dtype=float)
    z=np.clip((gains-cost)/temperature,-40,40)
    prior=1/(1+np.exp(-z));p=prior.copy()
    if not enabled:return p,0
    adjacency=np.zeros((len(gains),len(gains)))
    fixed=np.zeros(len(gains));keys=list(parents);indices={t:i for i,t in enumerate(keys)}
    for term,i in indices.items():
        for pair in parents[term]:
            if pair in indices:
                adjacency[i,indices[pair]]+=.15
                adjacency[indices[pair],i]+=.15
            elif pair in selected:
                fixed[i]+=.15
    for iteration in range(60):
        support=fixed+adjacency@(2*p-1)
        target=1/(1+np.exp(-np.clip(z+support,-40,40)))
        new=.5*p+.5*target
        if np.max(np.abs(new-p))<1e-8:return new,iteration+1
        p=new
    return p,60


def discover(x_train,y_train,x_validation,y_validation,*,max_terms=12,
             gain_fraction=.002,relaxation=True,refit=True):
    """Select on validation, optionally refit selected structure on both sets.

    Validation is queried adaptively; it is not the final unbiased test set.
    Linear terms are always included. Quartics require two selected pair
    parents, intentionally exposing a failure on pure hidden higher-order terms.
    """
    x,y=_data(x_train,y_train,'train');v,z=_data(x_validation,y_validation,'validation')
    if x.shape[1]!=v.shape[1]:raise ValueError('component counts differ')
    if not isinstance(max_terms,int) or max_terms<0 or not np.isfinite(gain_fraction) or gain_fraction<=0:
        raise ValueError('invalid discovery budget or gain penalty')
    d=x.shape[1];base=[(i,) for i in range(d)];selected=[];parents={t:() for t in combinations(range(d),2)}
    cost=max(1e-8,gain_fraction*np.var(y));temperature=max(1e-8,.02*np.var(y))
    history=[];iterations=0;stop='term budget'
    for depth in range(max_terms+1):
        terms=base+selected;design=features(x,terms);validation=features(v,terms)
        coef=np.linalg.lstsq(design,y,rcond=None)[0]
        residual=y-design@coef;vr=z-validation@coef;loss=float(np.mean(vr**2))
        record={'round':depth,'validation_mse':loss,'selected':[list(t) for t in selected],
                'proposed':len(parents),'candidate':None,'gain':0.,'active_strength':0.}
        history.append(record)
        if depth==max_terms:break
        # Promote two learned pair objects into one higher-order object. Equivalent
        # multiplication trees are canonicalized to one observable monomial.
        pair_nodes=[p for p in selected if len(p)==2]
        for a,b in combinations(pair_nodes,2):
            if set(a).isdisjoint(b):
                term=tuple(sorted(a+b));parents.setdefault(term,(a,b))
        record['proposed']=len(parents)
        candidates=[t for t in parents if t not in selected]
        if not candidates:stop='no candidates';break
        f=features(x,candidates)[:,1:];fv=features(v,candidates)[:,1:]
        # Residualize every candidate against the current model. These are exact
        # one-term least-squares improvements, evaluated on selection data.
        projection=np.linalg.lstsq(design,f,rcond=None)[0]
        q=f-design@projection;qv=fv-validation@projection
        norms=(q*q).sum(axis=0);beta=np.divide(q.T@residual,norms,out=np.zeros(len(candidates)),where=norms>1e-12)
        gains=(2*beta*(qv.T@vr)-beta**2*(qv*qv).sum(axis=0))/len(v)
        # Retained hypotheses remain in the relaxation graph. Their evidence
        # is the validation cost of removing/refitting that term, so parent and
        # child labels exchange state-dependent support, not merely a fixed bias.
        nodes=list(parents)
        node_gain={t:float(g) for t,g in zip(candidates,gains)}
        for term in selected:
            reduced=base+[t for t in selected if t!=term]
            reduced_coef=fit_linear(x,y,reduced)
            without=np.mean((z-features(v,reduced)@reduced_coef)**2)
            node_gain[term]=float(without-loss)
        labels,count=relax_hypotheses([node_gain[t] for t in nodes],cost,parents,selected,temperature=temperature,enabled=relaxation)
        active=np.array([labels[nodes.index(t)] for t in candidates])
        iterations+=count
        eligible=(gains>cost)&(active>.8)
        if not eligible.any():stop='validation gain/strength gate';break
        winner=max(np.flatnonzero(eligible),key=lambda i:(active[i],gains[i],tuple(-j for j in candidates[i])))
        term=candidates[winner]
        record.update(candidate=list(term),gain=float(gains[winner]),active_strength=float(active[winner]),proposed=len(parents))
        selected.append(term)
    terms=base+selected
    if refit:coef=fit_linear(np.vstack([x,v]),np.r_[y,z],terms)
    else:coef=fit_linear(x,y,terms)
    return DiscoveryResult(terms,coef,history,selected,iterations,stop)
