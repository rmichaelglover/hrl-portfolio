#!/usr/bin/env python3
"""Experiment 002: randomized supports, autonomous selection, sealed test set."""
from pathlib import Path
from itertools import combinations
import csv
import hashlib
import json
import platform
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hrl.meta_discovery import discover,features,fit_linear
OUT=Path(__file__).resolve().parent
METHODS=['Additive','Fixed pair averages','Hierarchical relaxation','Hierarchy without relaxation','Exhaustive polynomial']
SCENARIOS=['Pair-supported hierarchy','Hidden fourth order','Correlated inputs','Additive control']


def generate(seed,scenario):
    rng=np.random.default_rng(seed);n=12000;d=8;x=rng.normal(size=(n,d))
    if scenario=='Correlated inputs':
        common=rng.normal(size=(n,1));x=np.sqrt(.6)*x+np.sqrt(.4)*common
    order=rng.permutation(d);pairs=[tuple(sorted(map(int,order[k:k+2]))) for k in range(0,d,2)]
    coefficients=rng.uniform(.6,1.2,4)*rng.choice([-1,1],4)
    chosen=rng.choice(4,2,replace=False);quartic=tuple(sorted(pairs[chosen[0]]+pairs[chosen[1]]))
    signal=.15*x.sum(axis=1);truth=[]
    if scenario not in ['Hidden fourth order','Additive control']:
        for term,coefficient in zip(pairs,coefficients):signal+=coefficient*np.prod(x[:,term],axis=1);truth.append(term)
    if scenario!='Additive control':signal+=.9*np.prod(x[:,quartic],axis=1);truth.append(quartic)
    noise=rng.normal(0,.3,n);y=signal+noise
    # Truth is returned for evaluation ONLY. It is never an argument to discover.
    return x,y,noise,truth,{'pairs':[list(p) for p in pairs],'coefficients':coefficients.tolist(),'meta_support':list(quartic)}


def run(seed,scenario):
    x,y,noise,truth,generator=generate(seed,scenario)
    a,b,c=slice(0,6000),slice(6000,9000),slice(9000,12000)
    rows=[];discovered={};histories={}
    for method in METHODS:
        selected=[];iterations=0;history=[]
        if method=='Additive':
            terms=[(i,) for i in range(8)];coef=fit_linear(x[:9000],y[:9000],terms);prediction=features(x[c],terms)@coef;size=len(coef)
        elif method=='Fixed pair averages':
            coarse=x.reshape(len(x),4,2).mean(axis=2);terms=[(i,) for i in range(4)];coef=fit_linear(coarse[:9000],y[:9000],terms);prediction=features(coarse[c],terms)@coef;size=len(coef)
        elif method=='Exhaustive polynomial':
            terms=[term for degree in range(1,5) for term in combinations(range(8),degree)]
            coef=fit_linear(x[:9000],y[:9000],terms);prediction=features(x[c],terms)@coef;size=len(coef)
        else:
            result=discover(x[a],y[a],x[b],y[b],relaxation=method=='Hierarchical relaxation')
            prediction=result.predict(x[c]);selected=result.selected_interactions;iterations=result.relaxation_iterations;history=result.history;size=len(result.coefficients)
            discovered[method]=[list(t) for t in selected];histories[method]=history
        error=y[c]-prediction;mse=float(np.mean(error**2));variance=float(np.var(y[c]));ev=1-float(np.var(error))/variance;r2=1-mse/variance
        matches=len(set(selected)&set(truth));precision=matches/len(selected) if selected else None;recall=matches/len(truth) if truth else None
        if method not in ['Hierarchical relaxation','Hierarchy without relaxation']:precision=recall=None
        rows.append({'scenario':scenario,'seed':seed,'method':method,'mse':mse,'explained_variance':ev,'r2':r2,'parameters':size,'selected':len(selected),'true_support_matches':matches,'support_precision':precision,'support_recall':recall,'relaxation_iterations':iterations,'realized_noise_mse':float(np.mean(noise[c]**2))})
    example={'seed':seed,'generator':generator,'true_supports':[list(t) for t in truth],'discovered':discovered,'histories':histories}
    return rows,example


def main():
    start=time.perf_counter();records=[];examples={}
    for scenario in SCENARIOS:
        for seed in range(20):
            rows,example=run(seed,scenario);records.extend(rows)
            if seed==0:examples[scenario]=example
    results=[];rng=np.random.default_rng(812)
    for scenario in SCENARIOS:
        for method in METHODS:
            rows=[r for r in records if r['scenario']==scenario and r['method']==method]
            summary={k:float(np.mean([r[k] for r in rows])) for k in ['mse','explained_variance','r2','parameters','selected','true_support_matches','relaxation_iterations','realized_noise_mse']}
            for k in ['support_precision','support_recall']:
                values=[r[k] for r in rows if r[k] is not None];summary[k]=float(np.mean(values)) if values else None
            indices=rng.integers(0,len(rows),(1000,len(rows)))
            for k in ['mse','explained_variance']:
                values=np.array([r[k] for r in rows]);summary[k+'_ci95']=np.quantile(values[indices].mean(axis=1),[.025,.975]).tolist()
            results.append({'scenario':scenario,'method':method,**summary})
    output={'schema':1,'experiment':'002','kind':'Seeded synthetic autonomous interaction discovery within a fixed grammar',
            'seeds':list(range(20)),'observations_per_seed':12000,'fit_observations':6000,'selection_observations':3000,'test_observations':3000,
            'noise_variance':.09,'grammar':'linear leaves; all unordered pairs; degree-four products of selected disjoint pairs',
            'polynomial_baseline':'all square-free monomials through degree 4, 162 features plus intercept',
            'selection':{'max_interactions':12,'gain_fraction':.002,'active_strength_minimum':.8,'refit_on_all_9000':True},
            'scenarios':SCENARIOS,'methods':METHODS,'results':results,'examples':examples,
            'reported_001':{'verification':'User-supplied summary; source code and a_j coefficients not provided in workspace. Not independently reproduced here.','observations':12000,'held_out':3000,'mse':{'Additive':4.75248,'Ordinary coarse-graining':4.74778,'Relational + meta-interaction':.08968},'explained_variance':[.023,.024,.982]},
            'software':{'python':platform.python_version(),'numpy':np.__version__},
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'hrl/meta_discovery.py',Path(__file__).resolve()]},
            'runtime_seconds':round(time.perf_counter()-start,3)}
    (OUT/'data/results.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    with (OUT/'data/runs.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    for r in results:print(r['scenario'],r['method'],'EV',round(r['explained_variance'],4),'MSE',round(r['mse'],5),'parameters',r['parameters'],'recall',r['support_recall'])
    print('Seconds:',output['runtime_seconds'])

if __name__=='__main__':main()
