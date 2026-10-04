"""Local stability and healthy-reserve feasibility for THIS synthetic model."""
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import Parameters,PENETRATION,TRANSPORT
B=Path(__file__).resolve().parent

def invasion(C,p,clone):
    growth=p.growth*(1-p.mutation) if clone=='sensitive' else p.resistant_growth
    kill=p.kill_sensitive if clone=='sensitive' else p.kill_resistant
    A=np.diag(growth-kill*PENETRATION*C)+p.migration*TRANSPORT
    return float(np.linalg.eigvalsh(A)[-1])

def assess(p,reserve_floor=.7):
    # Stable tumor-free equilibrium requires BOTH invasion blocks negative.
    roots={}
    for clone in ['sensitive','resistant']:
        hi=1.
        while invasion(hi,p,clone)>0:
            hi*=2
            if hi>1e6:raise ValueError('no finite threshold found')
        roots[clone]=float(brentq(lambda C:invasion(C,p,clone),0,hi,xtol=1e-12))
    allowed=p.repair*(1-reserve_floor)/(p.toxicity*PENETRATION.max()*reserve_floor)
    needed=max(roots.values())
    return {'exposure_thresholds':roots,'maximum_exposure_for_reserve_floor':float(allowed),
            'required_exposure_strictly_greater_than':needed,
            'minimum_equilibrium_reserve_at_threshold':float(np.min(p.repair/(p.repair+p.toxicity*PENETRATION*needed))),
            'constant_exposure_feasible':bool(needed<allowed),
            'resistant_invasion_at_reserve_limit':invasion(allowed,p,'resistant')}

p=Parameters();nominal=assess(p)
previous=json.loads((B/'output/results.json').read_text())
params={e['replicate']:Parameters(**e['parameters']) for e in previous['ensemble']}
ensemble=[{'replicate':i,**assess(q)} for i,q in params.items()]
# Independent tests: eigenvalue negativity beyond thresholds and transport limit.
for clone,c in nominal['exposure_thresholds'].items():
    assert abs(invasion(c,p,clone))<1e-10
    assert invasion(c+1e-5,p,clone)<0
    assert invasion(c-1e-5,p,clone)>0
q=Parameters(migration=0)
assert abs(assess(q)['exposure_thresholds']['resistant']-q.resistant_growth/(q.kill_resistant*PENETRATION.min()))<1e-9
assert np.all(np.diff([invasion(c,p,'resistant') for c in np.linspace(0,8,101)])<0)
result={'scope':'exact linearization of the uncalibrated three-site synthetic model; not a biological cure or a clinical threshold',
        'reserve_floor':.7,'parameters':asdict(p),'nominal':nominal,'ensemble':ensemble,
        'feasible_constant_exposure_cases':sum(x['constant_exposure_feasible'] for x in ensemble),
        'checks':'threshold roots, crossing signs, monotonicity and zero-migration analytic limit passed',
        'limitations':'local stability only; not global eradication; no conclusion about arbitrary time-varying controls, actual patients or alternative biology'}
(B/'output/extinction-feasibility.json').write_text(json.dumps(result,indent=2))
C=np.linspace(0,6.5,300)
fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=True,layout='constrained')
for clone in ['sensitive','resistant']:axs[0].plot(C,[invasion(c,p,clone) for c in C],label=clone)
axs[0].axhline(0,color='black',lw=.8);axs[0].set(ylabel='Largest invasion eigenvalue',title='Tumor-free equilibrium: synthetic model stability');axs[0].legend()
for i,pen in enumerate(PENETRATION):axs[1].plot(C,p.repair/(p.repair+p.toxicity*pen*C),label=f'Site {i+1}')
axs[1].axhline(.7,color='black',ls='--',label='Assumed reserve floor');axs[1].set(xlabel='Constant dimensionless systemic exposure',ylabel='Healthy reserve at equilibrium');axs[1].legend()
for ax in axs:ax.axvspan(0,nominal['maximum_exposure_for_reserve_floor'],color='green',alpha=.15);ax.axvline(nominal['required_exposure_strictly_greater_than'],color='purple',ls=':');ax.grid(alpha=.2)
fig.savefig(B/'output/extinction-feasibility.png',dpi=180)
print(json.dumps(result,indent=2))
