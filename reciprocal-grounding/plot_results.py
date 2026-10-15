#!/usr/bin/env python3
"""Publication figures from the committed benchmark artifact."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'data/results.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
COLORS=['#1d6b99','#d58926','#178365','#835ca5','#b94f58']

def save(fig,name):
    fig.savefig(ROOT/f'figures/{name}.png',bbox_inches='tight')
    fig.savefig(ROOT/f'figures/{name}.pdf',bbox_inches='tight')
    plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
rows=[r for r in D['results'] if r['scenario']=='Independent views']
for ax,key,label in zip(axes,['accuracy','coverage'],['Accuracy among accepted pairs','Coverage over all things (including unknowns)']):
    vals=[r[key] for r in rows];ci=[r[key+'_ci95'] for r in rows]
    ax.bar(np.arange(len(rows)),vals,color=COLORS,width=.65)
    ax.errorbar(np.arange(len(rows)),vals,yerr=[[v-c[0] for v,c in zip(vals,ci)],[c[1]-v for v,c in zip(vals,ci)]],fmt='none',ecolor='#242b36',capsize=3)
    ax.set_xticks(range(len(rows)),[r['method'].replace(' ','\n') for r in rows]);ax.set_ylim(0,1.09);ax.set_ylabel(label)
    for i,v in enumerate(vals):ax.text(i,v+.035,f'{v:.1%}',ha='center',fontsize=9)
fig.suptitle('Independent views · held-out seeds 100–139\nThresholds selected on seeds 0–19; 95% seed-bootstrap intervals')
save(fig,'accuracy-coverage')
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
for ax,scenario in zip(axes.flat,D['scenarios']):
    for method,color in zip(D['methods'],COLORS):
        points=D['curves'][scenario][method]
        ax.plot([p['coverage'] for p in points],[p['risk'] for p in points],label=method,color=color,lw=1.7)
    ax.set_title(scenario);ax.set_xlabel('Coverage (all things)');ax.set_ylabel('Error among accepted pairs');ax.set_xlim(0,.85);ax.set_ylim(-.02,1.02);ax.grid(alpha=.15)
axes[0,0].legend(fontsize=8);fig.suptitle('Risk–coverage curves · pooled held-out candidates\nCurves stop at available candidates; no extrapolation or calibration guarantee')
save(fig,'risk-coverage')
ex=D['example'];f=np.array(ex['forward']);r=np.array(ex['reverse']);prior=np.array(ex['prior']);agreement=np.sqrt(f[:,:-1]*r[:,:-1].T)
fig,axes=plt.subplots(1,3,figsize=(12,5),layout='constrained')
for ax,array,title in zip(axes,[prior[:,:-1],f[:,:-1],agreement],['Forward prior','Relaxed forward strength','Reciprocal geometric-mean strength']):
    image=ax.imshow(array,vmin=0,vmax=1,cmap='viridis',aspect='auto');ax.set_title(title);ax.set_xlabel('Word / label index');ax.set_ylabel('Thing index');ax.set_yticks([0,5,10,15,19]);ax.axhline(15.5,color='white',ls=':',lw=.8)
fig.colorbar(image,ax=list(axes),label='Strength (not calibrated probability)',shrink=.7)
fig.suptitle('Seed 100 · 16 named things + 4 unknown distractors\nDashed line separates unknown rows; unknown columns omitted from these displays')
save(fig,'strength-fields')
print('Saved three standalone PNG/PDF figure pairs.')
