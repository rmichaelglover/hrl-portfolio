#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,sympy as sp,json
from scipy.integrate import quad
from pathlib import Path
R=Path(__file__).resolve().parent;F=R/'figures';F.mkdir(exist_ok=True)
# Columns identify source states; rows identify destination states.
D=sp.Matrix([[1,0,1,0],[0,1,0,1],[0,0,0,0],[0,0,0,0]])
T=sp.Matrix([[1,1,0,0],[0,0,0,0],[0,0,1,0],[0,0,0,1]])
C=T*D-D*T
assert C==sp.Matrix([[0,0,0,1],[0,0,0,-1],[0,0,0,0],[0,0,0,0]])
assert D*D==D and T*T==T
for M in [D,T]:assert all(sum(M[:,j])==1 for j in range(4))
# Exhaustive propositional check of the observer-state partition.
for a in [False,True]:
 for j in [False,True]:assert sum([a and j,a and not j,not a and j,not a and not j])==1
normal=lambda x:np.exp(-x*x/2)/np.sqrt(2*np.pi)
half=lambda x:2*normal(x)
def projected(y):
 if not 0<=y<1:return 0.
 x=y/(1-y);return half(x)/(1-y)**2
mass_normal=quad(normal,-np.inf,np.inf)[0];mass_projective=quad(projected,0,1)[0]
assert abs(mass_normal-1)<1e-10 and abs(mass_projective-1)<1e-10
# Finite binary paths inject into ternary Cantor-stage endpoints.
for n in range(1,11):
 values={sum(sp.Rational(2*int(bit),3**(i+1)) for i,bit in enumerate(format(k,f'0{n}b'))) for k in range(2**n)}
 assert len(values)==2**n
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150,'savefig.dpi':300})
def save(fig,name):
 fig.tight_layout();fig.savefig(F/(name+'.pdf'),bbox_inches='tight');fig.savefig(F/(name+'.png'),bbox_inches='tight');plt.close(fig)
labels=['KK','KU','UK','UU'];fig,axs=plt.subplots(1,3,figsize=(11,3.5))
for ax,M,title in zip(axs,[D,T,C],['Discovery D','Resolution R','Commutator RD − DR']):
 im=ax.imshow(np.array(M,dtype=float),vmin=-1,vmax=1,cmap='RdBu');ax.set_xticks(range(4),labels);ax.set_yticks(range(4),labels);ax.set_title(title);ax.set_xlabel('Source');ax.set_ylabel('Destination')
 for i in range(4):
  for j in range(4):ax.text(j,i,str(M[i,j]),ha='center',va='center',color='white' if abs(M[i,j]) else '#222')
save(fig,'operators')
fig,ax=plt.subplots(figsize=(9,3));ax.axis('off')
for y,states in [(.7,['UU','KU','KK']),(.25,['UU','UU','KU'])]:
 for x,s in zip([.12,.5,.88],states):ax.text(x,y,s,ha='center',va='center',fontsize=17,bbox={'boxstyle':'round,pad=.5','facecolor':'#DDEDF2','edgecolor':'#0072B2'},transform=ax.transAxes)
 for x1,x2,lab in zip([.17,.55],[.45,.83],['D','R'] if y>.5 else ['R','D']):
  ax.annotate('',xy=(x2,y),xytext=(x1,y),xycoords='axes fraction',arrowprops={'arrowstyle':'->'});ax.text((x1+x2)/2,y+.10,lab,ha='center',transform=ax.transAxes)
ax.set_title('The order of inquiry changes what the second operation can settle');save(fig,'paths')
fig,axs=plt.subplots(1,2,figsize=(10,3.8));intervals=[(0,1)]
for n in range(8):
 for a,b in intervals:axs[0].plot([a,b],[n,n],color='#0072B2',lw=max(1,6-n*.5))
 intervals=[z for a,b in intervals for z in [(a,a+(b-a)/3),(b-(b-a)/3,b)]]
axs[0].set(xlabel='Position in [0,1]',ylabel='Construction stage',title='a | Cantor-stage intervals');axs[0].invert_yaxis()
n=np.arange(16);axs[1].semilogy(n,(2/3)**n,'o-',color='#D55E00');axs[1].set(xlabel='Stage n',ylabel='Retained length (2/3)^n',title='b | Finite-stage measure');save(fig,'cantor')
fig,axs=plt.subplots(1,2,figsize=(10,3.8));x=np.linspace(-5,5,600)
for a in [.5,1,2]:axs[0].plot(x,normal(x/a)/a,label=f'scale a={a}')
axs[0].legend();axs[0].set(xlabel='Coordinate y',ylabel='Density',title='a | Affine views; total mass = 1')
y=np.linspace(0,.995,600);axs[1].plot(y,[projected(v) for v in y],color='#009E73');axs[1].set(xlabel='y = x/(1+x)',ylabel='Transformed half-normal density',title='b | A projective coordinate example');save(fig,'densities')
fig=plt.figure(figsize=(8,4.8));ax=fig.add_subplot(111,projection='3d');X,A=np.meshgrid(np.linspace(-4,4,120),np.linspace(.4,2.5,90));Z=np.exp(-(X/A)**2/2)/(A*np.sqrt(2*np.pi));ax.plot_surface(X,A,Z,cmap='viridis',linewidth=0);ax.set(xlabel='Coordinate y',ylabel='Scale a',zlabel='Density',title='Analytic density under a family of affine coordinates');save(fig,'density_3d')
fig,ax=plt.subplots(figsize=(10,3));ax.axis('off')
for x,title in zip([.1,.36,.63,.9],['Premises\nand rules','Derivation\nand checking','Model\ninterpretation','Empirical\ncomparison']):ax.text(x,.5,title,ha='center',va='center',bbox={'boxstyle':'round,pad=.7','facecolor':'#E9F2EE','edgecolor':'#009E73'},transform=ax.transAxes)
for a,b in zip([.18,.44,.71],[.28,.55,.82]):ax.annotate('',xy=(b,.5),xytext=(a,.5),xycoords='axes fraction',arrowprops={'arrowstyle':'->'})
ax.set_title('Different questions require different forms of justification');save(fig,'justification')
report={'status':'verified mathematical examples, not empirical findings','partition_cases':4,'D':np.array(D).astype(int).tolist(),'R':np.array(T).astype(int).tolist(),'RD_minus_DR':np.array(C).astype(int).tolist(),'discovery_idempotent':True,'resolution_idempotent':True,'normal_integral':mass_normal,'projective_integral':mass_projective,'finite_cantor_injection_verified_through_stage':10,'figures':6}
(R/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
