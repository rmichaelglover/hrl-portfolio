#!/usr/bin/env python3
"""Plot the candidate reaction cycle; no microscopic rate is empirically fitted."""
import csv
import io
import json
from pathlib import Path
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
raw=subprocess.check_output([str(ROOT/'build/enzyme_cycle_demo')],text=True)
(HERE/'trajectories.csv').write_text(raw)
rows=list(csv.DictReader(io.StringIO('\n'.join(x for x in raw.splitlines() if not x.startswith('#')))))
for row in rows:
    for key in row:row[key]=float(row[key])

def analytic(li,release_bound=.2):
    a,c,d,r,u=2,3,.5,1,.5
    b=li
    determinant=r*(release_bound+u)+b*release_bound
    dwell=(release_bound+u+b)/determinant
    free=(1+d/c)/a
    flux=1/(free+1/c+dwell)
    return flux,np.array([flux*free,flux/c,flux*(release_bound+u)/determinant,flux*b/determinant])

for row in rows:
    assert abs(sum(row[key] for key in ['free','substrate_bound','products_bound','products_lithium'])-1)<1e-11
    assert abs(row['stationary_flux']-analytic(row['lithium_mm'])[0])<1e-12
final=[r for r in rows if r['time_s']==60]
summary={'status':'candidate buffered microscopic mechanism, illustrative rates; distinct from fitted empirical assay layer',
         'reference':'Leech et al. 1993 doi:10.1111/j.1432-1033.1993.tb17707.x motivates examining product-associated states; does not determine these rates or joint release pathway',
         'isolated_one_second_probability':{'rate_1_per_s':float(-np.expm1(-1)), 'rate_0_2_per_s':float(-np.expm1(-.2))},
         'final_states':final,
         'no_effect_control':{'lithium_mm':5,'equal_product_release_rates':True,'stationary_flux':analytic(5,1)[0]},
         'validation':'Seven CTest suites; exact-event sample mean versus master equation; stationary analytic solution; probability normalization; semigroup propagation.'}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
t=np.linspace(0,5,200)
for rate in [1,.2]:axes[0,0].plot(t,-np.expm1(-rate*t),label=f'k = {rate:g} per second')
axes[0,0].set(title='A  Fixed-rate release probability',xlabel='Time interval (s)',ylabel='Probability');axes[0,0].legend()
li=np.linspace(0,5,200)
axes[0,1].plot(li,[analytic(x)[0] for x in li],label='Slower release with bound Li')
axes[0,1].plot(li,[analytic(x,1)[0] for x in li],'--',label='Equal release-rate control')
axes[0,1].scatter([r['lithium_mm'] for r in final],[(r['expected_cycles']-next(x['expected_cycles'] for x in rows if x['time_s']==50 and x['lithium_mm']==r['lithium_mm']))/10 for r in final],marker='x',color='black',label='Population slope, 50–60 s')
axes[0,1].set(title='B  Network turnover',xlabel='Buffered Li (mM)',ylabel='Cycles per enzyme per second');axes[0,1].legend(fontsize=8)
for concentration in [0,1,5]:
    subset=[r for r in rows if r['lithium_mm']==concentration]
    axes[1,0].plot([r['time_s'] for r in subset],[r['expected_cycles'] for r in subset],label=f'Li {concentration:g} mM')
axes[1,0].set(title='C  Expected completed cycles',xlabel='Time (s)',ylabel='Cycles per enzyme');axes[1,0].legend()
fractions=np.array([analytic(x)[1] for x in li]).T
axes[1,1].stackplot(li,*fractions,labels=['Free','Substrate','Products','Products + Li'],colors=['#b8c9b8','#648c8b','#3f6591','#b65c3c'])
axes[1,1].set(title='D  Stationary occupancy',xlabel='Buffered Li (mM)',ylabel='Enzyme fraction');axes[1,1].legend(fontsize=8,loc='upper left')
fig.suptitle('A product-release candidate mechanism\nIllustrative microscopic rates; not fitted to assay data or human outcomes',fontsize=14)
for ax in axes.flat:ax.grid(alpha=.12)
fig.savefig(HERE/'reaction-cycle.png',dpi=180)
fig.savefig(HERE/'reaction-cycle.pdf',metadata={'CreationDate':None,'ModDate':None})
print(json.dumps({'probabilities':summary['isolated_one_second_probability'], 'stationary_flux_li0':analytic(0)[0],'stationary_flux_li5':analytic(5)[0],'null_control':analytic(5,1)[0]},indent=2))
