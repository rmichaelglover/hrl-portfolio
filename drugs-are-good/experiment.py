from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import quad

B=Path(__file__).resolve().parent
(B/'figures').mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def save(name):
    plt.savefig(B/'figures'/f'{name}.pdf',bbox_inches='tight')
    plt.savefig(B/'figures'/f'{name}.png',dpi=160,bbox_inches='tight');plt.close()
t=np.linspace(0,12,601)
plt.figure(figsize=(8,3.7))
for k in [.25,.5,1.0]:plt.plot(t,np.exp(-k*t),label=f'k={k:g}; AUC={1/k:g}')
plt.xlabel('Dimensionless time');plt.ylabel('Dimensionless concentration');plt.title('Fictional compound: identical initial exposure, different elimination');plt.legend();save('elimination')
c=np.linspace(0,8,501)
benefit=c*c/(1+c*c);harm=c**4/(3**4+c**4)
plt.figure(figsize=(8,3.7));plt.plot(c,benefit,label='Invented benefit response');plt.plot(c,harm,label='Invented harm response');plt.plot(c,benefit-harm,label='Equal-weight illustrative difference');plt.xlabel('Dimensionless concentration');plt.ylabel('Normalized response');plt.legend();save('responses')
cs,ws=np.meshgrid(np.linspace(0,8,100),np.linspace(.2,3,80))
u=cs**2/(1+cs**2)-ws*cs**4/(81+cs**4)
fig=plt.figure(figsize=(8,4));ax=fig.add_subplot(projection='3d');ax.plot_surface(cs,ws,u,cmap='viridis',linewidth=0);ax.set_xlabel('Concentration');ax.set_ylabel('Harm weight');ax.set_zlabel('Toy utility');ax.set_title('An optimum depends on values as well as response');save('utility-surface')
grid=np.linspace(.5,3,101);opt=[]
for w in grid:opt.append(float(c[np.argmax(benefit-w*harm)]))
plt.figure(figsize=(8,3.7));plt.plot(grid,opt);plt.xlabel('Illustrative harm weight');plt.ylabel('Grid optimum, dimensionless');plt.title('A mathematical optimum is conditional on the chosen objective');save('optima')
rng=np.random.default_rng(20261004);ks=rng.lognormal(np.log(.5),.35,20000)
curves=np.exp(-ks[:,None]*t[None,:]);lo,med,hi=np.quantile(curves,[.05,.5,.95],axis=0)
plt.figure(figsize=(8,3.7));plt.fill_between(t,lo,hi,alpha=.25,label='90% synthetic population interval');plt.plot(t,med,label='Synthetic median');plt.xlabel('Dimensionless time');plt.ylabel('Concentration');plt.legend();save('uncertainty')
p=np.linspace(.001,.3,300);arr=.25*p
plt.figure(figsize=(8,3.7));plt.plot(p,100*arr);plt.xlabel('Invented untreated event probability');plt.ylabel('Absolute reduction (percentage points)');plt.title('Fixed 25% relative reduction, changing absolute benefit');save('absolute-benefit')
n=np.arange(10,10001)
upper=1-.05**(1/n)
plt.figure(figsize=(8,3.7));plt.loglog(n,upper,label='Exact one-sided 95% upper bound');plt.loglog(n,3/n,'--',label='Rule of three approximation');plt.xlabel('Independent observations with zero events');plt.ylabel('Event-probability upper bound');plt.legend();save('zero-events')
dtvalues=[.4,.2,.1,.05,.025];errors=[]
for dt in dtvalues:
    steps=round(4/dt);end=(1-.5*dt)**steps;errors.append(abs(end-np.exp(-2)))
plt.figure(figsize=(8,3.7));plt.loglog(dtvalues,errors,'o-');plt.xlabel('Euler time step');plt.ylabel('Endpoint absolute error');plt.title('Discretization error in a known analytic system');save('convergence')
checks={}
for k in [.25,.5,1.]:
    area=quad(lambda x:np.exp(-k*x),0,np.inf)[0]
    assert np.isclose(area,1/k)
    assert np.isclose(np.exp(-k*np.log(2)/k),.5)
    checks[str(k)]={'auc':float(area),'half_life':float(np.log(2)/k)}
assert np.all(np.diff(errors)<0)
assert np.all(lo<=med) and np.all(med<=hi)
assert np.all((harm>=0)&(harm<=1)) and np.all((benefit>=0)&(benefit<=1))
data={'seed':20261004,'status':'All quantities invented and dimensionless; no clinical calibration','analytic_checks':checks,'synthetic_k_quantiles':np.quantile(ks,[.05,.5,.95]).tolist(),'zero_event_upper_bound_n1000':float(1-.05**.001),'euler_steps':dtvalues,'euler_errors':errors,'equal_weight_grid_optimum':float(c[np.argmax(benefit-harm)]),'checks_passed':True}
(B/'results.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
