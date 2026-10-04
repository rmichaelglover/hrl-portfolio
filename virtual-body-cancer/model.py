"""Dimensionless, uncalibrated tumor/body simulator. No clinical units or dosing."""
from dataclasses import dataclass
import numpy as np

@dataclass
class Parameters:
    growth: float = .22
    resistant_growth: float = .18
    kill_sensitive: float = .65
    kill_resistant: float = .08
    immune_kill: float = .08
    mutation: float = .002
    migration: float = .015
    clearance: float = .7
    toxicity: float = .11
    repair: float = .035
    oxygen_supply: float = .8
    oxygen_consumption: float = .6
    immune_recruit: float = .07
    immune_decay: float = .1
    immune_toxicity: float = .08
    capacity: float = 1.

# Each site has [sensitive population, resistant population, immune activity,
# resource availability, healthy tissue reserve]; last coordinate is exposure.
S,R,E,O,H=range(5)
PENETRATION=np.array([1.,.65,.4])
TRANSPORT=np.array([[-2.,1.,1.],[1.,-2.,1.],[1.,1.,-2.]]) / 2
POLICIES=('none','continuous','pulsed','feedback')

def initial():
    x=np.zeros(16); a=x[:15].reshape(3,5)
    a[:,S]=[.28,.025,.005]; a[:,R]=[.012,.002,.001]
    a[:,E]=.12; a[:,O]=.8; a[:,H]=1.
    return x

def rhs(x,u,p):
    a=x[:15].reshape(3,5); d=np.zeros_like(a)
    s,r,e,o,h=a.T; n=s+r; c=x[-1]*PENETRATION
    birth_s=p.growth*o*s*(1-n/p.capacity)
    birth_r=p.resistant_growth*o*r*(1-n/p.capacity)
    conversion=p.mutation*p.growth*o*s # phenomenological state conversion
    d[:,S]=birth_s-conversion-(p.kill_sensitive*c+p.immune_kill*e)*s+p.migration*(TRANSPORT@s)
    d[:,R]=birth_r+conversion-(p.kill_resistant*c+p.immune_kill*e)*r+p.migration*(TRANSPORT@r)
    d[:,E]=p.immune_recruit*n/(.1+n)-p.immune_decay*e-p.immune_toxicity*c*e
    d[:,O]=p.oxygen_supply*h*(1-o)-p.oxygen_consumption*n*o
    d[:,H]=p.repair*(1-h)-p.toxicity*c*h
    return np.r_[d.ravel(),u-p.clearance*x[-1]]

def simulate(policy='none',p=None,dt=.05,horizon=50.):
    if policy not in POLICIES: raise ValueError('unknown policy')
    if dt<=0 or horizon<=0: raise ValueError('positive dt and horizon required')
    p=p or Parameters(); x=initial(); active=True; rows=[]
    steps=int(np.ceil(horizon/dt)); dt=horizon/steps
    for k in range(steps+1):
        t=k*dt; a=x[:15].reshape(3,5); burden=float(a[:,:2].sum())
        if policy=='feedback':
            if a[:,H].min()<.7 or burden<.12: active=False
            elif a[:,H].min()>.85 and burden>.25: active=True
        u={'none':0.,'continuous':.7,'pulsed':.9 if t%10<4 else 0.,'feedback':.7 if active else 0.}[policy]
        rows.append(np.r_[t,u,x])
        if k==steps: break
        f=lambda y:rhs(y,u,p)
        k1=f(x); k2=f(x+dt*k1/2); k3=f(x+dt*k2/2); k4=f(x+dt*k3)
        x=x+dt*(k1+2*k2+2*k3+k4)/6
        if not np.isfinite(x).all() or (x< -1e-10).any(): raise FloatingPointError('reduce time step')
        if (x[:15].reshape(3,5)[:,[O,H]]>1+1e-9).any(): raise FloatingPointError('reserve/resource bounds violated')
    return np.array(rows)

def metrics(rows):
    a=rows[:,2:17].reshape(-1,3,5); tumor=a[:,:,:2].sum(axis=(1,2))
    return dict(final_burden=float(tumor[-1]),burden_integral=float(np.trapz(tumor,rows[:,0])),
                min_reserve=float(a[:,:,H].min()),final_resistant_fraction=float(a[-1,:,R].sum()/tumor[-1]),
                input_integral=float(np.sum(rows[:-1,1]*np.diff(rows[:,0]))))
