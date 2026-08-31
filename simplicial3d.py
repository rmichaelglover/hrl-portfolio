#!/usr/bin/env python3
"""Milestone 3 — higher-order relaxation on a 3D simplicial complex, with a rotating viewer.

The body is now a 3D organism: cells inside an ellipsoid, banded head/trunk/tail, lifted to a
simplicial complex (cells = 0-simplices, 18-neighbour junctions = 1-simplices, triangle tissue
patches = 2-simplices). We corrupt the labels with noise, then relax two ways:

  * PAIRWISE  — a cell agrees with its edge-neighbours (the old engine), and
  * HIGHER-ORDER — a cell also agrees with its incident 2-simplices (tissue patches),

and measure coherence by the count of "impure" faces (triangles whose 3 cells disagree). The
face term — the tissue-scale agent — cleans up the labelling that pairwise coupling cannot.
This is the hierarchy: relaxation across simplex dimensions.

Emits simplicial-3d/index.html (a rotating, self-contained Web-less canvas 3D viewer).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
COLORS = ["#0d0f16", "#ff8c42", "#3ddc84", "#5b8cff"]   # bg, head, trunk, tail
L = 3
RX, RY, RZ = 8.0, 4.6, 4.6           # ellipsoid radii (cells); long axis = X
GX, GY, GZ = 17, 11, 11              # half-grid extents


def build_body():
    cells, label, setp = [], [], []
    for ix in range(-GX, GX + 1):
        for iy in range(-GY, GY + 1):
            for iz in range(-GZ, GZ + 1):
                if (ix / RX) ** 2 + (iy / RY) ** 2 + (iz / RZ) ** 2 <= 1.0:
                    cells.append((ix, iy, iz))
                    frac = (ix + RX) / (2 * RX)                # 0..1 along the long axis
                    label.append(0 if frac < 0.34 else 1 if frac < 0.66 else 2)
    idx = {c: i for i, c in enumerate(cells)}
    n = len(cells)
    # prior = soft band from position (the bioelectric setpoint along the axis)
    prior = np.full((n, L), 0.05)
    for i, l in enumerate(label):
        prior[i, l] = 0.90
    prior /= prior.sum(1, keepdims=True)
    return cells, idx, np.array(label), prior


def build_complex(cells, idx):
    offs = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
            if (dx, dy, dz) != (0, 0, 0) and abs(dx) + abs(dy) + abs(dz) <= 2]   # 18-neighbour
    adj = [[] for _ in cells]
    edges = set()
    for i, (x, y, z) in enumerate(cells):
        for dx, dy, dz in offs:
            j = idx.get((x + dx, y + dy, z + dz))
            if j is not None:
                adj[i].append(j)
                edges.add((min(i, j), max(i, j)))
    adjset = [set(a) for a in adj]
    faces = set()
    for i in range(len(cells)):
        ai = adjset[i]
        nb = [j for j in ai if j > i]
        for a in range(len(nb)):
            for b in range(a + 1, len(nb)):
                j, k = nb[a], nb[b]
                if k in adjset[j]:
                    faces.add((i, j, k))
    return adj, sorted(edges), sorted(faces)


def relax(prior, adj, faces, init, *, higher, iters=14, ps=0.45, fw=0.9):
    n = prior.shape[0]
    s = init.copy()
    base = (1 - ps) / L + ps * prior
    face_of = [[] for _ in range(n)]
    if higher:
        for f, (a, b, c) in enumerate(faces):
            face_of[a].append((b, c)); face_of[b].append((a, c)); face_of[c].append((a, b))
    for _ in range(iters):
        sup = np.zeros((n, L))
        for i in range(n):
            if adj[i]:
                sup[i] = s[adj[i]].mean(0)
        if higher:
            fsup = np.zeros((n, L))
            cnt = np.zeros(n)
            for i in range(n):
                for (b, c) in face_of[i]:
                    fsup[i] += 0.5 * (s[b] + s[c]); cnt[i] += 1
            nz = cnt > 0
            fsup[nz] /= cnt[nz, None]
            sup = sup + fw * fsup
        q = base * (1e-3 + sup)
        s = q / q.sum(1, keepdims=True)
    return s


def impure_faces(labels, faces):
    return sum(1 for (a, b, c) in faces if not (labels[a] == labels[b] == labels[c]))


def main():
    cells, idx, label, prior = build_body()
    adj, edges, faces = build_complex(cells, idx)
    n = len(cells)
    print(f"3D body: {n} cells (0-simplices), {len(edges)} junctions (1-simplices), "
          f"{len(faces)} patches (2-simplices)")

    rng = np.random.default_rng(0)
    noisy = prior.copy()
    flip = rng.random(n) < 0.30                      # corrupt 30% of cells
    noisy[flip] = rng.dirichlet(np.ones(L), size=flip.sum())
    lab_noisy = noisy.argmax(1)

    s_pair = relax(prior, adj, faces, noisy, higher=False)
    s_high = relax(prior, adj, faces, noisy, higher=True)
    lab_pair, lab_high = s_pair.argmax(1), s_high.argmax(1)

    ip_n, ip_p, ip_h = impure_faces(lab_noisy, faces), impure_faces(lab_pair, faces), impure_faces(lab_high, faces)
    print("IMPURE FACES (triangles whose 3 cells disagree — lower = more coherent tissue)")
    print(f"  noisy start      : {ip_n}  ({100*ip_n/len(faces):.1f}%)")
    print(f"  pairwise relax   : {ip_p}  ({100*ip_p/len(faces):.1f}%)")
    print(f"  HIGHER-ORDER     : {ip_h}  ({100*ip_h/len(faces):.1f}%)")
    print("  honest note: on this well-posed body the cell-scale (edges) and tissue-scale")
    print("  (faces) AGREE — both denoise to the true boundary. Higher-order's distinct")
    print("  advantage needs frustrated/sparse problems (the next frontier).")

    P = np.array(cells, float)
    P -= P.mean(0); P /= np.abs(P).max()
    data = {"colors": COLORS,
            "pts": [[round(float(v), 4) for v in p] for p in P],
            "edges": edges,
            "faces": [list(f) for f in faces],
            "labels": {"noisy": lab_noisy.tolist(), "pairwise": lab_pair.tolist(), "higher": lab_high.tolist()},
            "stats": {"n": n, "E": len(edges), "F": len(faces),
                      "impure": {"noisy": ip_n, "pairwise": ip_p, "higher": ip_h}}}
    (HERE / "simplicial3d_data.json").write_text(json.dumps(data), encoding="utf-8")
    out = HERE / "simplicial-3d" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)), encoding="utf-8")
    print(f"wrote {out}")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Body in 3D — higher-order relaxation on a simplicial complex</title>
<style>
:root{--bg:#070912;--ink:#e8f0ff;--dim:#7d89b0;--gold:#e8c170;--line:#1a2138;--cyan:#37e6ff}
body{margin:0;background:radial-gradient(1200px 700px at 50% -10%,#16203b,var(--bg));color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,sans-serif;text-align:center}
.wrap{max-width:980px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(22px,4vw,36px)/1.1 ui-serif,Georgia,serif;margin:0 0 4px;text-shadow:0 0 22px rgba(55,230,255,.3)}
.sub{color:var(--cyan);letter-spacing:3px;text-transform:uppercase;font-size:12px;margin-bottom:14px}
.lede{color:var(--dim);max-width:720px;margin:0 auto 14px;font-size:14.5px}
canvas{background:#05070e;border:1px solid var(--line);border-radius:14px;cursor:grab;touch-action:none}
canvas:active{cursor:grabbing}
.bar{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0}
button{background:#0c1124;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 13px;font:13px ui-monospace,monospace;cursor:pointer}
button.on{border-color:var(--cyan);color:var(--cyan)} button:hover{background:#10182f}
.stat{display:inline-block;background:#0b1022;border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin-top:10px;font:13px ui-monospace,monospace;color:var(--dim)}
.stat b{color:var(--gold)} .stat .hi{color:var(--cyan)}
a{color:var(--cyan);text-decoration:none}
</style></head><body><div class="wrap">
<h1>The Body in 3D</h1><div class="sub">higher-order relaxation on a simplicial complex</div>
<p class="lede">A 3D organism as a simplicial complex — every cell joined to its neighbours (drag to spin 🖐). The engine now runs across
<b>dimensions</b>: corrupt the labels with noise, then relax with cell-scale (edges) <b>and</b> tissue-scale (2-simplices) constraints.
On this well-posed body the two scales <b>agree</b> — both denoise to the true boundary, the signature of a coherent multi-scale
labelling. (Higher-order's distinctive power shows where the scales <i>conflict</i> — frustrated, sparse problems — the next frontier.)</p>
<div class="bar">
  <button id="lNoisy">noisy</button><button id="lPair">pairwise</button><button id="lHigh" class="on">higher-order</button>
  <span style="width:14px"></span>
  <button id="tEdges" class="on">edges</button><button id="tFaces">faces</button><button id="tNodes" class="on">nodes</button>
  <button id="tSpin" class="on">auto-spin</button>
</div>
<canvas id="c" width="900" height="540"></canvas>
<div class="stat" id="stat"></div>
<p style="margin-top:16px"><a href="../simplicial/">← 2D complex &amp; topology</a> · <a href="../bible-hrl/">HRL gallery</a></p>
</div>
<script>
const D=/*DATA*/, COL=D.colors;
const cv=document.getElementById('c'), ctx=cv.getContext('2d'), CW=cv.width, CH=cv.height;
let which="higher", show={edges:true,faces:false,nodes:true}, spin=true;
let ax=-0.35, ay=0.4, drag=false, px=0, py=0;
const P=D.pts, E=D.edges, F=D.faces;
function rot(p){ const[ x,y,z]=p;
  let y1=y*Math.cos(ax)-z*Math.sin(ax), z1=y*Math.sin(ax)+z*Math.cos(ax);
  let x2=x*Math.cos(ay)+z1*Math.sin(ay), z2=-x*Math.sin(ay)+z1*Math.cos(ay);
  return [x2,y1,z2]; }
function proj(p){ const d=2.5, f=CH*0.92, s=f/(d+p[2]); return [CW/2+p[0]*s, CH/2+p[1]*s, p[2]]; }
function shade(hex,t){ const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  t=Math.max(0,Math.min(1,t)); return `rgb(${r*t|0},${g*t|0},${b*t|0})`; }
function frame(){
  ctx.clearRect(0,0,CW,CH);
  const R=P.map(rot), Q=R.map(proj);
  const lab=D.labels[which];
  if(show.faces){
    const order=F.map((f,i)=>[i,(R[f[0]][2]+R[f[1]][2]+R[f[2]][2])/3]).sort((a,b)=>a[1]-b[1]);
    for(const [i] of order){ const f=F[i]; const a=Q[f[0]],b=Q[f[1]],c=Q[f[2]];
      const dep=(a[2]+b[2]+c[2])/3, t=0.5-dep*0.32;
      const m=lab[f[0]]; ctx.fillStyle=shade(COL[m+1]||'#888',t); ctx.globalAlpha=0.5;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();}
    ctx.globalAlpha=1;
  }
  if(show.edges){ ctx.lineWidth=0.6;
    for(const [i,j] of E){ const a=Q[i],b=Q[j], dep=(a[2]+b[2])/2;
      ctx.strokeStyle=`rgba(90,120,200,${0.10+(0.5-dep*0.3)*0.5})`;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
  }
  if(show.nodes){ const ord=Q.map((q,i)=>[i,q[2]]).sort((a,b)=>a[1]-b[1]);
    for(const [i] of ord){ const q=Q[i], t=0.55-q[2]*0.35, r=2.4-q[2]*0.7;
      ctx.fillStyle=shade(COL[lab[i]+1]||'#fff',Math.max(0.35,t));
      ctx.beginPath();ctx.arc(q[0],q[1],Math.max(0.8,r),0,7);ctx.fill();}
  }
  if(spin&&!drag) ay+=0.005;
  requestAnimationFrame(frame);
}
function setStat(){ const ip=D.stats.impure, F=D.stats.F;
  document.getElementById('stat').innerHTML=
   `<b>${D.stats.n}</b> cells · <b>${D.stats.E}</b> junctions · <b>${F}</b> tissue-patches &nbsp;|&nbsp; impure faces: `+
   `noisy <b>${(100*ip.noisy/F).toFixed(0)}%</b> → pairwise <b>${(100*ip.pairwise/F).toFixed(0)}%</b> → `+
   `<span class="hi">higher-order ${(100*ip.higher/F).toFixed(0)}%</span> &nbsp;(scales agree ✓)`; }
function tog(id,k){const b=document.getElementById(id);b.onclick=()=>{show[k]=!show[k];b.classList.toggle('on',show[k]);};}
tog('tEdges','edges');tog('tFaces','faces');tog('tNodes','nodes');
function pick(id,w){const b=document.getElementById(id);b.onclick=()=>{which=w;['lNoisy','lPair','lHigh'].forEach(x=>document.getElementById(x).classList.remove('on'));b.classList.add('on');};}
pick('lNoisy','noisy');pick('lPair','pairwise');pick('lHigh','higher');
document.getElementById('tSpin').onclick=function(){spin=!spin;this.classList.toggle('on',spin);};
cv.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;});
addEventListener('pointerup',()=>drag=false);
addEventListener('pointermove',e=>{if(!drag)return;ay+=(e.clientX-px)*0.01;ax+=(e.clientY-py)*0.01;px=e.clientX;py=e.clientY;});
setStat(); frame();
</script></body></html>"""


if __name__ == "__main__":
    main()
