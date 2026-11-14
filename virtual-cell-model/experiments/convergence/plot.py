"""Render measured C++ CSV output; no solver logic lives here."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
read=lambda name:list(csv.DictReader((ROOT/name).open()))
traces=read('traces.csv'); summary=read('summary.csv'); maps=read('compatibility.csv'); states=read('states.csv')
cases=list(dict.fromkeys(r['case'] for r in summary)); solvers=['relax-0.5','relax-1.0','newton']; colors=['#277da8','#d86522','#7853a6']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#faf9f5','axes.facecolor':'#faf9f5'})
def save(fig,name):
    fig.savefig(ROOT/(name+'.svg'),bbox_inches='tight');fig.savefig(ROOT/(name+'.png'),dpi=170,bbox_inches='tight');plt.close(fig)
for xkey,name,label in [('iteration','convergence','Accepted updates'),('evaluations','work','Map evaluations (includes Jacobian + line search)')]:
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    for ax,case in zip(axes.flat,cases):
        for solver,color in zip(solvers,colors):
            rows=[r for r in traces if r['case']==case and r['solver']==solver]
            ax.semilogy([int(r[xkey]) for r in rows],[max(float(r['residual']),1e-17) for r in rows],color=color,label=solver,lw=2)
        ax.axhline(1e-10,color='#56635b',ls=':',lw=1); ax.set_title(case);ax.set_xlabel(label);ax.set_ylabel('max |T(p) − p|');ax.grid(alpha=.15)
    axes.flat[-1].axis('off');axes.flat[-1].legend(*axes.flat[0].get_legend_handles_labels(),loc='center')
    fig.suptitle('Same map, same start, same residual target · 500-update budget',fontsize=15);fig.tight_layout();save(fig,name)
fig,ax=plt.subplots(figsize=(11,5)); x=np.arange(len(cases));
for j,(solver,color) in enumerate(zip(solvers,colors)):
    rows=[next(r for r in summary if r['case']==case and r['solver']==solver) for case in cases]
    values=np.array([float(r['median_us']) for r in rows]);lo=np.array([float(r['min_us']) for r in rows]);hi=np.array([float(r['max_us']) for r in rows])
    bars=ax.bar(x+(j-1)*.25,values,.24,color=color,label=solver,yerr=[values-lo,hi-values],capsize=2,error_kw={'lw':.8})
    for bar,row in zip(bars,rows):
        if row['converged']=='0':bar.set_hatch('///');bar.set_edgecolor('#242c32')
ax.set_xticks(x,cases);ax.set_yscale('log');ax.set_ylabel('Runtime (µs), log scale');ax.legend();ax.set_title('Median of 21 runs · whiskers: min–max · hatched: target not reached');fig.tight_layout();save(fig,'runtime')
fig,axes=plt.subplots(1,2,figsize=(12,5))
for ax,case in zip(axes,['gentle-8','conflicting-ring']):
    a=np.zeros((16,16))
    for r in maps:
        if r['case']==case:a[int(r['row']),int(r['column'])]+=float(r['weight'])
    im=ax.imshow(a,cmap='RdBu',vmin=-.5,vmax=.5);ax.set_title(case+' · raw C (before coupling)');ax.set_xlabel('Source object × label');ax.set_ylabel('Receiving object × label')
fig.colorbar(im,ax=axes.ravel().tolist(),label='Signed compatibility weight',shrink=.8);save(fig,'compatibility')
fig=plt.figure(figsize=(12,5));u,v=np.meshgrid(np.linspace(0,1,51),np.linspace(0,1,51))
for j,(beta,sign,title) in enumerate([(.4,1,'Gentle agreement · β = 0.4'),(6,-1,'Conflicting ring · β = 6')]):
    ax=fig.add_subplot(1,2,j+1,projection='3d');z=1/(1+np.exp(-(np.log(.52/.48)+sign*2*beta*(u+v-1))))
    ax.plot_surface(u,v,z,cmap='viridis',vmin=0,vmax=1,linewidth=0,alpha=.93);ax.set_xlabel('Left neighbor: label 0');ax.set_ylabel('Right neighbor: label 0');ax.set_zlabel('Target strength');ax.set_title(title);ax.view_init(25,-125)
fig.subplots_adjust(left=.12,right=.93,wspace=.35)
fig.suptitle('Local compatibility response Tᵢ(p) · representative prior (0.52, 0.48)');save(fig,'response-3d')
fig,axes=plt.subplots(1,2,figsize=(12,4))
for ax,case in zip(axes,['strong-agreement','conflicting-ring']):
    a=np.array([[float(r['label0']) for r in states if r['case']==case and r['solver']==s] for s in solvers])
    im=ax.imshow(a,vmin=0,vmax=1,cmap='viridis',aspect='auto');ax.set_yticks(range(3),solvers);ax.set_xlabel('Object');ax.set_title(case+' · final label-zero strength')
fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.8);save(fig,'final-states')
print('Rendered six figures as SVG and PNG.')
# Local stability of the SAME map at each reported terminal state.
with (ROOT/'stability.csv').open('w') as out:
    writer=csv.writer(out);writer.writerow(['case','solver','residual_target_met','rho_full','rho_half'])
    for row in summary:
        n=int(row['n']);beta=float(row['coupling']);case=row['case'];sign=-1 if case=='conflicting-ring' else 1
        p=np.array([float(r['label0']) for r in states if r['case']==case and r['solver']==row['solver']])
        prior=np.array([.50001+.000001*np.sin(i+.3) if case=='near-critical' else .52+.015*np.sin(i+.3) for i in range(n)])
        t=1/(1+np.exp(-(np.log(prior/(1-prior))+sign*2*beta*(np.roll(p,1)+np.roll(p,-1)-1))))
        jac=np.zeros((n,n))
        for i in range(n):
            for j in [(i+1)%n,(i+n-1)%n]:jac[i,j]+=sign*2*beta*t[i]*(1-t[i])
        writer.writerow([case,row['solver'],row['converged'],max(abs(np.linalg.eigvals(jac))),max(abs(np.linalg.eigvals(.5*np.eye(n)+.5*jac)))])
