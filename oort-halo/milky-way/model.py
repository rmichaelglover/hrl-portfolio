"""Real-data rotation-curve comparison; run with .venv/bin/python model.py."""
from pathlib import Path
import csv
import hashlib
import json
import importlib.metadata

import numpy as np
from bs4 import BeautifulSoup
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from galpy.potential.McMillan17 import McMillan_disk, McMillan_bulge, McMillan_halo, ro, vo
from galpy.potential import vcirc, evaluateRforces, evaluatePotentials, NFWPotential
from galpy.util import conversion

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://arxiv.org/html/1810.09466'
html = (ROOT / 'eilers-source.html').read_bytes()
table = BeautifulSoup(html, 'html.parser').find('table', id='S5.T1.2')
rows = []
for row in table.select('tr'):
    cells = [c.get_text(' ', strip=True) for c in row.find_all('td')]
    if len(cells) == 4:
        try:
            rows.append([float(c) for c in cells])
        except ValueError:
            pass
data = np.array(rows)
assert data.shape == (38, 4), data.shape
R, observed, minus, plus = data.T
assert np.all(np.diff(R) > 0) and np.all(data > 0)
assert np.allclose(data[0], [5.27, 226.83, 1.91, 1.90])
assert np.allclose(data[-1], [24.82, 198.42, 6.50, 6.12])
np.savetxt(ROOT / 'eilers-2019-table1.csv', data, delimiter=',',
           header='radius_kpc,vc_km_s,stat_minus_km_s,stat_plus_km_s', comments='', fmt='%.2f')

baryons = [McMillan_disk, McMillan_bulge]
def baryon_v2(radius):
    # Flattened disks use their radial force, never spherical enclosed mass.
    return np.array([vcirc(baryons, float(r)/ro, use_physical=False)**2 * vo**2
                     for r in np.atleast_1d(radius)])

# G matching galpy's own unit conversion, kpc (km/s)^2 / solar mass.
G = vo**2 * ro / (conversion.mass_in_msol(vo, ro))
def halo_mass(radius, rho_s, r_s):
    x = np.asarray(radius) / r_s
    return 4*np.pi*rho_s*r_s**3*(np.log1p(x)-x/(1+x))

def halo_v2(radius, rho_s, r_s):
    return G*halo_mass(radius, rho_s, r_s)/np.asarray(radius)

bv2 = baryon_v2(R)
mask = R < 20  # Outer measurements displayed but excluded from parameter fitting.
def fit(scale=1., floor=.03, max_radius=20.):
    selected = R < max_radius
    def residual(log_parameters):
        rho, rs = np.exp(log_parameters)
        prediction = np.sqrt(scale*bv2 + halo_v2(R, rho, rs))
        stat = np.where(prediction > observed, plus, minus)
        # This floor is an illustrative weighting rule, not a covariance model.
        weight = np.hypot(stat, floor*observed)
        return ((prediction-observed)/weight)[selected]
    optimum = least_squares(residual, np.log([8e6, 20.]),
                            bounds=(np.log([1e4, .5]), np.log([1e10, 200.])),
                            xtol=1e-12, ftol=1e-12, gtol=1e-12)
    assert optimum.success
    rho, rs = np.exp(optimum.x)
    prediction = np.sqrt(scale*bv2 + halo_v2(R, rho, rs))
    return dict(baryon_mass_scale=scale, assumed_fractional_floor=floor,
                fit_max_radius_kpc=max_radius, fit_bins=int(selected.sum()),
                rho_s_msun_kpc3=float(rho), r_s_kpc=float(rs),
                rmse_fit_km_s=float(np.sqrt(np.mean((prediction[selected]-observed[selected])**2))),
                rmse_outer_km_s=float(np.sqrt(np.mean((prediction[~selected]-observed[~selected])**2))),
                halo_mass_inside_20kpc_msun=float(halo_mass(20., rho, rs)),
                local_halo_density_msun_pc3=float(rho/((8.122/rs)*(1+8.122/rs)**2)/1e9),
                bound_reached=bool(np.any(optimum.active_mask)))

nominal = fit()
cases = [fit(scale, floor) for scale in [.8, 1., 1.2] for floor in [.02, .03, .05]]
cases += [fit(1., .03, 15.)]
rho, rs = nominal['rho_s_msun_kpc3'], nominal['r_s_kpc']
prediction = np.sqrt(bv2+halo_v2(R, rho, rs))

# Physical checks: analytic NFW agrees with library; potential gradient agrees
# with radial force; squared component speeds add to total speed squared.
check_r = np.array([5.27, 8.122, 15., 24.82])
nfw = NFWPotential(amp=4*np.pi*rho*rs**3/conversion.mass_in_msol(vo, ro), a=rs/ro)
for r in check_r:
    dimensionless = r/ro
    assert np.isclose(vcirc(nfw, dimensionless, use_physical=False)**2*vo**2,
                      halo_v2(r, rho, rs), rtol=1e-10)
    step = 1e-5
    derivative = (evaluatePotentials(baryons, dimensionless+step, 0., use_physical=False)
                  - evaluatePotentials(baryons, dimensionless-step, 0., use_physical=False))/(2*step)
    force = evaluateRforces(baryons, dimensionless, 0., use_physical=False)
    assert np.isclose(derivative, -force, rtol=2e-5)
    total = vcirc(baryons+[nfw], dimensionless, use_physical=False)**2*vo**2
    assert np.isclose(total, baryon_v2(r)[0]+halo_v2(r,rho,rs), rtol=1e-10)

np.savetxt(ROOT / 'comparison.csv', np.column_stack([data, np.sqrt(bv2), prediction,
           1-bv2/observed**2, mask.astype(int)]), delimiter=',', comments='',
           header='radius_kpc,observed_km_s,stat_minus_km_s,stat_plus_km_s,baryons_km_s,baryons_plus_halo_km_s,unaccounted_radial_force_fraction,used_for_fit', fmt='%.8g')
results = dict(data_source=SOURCE, source_sha256=hashlib.sha256(html).hexdigest(),
               data_rows=len(R), nominal=nominal, sensitivity=cases,
               baryon_only_rmse_fit_km_s=float(np.sqrt(np.mean((np.sqrt(bv2[mask])-observed[mask])**2))),
               checks='NFW formula, radial potential gradient, component-force addition, table endpoints passed',
               packages={p:importlib.metadata.version(p) for p in ['galpy','numpy','scipy','matplotlib','beautifulsoup4']},
               illustrative_samples=[dict(radius_kpc=float(R[i]), observed_km_s=float(observed[i]),
               baryons_km_s=float(np.sqrt(bv2[i])), fitted_total_km_s=float(prediction[i]),
               unaccounted_radial_force_fraction=float(1-bv2[i]/observed[i]**2)) for i in [6,19,29]])
(ROOT/'results.json').write_text(json.dumps(results, indent=2)+'\n')

grid = np.linspace(5.,25.,250)
grid_bv2 = baryon_v2(grid)
plt.rcParams.update({'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False})
fig,(ax,res) = plt.subplots(2,1,figsize=(10,8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
ax.axvspan(20,25,color='#eeeeee', label='Outside fitted interval')
ax.errorbar(R,observed,yerr=[minus,plus],fmt='o',ms=4,color='#222222',label='Eilers et al. table 1; statistical errors')
ax.fill_between(R,observed*.95,observed*1.05,color='#999999',alpha=.17,label='±5% illustration; not a confidence band')
ax.plot(grid,np.sqrt(grid_bv2),lw=2.5,color='#bd6c22',label='McMillan17 stars + gas + bulge')
ax.plot(grid,np.sqrt(halo_v2(grid,rho,rs)),ls='--',color='#426d9f',label='Fitted NFW halo contribution')
ax.plot(grid,np.sqrt(grid_bv2+halo_v2(grid,rho,rs)),lw=2.5,color='#216b50',label='Baryons + fitted halo')
ax.set(ylabel='Circular speed (km/s)',title='Milky Way: can the specified ordinary-matter model explain the curve?')
ax.legend(fontsize=9,loc='lower left')
res.axhline(0,color='#777777',lw=1)
res.axvspan(20,25,color='#eeeeee')
res.plot(R,observed-np.sqrt(bv2),'o-',ms=3,color='#bd6c22',label='Baryons only')
res.plot(R,observed-prediction,'o-',ms=3,color='#216b50',label='Baryons + halo')
res.set(xlabel='Galactocentric radius (kpc)',ylabel='Data − model\n(km/s)')
fig.text(.10,.015,'Disk forces computed in axisymmetric geometry. Fit: R < 20 kpc; illustrative 3% weight floor. No significance claim.',fontsize=9)
fig.tight_layout(rect=[0,.04,1,1])
for ext in ['png','pdf']: fig.savefig(ROOT/f'rotation-curve.{ext}',dpi=180)
plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5))
for scale,color in [(.8,'#416b9f'),(1.,'#216b50'),(1.2,'#bd6c22')]:
    case=next(c for c in cases if c['baryon_mass_scale']==scale and c['assumed_fractional_floor']==.03)
    ax.plot(grid,np.sqrt(scale*grid_bv2+halo_v2(grid,case['rho_s_msun_kpc3'],case['r_s_kpc'])),color=color,label=f'Baryon masses × {scale:g}; halo refitted')
ax.errorbar(R,observed,yerr=[minus,plus],fmt='.',color='#333333',alpha=.6)
ax.axvspan(20,25,color='#eeeeee')
ax.set(xlabel='Galactocentric radius (kpc)',ylabel='Circular speed (km/s)',title='Similar rotation curves can have different mass decompositions')
ax.legend(fontsize=9)
fig.tight_layout()
for ext in ['png','pdf']: fig.savefig(ROOT/f'sensitivity.{ext}',dpi=180)
print(json.dumps(results,indent=2))
