#!/usr/bin/env python3
"""Frozen seeded pilot: reciprocal finalization versus the same unfrozen update.

Set OPENBLAS_NUM_THREADS=1 before launching for the recorded timing protocol.
Timing includes constructor copies, cache packing, audits, and result assembly;
generation of the common input kernel is excluded for every method.
"""
from pathlib import Path
import hashlib
import json
import csv
import time
import sys
import platform
import numpy as np

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from hrl import MutualBestLabeler, FinalizationPolicy, pairwise_distance_compatibility


def delayed_swap():
    score=np.zeros((4,4));score[0,0]=score[2,2]=1.1
    score[0,2]=score[2,0]=.05;score[1,1]=score[3,3]=1
    c=np.broadcast_to(score[:,:,None,None]/4,(4,4,4,4)).copy()
    c[0,0,1,1]-=1;c[2,2,1,1]-=1;c[0,2,1,1]+=1.3;c[2,0,1,1]+=1.3
    prior=np.array([[.7,.1,.1,.1],[.499,.001,.25,.25],[.1,.1,.7,.1],[.05,.05,.05,.85]])
    return c,prior,np.array([2,1,0,3])


def geometry(n,seed,ambiguous=False):
    rng=np.random.default_rng(seed)
    labels=rng.normal(size=(n,3))
    if ambiguous:
        labels[-1]=labels[-2]+[.0001,0,0]
    truth=rng.permutation(n)
    objects=labels[truth]+rng.normal(0,.015,size=labels.shape)
    c=pairwise_distance_compatibility(objects,labels,sigma=.18,exclusion_penalty=-.1)
    prior=rng.uniform(.8,1.2,size=(n,n))
    # 25% of rows get a useful identity prior; the rest must use geometry.
    for i in range(n//4):prior[i,truth[i]]+=n*.7
    prior/=prior.sum(axis=1,keepdims=True)
    return c,prior,truth


def unresolved_tail(n,seed):
    rng=np.random.default_rng(seed);easy=n-4
    score=np.eye(n);score[easy:]=.2
    c=np.broadcast_to(score[:,:,None,None]/n,(n,n,n,n)).copy()
    prior=np.full((n,n),.2/max(1,n-1))
    np.fill_diagonal(prior,.8)
    prior[easy:]=1/n
    # Controlled scheduling workload: strong easy matches plus a tied tail.
    # No claim that this hand-constructed unary support is a hard vision problem.
    return c,prior,np.arange(n)


def run_case(c,prior,ps,mode,repetitions=3):
    times=[];result=None
    for _ in range(repetitions):
        start=time.perf_counter()
        result=MutualBestLabeler(c,prior,one_to_one=True,policy=FinalizationPolicy(mode=mode),
                                 prior_strength=ps,max_iterations=120,tol=1e-8).run()
        times.append(time.perf_counter()-start)
    return result, float(np.median(times)), times


def main():
    out=ROOT/'data';out.mkdir(exist_ok=True)
    rows=[];examples={}
    scenarios=[('geometric',geometry,False),('near_duplicate',geometry,True),('tied_tail',unresolved_tail,None)]
    for name,generator,flag in scenarios:
        for n in [12,24,36]:
            for seed in range(4):
                args=(n,seed+20261016)
                c,prior,truth=generator(*args,ambiguous=flag) if flag is not None else generator(*args)
                ref,base_time,base_samples=run_case(c,prior,.18,'off')
                for mode in ['off','audited','permanent']:
                    r,seconds,samples=(ref,base_time,base_samples) if mode=='off' else run_case(c,prior,.18,mode)
                    locked=np.flatnonzero(r.finalized)
                    row={'scenario':name,'n':n,'seed':seed,'mode':mode,'seconds_median':seconds,
                         'reference_seconds':base_time,'speedup':base_time/seconds,
                         'iterations':r.iterations,'reference_iterations':ref.iterations,
                         'finalized':int(r.finalized.sum()),'reopenings':r.statistics['reopenings'],
                         'assignment_disagreements':int(np.sum(r.assignments!=ref.assignments)),
                         'locked_disagreements':int(np.sum(r.assignments[locked]!=ref.assignments[locked])),
                         'correct':int(np.sum(r.assignments==truth)), 'reference_correct':int(np.sum(ref.assignments==truth)),
                         'max_strength_difference':float(np.max(np.abs(r.strengths-ref.strengths))),
                         'full_update_residual':r.full_update_residual,'numerically_converged':r.converged,
                         'stop_reason':r.stop_reason,'support_multiply_adds':r.statistics['support_multiply_adds'],
                         'work_ratio':r.statistics['support_multiply_adds']/ref.statistics['support_multiply_adds'],
                         'cache_rebuilds':r.statistics['cache_rebuilds'],'full_checks':r.statistics['full_checks'],
                         'timing_samples':samples}
                    rows.append(row)
                    if seed==0 and n==24:examples[f'{name}:{mode}']={'trace':r.trace,'audit_log':r.audit_log,'finalized_at':r.finalized_at.tolist(),'assignments':r.assignments.tolist()}
    c,prior,truth=delayed_swap();stress={}
    for mode in ['off','audited','permanent']:
        r=MutualBestLabeler(c,prior,one_to_one=True,policy=FinalizationPolicy(mode=mode),
                           prior_strength=0,max_iterations=120,tol=1e-9).run()
        stress[mode]={'assignments':r.assignments.tolist(),'iterations':r.iterations,'finalized_at':r.finalized_at.tolist(),
                      'reopenings':r.statistics['reopenings'],'full_update_residual':r.full_update_residual,
                      'stop_reason':r.stop_reason,'trace':r.trace,'audit_log':r.audit_log}
    assert stress['off']['assignments']==truth.tolist()
    assert stress['permanent']['assignments']!=truth.tolist()
    assert stress['audited']['assignments']==truth.tolist() and stress['audited']['reopenings']>=2
    summary=[]
    for name,_,_ in scenarios:
        for mode in ['off','audited','permanent']:
            group=[r for r in rows if r['scenario']==name and r['mode']==mode]
            summary.append({'scenario':name,'mode':mode,'cases':len(group),
                            'median_speedup':float(np.median([r['speedup'] for r in group])),
                            'median_work_ratio':float(np.median([r['work_ratio'] for r in group])),
                            'assignment_disagreements':sum(r['assignment_disagreements'] for r in group),
                            'locked_disagreements':sum(r['locked_disagreements'] for r in group),
                            'correct':sum(r['correct'] for r in group),'reference_correct':sum(r['reference_correct'] for r in group),
                            'total_objects':sum(r['n'] for r in group),'finalized':sum(r['finalized'] for r in group)})
    sources=[ROOT.parent/'hrl/finalization.py',ROOT.parent/'hrl/core.py',Path('/home/rmichaelglover/Code/relaxation-labeling/cpp/source/relax/relax.cpp'),Path(__file__)]
    result={'date':'2026-10-16','kind':'seeded synthetic pilot; heuristic assignments, not fixed-point equivalence',
            'policy':FinalizationPolicy().__dict__,'protocol':{'seeds':list(range(4)),'sizes':[12,24,36],
            'timing_repetitions':3,'max_iterations':120,'tol':1e-8,'prior_strength':.18,
            'input_generation_in_timing':False,'constructor_and_cache_cost_in_timing':True},
            'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
            'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'summary':summary,'runs':rows,'examples':examples,'delayed_swap':stress}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    with (out/'runs.csv').open('w') as f:
        fields=[k for k in rows[0] if k!='timing_samples'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
        w.writerows({k:v for k,v in row.items() if k in fields} for row in rows)
    lines=['# Mutual-best early finalization: first measured pilot','',
           'Michael Emanuel Glover · 16 October 2026 · synthetic correspondence experiments','',
           'Matched comparator: identical dense-to-matrix update with finalization disabled. Timing includes constructor copies, cache packing, audits, and result construction. Input generation is excluded for all methods. Three timing repetitions per case; four seeds at each of 12, 24, and 36 objects. These are exploratory local timings, not a calibrated risk guarantee.','',
           '| Scenario | Policy | Median speedup | Median work ratio | Disagreements / objects | Locked disagreements | Finalized |',
           '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in summary:
        lines.append(f"| {r['scenario']} | {r['mode']} | {r['median_speedup']:.3f}× | {r['median_work_ratio']:.3f} | {r['assignment_disagreements']} / {r['total_objects']} | {r['locked_disagreements']} | {r['finalized']} |")
    lines+=['','## Delayed support reversal','',
            'A four-object fixed compatibility tensor makes two initially strong reciprocal winners swap after a weak driver gains strength. Permanent locking retains wrong early labels; periodic full support audits reopen them. This is one tested recovery case, not proof that auditing catches every late reversal.','']
    for mode,r in stress.items():lines.append(f"- {mode}: {r['assignments']}; {r['iterations']} sweeps; {r['reopenings']} reopenings; full-update residual {r['full_update_residual']:.4g}.")
    lines+=['','## Interpretation','',
            'The geometric cases use noisy, shuffled 3D point constellations and partial informative priors. The near-duplicate cases deliberately make two identities geometrically ambiguous. The tied-tail workload is a hand-built scheduling control with four unresolved tied rows, not an independent real-data benchmark. Ground-truth accuracy and unfrozen-reference agreement are separate columns in the CSV/JSON.','',
            'Frozen distributions remain soft. A stopped finalized solution can have a nonzero full-update residual and different strengths from the unfrozen solution. `converged` is true only when that full residual is below tolerance. Cache arithmetic, audits, and rebuilding are charged to the work count. Multiplication counts exclude memory copies, sorting, and allocation; wall-clock measurements include them.','',
            'Three observed mutual wins are an operational policy, not a theorem about future winners or truth. Column comparisons use raw support, which can be degree-biased on irregular graphs. Ordinary many-to-one class labeling is outside this policy. Real marker logs, larger label vocabularies, distribution shifts, and stronger assignment baselines remain future evaluation.']
    (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
