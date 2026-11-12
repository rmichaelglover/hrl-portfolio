#!/usr/bin/env python3
"""Actual HRL/GRRLE engines applied to boundary evidence, with held-out controls."""
from pathlib import Path
import csv, hashlib, json, sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
from hrl_generic import HRL, pairwise_factor
from grrle import GRRLE, Hypothesis, Relation
HERE=Path(__file__).resolve().parent
CHANNELS=('left_visual','right_visual','interoceptive')
# Fixed before test evaluation. No simplex without an irreducibly three-way rule.
GAINS=(0., .25, .5, 1.)

def sample(seed,n=180,shift=False):
    rng=np.random.default_rng(seed)
    y=rng.integers(0,2,n) # 0 internal, 1 external
    rates=np.array([[2.,2.,8.],[12.,12.,2.]])
    means=rates[y].copy()
    if shift:
        # Common latent retinal activation violates independent-eye assumption.
        shared=rng.poisson(9.,n)
        x=rng.poisson(means)
        x[:,:2]+=shared[:,None]
    else:
        x=rng.poisson(means)
    return x,y

def fitted_rates(x,y):
    # Gamma(1,1) smoothing; training only, one-second windows.
    return np.stack([(x[y==label].sum(axis=0)+1)/(sum(y==label)+1) for label in (0,1)])

def unary(x,rates):
    logratio=x*np.log(rates[1]/rates[0])-(rates[1]-rates[0])
    p=1/(1+np.exp(-np.clip(logratio,-60,60)))
    return np.stack([1-p,p],axis=-1),logratio

def infer(priors,engine,gain=0.,reverse=False):
    # Three sensor objects + one neutral parent. No extra parent likelihood.
    p=np.vstack([priors,[.5,.5]])
    if engine=='hrl':
        c=np.array([[1.,-1.],[-1.,1.]])
        if reverse:c=-c
        f=pairwise_factor(np.array([[0,3],[1,3],[2,3]]),c)
        r=HRL(4,2,[f],p,prior_strength=.85,support_factor=gain,
              max_iterations=150,tol=1e-8,record_history=True).run()
        return r.strengths[-1,1],r.converged,r.iterations
    hypotheses=[Hypothesis(f'{i}:{a}',0 if i<3 else 1,0,1,
                           ('internal','external')[a],float(p[i,a])) for i in range(4) for a in range(2)]
    relations=[]
    for i in range(3):
        for a in range(2):
            for b in range(2):
                w=(1 if a==b else -1)*(-1 if reverse else 1)
                # Parent averages evidence; feedback has bounded total support.
                relations.extend([Relation(f'3:{a}',f'{i}:{b}',w/3,'sensor_to_parent'),
                                  Relation(f'{i}:{b}',f'3:{a}',w,'parent_to_sensor')])
    r=GRRLE(hypotheses,relations,gain=gain,max_iterations=150,
            tol=1e-8,record_history=True).run()
    # GRRLE memberships are NOT a categorical posterior; score is explicit.
    score=r.strength('3:1')-r.strength('3:0')
    return .5+.5*score,r.converged,r.iterations

def fuzzy(x):
    active=x/(x+5.)
    # min t-norm for both-eye activity with low bodily activation.
    return np.minimum(np.minimum(active[:,0],active[:,1]),1-active[:,2])

def scores(x,rates,engine,gain=0,reverse=False):
    p,llr=unary(x,rates)
    if engine=='bayes':return 1/(1+np.exp(-np.clip(llr.sum(axis=1),-60,60))),0
    if engine=='fuzzy':return fuzzy(x),0
    values=[infer(row,engine,gain,reverse) for row in p]
    return np.array([v[0] for v in values]),sum(not v[1] for v in values)

def metrics(score,y):
    decided=np.abs(score-.5)>=.1
    return dict(accuracy=float(np.mean((score>.5)==y)),
                coverage=float(np.mean(decided)),
                selective_accuracy=float(np.mean((score[decided]>.5)==y[decided])) if decided.any() else None)

def eye_traces(rates,gains):
    output=[]
    for scenario in ('light','closed','one-eye','endogenous','decline'):
        path=HERE.parent/'eyes'/f'{scenario}.csv'
        with path.open() as f:rows=list(csv.DictReader(line for line in f if not line.startswith('#')))
        previous=np.zeros(2)
        for row in rows:
            t=float(row['time_ms'])
            if t==0 or t%100:continue
            counts=np.array([float(row['left_ganglion']),float(row['right_ganglion'])])
            # Convert 100-ms counts to rates. No endogenous/photon truth fields read.
            # Interoception absent: use only retinal channels and a neutral third unary.
            rates_observed=(counts-previous)*10;previous=counts
            p=np.full((3,2),.5)
            record=dict(scenario=scenario,time_ms=t,left_events=int(rates_observed[0]/10),
                        right_events=int(rates_observed[1]/10),interoception='missing',
                        observation_domain='existing mechanistic simulation; no target labels')
            # Counts evaluated at their actual exposure, not as one-second rates.
            llr= rates_observed/10*np.log(rates[1,:2]/rates[0,:2])-(rates[1,:2]-rates[0,:2])*.1
            pp=1/(1+np.exp(-np.clip(llr,-60,60)))
            p[:2]=np.stack([1-pp,pp],axis=-1)
            for engine in ('hrl','grrle'):
                record[engine+'_external_score']=infer(p,engine,gains[engine])[0]
            output.append(record)
    with (HERE/'sensory-inference.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(output[0]),lineterminator="\n");writer.writeheader();writer.writerows(output)
    return output

def main():
    train,ytrain=sample(1101);valid,yvalid=sample(2202)
    rates=fitted_rates(train,ytrain)
    gains={};validation={}
    for engine in ('hrl','grrle'):
        validation[engine]=[]
        for gain in GAINS:
            s,nonconv=scores(valid,rates,engine,gain)
            validation[engine].append(dict(gain=gain,nonconverged=nonconv,**metrics(s,yvalid)))
        # Max validation accuracy; simpler smaller gain wins exact ties.
        gains[engine]=max(validation[engine],key=lambda r:(r['accuracy'],-r['gain']))['gain']
    report=dict(originator='Michael Emanuel Glover',implementation='Assistant implementation and numerical experiments',
                data='Synthetic independent scenes; existing mechanistic Eye traces separately unlabelled',
                split=dict(train_seed=1101,validation_seed=2202,test_seed=3303,shift_seed=4404,scenes_each=180),
                fitted_rates=rates.tolist(),validation=validation,selected_gains=gains,tests={})
    raw=[]
    for domain,seed,shift in [('matched',3303,False),('correlated_shift',4404,True)]:
        x,y=sample(seed,shift=shift);results={}
        for name,engine,gain,reverse in [('bayes','bayes',0,False),('fuzzy','fuzzy',0,False),
                ('hrl_selected','hrl',gains['hrl'],False),('grrle_selected','grrle',gains['grrle'],False),
                ('hrl_no_links','hrl',0,False),('grrle_no_links','grrle',0,False),
                ('hrl_fixed_gain_1','hrl',1,False),('grrle_fixed_gain_1','grrle',1,False),
                ('hrl_wrong_relations','hrl',1,True),('grrle_wrong_relations','grrle',1,True)]:
            s,nonconv=scores(x,rates,engine,gain,reverse)
            results[name]=dict(nonconverged=nonconv,**metrics(s,y))
            for i,(score,target) in enumerate(zip(s,y)):
                raw.append(dict(domain=domain,scene=i,method=name,target=int(target),score=float(score)))
            # Proper probability scoring is reserved for the generative baseline.
            if engine=='bayes':
                results[name]['brier']=float(np.mean((s-y)**2))
                clipped=np.clip(s,1e-12,1-1e-12)
                results[name]['log_loss']=float(-np.mean(y*np.log(clipped)+(1-y)*np.log1p(-clipped)))
        report['tests'][domain]=results
    traces=eye_traces(rates,gains)
    report['mechanistic_windows']=len(traces)
    report['empirical_anchor']=dict(path='../impase/data/digitized.csv',
          sha256=hashlib.sha256((HERE.parent/'impase/data/digitized.csv').read_bytes()).hexdigest(),
          role='Independent measured biochemical calibration retained; not used as sensory ground truth.')
    (HERE/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    with (HERE/'predictions.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(raw[0]),lineterminator="\n");writer.writeheader();writer.writerows(raw)
    plot(report)
    print(json.dumps({'selected_gains':gains,'matched':report['tests']['matched'],
                      'shift':report['tests']['correlated_shift']},indent=2))

def plot(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    names=['bayes','fuzzy','hrl_selected','grrle_selected','hrl_wrong_relations','grrle_wrong_relations']
    fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,(domain,rows) in zip(axes,report['tests'].items()):
        ax.barh(names,[rows[n]['accuracy'] for n in names],color=['#325d79','#b77939','#3c8060','#3c8060','#b64a45','#b64a45'])
        ax.set(xlim=(0,1),xlabel='Held-out classification accuracy',title=domain.replace('_',' ').title())
    fig.suptitle('Boundary inference: synthetic scene controls (180 scenes per domain)')
    fig.savefig(HERE/'comparison.png',dpi=160);fig.savefig(HERE/'comparison.pdf');plt.close(fig)

if __name__=='__main__':main()
