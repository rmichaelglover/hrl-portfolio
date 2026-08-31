#!/usr/bin/env python3
"""The real cosmic web -> relaxation-labeled into void / filament / cluster.

REAL DATA: 25,000 galaxies from the Sloan Digital Sky Survey (SDSS DR17), a thin declination
slice (-1.5deg < Dec < 2.5deg), 0.005 < z < 0.15, fetched from SkyServer. We place each galaxy
in a redshift wedge (comoving distance from z) and see the actual large-scale structure — the
filaments, walls, and voids of the Cosmic Web.

Then the SAME engine that ran through Manny's career labels the web: each galaxy's LOCAL DENSITY
(k-th nearest-neighbour distance) seeds a prior over {void, filament, cluster}, and a sparse
relaxation over each galaxy's neighbours lets the labels 'fall into place' — clusters are the
clogged, stagnant knots (dark-matter-dominated); voids are the free-flowing dark-energy expanse.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
C_OVER_H0 = 299792.458 / 70.0                 # Mpc  (H0 = 70 km/s/Mpc)
LABELS = ["void", "filament", "cluster"]


def load():
    ra, dec, z = [], [], []
    with open(HERE / "sdss.csv") as fh:
        for row in fh:
            row = row.strip()
            if not row or row.startswith("#") or row.startswith("ra"):
                continue
            p = row.split(",")
            if len(p) < 3:
                continue
            try:
                ra.append(float(p[0])); dec.append(float(p[1])); z.append(float(p[2]))
            except ValueError:
                continue
    return np.array(ra), np.array(dec), np.array(z)


def main():
    ra, dec, z = load()
    d = C_OVER_H0 * z                          # comoving distance (Mpc), linear Hubble (z<0.15)
    # wedge coordinates: apex at origin, RA -> fan angle, radius = distance
    th = (ra - 185.0) / 150.0 * math.radians(150)     # spread the RA range over ~150 deg
    x = d * np.sin(th); y = d * np.cos(th)
    N = len(x)

    # local density from k-th nearest-neighbour distance
    P = np.column_stack([x, y])
    tree = cKDTree(P)
    k = 6
    dist, idx = tree.query(P, k=k + 1)         # idx[:,0] is self
    rk = dist[:, -1]
    dens = k / (math.pi * rk ** 2 + 1e-6)
    logd = np.log10(dens + 1e-9)
    def rnk(v): return np.argsort(np.argsort(v)) / (len(v) - 1)
    dr = rnk(logd)                             # 0 void .. 1 cluster

    # ordinal prior over {void, filament, cluster}
    VO = np.clip(1 - 2 * dr, 0, 1)
    CL = np.clip(2 * dr - 1, 0, 1)
    FI = 1 - np.abs(2 * dr - 1)
    prior = np.stack([VO, FI, CL], 1) + 1e-3
    prior /= prior.sum(1, keepdims=True)

    # sparse relaxation labeling over the k-NN graph (scales to 25k; same algorithm, sparse)
    R = np.array([[1.0, 0.5, 0.05], [0.5, 1.0, 0.5], [0.05, 0.5, 1.0]])   # ordinal affinity
    nbr = idx[:, 1:]                            # [N, k]
    p = prior.copy(); ps, sf = 0.4, 1.6
    for _ in range(16):
        nbrsum = p[nbr].sum(axis=1)            # [N, 3]  sum of neighbour label vectors
        support = nbrsum @ R.T                  # [N, 3]
        lo = support.min(1, keepdims=True); hi = support.max(1, keepdims=True)
        support = (support - lo) / (hi - lo + 1e-9)
        p = (prior ** ps) * (p ** (1 - ps)) * (1 + sf * support)
        p = p / p.sum(1, keepdims=True)
    cls = p.argmax(1)
    counts = {LABELS[i]: int((cls == i).sum()) for i in range(3)}

    # pack for the browser (round to save space)
    xs = np.round(x, 1).tolist(); ys = np.round(y, 1).tolist(); cl = cls.tolist()
    data = dict(N=N, x=xs, y=ys, cls=cl, counts=counts,
                dmax=round(float(d.max()), 1), zmin=0.005, zmax=0.15)
    (HERE / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data, separators=(",", ":"))))
    print(f"{N} real SDSS galaxies; wedge to {d.max():.0f} Mpc")
    print(f"HRL cosmic-web labels: {counts}")
    print(f"wrote {HERE/'index.html'}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Real Cosmic Web — SDSS, relaxation-labeled</title>
<style>
:root{--bg:#04050b;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;--void:#3a3f7a;--fila:#37e6ff;--clus:#e8c170}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#0e1530,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:940px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--fila);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:750px;margin:0 auto 12px;font-size:14.5px}.lede b{color:var(--ink)}.lede i{color:var(--fila)}
#web{background:#02030a;border:1px solid var(--line);border-radius:12px;max-width:620px;width:100%}
.leg{display:flex;gap:16px;justify-content:center;margin:12px auto;font:12.5px ui-monospace,monospace;color:var(--dim);flex-wrap:wrap}
.leg span{display:inline-flex;align-items:center;gap:6px}.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.leg b{color:var(--ink)}
.note{color:var(--dim);font-size:12.5px;max-width:800px;margin:18px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--fila)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--clus);font-size:12px}
a{color:var(--fila);text-decoration:none}
button{background:#0c1226;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 14px;font:13px ui-serif,Georgia;cursor:pointer;margin:4px}
button:hover{background:#141d3a}
</style></head><body><div class="wrap">
<h1>The Real Cosmic Web</h1><div class="sub">25,000 SDSS galaxies · relaxation-labeled</div>
<p class="lede">This wedge is <b>real</b>: every point is a galaxy the Sloan survey measured, placed by its redshift. You are looking at
the actual <b>Cosmic Web</b> — <i>filaments</i> strung between <i>clusters</i>, draped around vast empty <i>voids</i>. Then the
relaxation engine labels the web from each galaxy's local density: the <span style="color:var(--clus)">clusters</span> are the
clogged, stagnant knots; the <span style="color:var(--void)">voids</span> are the free-flowing expanse; the
<span style="color:var(--fila)">filaments</span> are the bridges between.</p>
<canvas id="web" width="620" height="620"></canvas>
<div class="leg" id="leg"></div>
<div>
  <button id="bAll">all</button><button id="bVoid">voids</button><button id="bFila">filaments</button><button id="bClus">clusters</button>
</div>
<div class="note">
<b>What's real.</b> The galaxy positions and the web are real SDSS DR17 data (a 4°-thick Dec slice, z&lt;0.15). Comoving distance
uses <code>d = (c/H₀)·z</code> with H₀=70 — the radial "fingers" pointing at the apex are the classic redshift-space distortion
(<i>Fingers of God</i>): clusters smeared by their own orbital motion, itself a signature of unseen mass. The void/filament/cluster
labels come from the same relaxation engine as the rest of this site, run on the galaxies' local density.
<br><br>
<b>Where it meets our model.</b> Clusters = the <a href="../rar/">clogged</a>, dark-matter-dominated knots; voids = the free-flowing,
dark-energy expanse — the same <a href="../ontology/">poles</a>, now sorted from <i>real</i> cosmic structure instead of synthetic parcels.
</div>
<p style="margin-top:14px"><a href="../rar/">← The Clog Threshold</a> · <a href="../ontology/">The Four Poles</a> · <a href="../">Genesis</a> · <span style="color:var(--dim)">data: SDSS DR17</span></p>
</div>
<script>
const D = /*DATA*/;
const COL=['#5a60b0','#37e6ff','#e8c170'];   // void filament cluster (brighter void for visibility)
const cv=document.getElementById('web'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
const filt={0:true,1:true,2:true};
const sc=(H-40)/D.dmax, apx=W/2, apy=H-16;   // apex bottom-center
function draw(){
  ctx.clearRect(0,0,W,H);
  // faint wedge frame
  ctx.strokeStyle='rgba(120,140,190,.14)';
  for(const dd of [100,200,300,400,500,600]){ if(dd>D.dmax)continue;
    ctx.beginPath(); for(let a=-75;a<=75;a+=3){const r=dd*sc,t=a*Math.PI/180;
      const px=apx+r*Math.sin(t),py=apy-r*Math.cos(t); a===-75?ctx.moveTo(px,py):ctx.lineTo(px,py);} ctx.stroke(); }
  for(const c of [0,1,2]){ if(!filt[c])continue;
    ctx.fillStyle=COL[c]; const al=c===2?0.85:(c===1?0.6:0.4);
    for(let i=0;i<D.N;i++){ if(D.cls[i]!==c)continue;
      const px=apx+D.x[i]*sc, py=apy-D.y[i]*sc;
      ctx.globalAlpha=al; ctx.fillRect(px,py,c===2?1.7:1.3,c===2?1.7:1.3); } }
  ctx.globalAlpha=1;
  ctx.fillStyle='#7f8bb0'; ctx.font='10px ui-monospace,monospace'; ctx.textAlign='center';
  ctx.fillText('Earth', apx, apy+13);
  ctx.fillText(Math.round(D.dmax)+' Mpc', apx, apy-D.dmax*sc-4);
}
const names=['void','filament','cluster'];
document.getElementById('leg').innerHTML=names.map((n,i)=>
  `<span><i class="dot" style="background:${COL[i]}"></i>${n} · <b>${(D.counts[n]||0).toLocaleString()}</b> (${(100*D.counts[n]/D.N).toFixed(0)}%)</span>`).join('');
draw();
function setF(v){filt[0]=filt[1]=filt[2]=false; if(v<0){filt[0]=filt[1]=filt[2]=true;}else filt[v]=true; draw();}
bAll.onclick=()=>setF(-1); bVoid.onclick=()=>setF(0); bFila.onclick=()=>setF(1); bClus.onclick=()=>setF(2);
</script></body></html>
"""


if __name__ == "__main__":
    main()
