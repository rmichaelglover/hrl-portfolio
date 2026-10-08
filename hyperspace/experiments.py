"""Reproduce original toy experiments and vector plots; python3 experiments.py."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
HERE=Path(__file__).resolve().parent
OUT=HERE/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fbfaf5','axes.facecolor':'#fbfaf5','savefig.facecolor':'#fbfaf5','pdf.fonttype':42})
colors=['#287e88','#da9657','#826aab']
def save(name):
    plt.tight_layout();plt.savefig(OUT/(name+'.pdf'),bbox_inches='tight');plt.savefig(OUT/(name+'.png'),dpi=170,bbox_inches='tight');plt.close()
def effective(A,alpha=.5):
    return (1-alpha)*np.eye(len(A))+alpha*A/A.sum(1)[:,None]
# Diagram: one location, distinct information layers.
fig,ax=plt.subplots(figsize=(8,3.7));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off')
for y,label,col in [(1,'Physical location: geography',colors[0]),(2.5,'Information: observations + provenance',colors[1]),(4,'Interpretation: roles + choices',colors[2])]:
    ax.plot([1,9],[y,y],lw=20,color=col,alpha=.17)
    ax.scatter([2,5,8],[y]*3,s=110,color=col);ax.text(1,y+.32,label,weight='bold',color=col)
for x in [2,5,8]:
    ax.annotate('',(x,3.8),(x,1.2),arrowprops=dict(arrowstyle='<->',color='#485653',lw=1.2))
ax.text(5,.2,'Coupled descriptions do not create extra physical dimensions.',ha='center')
save('layers')
# Relativity: diagram in c=1 units.
fig,ax=plt.subplots(figsize=(7,4));x=np.linspace(-2,2,201)
ax.fill_between(x,abs(x),2,color=colors[0],alpha=.19);ax.fill_between(x,-2,-abs(x),color=colors[2],alpha=.16)
ax.plot(x,abs(x),color=colors[0]);ax.plot(x,-abs(x),color=colors[2]);ax.axhline(0,color='#888',lw=.6);ax.axvline(0,color='#888',lw=.6)
ax.text(0,1.5,'Causal future',ha='center');ax.text(0,-1.5,'Causal past',ha='center');ax.text(1.5,.15,'Spacelike',ha='center');ax.scatter([0],[0],color='#222')
ax.set(xlabel='Spatial coordinate x',ylabel='Time coordinate ct',xlim=(-2,2),ylim=(-2,2));save('causal')
# Cycle + reproducible information shortcuts; anchored at node 0.
rng=np.random.default_rng(20261008);n=40;Ag=np.zeros((n,n))
for i in range(n):Ag[i,(i+1)%n]=Ag[(i+1)%n,i]=1
Ac=np.zeros_like(Ag);pairs=[]
while len(pairs)<12:
    i,j=sorted(rng.choice(n,2,replace=False))
    if Ag[i,j]==0 and Ac[i,j]==0:Ac[i,j]=Ac[j,i]=1;pairs.append([int(i),int(j)])
Ah=Ag+.35*Ac
fig,ax=plt.subplots(figsize=(7,4.8));theta=np.arange(n)*2*np.pi/n;xy=np.c_[np.cos(theta),np.sin(theta)]
for i in range(n):j=(i+1)%n;ax.plot(xy[[i,j],0],xy[[i,j],1],color=colors[0],lw=1.5)
for i,j in pairs:ax.plot(xy[[i,j],0],xy[[i,j],1],color=colors[1],alpha=.8,lw=1)
ax.scatter(xy[:,0],xy[:,1],s=35,color=colors[0]);ax.scatter(*xy[0],s=180,marker='*',color='#222',label='Fixed home')
ax.set_aspect('equal');ax.axis('off');ax.legend(loc='upper left');save('graph')
metrics={'seed':20261008,'shortcuts':pairs,'cycle_nodes':n,'alpha':.5,'shortcut_weight':.35}
fig,axs=plt.subplots(1,2,figsize=(9,3.7));series=[]
for A,label,col in [(Ag,'Geographic cycle',colors[0]),(Ah,'Cycle + information links',colors[1])]:
    T=effective(A);Q=T[1:,1:];R=T[1:,:1];Z=np.linalg.inv(np.eye(n-1)-Q);K=Z@R
    assert np.allclose(K,1,atol=1e-11)
    rho=float(max(abs(np.linalg.eigvals(Q))));e=np.ones(n-1);errors=[]
    for t in range(4001):errors.append(float(max(abs(e))));e=Q@e
    errors=np.array(errors);cross=np.flatnonzero(errors<1e-3)
    metrics[label]={'rho':rho,'max_expected_absorption_steps':float(max(Z.sum(1))),'first_step_below_0.001':int(cross[0]) if len(cross) else None}
    axs[0].semilogy(errors,label=label,color=col);axs[1].plot(Z.sum(1),color=col,label=label);series.append(errors)
axs[0].set(xlabel='Iteration',ylabel='Maximum distance from home');axs[0].legend(fontsize=8)
axs[1].set(xlabel='Unanchored node index',ylabel='Expected updates to absorption');save('mixing')
np.savetxt(HERE/'convergence.csv',np.column_stack([np.arange(4001),*series]),delimiter=',',header='iteration,geographic_error,hybrid_error',comments='')
# Three anchors, triangular lattice, six possible neighboring directions.
m=18;verts=[(i,j) for i in range(m+1) for j in range(m+1-i)];ix={v:k for k,v in enumerate(verts)};a=np.zeros((len(verts),len(verts)))
for (i,j),k in ix.items():
    for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]:
        v=(i+di,j+dj)
        if v in ix:a[k,ix[v]]=1
b=[ix[(0,0)],ix[(m,0)],ix[(0,m)]];u=[k for k in range(len(verts)) if k not in b];T=effective(a)
Q=T[np.ix_(u,u)];R=T[np.ix_(u,b)];p=np.zeros((len(verts),3));p[b]=np.eye(3);p[u]=np.linalg.solve(np.eye(len(u))-Q,R)
assert np.max(abs(p.sum(1)-1))<1e-12 and p.min()>-1e-12
res=float(np.max(abs(p[u]-(T@p)[u])));metrics['ternary']={'nodes':len(verts),'harmonic_residual':res}
xy=np.array([(i+j/2,np.sqrt(3)*j/2) for i,j in verts]);palette=np.array([[.16,.49,.53],[.85,.59,.34],[.51,.42,.67]])
fig,axs=plt.subplots(1,2,figsize=(9,3.8));axs[0].scatter(*xy.T,c=p@palette,s=60);axs[0].scatter(*xy[b].T,c=palette,s=190,marker='*',edgecolors='#222')
axs[0].set(title='Space: harmonic label mixtures',aspect='equal');axs[0].axis('off')
sxy=np.c_[p[:,1]+p[:,2]/2,np.sqrt(3)*p[:,2]/2];axs[1].plot([0,1,.5,0],[0,0,np.sqrt(3)/2,0],color='#888');axs[1].scatter(*sxy.T,c=p@palette,s=18)
axs[1].set(title='Information: the ternary simplex',aspect='equal');axs[1].axis('off');save('ternary')
# Nonlinear equal-label compatibility instability and entropy.
fig,axs=plt.subplots(1,2,figsize=(9,3.6))
for x0,col in zip([.49,.5,.51],colors):
    x=x0;xx=[]
    for t in range(11):xx.append(x);x=x*x/(x*x+(1-x)**2)
    xx=np.array(xx);h=-np.sum(np.where(np.c_[xx,1-xx]>0,np.c_[xx,1-xx]*np.log2(np.maximum(np.c_[xx,1-xx],1e-300)),0),axis=1)
    axs[0].plot(xx,'o-',color=col,label=f'Initial label weight {x0}');axs[1].plot(h,'o-',color=col)
axs[0].set(xlabel='Relaxation step',ylabel='Weight of label A',ylim=(-.03,1.03));axs[0].legend(fontsize=8)
axs[1].set(xlabel='Relaxation step',ylabel='Shannon entropy (bits)',ylim=(-.03,1.03));save('nonlinear')
# Time-varying counterexample and period-two counterexample.
t=np.arange(101);dec=(t+2)/(2*(t+1));fig,axs=plt.subplots(1,2,figsize=(9,3.5))
axs[0].plot(t,dec,color=colors[1]);axs[0].axhline(.5,color='#777',ls='--');axs[0].set(xlabel='Iteration',ylabel='Error / initial error',title='Every step has a home edge; error persists')
tt=np.arange(20);axs[1].plot(tt,(-1.)**tt,'o-',color=colors[2],label='Full update: alpha = 1');axs[1].plot(tt,.2**tt,'o-',color=colors[0],label='Lazy update: alpha = 0.4');axs[1].legend(fontsize=8);axs[1].set(xlabel='Iteration',ylabel='Difference of two node values',title='Periodicity without laziness');save('failures')
# Exact small-chain example and block stopping certificate.
Q=np.array([[.4,.3],[.6,.4]]);Z=np.linalg.inv(np.eye(2)-Q);assert np.allclose(Z,[[10/3,5/3],[10/3,10/3]])
e=np.ones(2);err=[];cert=[]
for t in range(70):err.append(max(abs(e)));cert.append(max(abs(Q@Q@e-e))/.18);e=Q@e
assert np.all(np.array(err)<=np.array(cert)+1e-14)
fig,ax=plt.subplots(figsize=(7,3.7));ax.semilogy(err,label='Actual error',color=colors[0]);ax.semilogy(.82**(np.arange(70)//2),label='Proven two-step bound',color=colors[1]);ax.semilogy(cert,label='Residual certificate',color=colors[2],ls='--');ax.set(xlabel='Iteration',ylabel='Maximum error / bound');ax.legend();save('certificate')
metrics['small_chain']={'rho':float(max(abs(np.linalg.eigvals(Q)))),'block_delta':.18,'expected_steps':Z.sum(1).tolist()}
(HERE/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('PASS: absorbing weights, simplex, harmonic residual, exact inverse, and stopping bounds.')
