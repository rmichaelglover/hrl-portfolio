from pathlib import Path
from dataclasses import asdict
import csv,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import Parameters,simulate,metrics,POLICIES,S,R,E,O,H
from vendor.hrl_engine import HRL,pairwise_factor,triangle_factor
BASE=Path(__file__).resolve().parent
OUT=BASE/'output'; OUT.mkdir(exist_ok=True)

def inference_demo():
    rng=np.random.default_rng(204); n=120
    # Synthetic patch labels; homophily is true by construction, not learned biology.
    truth=np.repeat(np.arange(4),30)
    logits=rng.normal(0,1.4,(n,4)); logits[np.arange(n),truth]+=1.5
    prior=np.exp(logits-logits.max(axis=1,keepdims=True)); prior/=prior.sum(axis=1,keepdims=True)
    edges=np.array([(i,i+1) for i in range(n-1) if (i+1)%30])
    triangles=np.array([(i,i+1,i+2) for i in range(n-2) if i%30<28])
    c=np.zeros((4,4,4)); c[np.arange(4),np.arange(4),np.arange(4)]=1
    modes={'prior':[], 'pairwise':[pairwise_factor(edges,np.eye(4))],
           'pairwise_and_triples':[pairwise_factor(edges,np.eye(4)),triangle_factor(triangles,c)]}
    result={}
    for name,factors in modes.items():
        fit=HRL(n,4,factors,prior,prior_strength=.8,max_iterations=200,tol=1e-8).run()
        assert np.allclose(fit.strengths.sum(axis=1),1)
        result[name]={'synthetic_accuracy':float(np.mean(fit.assignments==truth)),
                     'converged':bool(fit.converged),'iterations':int(fit.iterations)}
    # Unknown state remains an explicit option; it is not a calibrated uncertainty.
    unknown=HRL(n,4,modes['pairwise'],prior,noise=True,noise_gain=.6,max_iterations=200).run()
    result['unknown_label']={'rejected':int((unknown.assignments==-1).sum()),'converged':bool(unknown.converged)}
    return result

fig,axs=plt.subplots(2,2,figsize=(11,8),layout='constrained')
nominal={}
for policy in POLICIES:
    rows=simulate(policy); a=rows[:,2:17].reshape(-1,3,5); t=rows[:,0]
    nominal[policy]=metrics(rows)
    names=['time','input']+[f'{site}_{var}' for site in ['primary','secondary','third'] for var in ['sensitive','resistant','immune','resource','reserve']]+['exposure']
    with (OUT/f'{policy}.csv').open('w') as f:
        w=csv.writer(f); w.writerow(names); w.writerows(rows)
    axs[0,0].plot(t,a[:,:,:2].sum(axis=(1,2)),label=policy)
    axs[0,1].plot(t,a[:,:,R].sum(axis=1),label=policy)
    axs[1,0].plot(t,a[:,:,H].min(axis=1),label=policy)
    axs[1,1].plot(t,rows[:,-1],label=policy)
for ax,title in zip(axs.ravel(),['Total tumor population','Resistant population','Minimum healthy reserve','Systemic exposure']):
    ax.set(title=title,xlabel='Dimensionless time'); ax.grid(alpha=.2); ax.legend(fontsize=8)
fig.suptitle('Uncalibrated synthetic model — not patient predictions'); fig.savefig(OUT/'trajectories.png',dpi=180); plt.close(fig)
rng=np.random.default_rng(42); ensemble=[]
# Shared parameter draw across policies; arbitrary ranges, not a patient distribution.
for replicate in range(24):
    p=Parameters(growth=float(rng.uniform(.16,.29)),resistant_growth=float(rng.uniform(.12,.25)),
                 kill_sensitive=float(rng.uniform(.4,.85)),kill_resistant=float(rng.uniform(.02,.16)),
                 toxicity=float(rng.uniform(.06,.18)),migration=float(rng.uniform(.005,.03)))
    for policy in POLICIES:
        ensemble.append({'replicate':replicate,'policy':policy,'parameters':asdict(p),**metrics(simulate(policy,p))})
fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
for policy in POLICIES:
    pts=[r for r in ensemble if r['policy']==policy]
    ax.scatter([r['min_reserve'] for r in pts],[r['final_burden'] for r in pts],label=policy,alpha=.7)
ax.set(xlabel='Minimum healthy tissue reserve',ylabel='Final tumor population',title='Synthetic parameter sensitivity: burden and tissue preservation'); ax.legend(); ax.grid(alpha=.2)
fig.savefig(OUT/'tradeoffs.png',dpi=180);plt.close(fig)
results={'status':'uncalibrated synthetic feasibility prototype','seed':42,'replicates':24,'parameters':asdict(Parameters()),
         'nominal':nominal,'ensemble':ensemble,'inference':inference_demo()}
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'nominal':nominal,'inference':results['inference']},indent=2))
manifest={'files':[]}
for p in sorted(BASE.rglob('*')):
    if p.is_file() and '__pycache__' not in str(p) and p.name not in ['manifest.json','VIRTUAL-BODY-SOURCE.zip']:
        manifest['files'].append({'path':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2))
