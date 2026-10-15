#!/usr/bin/env python3
"""Portable numerical reproduction of the supplied Experiment 001 source.

The supplied script writes its chart to /mnt/data. This runner preserves its
seed, generator, shuffled split and feature matrices without that fixed path.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
ROOT=Path(__file__).resolve().parent


def reproduce():
    rng=np.random.default_rng(20261015);n=12000
    x=rng.choice([-1.,1.],size=(n,8));pairs=x[:,0::2]*x[:,1::2]
    y=.15*x.sum(axis=1)+1.1*pairs[:,0]+.95*pairs[:,1]+pairs[:,2]+.85*pairs[:,3]+.9*pairs[:,0]*pairs[:,2]+rng.normal(0,.3,n)
    order=rng.permutation(n);train,test=order[:9000],order[9000:]
    coarse=x.reshape(n,4,2).mean(axis=2)
    matrices={'Additive':x,'Fixed pair averages':coarse,'Supplied relational features':np.column_stack([coarse,pairs,pairs[:,0]*pairs[:,2]])}
    rows=[]
    for name,f in matrices.items():
        a=np.column_stack([np.ones(len(train)),f[train]]);coef=np.linalg.lstsq(a,y[train],rcond=None)[0]
        error=y[test]-np.column_stack([np.ones(len(test)),f[test]])@coef
        mse=float(np.mean(error**2));rows.append({'method':name,'mse':mse,'r2':1-mse/float(np.var(y[test])),'explained_variance':1-float(np.var(error))/float(np.var(y[test]))})
    return {'verification':'Numerically reproduced from supplied source; generating features supplied, not discovered',
            'seed':20261015,'components':'independent binary -1/+1','observations':n,'train':9000,'test':3000,'noise_variance':.09,
            'source_sha256':hashlib.sha256((ROOT/'meta_renormalization_experiment.py').read_bytes()).hexdigest(),'results':rows}

if __name__=='__main__':
    output=reproduce();(ROOT/'data/experiment001.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
