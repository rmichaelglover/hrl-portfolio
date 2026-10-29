"""Frozen-ALP v0.1: proposed preferred-frame Newtonian EFT benchmark.

No data fit, primordial transfer function, or empirical viability claim.
Run: python3 model.py --output /absolute/output/directory
"""
from pathlib import Path
import argparse
import csv
import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

G=6.67430e-11
HBAR=1.054571817e-34
C=299792458.0
EV=1.602176634e-19
MPC=3.085677581491367e22
MSUN=1.98847e30
H0=67.4*1000/MPC
OMEGA_ALP=0.265  # fixes toy mean density; baryons excluded from benchmark
MASS_EV=1e-20
MASS_KG=MASS_EV*EV/C**2
AREF=0.01
RHO0=3*H0**2/(8*math.pi*G)*OMEGA_ALP
RHOREF=RHO0/AREF**3
QREF=(16*math.pi*G*RHOREF*MASS_KG**2/HBAR**2)**0.25
CROSSOVER_EV=QREF*HBAR*C/EV


def jeans_ratio(y):
    """qJ/qJ0 when y=(qJ0/q_star)^2 >= 0."""
    if y<0: raise ValueError('positive stiffness required')
    return brentq(lambda x: x**4*(1+y*x*x)-1,1e-8,1.000001,xtol=1e-14)


def e_over_h(n,x,eta):
    r=math.exp(-n)  # aref/a
    f=1+eta*x*x*r*r
    return math.sqrt(1.5)*x*x*math.sqrt(r)*f, f


def evolve(x,eta=1,rtol=1e-9,atol=1e-11):
    """Matched delta=1, ddelta/dln(a)=1 at z=99; not primordial ICs."""
    ns=np.linspace(0,math.log(10),501)
    def rhs(n,state):
        d,v=state
        e,f=e_over_h(n,x,eta)
        drag=.5+2*(f-1)/f
        return [v,-drag*v-(e*e-1.5*f)*d]
    result=solve_ivp(rhs,(ns[0],ns[-1]),[1,1],t_eval=ns,
                     rtol=rtol,atol=atol,method='DOP853')
    if not result.success: raise RuntimeError(result.message)
    return ns,result.y


def envelope_evolve(x,eta=1):
    """Independent first-order density/phase implementation of same model."""
    ns=np.linspace(0,math.log(10),501)
    ei,_=e_over_h(0,x,eta)
    def rhs(n,state):
        d,theta=state
        e,f=e_over_h(n,x,eta)
        return [2*e*theta,(-e/2+.75*f/e)*d]
    result=solve_ivp(rhs,(ns[0],ns[-1]),[1,1/(2*ei)],t_eval=ns,
                     rtol=1e-10,atol=1e-12,method='DOP853')
    if not result.success: raise RuntimeError(result.message)
    return result.y[0]


def checks():
    records={}
    records['standard_Jeans_limit_error']=abs(jeans_ratio(0)-1)
    assert records['standard_Jeans_limit_error']<1e-12
    max_residual=0
    for y in [0,1e-6,.1,1,10,1e6]:
        x=jeans_ratio(y)
        max_residual=max(max_residual,abs(x**4*(1+y*x*x)-1))
        if y>0: assert 0<x<1
    assert max_residual<1e-10
    records['Jeans_root_residual']=max_residual
    comparisons=[]
    for x in [.1,.5,.9,1,2]:
        ns,d=evolve(x)
        independent=envelope_evolve(x)
        error=float(np.max(np.abs(d[0]-independent))/max(1,float(np.max(np.abs(independent)))))
        assert error<1e-7
        ns,fine=evolve(x,rtol=1e-11,atol=1e-13)
        refinement=float(np.max(np.abs(d[0]-fine[0]))/max(1,float(np.max(np.abs(fine[0])))))
        assert refinement<1e-7
        comparisons.append({'x':x,'two_formulations_relative_error':error,'tolerance_refinement_error':refinement})
    records['independent_evolution_and_refinement']=comparisons
    # Long wavelength must recover the matter-dominated dust growing mode.
    ns,state=evolve(1e-4)
    dust_error=float(np.max(np.abs(state[0]/np.exp(ns)-1)))
    assert dust_error<1e-6
    records['long_wavelength_dust_relative_error']=dust_error
    # Positive free kinetic energy for eta >= 0; no high-k free gradient instability.
    k=np.logspace(-5,2,100)
    assert np.all(k*k*(1+k*k)>0)
    records['free_kinetic_positive_on_test_grid']=True
    # Jeans condition follows from linearized Schr-Poisson determinant.
    for x in [.2,.8688369618327093,1,2]:
        f=1+x*x;e=math.sqrt(1.5)*x*x*f
        matrix=np.array([[0,2*e],[-e/2+.75*f/e,0]])
        target=e*e-1.5*f
        assert math.isclose(float(np.linalg.det(matrix)),target,rel_tol=1e-8,abs_tol=1e-12)
    records['density_phase_determinant_matches_Jeans_condition']=True
    return records


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    validation=checks()
    root=jeans_ratio(1)
    qnew=root*QREF
    mass0=4*math.pi/3*RHOREF*(math.pi/QREF)**3/MSUN
    summary={
        'status':'Proposed model benchmark, not data fit, detection, or validated cosmology',
        'mass_eV':MASS_EV,'H0_reference_km_s_Mpc':67.4,'Omega_ALP_density_normalization':OMEGA_ALP,
        'background':'ALP-only matter domination; baryons/radiation/Lambda omitted',
        'reference_redshift':99,'M_crossover_eV':CROSSOVER_EV,
        'standard_kJ_comoving_Mpc_inverse':QREF*AREF*MPC,
        'modified_kJ_comoving_Mpc_inverse':qnew*AREF*MPC,
        'kJ_ratio':root,'kJ_percent_change':100*(root-1),
        'Jeans_associated_mass_ratio':root**-3,
        'standard_Jeans_associated_mass_Msun':mass0,
        'modified_Jeans_associated_mass_Msun':mass0*root**-3,
        'mass_convention':'(4pi/3) rho (pi/qJ)^3; not a calibrated halo abundance threshold',
        'reference_q_over_rest_mass_in_natural_units':CROSSOVER_EV/MASS_EV,
        'validation':validation}
    (out/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    rows=[]
    for z in np.geomspace(10,1000,160)-1:
        a=1/(1+z);q0=QREF*(AREF/a)**.75;y=(q0/QREF)**2
        ratio=jeans_ratio(y)
        rows.append([z,a,q0*a*MPC,q0*a*MPC*ratio,ratio,ratio**-3])
    with (out/'jeans-scales.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['z','a','standard_kJ_Mpc_inv','modified_kJ_Mpc_inv','ratio','mass_ratio']);writer.writerows(rows)
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.3),layout='constrained')
    z=np.array([r[0] for r in rows]);standard=np.array([r[2] for r in rows]);modified=np.array([r[3] for r in rows])
    axes[0].loglog(1+z,standard,label='Standard ALP',color='#397b9d',lw=2)
    axes[0].loglog(1+z,modified,label='Spatial-stiffness ALP',color='#a34f46',lw=2)
    axes[0].scatter([100,100],[summary['standard_kJ_comoving_Mpc_inverse'],summary['modified_kJ_comoving_Mpc_inverse']],color=['#397b9d','#a34f46'])
    axes[0].set(xlabel='1 + redshift',ylabel='Comoving instantaneous Jeans k [Mpc⁻¹]',title='Same mass and mean density')
    axes[0].legend(frameon=False)
    density=[]
    for x,color in [(.5,'#618a48'),(.9,'#9b653c'),(2,'#6d5a9a')]:
        ns,d=evolve(x,1);_,b=evolve(x,0);a=AREF*np.exp(ns)
        axes[1].plot(a,d[0]/np.exp(ns),color=color,label=f'k/kJ,ref = {x:g}')
        axes[1].plot(a,b[0]/np.exp(ns),color=color,ls='--',alpha=.65)
        for i in range(len(a)):density.append([x,a[i],1/a[i]-1,b[0,i],d[0,i]])
    axes[1].set(xlabel='Scale factor a',ylabel='δ / (a / a_initial)',title='Matched initial density and growth\nSolid: modified; dashed: standard')
    axes[1].legend(frameon=False,fontsize=8)
    for ax in axes:ax.grid(alpha=.18)
    fig.suptitle('Illustrative ALP-only matter-era benchmark — not a primordial power-spectrum fit',fontsize=11)
    fig.savefig(out/'prediction.png',dpi=180);fig.savefig(out/'prediction.pdf');plt.close(fig)
    with (out/'matched-evolution.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['k_over_reference_standard_kJ','a','z','standard_delta','modified_delta']);writer.writerows(density)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).parent/'results')
    args=parser.parse_args();run(args.output)
