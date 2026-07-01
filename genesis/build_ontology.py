#!/usr/bin/env python3
"""Genesis -> four-pole ontology.

Pipeline:
  1. Run a self-gravitating-light sim (the numpy twin of genesis/index.html).
  2. Extract the emergent halos and measure each one's (clumping, speed, geodesic clutter).
  3. Relaxation-label the halos across FOUR ontological poles
        Ordinary Matter | Ordinary Energy | Dark Matter | Dark Energy
     with a NOISE label (the null set / fifth pole).  Cluttered, uncommittable halos
     drift toward the noise-centroid -> Manny's "dark matter = the noise of the cosmic
     relaxation-labeling least-action process."
  4. Embed each parcel's per-iteration label-strengths as a point inside a regular
     tetrahedron (noise strength pulls it to the centroid) and export the trajectory.

Physics-anchored: the four poles are the 2x2 (Dark<->Ordinary) x (Matter<->Energy);
compatibility encodes E=mc^2 matter<->energy conversion, matter-matter clustering,
and dark-energy's repulsion of clustering.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/rmichaelglover/Code/hrl-portfolio")
from hrl.core import RelaxationLabeler

RNG = np.random.default_rng(7)
GN, N, STEPS = 140, 6000, 260
POLES = ["Ordinary Matter", "Ordinary Energy", "Dark Matter", "Dark Energy"]


# ---------------------------------------------------------------- 1. the sim
def run_genesis():
    px = RNG.random(N) * GN; py = RNG.random(N) * GN
    a = RNG.random(N) * 2 * np.pi; sp = 0.9 * (0.6 + 0.8 * RNG.random(N))
    vx = np.cos(a) * sp; vy = np.sin(a) * sp
    grav, cool = 0.6, 0.2
    for _ in range(STEPS):
        dens = np.zeros((GN, GN))
        gx = px.astype(int) % GN; gy = py.astype(int) % GN
        np.add.at(dens, (gy, gx), 1.0)
        blr = _blur(_blur(dens))
        g = grav * 3.6; damp = 1 - cool * 0.06
        gxs = np.clip(px.astype(int), 0, GN - 1); gys = np.clip(py.astype(int), 0, GN - 1)
        ax = (blr[gys, (gxs + 1) % GN] - blr[gys, (gxs - 1) % GN]) * g
        ay = (blr[(gys + 1) % GN, gxs] - blr[(gys - 1) % GN, gxs]) * g
        vx = (vx + ax) * damp; vy = (vy + ay) * damp
        s = np.hypot(vx, vy); m = s > 2.0
        vx[m] *= 2.0 / s[m]; vy[m] *= 2.0 / s[m]
        px = (px + vx) % GN; py = (py + vy) % GN
    return px, py, vx, vy


def _blur(a, r=2):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    out = a.copy()
    for ax in (0, 1):
        out = np.apply_along_axis(lambda m: np.convolve(np.r_[m[-r:], m, m[:r]], k, "valid"), ax, out)
    return out


# --------------------------------- 2. sample DIVERSE parcels across the field
def extract_parcels(px, py, vx, vy, blocks=10):
    """Tile the field into blocks; each block is a parcel with local
    (clumping, speed, geodesic clutter) — spanning halos, voids, streams, junctions."""
    dens = np.zeros((GN, GN))
    gx = px.astype(int) % GN; gy = py.astype(int) % GN
    np.add.at(dens, (gy, gx), 1.0)
    blr = _blur(_blur(dens))
    speed = np.hypot(vx, vy); ang = np.arctan2(vy, vx)
    bs = GN / blocks
    bx = np.clip((px // bs).astype(int), 0, blocks - 1)
    by = np.clip((py // bs).astype(int), 0, blocks - 1)
    parcels = []
    for i in range(blocks):
        for j in range(blocks):
            y0, y1 = int(i * bs), int((i + 1) * bs); x0, x1 = int(j * bs), int((j + 1) * bs)
            blk = blr[y0:y1, x0:x1]
            sel = (bx == j) & (by == i); cnt = int(sel.sum())
            if cnt >= 3:
                spd = float(speed[sel].mean()); aa = ang[sel]
                clutter = float(1 - np.hypot(np.cos(aa).mean(), np.sin(aa).mean()))
            else:                                           # a void: still, but the purest "dark" region
                spd, clutter = 0.05, 0.6
            parcels.append(dict(mass=float(cnt), peak=float(blk.max()),
                                clumping=float(blk.mean()), speed=spd, clutter=clutter,
                                cx=(x0 + x1) / 2, cy=(y0 + y1) / 2))
    return parcels, blr


def _norm(v):                                   # rank-normalize -> uniform [0,1] (balances poles)
    v = np.asarray(v, float)
    order = np.argsort(np.argsort(v))
    return order / (len(v) - 1 + 1e-9)


# ---------------------------------------- 3. four-pole prior + compatibility
def label_halos(halos):
    n = len(halos)
    c = _norm([h["clumping"] for h in halos])             # local density (clumping)
    s = _norm([h["speed"] for h in halos])                # hot/fast
    k = _norm([h["clutter"] for h in halos])              # geodesic clutter
    # the clean 2x2:
    #   matter<->energy (a):  clumped & cold (1)  ..  diffuse & fast (0)
    #   ordinary<->dark (dk): clean/luminous (0)  ..  DARK = cluttered OR diffuse (1)
    a = _norm(c * (1 - s))                     # matterness
    dk = _norm(k + (1 - c))                    # darkness = geodesic clutter OR emptiness
    OM = a * (1 - dk)                          # clumped, cold, clean     -> ordinary matter
    DM = a * dk                                # clumped, cold, CLUTTERED -> dark matter
    OE = (1 - a) * (1 - dk)                    # fast, coherent           -> ordinary energy
    DE = (1 - a) * dk                          # diffuse, dark, uniform   -> dark energy
    prior = np.stack([OM, OE, DM, DE], 1) + 1e-3
    prior /= prior.sum(1, keepdims=True)
    # ontological label-label affinity  R[OM,OE,DM,DE]
    R = np.array([
        [1.0, 0.6, 0.7, 0.1],    # OM: clusters w/ matter (OM,DM); E=mc^2 to OE; repelled by DE
        [0.6, 1.0, 0.3, 0.6],    # OE: energy<->energy (DE), convertible to OM
        [0.7, 0.3, 1.0, 0.3],    # DM: clusters w/ matter; wary of DE
        [0.1, 0.6, 0.3, 1.0],    # DE: repels clustering, kin to energy
    ])
    # reinforcement is LOCAL: nearby AND feature-similar parcels only -> spatial domains
    F = np.stack([c, s, k], 1)
    df2 = ((F[:, None, :] - F[None, :, :]) ** 2).sum(-1)
    P = np.stack([[h["cx"], h["cy"]] for h in halos], 0)
    dp2 = ((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)
    W = np.exp(-df2 / 0.14) * np.exp(-dp2 / (2 * (GN / 4.5) ** 2)); np.fill_diagonal(W, 0.0)
    C = np.einsum("ik,lm->ilkm", W, R)          # C[i,lab_i,k,lab_k] = W(i,k)*R(lab_i,lab_k)
    C /= C.max()
    res = RelaxationLabeler(C, prior, noise=True, noise_gain=0.03,
                            prior_strength=0.5, max_iterations=26, record_history=True).run()
    return res, dict(clump=c, speed=s, clutter=k, prior=prior)


# ---------------------------------------------- 4. embed in the tetrahedron
def embed(res):
    V = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float) * 1.0  # OM OE DM DE
    frames = []
    for H in res.history:                       # H: [n, 4+noise], rows already sum to 1
        real = H[:, :4]; noise = H[:, 4]
        pos = real @ V                          # noise weight -> pulls toward centroid (origin)
        frames.append([[round(float(x), 3) for x in p] for p in pos])
    dom = res.assignments
    parcels = [{"pole": int(d) if d >= 0 else -1} for d in dom]
    return V.tolist(), frames, parcels


def main():
    print("running self-gravitating-light sim ...")
    px, py, vx, vy = run_genesis()
    halos, _blrfield = extract_parcels(px, py, vx, vy)
    print(f"  sampled {len(halos)} parcels across the field")
    res, feats = label_halos(halos)
    from collections import Counter
    cnt = Counter("noise" if a < 0 else POLES[a] for a in res.assignments)
    print(f"  relaxed in {res.iterations} iters (converged={res.converged}):")
    for k in sorted(cnt): print(f"    {k:18}: {cnt[k]}")
    V, frames, parcels = embed(res)
    for i, h in enumerate(halos):
        parcels[i].update(mass=round(h["mass"], 1),
                          clump=round(float(feats['clump'][i]), 2),
                          speed=round(float(feats['speed'][i]), 2),
                          clutter=round(float(feats['clutter'][i]), 2))
    data = dict(poles=POLES, vertices=V, n_iter=len(frames),
                frames=frames, parcels=parcels,
                counts={("noise" if a < 0 else POLES[a]): 0 for a in res.assignments})
    for a in res.assignments:
        data["counts"]["noise" if a < 0 else POLES[a]] += 1
    out = Path(__file__).resolve().parent / "ontology"
    out.mkdir(exist_ok=True)
    (out / "data.json").write_text(json.dumps(data))
    (out / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)))
    print(f"  wrote {out/'data.json'} and index.html  ({len(frames)} frames, {len(parcels)} parcels)")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Four Poles — Ontological Assignment Space</title>
<style>
:root{--bg:#05060c;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;
 --om:#e8c170;--oe:#37e6ff;--dm:#c060ff;--de:#4a6bff;--noise:#aeb8d0}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#111a34,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:900px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--dm);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:14px}
.lede{color:var(--dim);max-width:730px;margin:0 auto 14px;font-size:14.5px}.lede b{color:var(--ink)}
#c{width:100%;max-width:600px;aspect-ratio:1;background:#02030a;border:1px solid var(--line);
 border-radius:14px;cursor:grab;touch-action:none;box-shadow:0 0 40px rgba(160,96,255,.10)}
.panel{display:flex;flex-wrap:wrap;gap:14px 22px;justify-content:center;align-items:center;margin:14px auto;max-width:660px}
button{background:#0c1226;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 15px;
 font:14px ui-serif,Georgia,serif;cursor:pointer}button:hover{background:#141d3a}
input[type=range]{width:230px;accent-color:var(--dm)}
.leg{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:center;margin:10px auto;max-width:640px;font:12.5px ui-monospace,monospace}
.leg span{display:inline-flex;align-items:center;gap:6px;color:var(--dim)}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.stat{font:12.5px ui-monospace,monospace;color:var(--dim);margin-top:6px}.stat b{color:var(--om)}
.note{color:var(--dim);font-size:12.5px;max-width:770px;margin:18px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--dm)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--om);font-size:12px}
a{color:var(--oe);text-decoration:none}
</style></head><body><div class="wrap">
<h1>The Four Poles</h1><div class="sub">ontological assignment space · dark matter = the noise</div>
<p class="lede">The <b>halos</b> that condensed in <a href="../">Project Genesis</a> become <b>parcels of stuff</b>, each measured for
<b>clumping</b>, <b>speed</b>, and <b>geodesic clutter</b>. The relaxation-labeling engine sorts them across the <b>four poles</b> —
<span style="color:var(--om)">Ordinary Matter</span>, <span style="color:var(--oe)">Ordinary Energy</span>,
<span style="color:var(--dm)">Dark Matter</span>, <span style="color:var(--de)">Dark Energy</span> — the 2×2 of
(Dark↔Ordinary)×(Matter↔Energy). Each parcel's identity is a <b>point inside the tetrahedron</b>; the ones too cluttered to commit
drift to the glowing <b>centroid</b> — the null set, the invisible fifth pole.</p>
<canvas id="c" width="600" height="600"></canvas>
<div class="panel">
  <button id="play">⏸ Pause</button>
  <button id="spin">◑ Spin: on</button>
  <label style="font:12px ui-monospace,monospace;color:var(--dim)">iteration <input id="scrub" type="range" min="0" max="1" value="0"></label>
</div>
<div class="leg" id="leg"></div>
<div class="stat" id="stat"></div>
<div class="note">
<b>Why the centroid is the null set.</b> In relaxation labeling every parcel's four label-strengths sum to 1 — so its identity is
literally a point in the simplex spanned by the labels. Four labels → a <b>tetrahedron</b>, and its <b>centroid is the
maximum-entropy, least-committed point</b>: the <code>noise</code> label Manny invented at Motion Reality. Where matter/energy
geodesics get too cluttered to assign cleanly, the least-action relaxation dumps them into noise — the centroid — which cashes out
physically at the <b>Dark Matter</b> pole. Dark matter as the cosmos's own unassignable residue.
<br><br>
<b>Honest framing.</b> This is a <i>conceptual model</i>, not a physics prediction — the parcels are real emergent structures from
the light sim, and the sorting is the real engine, but the four-pole ontology and the dark-matter-as-noise identification are a
hypothesis being <i>visualized</i>, not a measurement of the universe.
</div>
<p style="margin-top:14px"><a href="../">← Project Genesis</a> · <a href="../monad/">The Windowed Monad</a> · <a href="../sparc/">Real dark matter: 165 galaxies →</a></p>
</div>
<script>
const D = /*DATA*/;
const V = D.vertices, POLES = D.poles;
const COL = ['#e8c170','#37e6ff','#c060ff','#4a6bff'], NOISE='#aeb8d0';
const cv=document.getElementById('c'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
let yaw=0.7, pitch=-0.34, t=0, sub=0, playing=true, spin=true, drag=null;
const NF=D.n_iter;
document.getElementById('scrub').max=NF-1;
function rot(p){ let x=p[0],y=p[1],z=p[2];
  let x1=x*Math.cos(yaw)+z*Math.sin(yaw), z1=-x*Math.sin(yaw)+z*Math.cos(yaw);
  let y2=y*Math.cos(pitch)-z1*Math.sin(pitch), z2=y*Math.sin(pitch)+z1*Math.cos(pitch);
  return [x1,y2,z2]; }
function proj(p){ const r=rot(p), s=Math.min(W,H)*0.29; return [W/2+r[0]*s, H/2-r[1]*s, r[2]]; }
function draw(){
  ctx.clearRect(0,0,W,H);
  // edges of the tetrahedron
  ctx.strokeStyle='rgba(120,140,190,.28)'; ctx.lineWidth=1.4;
  for(let i=0;i<4;i++)for(let j=i+1;j<4;j++){const a=proj(V[i]),b=proj(V[j]);
    ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
  // centroid glow (the null set / fifth pole)
  const c0=proj([0,0,0]); const g=ctx.createRadialGradient(c0[0],c0[1],0,c0[0],c0[1],46);
  g.addColorStop(0,'rgba(200,210,235,.55)');g.addColorStop(.5,'rgba(160,120,220,.20)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(c0[0],c0[1],46,0,7);ctx.fill();
  // parcels at iteration t, depth-sorted
  const F=D.frames[t]; const idx=[...Array(F.length).keys()];
  const pr=F.map(proj); idx.sort((a,b)=>pr[a][2]-pr[b][2]);
  for(const i of idx){ const p=pr[i], pole=D.parcels[i].pole;
    const col=pole<0?NOISE:COL[pole]; const dep=(p[2]+1.8)/3.6;
    ctx.globalAlpha=0.45+0.5*dep; ctx.fillStyle=col;
    ctx.beginPath();ctx.arc(p[0],p[1],pole<0?2.6:3.4,0,7);ctx.fill();
    if(pole<0){ctx.globalAlpha=0.18;ctx.beginPath();ctx.arc(p[0],p[1],6,0,7);ctx.fill();}
  }
  ctx.globalAlpha=1;
  // vertex labels
  ctx.font='600 13px ui-serif,Georgia,serif'; ctx.textAlign='center';
  for(let i=0;i<4;i++){ const p=proj(V[i]);
    ctx.fillStyle=COL[i]; ctx.beginPath();ctx.arc(p[0],p[1],6,0,7);ctx.fill();
    ctx.shadowColor=COL[i];ctx.shadowBlur=8;
    ctx.fillText(POLES[i], p[0], p[1]+(V[i][1]>0?-14:22)); ctx.shadowBlur=0; }
}
function tick(){
  if(spin && !drag){ yaw+=0.0045; }
  if(playing){ sub++; if(sub>=5){sub=0; t=(t+1)%NF; document.getElementById('scrub').value=t;} }
  draw(); updateStat(); requestAnimationFrame(tick);
}
function updateStat(){
  document.getElementById('stat').innerHTML=`iteration <b>${t}</b> / ${NF-1} &nbsp;·&nbsp; ${D.parcels.length} parcels condensed from Genesis halos`;
}
// legend + counts
const names=['Ordinary Matter','Ordinary Energy','Dark Matter','Dark Energy'];
let lg=''; for(let i=0;i<4;i++) lg+=`<span><i class="dot" style="background:${COL[i]}"></i>${names[i]} · ${D.counts[POLES[i]]||0}</span>`;
lg+=`<span><i class="dot" style="background:${NOISE}"></i>noise → centroid · ${D.counts['noise']||0}</span>`;
document.getElementById('leg').innerHTML=lg;
document.getElementById('play').onclick=function(){playing=!playing;this.textContent=playing?'⏸ Pause':'▶ Play';};
document.getElementById('spin').onclick=function(){spin=!spin;this.textContent='◑ Spin: '+(spin?'on':'off');};
document.getElementById('scrub').oninput=function(){t=+this.value; playing=false;document.getElementById('play').textContent='▶ Play';};
cv.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];});
addEventListener('pointerup',()=>drag=null);
addEventListener('pointermove',e=>{ if(!drag)return; yaw+=(e.clientX-drag[0])*0.008; pitch+=(e.clientY-drag[1])*0.008;
  pitch=Math.max(-1.4,Math.min(1.4,pitch)); drag=[e.clientX,e.clientY];});
tick();
</script></body></html>
"""


if __name__ == "__main__":
    main()
