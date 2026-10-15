#!/usr/bin/env python3
"""Seed-separated synthetic reciprocal-grounding benchmark. Run at repo root."""
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
from hrl.reciprocal import relax_view, accept_reciprocal, audit_anchors
OUT=Path(__file__).resolve().parent
METHODS=['Forward','Reverse','Reciprocal','No relaxation','Copied reverse']
SCENARIOS=['Independent views','Correlated noise','Shared wrong dictionary','Uninformative reverse']
PARAMETERS={'words':16,'things':20,'dimensions':5,'noise':.65,'temperature':.65,
            'unknown_logit':-4.,'graph_gain':2.,'margin':.06,'perturbation_sd':.12,'perturbations':3}


def graph(features):
    d=((features[:,None]-features[None,:])**2).sum(axis=2)
    g=np.exp(-d/10);np.fill_diagonal(g,0);return g


def logits(a,b):
    d=((a[:,None]-b[None,:])**2).sum(axis=2)
    return np.column_stack([-d/(2*PARAMETERS['temperature']**2),np.full(len(a),PARAMETERS['unknown_logit'])])


def dataset(seed,scenario):
    rng=np.random.default_rng(seed);m=PARAMETERS['words'];n=PARAMETERS['things'];d=PARAMETERS['dimensions']
    latent=rng.normal(0,1.4,(m,d));truth=np.r_[rng.permutation(m),np.full(n-m,-1)]
    base=np.vstack([latent[truth[:m]],rng.normal(6,1,(n-m,d))])
    e1=rng.normal(0,PARAMETERS['noise'],(n,d));e2=rng.normal(0,PARAMETERS['noise'],(n,d))
    if scenario=='Correlated noise':e2=.95*e1+np.sqrt(1-.95**2)*e2
    things1=base+e1;things2=base+e2
    words1=latent+rng.normal(0,.25,(m,d));words2=latent+rng.normal(0,.25,(m,d))
    if scenario=='Shared wrong dictionary':
        order=np.roll(np.arange(m),1);words1=words1[order];words2=words2[order]
    if scenario=='Uninformative reverse':
        words2=rng.normal(0,1.4,(m,d));things2=rng.normal(0,1.4,(n,d))
    return logits(things1,words1),logits(words2,things2),graph(things1),graph(words1),graph(words2),graph(things2),truth


def winners(p):
    chosen=p.argmax(axis=1);margin=np.sort(p,axis=1)[:,-1]-np.sort(p,axis=1)[:,-2]
    good=(chosen<p.shape[1]-1)&(margin>PARAMETERS['margin'])
    return chosen,p.max(axis=1),good


def forward_candidates(p,perturbed):
    chosen,score,good=winners(p)
    for other in perturbed:good&=other.argmax(axis=1)==chosen
    return chosen,score,good,score.copy()


def reverse_candidates(r,perturbed,n):
    chosen,confidence,good=winners(r)
    for other in perturbed:good&=other.argmax(axis=1)==chosen
    labels=np.full(n,-1);score=np.zeros(n)
    for w in np.flatnonzero(good):
        i=chosen[w]
        if confidence[w]>score[i]:labels[i]=w;score[i]=confidence[w]
    return labels,score,labels>=0,score.copy()


def fit(seed,scenario):
    f,r,a,b,c,d,truth=dataset(seed,scenario)
    rng=np.random.default_rng(seed+50000)
    fv=relax_view(f,a,b,gain=PARAMETERS['graph_gain']);rv=relax_view(r,c,d,gain=PARAMETERS['graph_gain'])
    fps=[];rps=[];perturbed_logits=[]
    for _ in range(PARAMETERS['perturbations']):
        pf=f+rng.normal(0,.12,f.shape);pr=r+rng.normal(0,.12,r.shape);perturbed_logits.append((pf,pr))
        fps.append(relax_view(pf,a,b).strengths)
        rps.append(relax_view(pr,c,d).strengths)
    rec=accept_reciprocal(fv.strengths,rv.strengths,threshold=0,margin=PARAMETERS['margin'],perturbations=list(zip(fps,rps)))
    rows=np.arange(len(truth));word=np.minimum(fv.strengths.argmax(axis=1),r.shape[0]-1)
    gate=np.minimum(fv.strengths[rows,word],rv.strengths[word,rows])
    # Copied reverse ablation: column-normalized transpose plus explicit null.
    def copy_reverse(p):
        q=np.column_stack([p[:,:-1].T,np.full(r.shape[0],.03)]);return q/q.sum(axis=1,keepdims=True)
    copied=copy_reverse(fv.strengths);copied_ps=[copy_reverse(p) for p in fps]
    cr=accept_reciprocal(fv.strengths,copied,threshold=0,margin=PARAMETERS['margin'],perturbations=list(zip(fps,copied_ps)))
    copygate=np.minimum(fv.strengths[rows,word],copied[word,rows])
    from hrl.reciprocal import softmax
    nr=accept_reciprocal(softmax(f),softmax(r),threshold=0,margin=PARAMETERS['margin'],perturbations=[(softmax(pf),softmax(pr)) for pf,pr in perturbed_logits])
    nw=np.minimum(softmax(f).argmax(axis=1),r.shape[0]-1);ngate=np.minimum(softmax(f)[rows,nw],softmax(r)[nw,rows])
    candidates={'Forward':forward_candidates(fv.strengths,fps),'Reverse':reverse_candidates(rv.strengths,rps,len(truth)),
                'Reciprocal':(rec.labels,rec.score,rec.labels>=0,gate),
                'No relaxation':(nr.labels,nr.score,nr.labels>=0,ngate),
                'Copied reverse':(cr.labels,cr.score,cr.labels>=0,copygate)}
    return {'truth':truth,'candidates':candidates,'forward':fv,'reverse':rv,'agreement':rec,'prior':softmax(f)}


def evaluate(run,method,threshold):
    labels,score,eligible,gate=run['candidates'][method];accepted=eligible&(gate>=threshold);truth=run['truth']
    correct=accepted&(truth>=0)&(labels==truth)
    return {'accepted':int(accepted.sum()),'correct':int(correct.sum()),'total':len(truth),
            'unknown_accepted':int((accepted&(truth<0)).sum()),'unknown_total':int((truth<0).sum())}


def summarize(records):
    accepted=sum(r['accepted'] for r in records);correct=sum(r['correct'] for r in records);total=sum(r['total'] for r in records)
    unknown=sum(r['unknown_accepted'] for r in records);unknown_total=sum(r['unknown_total'] for r in records)
    return {'accepted':accepted,'correct':correct,'total':total,'accuracy':correct/accepted if accepted else None,
            'coverage':accepted/total,'unknown_acceptance':unknown/unknown_total if unknown_total else None}


def bootstrap(records,seed=812):
    rng=np.random.default_rng(seed);acc=[];coverage=[]
    for _ in range(1000):
        sample=[records[i] for i in rng.integers(0,len(records),len(records))];s=summarize(sample)
        if s['accuracy'] is not None:acc.append(s['accuracy'])
        coverage.append(s['coverage'])
    return {'accuracy_ci95':np.quantile(acc,[.025,.975]).tolist() if acc else None,'coverage_ci95':np.quantile(coverage,[.025,.975]).tolist()}


def risk_curve(runs,method):
    ranked=[]
    for run in runs:
        labels,score,eligible,_=run['candidates'][method]
        for i in np.flatnonzero(eligible):ranked.append((float(score[i]),bool(run['truth'][i]>=0 and labels[i]==run['truth'][i])))
    ranked.sort(key=lambda x:x[0],reverse=True);total=sum(len(r['truth']) for r in runs)
    correct=np.cumsum([r[1] for r in ranked]);ks=np.unique(np.linspace(1,len(ranked),min(100,len(ranked)),dtype=int)) if ranked else []
    return [{'coverage':int(k)/total,'risk':1-float(correct[k-1])/int(k),'accepted':int(k)} for k in ks]


def main():
    start=time.perf_counter();validation=[fit(seed,'Independent views') for seed in range(20)]
    thresholds={}
    for method in METHODS:
        possible=[]
        for threshold in np.arange(.2,1.001,.025):
            s=summarize([evaluate(run,method,float(threshold)) for run in validation])
            if s['accepted']>=10 and s['accuracy']>=.95:possible.append((s['coverage'],float(threshold)))
        thresholds[method]=max(possible,key=lambda x:(x[0],-x[1]))[1] if possible else 1.
    results=[];curves={};representative=None;nonconverged=0;raw=[]
    for scenario in SCENARIOS:
        runs=[fit(seed,scenario) for seed in range(100,140)]
        nonconverged+=sum(not run[view].converged for run in runs for view in ['forward','reverse'])
        curves[scenario]={}
        for method in METHODS:
            records=[evaluate(run,method,thresholds[method]) for run in runs]
            results.append({'scenario':scenario,'method':method,'threshold':thresholds[method],**summarize(records),**bootstrap(records)})
            curves[scenario][method]=risk_curve(runs,method)
            for seed,record in zip(range(100,140),records):raw.append({'scenario':scenario,'method':method,'seed':seed,**record})
        if scenario=='Independent views':
            run=runs[0];rec=run['agreement']
            # The verifier is deliberately outside fitting; synthetic truth is an
            # oracle illustration, not additional evidence discovered by a model.
            representative={'seed':100,'truth':run['truth'].tolist(),'prior':run['prior'].tolist(),
                'forward':run['forward'].strengths.tolist(),'reverse':run['reverse'].strengths.tolist(),
                'score':rec.score.tolist(),'candidates':rec.labels.tolist(),'stability':rec.stability.tolist(),
                'deltas_forward':run['forward'].deltas,'deltas_reverse':run['reverse'].deltas,
                'audit':audit_anchors(rec,lambda i,j:run['truth'][i]==j,provenance='synthetic hidden oracle; illustration only')}
    # A separate known wrong reciprocal pair is a deterministic counterexample.
    artifact={'schema':1,'title':'Reciprocal Grounding','data_kind':'Synthetic instance-matching benchmark; not natural-language grounding',
        'parameters':PARAMETERS,'validation_seeds':[0,19],'test_seeds':[100,139],'threshold_selection':'Independent views only; maximize validation coverage at empirical precision >= 0.95 and >=10 accepts; otherwise threshold 1',
        'scenarios':SCENARIOS,'methods':METHODS,'thresholds':thresholds,'results':results,'curves':curves,'example':representative,
        'base_nonconverged':nonconverged,'software':{'python':platform.python_version(),'numpy':np.__version__},
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'hrl/reciprocal.py',Path(__file__).resolve()]},
        'runtime_seconds':round(time.perf_counter()-start,3)}
    (OUT/'data/results.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    with (OUT/'data/runs.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]));writer.writeheader();writer.writerows(raw)
    print(json.dumps({'thresholds':thresholds,'results':results,'seconds':artifact['runtime_seconds']},indent=2))

if __name__=='__main__':main()
