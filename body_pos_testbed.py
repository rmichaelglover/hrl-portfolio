#!/usr/bin/env python3
"""HRL on REAL data — wearable accelerometer body-position labeling (Huxley study).

For each subject's clinician-labelled accelerometer recording we:
  1. bin to ~600 coarse time-steps (posture is stable over minutes),
  2. discover the subject's posture directions unsupervised (k-means on the gravity
     vector — sensor mounting is subject-specific, so we calibrate per subject),
  3. run the real hrl RelaxationLabeler (affinity prior + temporal smoothing + noise),
  4. match clusters to the clinician's ground-truth codes by majority vote and score.

Emits body-pos/index.html: a per-subject data table, an aggregate confusion matrix,
a 2D accelerometer timeline, and a 3D gravity-vector scatter coloured by posture.
"""
from __future__ import annotations
import csv, glob, json, os, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from hrl.body_pos import affinity_prior, session_compatibility
from hrl.core import RelaxationLabeler
from sklearn.cluster import KMeans

DATA = "/home/rmichaelglover/Code/Huxley/**/*.accel.pos.csv"   # recursive: PSS + UofM subjects
TARGET = 600


def load_binned(path, target=TARGET):
    T, X, P = [], [], []
    with open(path) as fh:
        for d in csv.DictReader(fh):
            try:
                t = float(d["time"]); x, y, z = float(d["x"]), float(d["y"]), float(d["z"]); p = d["pos"].strip()
            except Exception:
                continue
            if p == "":
                continue
            T.append(t); X.append((x, y, z)); P.append(int(float(p)))
    if len(T) < 50:
        return None
    T, X, P = np.array(T), np.array(X), np.array(P)
    ok = (np.linalg.norm(X, axis=1) > 3) & (P >= 0)        # drop dead rows + unknown(-1) labels
    T, X, P = T[ok], X[ok], P[ok]
    if len(T) < 50:
        return None
    edges = np.linspace(T[0], T[-1], target + 1)
    idx = np.clip(np.digitize(T, edges) - 1, 0, target - 1)
    bt, bx, bp = [], [], []
    for b in range(target):
        m = idx == b
        if m.sum() < 3:
            continue
        bt.append(T[m].mean()); bx.append(X[m].mean(0)); bp.append(np.bincount(P[m]).argmax())
    return np.array(bt), np.array(bx), np.array(bp)


def run_subject(path):
    out = load_binned(path)
    if out is None:
        return None
    t, X, gt = out
    codes = sorted(set(gt.tolist()))
    k = max(2, len(codes))
    U = X / np.linalg.norm(X, axis=1, keepdims=True)
    modes = KMeans(n_clusters=k, n_init=5, random_state=0).fit(U).cluster_centers_
    modes = modes / np.linalg.norm(modes, axis=1, keepdims=True) * 9.81
    prior = affinity_prior(X, modes)
    compat = session_compatibility(X, modes, t, temporal_strength=0.6)
    res = RelaxationLabeler(compat, prior, noise=True, noise_gain=1.2,
                            prior_strength=0.6, max_iterations=60).run()
    hrl, raw = res.assignments, prior.argmax(1)
    # map cluster -> ground-truth code by majority vote
    cmap = {}
    for c in set(hrl.tolist()):
        if c == -1:
            continue
        g = gt[hrl == c]
        cmap[c] = int(np.bincount(g).argmax()) if len(g) else -1
    pred = np.array([cmap.get(c, -1) for c in hrl])
    valid = hrl != -1
    acc = float((pred[valid] == gt[valid]).mean()) if valid.any() else 0.0
    flips = lambda a: int((a[1:] != a[:-1]).sum())
    return {"subject": os.path.basename(path).split(".")[0], "n": int(len(gt)),
            "codes": codes, "acc": round(acc, 4),
            "flips_hrl": flips(hrl), "flips_truth": flips(gt),
            "noise": int((hrl == -1).sum()),
            "t": t, "X": X, "gt": gt, "hrl": hrl, "pred": pred, "modes": modes}


def main():
    files = sorted(f for f in glob.glob(DATA, recursive=True) if ".original" not in f)
    print(f"{len(files)} labelled subjects")
    rows, conf = [], {}
    sample = None
    accs = []
    for f in files:
        r = run_subject(f)
        if r is None:
            continue
        rows.append({k: r[k] for k in ("subject", "n", "codes", "acc", "flips_hrl", "flips_truth", "noise")})
        accs.append(r["acc"])
        for g, p in zip(r["gt"], r["pred"]):
            if p < 0:
                continue
            conf[(int(g), int(p))] = conf.get((int(g), int(p)), 0) + 1
        if sample is None and r["acc"] > 0.9:
            sample = r
        print(f"  {r['subject']:14} n={r['n']:4d} acc={r['acc']:.3f} flips(hrl/truth)={r['flips_hrl']}/{r['flips_truth']}")
    print(f"\nMEAN ACCURACY across {len(accs)} subjects: {np.mean(accs):.3f}")

    codes = sorted({c for (g, p) in conf for c in (g, p)})
    cmat = [[conf.get((g, p), 0) for p in codes] for g in codes]

    # 3D gravity vectors (subsample) coloured by HRL posture, from the sample subject
    s = sample
    step = max(1, len(s["X"]) // 400)
    pts = [{"v": [round(float(x), 2) for x in s["X"][i]], "p": int(s["pred"][i]), "g": int(s["gt"][i])}
           for i in range(0, len(s["X"]), step)]
    timeline = {"t": [round(float(x - s["t"][0]), 1) for x in s["t"]],
                "ax": [round(float(v), 2) for v in s["X"][:, 0]],
                "ay": [round(float(v), 2) for v in s["X"][:, 1]],
                "az": [round(float(v), 2) for v in s["X"][:, 2]],
                "gt": [int(v) for v in s["gt"]], "hrl_pred": [int(v) for v in s["pred"]],
                "subject": s["subject"]}

    data = {"rows": rows, "mean_acc": round(float(np.mean(accs)), 4), "n_subj": len(accs),
            "codes": codes, "cmat": cmat, "pts3d": pts, "timeline": timeline}
    (HERE / "body_pos_data.json").write_text(json.dumps(data), encoding="utf-8")
    out = HERE / "body-pos" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)), encoding="utf-8")
    print(f"wrote body_pos_data.json + {out} ({len(rows)} subjects, confusion {len(codes)}x{len(codes)})")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HRL on Real Data — wearable body-position labeling</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--line:#2b2740;--cyan:#37e6ff}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:34px 18px 70px}
h1{font:700 clamp(22px,4vw,38px)/1.1 ui-serif,Georgia,serif;margin:0 0 4px;text-align:center}
.sub{text-align:center;color:var(--cyan);letter-spacing:3px;text-transform:uppercase;font-size:12px;margin-bottom:14px}
.lede{color:var(--dim);max-width:760px;margin:0 auto 16px;font-size:14.5px;text-align:center}
.big{text-align:center;margin:14px 0}.big .n{font:700 46px ui-serif,Georgia,serif;color:var(--cyan)}.big .l{color:var(--dim);font-size:13px}
h2{font-size:20px;border-bottom:1px solid var(--line);padding-bottom:8px;margin:30px 0 12px;font-family:ui-serif,Georgia,serif}
table{width:100%;border-collapse:collapse;font:12.5px ui-monospace,monospace}
th,td{padding:4px 8px;text-align:right;border-bottom:1px solid #1b1830}th{color:var(--gold);text-align:right}
td:first-child,th:first-child{text-align:left}
.barcell{position:relative}.barcell .b{position:absolute;left:0;top:2px;bottom:2px;background:rgba(55,230,255,.18);border-radius:3px}
svg,canvas{display:block;max-width:100%}
#tl{width:100%;height:300px} #cm{width:100%;max-width:460px;margin:0 auto} #c3{width:100%;height:420px;cursor:grab}
.note{color:var(--dim);font-size:13px;margin-top:8px}
.legend{color:var(--dim);font-size:12.5px;margin-top:6px}.legend i{display:inline-block;width:11px;height:11px;border-radius:50%;vertical-align:middle;margin:0 4px}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:12.5px}
</style></head><body><div class="wrap">
<h1>HRL on Real Data</h1><div class="sub">wearable accelerometer · body-position labeling</div>
<p class="lede">Real clinician-labelled accelerometer recordings (the Huxley body-position study). Each second's gravity vector is a reading;
the <code>hrl.RelaxationLabeler</code> (affinity prior + temporal smoothing + a noise label) assigns a posture. Postures are calibrated
per subject (sensor mounting varies), then matched to the clinician's codes and scored. No synthetic data.</p>
<div class="big"><span class="n" id="macc"></span><div class="l">mean accuracy across <span id="nsub"></span> subjects vs. clinician ground truth</div></div>

<h2>Per-subject results</h2>
<table id="tbl"><thead><tr><th>subject</th><th>seconds</th><th>positions</th><th>accuracy</th><th>HRL flips</th><th>clinician flips</th><th>noise</th></tr></thead><tbody></tbody></table>
<p class="note">HRL flips &gt; clinician flips: the engine slightly over-segments (flags more posture changes than the clinician marked) — an honest artifact of per-second labeling without heavier temporal damping.</p>

<h2>A recording, second by second <small id="tlsub" style="color:var(--dim);font-weight:400"></small></h2>
<svg id="tl"></svg>
<div class="legend" id="tlleg"></div>

<h2>Confusion matrix <small style="color:var(--dim);font-weight:400">— clinician (rows) vs HRL (cols)</small></h2>
<svg id="cm"></svg>

<h2>The gravity vectors in 3D <small style="color:var(--dim);font-weight:400">— drag to spin; coloured by HRL posture</small></h2>
<canvas id="c3" width="900" height="420"></canvas>
<div class="legend">each point a one-second reading; postures cluster where the torso held still. The clusters are the per-subject "canonical directions".</div>
<p style="margin-top:18px"><a href="../bible-hrl/">← HRL gallery</a> · the same engine that reads scripture and grows bodies, here on real wearable sensor logs.</p>
</div>
<script>
const D=/*DATA*/, ns="http://www.w3.org/2000/svg";
const PAL=["#ff8c42","#3ddc84","#5b8cff","#e8c170","#ff5470","#a98bff","#37e6ff","#ff84c8","#9bd45b"];
const codeColor={}; D.codes.forEach((c,i)=>codeColor[c]=PAL[i%PAL.length]);
const mk=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
document.getElementById('macc').textContent=(D.mean_acc*100).toFixed(1)+'%';
document.getElementById('nsub').textContent=D.n_subj;
// table
const tb=document.querySelector('#tbl tbody');
D.rows.slice().sort((a,b)=>b.acc-a.acc).forEach(r=>{
  const tr=document.createElement('tr');
  tr.innerHTML=`<td>${r.subject}</td><td>${r.n}</td><td>${r.codes.join(' ')}</td>`+
    `<td class="barcell"><div class="b" style="width:${(r.acc*100).toFixed(0)}%"></div>${(r.acc*100).toFixed(1)}%</td>`+
    `<td>${r.flips_hrl}</td><td>${r.flips_truth}</td><td>${r.noise}</td>`;
  tb.appendChild(tr);
});
// timeline
(function(){
 const T=D.timeline, svg=document.getElementById('tl'), W=960,H=300,L=40,Rp=10,Tp=10,Bp=70;
 svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
 document.getElementById('tlsub').textContent='· subject '+T.subject;
 const n=T.t.length, X=i=>L+(W-L-Rp)*i/(n-1);
 const all=T.ax.concat(T.ay,T.az), mn=Math.min(...all),mx=Math.max(...all), Y=v=>Tp+(H-Tp-Bp)*(1-(v-mn)/(mx-mn));
 [['ax','#ff5470'],['ay','#3ddc84'],['az','#5b8cff']].forEach(([k,c])=>{
   let d=''; T[k].forEach((v,i)=>d+=(i?'L':'M')+X(i)+' '+Y(v)+' ');
   svg.appendChild(mk('path',{d,fill:'none',stroke:c,'stroke-width':1,'stroke-opacity':0.85}));});
 // posture strips
 function strip(arr,y,label){ for(let i=0;i<n;i++){ svg.appendChild(mk('rect',{x:X(i),y:y,width:(W-L-Rp)/n+0.6,height:18,fill:codeColor[arr[i]]||'#333'})); }
   const t=mk('text',{x:L-6,y:y+13,fill:'#9b93b8','font-size':11,'text-anchor':'end','font-family':'ui-monospace'});t.textContent=label;svg.appendChild(t);}
 strip(T.gt,H-Bp+18,'clinician'); strip(T.hrl_pred,H-Bp+42,'HRL');
 const xl=mk('text',{x:(W+L)/2,y:H-4,fill:'#cfc7e6','font-size':12,'text-anchor':'middle'});xl.textContent='time (binned) →';svg.appendChild(xl);
 document.getElementById('tlleg').innerHTML='accel <span style="color:#ff5470">x</span> <span style="color:#3ddc84">y</span> <span style="color:#5b8cff">z</span> · strips coloured by posture code: '+D.codes.map(c=>`<i style="background:${codeColor[c]}"></i>${c}`).join(' ');
})();
// confusion matrix
(function(){
 const svg=document.getElementById('cm'), K=D.codes.length, cell=Math.min(56,420/K), M=42, S=K*cell;
 svg.setAttribute('viewBox',`0 0 ${S+M} ${S+M}`);
 const max=Math.max(...D.cmat.flat(),1);
 for(let i=0;i<K;i++)for(let j=0;j<K;j++){ const v=D.cmat[i][j], t=v/max;
   svg.appendChild(mk('rect',{x:M+j*cell,y:M+i*cell,width:cell-1,height:cell-1,fill:`rgba(55,230,255,${0.06+0.9*t})`}));
   if(v){const tx=mk('text',{x:M+j*cell+cell/2,y:M+i*cell+cell/2+4,fill:t>0.5?'#06121a':'#cfe','font-size':10,'text-anchor':'middle','font-family':'ui-monospace'});tx.textContent=v;svg.appendChild(tx);} }
 D.codes.forEach((c,i)=>{ const a=mk('text',{x:M-6,y:M+i*cell+cell/2+4,fill:codeColor[c],'font-size':11,'text-anchor':'end','font-family':'ui-monospace'});a.textContent=c;svg.appendChild(a);
   const b=mk('text',{x:M+i*cell+cell/2,y:M-6,fill:codeColor[c],'font-size':11,'text-anchor':'middle','font-family':'ui-monospace'});b.textContent=c;svg.appendChild(b);});
})();
// 3D gravity vectors
(function(){
 const cv=document.getElementById('c3'), ctx=cv.getContext('2d'), CW=cv.width,CH=cv.height;
 const P=D.pts3d.map(p=>({v:p.v,c:codeColor[p.p]||'#888'}));
 let ax=-0.4,ay=0.5,drag=false,px=0,py=0;
 function frame(){ ctx.clearRect(0,0,CW,CH);
  const R=P.map(p=>{const[x,y,z]=p.v;
    let y1=y*Math.cos(ax)-z*Math.sin(ax),z1=y*Math.sin(ax)+z*Math.cos(ax);
    let x2=x*Math.cos(ay)+z1*Math.sin(ay),z2=-x*Math.sin(ay)+z1*Math.cos(ay);
    return {x:x2,y:y1,z:z2,c:p.c};}).sort((a,b)=>a.z-b.z);
  // axes
  ctx.strokeStyle='#2b2740';ctx.lineWidth=1;
  for(const R2 of R){ const s=CH*0.34/(20+R2.z), X=CW/2+R2.x*s, Y=CH/2+R2.y*s, t=0.5-R2.z*0.02;
    ctx.fillStyle=R2.c; ctx.globalAlpha=Math.max(0.4,t); ctx.beginPath();ctx.arc(X,Y,3.0,0,7);ctx.fill();}
  ctx.globalAlpha=1; if(!drag) ay+=0.004; requestAnimationFrame(frame); }
 cv.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;});
 addEventListener('pointerup',()=>drag=false);
 addEventListener('pointermove',e=>{if(!drag)return;ay+=(e.clientX-px)*0.01;ax+=(e.clientY-py)*0.01;px=e.clientX;py=e.clientY;});
 frame();
})();
</script></body></html>"""


if __name__ == "__main__":
    main()
