#!/usr/bin/env python3
"""Recursive representation study; no target correspondence labels in fitting."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hrl.recursive_grounding import RecursiveConfig, recursive_refine, infer, evidence, relations
from hrl.reciprocal import relax_view, accept_reciprocal
from experiment import summarize, bootstrap
OUT=Path(__file__).resolve().parent
METHODS=['Single observation','Robust self-only','Guarded recursion','No validation','Unregularized recursion']
SCENARIOS=['Independent observations','Training outliers','Shared wrong dictionary']


def dataset(seed,scenario):
    rng=np.random.default_rng(seed);n,m,d=20,16,5
    prototypes=rng.normal(0,1.4,(m,d));truth=np.r_[rng.permutation(m),[-1]*4]
    things=np.vstack([prototypes[truth[:m]],rng.normal(6,1,(4,d))])
    names=prototypes.copy()
    if scenario=='Shared wrong dictionary':names=names[np.roll(np.arange(m),1)]
    def observe(base,k,noise):return tuple(base[:,None]+rng.normal(0,noise,(len(base),k,d)) for _ in range(2))
    tx,tw=observe(things,5,.9),observe(names,5,.7)
    vx,vw=observe(things,3,.9),observe(names,3,.7)
    qx,qw=observe(things,3,.9),observe(names,3,.7)
    if scenario=='Training outliers':
        # One gross corrupted leaf for a quarter of training identities, in each
        # direction. Validation/test observations are not modified.
        for view in range(2):
            tx[view][:5,0]+=rng.normal(0,5,(5,d))
            tw[view][:4,0]+=rng.normal(0,5,(4,d))
    return tx,tw,vx,vw,qx,qw,truth,things,names


def validation_loss(xs,ws,vx,vw):
    return float(np.mean([np.mean((x[:,None]-v)**2) for x,v in zip(xs,vx)])+np.mean([np.mean((w[:,None]-v)**2) for w,v in zip(ws,vw)]))


def run(seed,scenario):
    tx,tw,vx,vw,qx,qw,truth,latent_x,latent_w=dataset(seed,scenario)
    outcomes={}
    for method in METHODS:
        history=[];selected=0
        if method=='Single observation':xs=tuple(a[:,0] for a in tx);ws=tuple(a[:,0] for a in tw)
        elif method=='Robust self-only':xs=tuple(np.median(a,axis=1) for a in tx);ws=tuple(np.median(a,axis=1) for a in tw)
        else:
            config=RecursiveConfig()
            if method=='No validation':config.select_validation=False
            if method=='Unregularized recursion':config=RecursiveConfig(self_weight=0,cross_weight=1,bounded=False,damping=.9,select_validation=False,require_persistence=False)
            result=recursive_refine(tx,tw,vx,vw,config=config);xs,ws=result.things,result.names;history=result.history;selected=result.selected_round
        # The query things are NEW measurements, never passed into refinement.
        query=tuple(np.mean(a,axis=1) for a in qx)
        f,r=infer(query,ws)
        rng=np.random.default_rng(seed+81200)
        pf=[];pr=[]
        for _ in range(3):
            lf=evidence(query[0],ws[0])+rng.normal(0,.12,f.shape)
            lr=evidence(ws[1],query[1])+rng.normal(0,.12,r.shape)
            pf.append(relax_view(lf,relations(query[0]),relations(ws[0])).strengths)
            pr.append(relax_view(lr,relations(ws[1]),relations(query[1])).strengths)
        accepted=accept_reciprocal(f,r,threshold=0,margin=.06,perturbations=list(zip(pf,pr)))
        chosen=np.minimum(f.argmax(axis=1),len(ws[0])-1);rows=np.arange(len(truth));gate=np.minimum(f[rows,chosen],r[chosen,rows])
        train=validation_loss(xs,ws,tx,tw);valid=validation_loss(xs,ws,vx,vw);test=validation_loss(xs,ws,qx,qw)
        latent=float(np.mean([np.mean((x-latent_x)**2) for x in xs])+np.mean([np.mean((w-latent_w)**2) for w in ws]))
        outcomes[method]={'labels':accepted.labels,'gate':gate,'truth':truth,'train_loss':train,'validation_loss':valid,'test_loss':test,'latent_mse':latent,'selected_round':selected,'history':history,'things':[x.tolist() for x in xs],'names':[w.tolist() for w in ws]}
    return outcomes


def counts(result,threshold):
    accepted=(result['labels']>=0)&(result['gate']>=threshold);truth=result['truth'];correct=accepted&(truth>=0)&(result['labels']==truth)
    return {'accepted':int(accepted.sum()),'correct':int(correct.sum()),'total':len(truth),'unknown_accepted':int((accepted&(truth<0)).sum()),'unknown_total':int((truth<0).sum())}


def main():
    start=time.perf_counter();validation=[run(seed,'Independent observations') for seed in range(20)]
    thresholds={}
    for method in METHODS:
        choices=[]
        for threshold in np.arange(.2,1.001,.025):
            s=summarize([counts(r[method],threshold) for r in validation])
            if s['accepted']>=10 and s['accuracy']>=.95:choices.append((s['coverage'],float(threshold)))
        thresholds[method]=max(choices,key=lambda p:(p[0],-p[1]))[1] if choices else 1.
    rows=[];results=[];traces={};example={};selection={}
    for scenario in SCENARIOS:
        runs=[run(seed,scenario) for seed in range(100,140)]
        traces[scenario]={}
        for method in METHODS:
            records=[counts(r[method],thresholds[method]) for r in runs]
            extra={key:float(np.mean([r[method][key] for r in runs])) for key in ['train_loss','validation_loss','test_loss','latent_mse','selected_round']}
            results.append({'scenario':scenario,'method':method,'threshold':thresholds[method],**summarize(records),**bootstrap(records),**extra})
            traces[scenario][method]=[{'seed':seed,'selected_round':r[method]['selected_round'],'history':r[method]['history']} for seed,r in zip(range(100,140),runs) if r[method]['history']]
            for seed,r,record in zip(range(100,140),runs,records):rows.append({'scenario':scenario,'method':method,'seed':seed,**record,**{k:r[method][k] for k in extra}})
        example[scenario]={m:{k:v for k,v in runs[0][m].items() if k in ['things','names','selected_round','history']} for m in METHODS}
    output={'schema':1,'data_kind':'Synthetic repeated measurements; same identities, fresh test observations, not unseen semantic categories',
            'validation_seeds':[0,19],'test_seeds':[100,139],'methods':METHODS,'scenarios':SCENARIOS,'thresholds':thresholds,
            'config':vars(RecursiveConfig()),'measurements':{'things':20,'names':16,'dimensions':5,'training_repeats':5,'validation_repeats':3,'test_repeats':3,'thing_noise':.9,'name_noise':.7},
            'results':results,'traces':traces,'example':example,
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'hrl/recursive_grounding.py',ROOT/'hrl/reciprocal.py',Path(__file__).resolve()]},
            'software':{'python':platform.python_version(),'numpy':np.__version__},'runtime_seconds':round(time.perf_counter()-start,3)}
    (OUT/'data/recursive-results.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    with (OUT/'data/recursive-runs.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    for r in results:print(r['scenario'],r['method'],'acc',r['accuracy'],'coverage',r['coverage'],'train',round(r['train_loss'],3),'test',round(r['test_loss'],3),'round',round(r['selected_round'],1))
    print('Seconds:',output['runtime_seconds'])

if __name__=='__main__':main()
