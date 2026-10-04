"""Synthetic geometry experiments. No patients, diagnosis or medication dosing."""
from pathlib import Path
import json,itertools
import numpy as np
from scipy.stats import multivariate_normal,norm
from scipy.integrate import quad,quad_vec
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent;F=B/'figures';F.mkdir(exist_ok=True)
rng=np.random.default_rng(20261004)
w=np.array([.25,.2,.55]);mu=np.array([[1.4,-.2,.6,.2],[-.3,1.3,.4,-.2],[0,0,-.2,0.]])
M=np.array([[1.,0,0],[0,1.,0],[0,0,1.],[.4,-.2,.3]])
covs=np.array([np.diag([.9,.7,.8,.5])**2,np.diag([.7,1.,.7,.6])**2,M@np.diag([.8,.7,.9])@M.T+.3**2*np.eye(4)])
assert np.all(np.linalg.eigvalsh(covs)>0) and w.sum()==1
pdfs=[multivariate_normal(m,c) for m,c in zip(mu,covs)]
def density(x):return sum(a*g.pdf(x) for a,g in zip(w,pdfs))
def save(fig,name):
 fig.savefig(F/f'{name}.pdf',bbox_inches='tight');fig.savefig(F/f'{name}.png',dpi=180,bbox_inches='tight');plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.titlesize':11})
x=np.linspace(-4,4,100);X,Y=np.meshgrid(x,x);xy=np.c_[X.ravel(),Y.ravel()]
latent=sum(a*multivariate_normal(m[:2],c[:2,:2]).pdf(xy) for a,m,c in zip(w,mu,covs)).reshape(X.shape)
fig=plt.figure(figsize=(9,5));ax=fig.add_subplot(111,projection='3d');ax.plot_surface(X,Y,latent,cmap='viridis',linewidth=0);ax.set(xlabel='Latent coordinate 1',ylabel='Latent coordinate 2',zlabel='Marginal density',title='Three-component 4D mixture: a 2D marginal');save(fig,'latent-mixture')
N=100000;k=rng.choice(3,N,p=w);samples=np.empty((N,4))
for j in range(3):samples[k==j]=rng.multivariate_normal(mu[j],covs[j],size=(k==j).sum())
h=1.;eps=.05;retained=samples[:,3]<h-eps;d=h-samples[retained,3];projected=samples[retained,:3]/d[:,None]
Z=float(sum(a*norm.cdf((h-eps-m[3])/np.sqrt(c[3,3])) for a,m,c in zip(w,mu,covs)))
observed=retained.mean();assert abs(observed-Z)<5*np.sqrt(Z*(1-Z)/N)
# Projected 3D density cross-section at y3=0; do not call it a normalized 2D marginal.
y=np.linspace(-5,5,41);GX,GY=np.meshgrid(y,y);grid=np.c_[GX.ravel(),GY.ravel(),np.zeros(GX.size)]
values,err=quad_vec(lambda depth:depth**3*density(np.c_[depth*grid,np.full(len(grid),h-depth)])/Z,eps,np.inf,epsabs=1e-7,epsrel=1e-7)
fig=plt.figure(figsize=(9,5));ax=fig.add_subplot(111,projection='3d');ax.plot_surface(GX,GY,values.reshape(GX.shape),cmap='magma',linewidth=0);ax.set(xlabel='Projected coordinate 1',ylabel='Projected coordinate 2',zlabel='3D density at coordinate 3 = 0',title='Projective-horizon density cross-section');save(fig,'projected-density')
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
axs[0].hexbin(samples[:,0],samples[:,1],gridsize=45,mincnt=1,cmap='viridis');axs[0].set(xlabel='Latent coordinate 1',ylabel='Latent coordinate 2',title='Latent synthetic sample')
axs[1].hexbin(projected[:,0],projected[:,1],gridsize=45,mincnt=1,cmap='magma',extent=(-8,8,-8,8));axs[1].set(xlabel='Projected coordinate 1',ylabel='Projected coordinate 2',title='Observed window of projected sample',xlim=(-8,8),ylim=(-8,8));save(fig,'perspective-samples')
# Exact Cauchy ratio example, independent of the clinical interpretation.
normal=rng.standard_normal((200000,2));ratios=normal[:,0]/normal[:,1];bins=np.linspace(-8,8,121);counts,_=np.histogram(ratios,bins=bins);centers=(bins[:-1]+bins[1:])/2
fig,ax=plt.subplots(figsize=(9,4),layout='constrained');ax.bar(centers,counts/(len(ratios)*np.diff(bins)),width=np.diff(bins),alpha=.6,label='Synthetic ratio histogram');u=np.linspace(-8,8,500);ax.plot(u,1/(np.pi*(1+u*u)),color='#d55e00',lw=2,label='Exact Cauchy density');ax.plot(u,norm.pdf(u),color='#009e73',label='Standard Gaussian reference');ax.set(xlabel='Independent normal / normal',ylabel='Unconditional density',title='A projective ratio can be heavy-tailed without a heavy-tailed source');ax.legend();save(fig,'cauchy-ratio')
exact=1-2*np.arctan(5)/np.pi;emp=float(np.mean(abs(ratios)>5));assert abs(emp-exact)<5*np.sqrt(exact*(1-exact)/len(ratios))
cauchy_mass=quad(lambda z:1/(np.pi*(1+z*z)),-np.inf,np.inf)[0];assert abs(cauchy_mass-1)<1e-9
# Rank-three plane plus finite observation noise.
taus=[1.,.3,.1,.03,.01,0.];eigens=[]
for tau in taus:eigens.append(np.linalg.eigvalsh(M@np.diag([.8,.7,.9])@M.T+tau*tau*np.eye(4)).tolist())
assert sum(np.array(eigens[-1])>1e-8)==3
fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
for j in range(4):ax.plot(taus[:-1],[e[j] for e in eigens[:-1]],'o-',label=f'Eigenvalue {j+1}')
ax.set(xscale='log',yscale='log',xlabel='Ambient noise scale',ylabel='Covariance eigenvalue',title='Three-dimensional subspace and full four-dimensional density');ax.legend();save(fig,'manifold-noise')
# Label permutation leaves the mixture unchanged.
probe=rng.standard_normal((80,4));base=density(probe);perm_errors=[]
for order in itertools.permutations(range(3)):
 p=sum(w[j]*pdfs[j].pdf(probe) for j in order);perm_errors.append(float(abs(p-base).max()))
assert max(perm_errors)<1e-14
# Perspective sensitivity is geometry, not a suicide/violence forecast.
horizons=[.5,1.,2.,3.];perspective=[]
for horizon in horizons:
 valid=samples[:,3]<horizon-eps;v=samples[valid,0]/(horizon-samples[valid,3]);perspective.append({'horizon':horizon,'retained':int(valid.sum()),'median':float(np.median(v)),'q05':float(np.quantile(v,.05)),'q95':float(np.quantile(v,.95))})
fig,ax=plt.subplots(figsize=(9,4),layout='constrained');med=np.array([v['median'] for v in perspective]);lo=np.array([v['q05'] for v in perspective]);hi=np.array([v['q95'] for v in perspective]);ax.errorbar(horizons,med,yerr=[med-lo,hi-med],fmt='o',capsize=5,color='#0072b2');ax.set(xlabel='Assumed projective horizon',ylabel='Projected coordinate: median and 5-95% interval',title='Observer geometry changes the display of the same source sample');save(fig,'horizon-sensitivity')
# Generic base-rate arithmetic, not a tested clinical predictor.
prevalence=np.array([.001,.005,.01,.05,.1]);sensitivity=.8;specificity=.95
ppv=sensitivity*prevalence/(sensitivity*prevalence+(1-specificity)*(1-prevalence))
fig,ax=plt.subplots(figsize=(9,4),layout='constrained');ax.plot(prevalence,ppv,'o-',color='#cc79a7');ax.set(xlabel='Assumed generic event prevalence',ylabel='Positive predictive value',title='Illustrative base-rate arithmetic: sensitivity 0.8, specificity 0.95',ylim=(0,1));ax.grid(alpha=.2);save(fig,'base-rates')
# Projection derivative verified against independent finite differences.
x0=np.array([.4,-.2,.5,.3]);depth=h-x0[3];J=np.c_[np.eye(3)/depth,x0[:3]/depth**2];step=1e-6
f=lambda x:x[:3]/(h-x[3]);numeric=np.column_stack([(f(x0+step*np.eye(4)[j])-f(x0-step*np.eye(4)[j]))/(2*step) for j in range(4)])
assert np.allclose(J,numeric,atol=1e-8)
# Affine inverse and conditional projection determinant.
D=.7;assert abs(np.linalg.det(np.block([[D*np.eye(3),np.array([[.1],[.2],[-.3]])],[np.zeros((1,3)),np.array([[-1.]])]])))==D**3 or np.isclose(abs(np.linalg.det(np.block([[D*np.eye(3),np.array([[.1],[.2],[-.3]])],[np.zeros((1,3)),np.array([[-1.]])]]))),D**3)
result={'status':'synthetic mathematical illustrations only; no patient data or fitted clinical parameters','seed':20261004,'source_samples':N,'weights':w.tolist(),'means':mu.tolist(),'covariances':covs.tolist(),'horizon':h,'epsilon':eps,'retention_analytic':Z,'retention_observed':float(observed),'projected_slice_quadrature_error_norm':float(err),'cauchy_sample_size':len(ratios),'cauchy_tail_gt5_analytic':float(exact),'cauchy_tail_gt5_observed':emp,'cauchy_density_integral':float(cauchy_mass),'tau_values':taus,'covariance_eigenvalues':eigens,'perspective_sensitivity':perspective,'generic_base_rates':prevalence.tolist(),'generic_ppv':ppv.tolist(),'label_permutation_max_error':max(perm_errors),'projection_jacobian_max_error':float(abs(J-numeric).max()),'checks_passed':True}
(B/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['retention_analytic','retention_observed','cauchy_tail_gt5_analytic','cauchy_tail_gt5_observed','checks_passed']},indent=2))
