"""Numerical and structural checks, not biological validation."""
import json
from pathlib import Path
import numpy as np
from model import Parameters,initial,rhs,simulate,metrics,POLICIES,TRANSPORT
checks={}
p=Parameters(growth=0,resistant_growth=0,kill_sensitive=0,kill_resistant=0,immune_kill=0,mutation=0)
x=initial(); dx=rhs(x,0,p).reshape(-1)
checks['migration_conserves_each_clone']=bool(np.allclose(dx[:15].reshape(3,5)[:,:2].sum(axis=0),0,atol=1e-12) and np.allclose(TRANSPORT.sum(axis=0),0))
x[:15]=0; dx=rhs(x,.7,Parameters())
checks['no_spontaneous_tumor']=bool(np.all(dx[:15].reshape(3,5)[:,:2]==0))
rows=simulate('continuous',horizon=5,dt=.05)
analytic=.7/.7*(1-np.exp(-.7*5))
checks['constant_input_exposure_exact']=bool(abs(rows[-1,-1]-analytic)<1e-7)
errors={}
for policy in POLICIES:
    r=simulate(policy,dt=.05); fine=simulate(policy,dt=.025)
    checks[policy+'_nonnegative']=bool((r[:,2:]>=0).all())
    errors[policy]=float(np.max(np.abs(r[-1,2:]-fine[-1,2:])))
    checks[policy+'_step_refinement']=errors[policy]<.005
checks['all_passed']=all(checks.values())
report={'checks':checks,'final_state_step_refinement_error':errors,'scope':'numerics only; no cancer biology validation'}
Path(__file__).with_name('output').mkdir(exist_ok=True)
Path(__file__).with_name('output').joinpath('verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert checks['all_passed']
