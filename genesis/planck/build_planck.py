#!/usr/bin/env python3
"""Planck-seeded Genesis — grow a cosmic web from the REAL primordial power spectrum.

Instead of white noise, we seed structure from the actual LambdaCDM matter power spectrum:
the Eisenstein & Hu (1998) transfer function with Planck 2018 cosmological parameters. A
Gaussian random field with that spectrum is the universe's real initial condition; we then
grow it with the Zel'dovich approximation (the standard first-order structure-formation map).
Filaments, clusters and voids condense with the RIGHT correlation statistics — the same web
we see in the real SDSS data.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg

HERE = Path(__file__).resolve().parent
FR = HERE / "frames"; FR.mkdir(exist_ok=True)

# Planck 2018 (TT,TE,EE+lowE+lensing)
Om, Ob, h, ns, Tcmb = 0.3153, 0.0493, 0.6736, 0.9649, 2.7255
N, L = 320, 320.0                                   # grid, box size (Mpc)
RNG = np.random.default_rng(42)


def eh98_nowiggle(k):
    """Eisenstein-Hu (1998) no-wiggle transfer function. k in 1/Mpc."""
    k = np.maximum(k, 1e-6)
    Om_h2, Ob_h2 = Om * h * h, Ob * h * h
    theta = Tcmb / 2.7
    s = 44.5 * np.log(9.83 / Om_h2) / np.sqrt(1 + 10 * Ob_h2 ** 0.75)
    alpha = (1 - 0.328 * np.log(431 * Om_h2) * (Ob / Om)
             + 0.38 * np.log(22.3 * Om_h2) * (Ob / Om) ** 2)
    Geff = Om * h * (alpha + (1 - alpha) / (1 + (0.43 * k * s) ** 4))
    q = k * theta * theta / Geff
    L0 = np.log(2 * np.e + 1.8 * q)
    C0 = 14.2 + 731.0 / (1 + 62.5 * q)
    return L0 / (L0 + C0 * q * q)


def power(k):
    T = eh98_nowiggle(k)
    return (k ** ns) * T * T


def make_field(spectrum=True):
    kf = 2 * np.pi / L
    kx = np.fft.fftfreq(N, d=L / N)[:, None] * 2 * np.pi
    ky = np.fft.fftfreq(N, d=L / N)[None, :] * 2 * np.pi
    k2 = kx ** 2 + ky ** 2
    kk = np.sqrt(k2); kk[0, 0] = 1e-6
    P = power(kk) if spectrum else np.ones_like(kk)
    P[0, 0] = 0.0
    wn = RNG.normal(size=(N, N)) + 1j * RNG.normal(size=(N, N))
    dk = wn * np.sqrt(P)
    delta = np.fft.ifft2(dk).real
    delta /= delta.std()
    return delta, dk, kx, ky, k2


def zeldovich(dk, kx, ky, k2, D):
    """Displace a grid of particles by D * (-grad phi), phi = delta/k^2. Return density."""
    inv = np.zeros_like(k2); inv[k2 > 0] = 1.0 / k2[k2 > 0]
    psi_x = np.fft.ifft2(1j * kx * dk * inv).real
    psi_y = np.fft.ifft2(1j * ky * dk * inv).real
    psi_x /= psi_x.std(); psi_y /= psi_y.std()
    M = 2                                          # oversample particles + jitter -> break the lattice
    gy, gx = np.mgrid[0:N * M, 0:N * M].astype(float) / M
    ii = gy.astype(int) % N; jj = gx.astype(int) % N
    jx = (RNG.random(gx.shape) - 0.5) / M; jy = (RNG.random(gx.shape) - 0.5) / M
    x = (gx + jx + D * psi_x[ii, jj]) % N
    y = (gy + jy + D * psi_y[ii, jj]) % N
    dens = np.zeros((N, N))
    np.add.at(dens, (y.astype(int) % N, x.astype(int) % N), 1.0)
    return dens


def save_img(field, name, gamma=0.4, cmap="magma", smooth=True):
    a = field.copy()
    if smooth:                                     # light blur for glow
        for ax in (0, 1):
            a = (a + np.roll(a, 1, ax) + np.roll(a, -1, ax)) / 3
    a = np.log1p(a - a.min())
    a = (a - a.min()) / (a.max() - a.min() + 1e-9)
    a = a ** gamma
    mpimg.imsave(FR / name, a, cmap=cmap, origin="lower")
    return name


def main():
    delta, dk, kx, ky, k2 = make_field(spectrum=True)
    # initial linear field
    save_img((delta - delta.min()), "seed.png", gamma=0.7, cmap="magma")
    # growth sequence (Zel'dovich)
    stages = [6, 12, 20, 30]
    frames = []
    for i, D in enumerate(stages):
        frames.append(save_img(zeldovich(dk, kx, ky, k2, D), f"web_{i}.png", gamma=0.42))
    # white-noise comparison at the strongest growth
    dn, dkn, kxn, kyn, k2n = make_field(spectrum=False)
    save_img(zeldovich(dkn, kxn, kyn, k2n, 30), "whitenoise.png", gamma=0.42)

    # real P(k) curve for the plot
    ks = np.logspace(-2.3, 0.3, 80)                # 1/Mpc
    Pk = power(ks)
    Pk = Pk / Pk.max()
    kturn = ks[np.argmax(Pk)]
    pkcurve = [[round(float(np.log10(k)), 3), round(float(np.log10(p + 1e-12)), 3)]
               for k, p in zip(ks, Pk)]

    data = dict(params=dict(Om=Om, Ob=Ob, h=h, ns=ns),
                box=L, N=N, stages=stages, frames=frames,
                pk=pkcurve, kturn_log=round(float(np.log10(kturn)), 3))
    (HERE / "data.json").write_text(json.dumps(data))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)))
    print(f"generated Planck-seeded web: {len(frames)} growth stages + seed + white-noise control")
    print(f"P(k) turnover near k = {kturn:.3f} /Mpc  (horizon at matter-radiation equality)")
    print(f"wrote {HERE/'index.html'}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seeded by the Big Bang — Planck power spectrum -> cosmic web</title>
<style>
:root{--bg:#04050b;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;--hot:#ff9e5e;--cool:#37e6ff}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#12102a,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:940px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--hot);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:750px;margin:0 auto 14px;font-size:14.5px}.lede b{color:var(--ink)}.lede i{color:var(--hot)}
.stage{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;align-items:flex-start;margin:14px auto}
.web{max-width:440px;flex:1 1 380px}
.web img{width:100%;border-radius:12px;border:1px solid var(--line);display:block;background:#000;image-rendering:auto}
#pk{background:#02030a;border:1px solid var(--line);border-radius:12px;flex:1 1 320px;max-width:380px}
.panel{display:flex;gap:12px;justify-content:center;align-items:center;margin:10px auto;flex-wrap:wrap}
button{background:#0c1226;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 15px;font:14px ui-serif,Georgia;cursor:pointer}button:hover{background:#161334}
input[type=range]{width:220px;accent-color:var(--hot)}
.cmp{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:18px}
.cmp figure{margin:0;max-width:300px}.cmp img{width:100%;border-radius:10px;border:1px solid var(--line)}
.cmp figcaption{font:12px ui-monospace,monospace;color:var(--dim);margin-top:5px}.cmp b{color:var(--ink)}
.stat{font:12.5px ui-monospace,monospace;color:var(--dim);margin-top:6px}.stat b{color:var(--hot)}
.note{color:var(--dim);font-size:12.5px;max-width:800px;margin:20px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--hot)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--cool);font-size:12px}
a{color:var(--cool);text-decoration:none}
</style></head><body><div class="wrap">
<h1>Seeded by the Big Bang</h1><div class="sub">Planck power spectrum → cosmic web</div>
<p class="lede">Project Genesis started from <i>white noise</i>. But the real universe didn't — its initial ripples have a specific
<b>power spectrum</b>, measured by Planck. Here we seed structure from the true <b>ΛCDM spectrum</b> (Eisenstein–Hu transfer
function, Planck 2018 parameters) and grow it. Filaments, clusters and voids condense with the <i>correct correlations</i> — the same
web the <a href="../sdss/">real SDSS data</a> shows.</p>
<div class="stage">
  <div class="web"><img id="webimg" src="frames/web_3.png" alt="cosmic web grown from the Planck power spectrum"></div>
  <canvas id="pk" width="380" height="360"></canvas>
</div>
<div class="panel">
  <button id="play">▶ Grow</button>
  <label style="font:12px ui-monospace,monospace;color:var(--dim)">growth <input id="scrub" type="range" min="0" max="3" value="3"></label>
</div>
<div class="stat" id="stat"></div>
<div class="cmp">
  <figure><img src="frames/whitenoise.png" alt="white noise seed"><figcaption><b>white-noise</b> seed — grainy, no large-scale web</figcaption></figure>
  <figure><img src="frames/web_3.png" alt="planck seed"><figcaption><b>Planck</b> seed — real correlations → filaments &amp; voids</figcaption></figure>
</div>
<div class="note">
<b>What's real.</b> The <code>P(k)</code> plotted at right is the genuine ΛCDM matter power spectrum (Eisenstein–Hu 1998 transfer
function, Planck 2018 Ω<sub>m</sub>=0.315, Ω<sub>b</sub>=0.049, h=0.674, n<sub>s</sub>=0.965). Its <b>turnover</b> marks the horizon
size at matter–radiation equality — a real, measured scale. The structure is grown with the <b>Zel'dovich approximation</b>, the
standard first-order map of how those ripples become the cosmic web. <b>Honest limit:</b> Zel'dovich is first-order (it blurs after
shell-crossing) and this is 2-D — a faithful <i>seed-and-grow</i>, not a full N-body simulation. But the initial conditions are the
real ones, so the web inherits the universe's true statistics.
</div>
<p style="margin-top:14px"><a href="../sdss/">← Real Cosmic Web</a> · <a href="../ontology/">The Four Poles</a> · <a href="../">Genesis</a> · <span style="color:var(--dim)">params: Planck 2018</span></p>
</div>
<script>
const D = /*DATA*/;
const img=document.getElementById('webimg'), sc=document.getElementById('scrub');
let t=3, playing=false, fr=0;
function show(){ img.src='frames/'+D.frames[t]; sc.value=t;
  document.getElementById('stat').innerHTML=`growth stage <b>${t+1}</b>/${D.frames.length} · Zel'dovich displacement D=${D.stages[t]} · seeded by real ΛCDM P(k)`; }
sc.oninput=()=>{t=+sc.value; playing=false; document.getElementById('play').textContent='▶ Grow'; show();};
document.getElementById('play').onclick=function(){ playing=!playing; this.textContent=playing?'⏸':'▶ Grow';
  if(playing && t>=D.frames.length-1) t=0; };
setInterval(()=>{ if(playing){ fr++; if(fr%9===0){ t++; if(t>=D.frames.length){t=D.frames.length-1;playing=false;document.getElementById('play').textContent='▶ Grow';} show(); } } }, 60);
show();
// P(k) plot
const cv=document.getElementById('pk'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
const PAD={l:44,r:12,t:16,b:40};
const xs=D.pk.map(p=>p[0]), ysv=D.pk.map(p=>p[1]);
const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ysv),ymax=Math.max(...ysv);
const X=x=>PAD.l+(x-xmin)/(xmax-xmin)*(W-PAD.l-PAD.r), Y=y=>H-PAD.b-(y-ymin)/(ymax-ymin)*(H-PAD.t-PAD.b);
ctx.strokeStyle='rgba(120,140,190,.16)'; ctx.fillStyle='#7f8bb0'; ctx.font='10px ui-monospace,monospace';
for(let g=Math.ceil(xmin);g<=xmax;g++){ctx.beginPath();ctx.moveTo(X(g),PAD.t);ctx.lineTo(X(g),H-PAD.b);ctx.stroke();
  ctx.textAlign='center';ctx.fillText('10'+g,X(g),H-PAD.b+14);}
ctx.fillStyle='#9aa6c8';ctx.fillText('wavenumber k  (1/Mpc)',W/2,H-6);
ctx.save();ctx.translate(13,H/2);ctx.rotate(-Math.PI/2);ctx.fillText('power  P(k)',0,0);ctx.restore();
// turnover marker
ctx.strokeStyle='rgba(255,158,94,.4)';ctx.setLineDash([3,4]);
ctx.beginPath();ctx.moveTo(X(D.kturn_log),PAD.t);ctx.lineTo(X(D.kturn_log),H-PAD.b);ctx.stroke();ctx.setLineDash([]);
ctx.fillStyle='#ff9e5e';ctx.textAlign='left';ctx.font='italic 10px ui-serif,Georgia';
ctx.fillText('turnover (horizon @ eq.)',X(D.kturn_log)+4,PAD.t+40);
ctx.strokeStyle='#37e6ff';ctx.lineWidth=2;ctx.beginPath();
D.pk.forEach((p,i)=>{const x=X(p[0]),y=Y(p[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
ctx.fillStyle='#8a97b8';ctx.font='11px ui-serif,Georgia';ctx.textAlign='center';
ctx.fillText('real ΛCDM matter power spectrum',W/2,PAD.t+4);
</script></body></html>
"""


if __name__ == "__main__":
    main()
