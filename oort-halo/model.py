"""Reproducible spherical mass-distribution comparison; not an observational fit."""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
PARAMETERS = dict(central_mass=1.0, extra_mass=4.0, shell_inner_radius=2.0,
                  outer_radius=10.0, halo_core_radius=0.3,
                  solar_cloud_earth_masses=10.0, earth_to_sun_mass_ratio=3.00349e-6,
                  solar_shell_inner_au=2000.0, solar_shell_outer_au=100000.0)

def shell_mass(r, mass, inner, outer):
    """Uniform-density thick shell: zero enclosed cloud mass in its cavity."""
    r = np.asarray(r, dtype=float)
    return mass * np.clip((r**3 - inner**3) / (outer**3 - inner**3), 0, 1)

def halo_mass(r, mass, core, outer):
    """rho(r)=rho0/[1+(r/core)^2], truncated at outer; analytic integral."""
    r = np.minimum(np.asarray(r, dtype=float), outer)
    x = r / core
    xmax = outer / core
    return mass * (x - np.arctan(x)) / (xmax - np.arctan(xmax))

def predictions(r, extra, central=1.0):
    """Units G=M0=r0=1. Acceleration is inward magnitude; speed is circular."""
    total = central + extra
    return np.sqrt(total / r), total / r**2

def verify():
    p = PARAMETERS
    mass, inner, outer, core = (p[k] for k in ('extra_mass','shell_inner_radius','outer_radius','halo_core_radius'))
    assert np.all(shell_mass([0, 0.5, inner], mass, inner, outer) == 0)
    assert np.all(shell_mass([outer, 2*outer], mass, inner, outer) == mass)
    assert np.isclose(halo_mass(outer, mass, core, outer), mass)
    assert np.isclose(halo_mass(2*outer, mass, core, outer), mass)
    assert halo_mass(0, mass, core, outer) == 0
    assert halo_mass(0.5, mass, core, outer) > 0
    r = np.geomspace(0.01, 100, 1000)
    for enclosed in [shell_mass(r, mass, inner, outer), halo_mass(r, mass, core, outer)]:
        assert np.all(np.diff(enclosed) >= -1e-12)
        v, acceleration = predictions(r, enclosed)
        np.testing.assert_allclose(v**2/r, acceleration, rtol=1e-13)
        np.testing.assert_allclose(acceleration*r*r-1, enclosed, atol=1e-13)
    # Check the analytic halo integral independently by quadrature.
    rho0 = mass / (4*np.pi*core**3*(outer/core-np.arctan(outer/core)))
    for radius in [0.1, 1, 3, outer]:
        rr = np.linspace(0, radius, 50001)
        numeric = np.trapz(4*np.pi*rr**2*rho0/(1+(rr/core)**2), rr)
        np.testing.assert_allclose(numeric, halo_mass(radius,mass,core,outer), rtol=1e-8)
    # Independent vector-force integral over a spherical thin shell.
    # Discretize solid angle with Gauss-Legendre nodes: interior net force cancels.
    mu, weight = np.polynomial.legendre.leggauss(128)
    shell_radius = 2.0
    for radius in [0.1, 0.5, 1.0, 1.5]:
        force = 0.5*np.sum(weight*(radius-shell_radius*mu)/
                          (radius**2+shell_radius**2-2*radius*shell_radius*mu)**1.5)
        assert abs(force) < 1e-12, force
    # Outside the thin shell, its force is that of a point mass.
    radius = 4.0
    force = 0.5*np.sum(weight*(radius-shell_radius*mu)/
                     (radius**2+shell_radius**2-2*radius*shell_radius*mu)**1.5)
    np.testing.assert_allclose(force,1/radius**2,rtol=1e-12)
    return 'PASS: mass normalization, cavity cancellation, halo quadrature, monotonic mass, circular force balance, and independent shell-force integration.'

def build():
    verification = verify()
    p = PARAMETERS
    r = np.geomspace(0.1, 30, 800)
    extra = {'Central mass only':np.zeros_like(r),
             'Central + outer shell':shell_mass(r,p['extra_mass'],p['shell_inner_radius'],p['outer_radius']),
             'Central + extended halo':halo_mass(r,p['extra_mass'],p['halo_core_radius'],p['outer_radius'])}
    colors = ['#526477','#be752f','#21796c']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'figure.facecolor':'#faf9f5','axes.facecolor':'#faf9f5'})
    fig, axes = plt.subplots(2,2,figsize=(12,8),layout='constrained')
    fig.suptitle('An outer shell and an extended halo are different gravitational models',fontsize=17,fontweight='bold')
    for (name,enclosed), color in zip(extra.items(), colors):
        speed, acceleration = predictions(r,enclosed)
        axes[0,0].plot(r, speed, label=name, color=color,lw=2.5)
        axes[0,1].plot(r, acceleration, color=color,lw=2.5)
        axes[1,0].plot(r, enclosed, color=color,lw=2.5)
        axes[1,1].plot(r, enclosed, color=color,lw=2.5)
    titles=['Circular-orbit speed','Inward gravitational acceleration','Enclosed extra mass','Extra acceleration relative to central-only']
    ylabels=[r'$v_c\,/\,\sqrt{GM_0/r_0}$',r'$|g|\,/\,(GM_0/r_0^2)$',r'$M_{\rm extra}(<r)\,/\,M_0$',r'$\Delta |g|\,/\,|g_0|$']
    for ax,title,ylabel in zip(axes.flat,titles,ylabels):
        ax.set_xscale('log');ax.set_title(title,loc='left',fontweight='bold');ax.set_xlabel(r'Radius $r/r_0$');ax.set_ylabel(ylabel)
        ax.axvspan(0.1,p['shell_inner_radius'],color='#be752f',alpha=.06)
        for boundary in [p['shell_inner_radius'],p['outer_radius']]:ax.axvline(boundary,color='#aaa69d',ls=':',lw=1)
        ax.grid(alpha=.17);ax.set_xlim(0.1,30)
    axes[0,0].set_yscale('log');axes[0,1].set_yscale('log')
    axes[0,0].legend(fontsize=9,frameon=False)
    axes[1,0].text(.13,3.35,'Shaded region: shell cavity\nThe shell adds no inward force here.',fontsize=9,color='#88551f')
    axes[1,1].text(.13,3.3,'These two lower curves match because\nextra force / central force = extra mass / M₀.',fontsize=9,color='#526477')
    fig.supxlabel('Toy comparison: same extra mass (4 M₀), same outer edge (10 r₀); uniform shell starts at 2 r₀.\nCored halo: ρ ∝ 1 / [1 + (r / 0.3r₀)²]. All three are Keplerian beyond the outer edge.',fontsize=9)
    fig.savefig(OUT/'three-models.png',dpi=180);fig.savefig(OUT/'three-models.pdf');plt.close(fig)
    with (OUT/'three-models.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['radius_r0','model','extra_enclosed_mass_M0','circular_speed_unit','inward_acceleration_unit'])
        for name,enclosed in extra.items():
            speed, acceleration=predictions(r,enclosed)
            writer.writerows(zip(r,[name]*len(r),enclosed,speed,acceleration))
    # A separate Sun-dominated scale illustration. Cloud mass is an assumption.
    au=np.geomspace(1,200000,1000)
    cloud_mass=p['solar_cloud_earth_masses']*p['earth_to_sun_mass_ratio']
    enclosed=shell_mass(au,cloud_mass,p['solar_shell_inner_au'],p['solar_shell_outer_au'])
    gm_sun=1.32712440018e20; au_m=149597870700.0
    baseline=np.sqrt(gm_sun/(au*au_m))/1000
    combined=baseline*np.sqrt(1+enclosed)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    fig.suptitle('A low-mass, Oort-like shell barely changes the Sun’s gravity',fontsize=16,fontweight='bold')
    axes[0].loglog(au,baseline,color=colors[0],lw=2.8,label='Sun alone')
    axes[0].loglog(au,combined,color=colors[1],lw=1.6,ls='--',label='Sun + illustrative cloud (overlaps)')
    axes[0].set_ylabel('Circular-orbit speed (km/s)');axes[0].set_title('Speed curves overlap',loc='left');axes[0].legend(frameon=False,fontsize=9)
    axes[1].semilogx(au,enclosed*1e6,color=colors[1],lw=2.5)
    axes[1].set_ylabel('Extra inward acceleration (parts per million)');axes[1].set_title('Show the small difference directly',loc='left')
    for ax in axes:
        ax.set_xlabel('Distance from the Sun (AU)');ax.grid(alpha=.17)
        ax.axvspan(2000,100000,color=colors[1],alpha=.08)
        ax.axvline(30,color=colors[2],lw=1,ls=':');ax.set_xlim(1,200000)
    axes[1].annotate('No shell force inside 2,000 AU',xy=(400,0),xytext=(4,20),arrowprops={'arrowstyle':'->','color':colors[0]},fontsize=9)
    fig.supxlabel('Illustration, not an Oort Cloud mass measurement: 10 Earth masses spread uniformly from 2,000 to 100,000 AU.\nDotted line: approximately Neptune’s orbital distance. Galactic tides, planets, encounters, and cloud clumpiness omitted.',fontsize=9)
    fig.savefig(OUT/'solar-shell.png',dpi=180);fig.savefig(OUT/'solar-shell.pdf');plt.close(fig)
    rows=[]
    for radius in [0.5,1,2,5,10,20]:
        row={'radius_r0':radius}
        for name,enclosed in [('central',0.0),('shell',float(shell_mass(radius,4,2,10))),('halo',float(halo_mass(radius,4,.3,10)))]:
            v,g=predictions(radius,enclosed);row[name]=dict(extra_mass=enclosed,speed=float(v),acceleration=float(g))
        rows.append(row)
    (OUT/'results.json').write_text(json.dumps(dict(parameters=p,verification=verification,sample_results=rows,solar_maximum_extra_force_ppm=cloud_mass*1e6),indent=2)+'\n')
    print(verification)
    for row in rows:print(f'r={row["radius_r0"]:g}: speeds central={row["central"]["speed"]:.4f}, shell={row["shell"]["speed"]:.4f}, halo={row["halo"]["speed"]:.4f}')
    print(f'Illustrative solar shell: maximum extra force {cloud_mass*1e6:.4f} ppm; zero in its cavity.')

if __name__=='__main__':build()
