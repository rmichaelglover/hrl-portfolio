#!/usr/bin/env python3
"""The Radial Acceleration Relation — the 'clog threshold' of dark matter, in REAL data.

For every radial point of every SPARC galaxy we form two accelerations:
    g_bar = V_bar^2 / R      (the pull the VISIBLE matter can source)
    g_obs = V_obs^2 / R      (the pull actually MEASURED)
McGaugh, Lelli & Schombert (2016) found all ~2700 points from 150+ galaxies collapse onto ONE
tight curve with a characteristic scale g_dagger ~= 1.2e-10 m/s^2:
  * above g_dagger  ->  g_obs = g_bar   (fast free flow: light explains the spin, no dark matter)
  * below g_dagger  ->  g_obs > g_bar   (slow stagnation: the 'clog' — dark matter appears)

Manny's metaphor: free-flowing whirlpool vs a hair-clogged drain. The clog threshold is g_dagger.
We also relaxation-label the galaxies into free-flow / transitional / clogged regimes (HRL on real data).
"""
from __future__ import annotations
import sys, json, math
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/rmichaelglover/Code/hrl-portfolio")
from hrl.core import RelaxationLabeler

HERE = Path(__file__).resolve().parent
DAT = HERE.parent / "sparc" / "rotmod"
Y_DISK, Y_BUL = 0.5, 0.7
G_DAGGER = 1.2e-10                          # m/s^2, the RAR acceleration scale
CONV = 3.2408e-14                           # (km/s)^2 / kpc  ->  m/s^2
LABELS = ["free-flow", "transitional", "clogged"]


def parse(path):
    dist, R, Vobs, Vbar = None, [], [], []
    Vg, Vd, Vb = [], [], []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            if "Distance" in line:
                try: dist = float(line.split("=")[1].split("Mpc")[0])
                except Exception: pass
            continue
        p = line.split()
        if len(p) < 6: continue
        R.append(float(p[0])); Vobs.append(float(p[1]))
        Vg.append(float(p[3])); Vd.append(float(p[4])); Vb.append(float(p[5]))
    for g, d, b in zip(Vg, Vd, Vb):
        vb2 = g * abs(g) + Y_DISK * d * d + Y_BUL * b * b
        Vbar.append(math.sqrt(vb2) if vb2 > 0 else 0.0)
    return dist, R, Vobs, Vbar


def main():
    pts = []                                 # [log10 g_bar, log10 g_obs]
    gal_feat = []                            # per galaxy: outer dm fraction, mean log g_bar
    names = []
    for f in sorted(DAT.glob("*_rotmod.dat")):
        dist, R, Vobs, Vbar = parse(f)
        if len(R) < 6 or max(Vobs) <= 10:
            continue
        gb_last, go_last = [], []
        for r, vo, vb in zip(R, Vobs, Vbar):
            if r <= 0 or vb <= 0 or vo <= 0:
                continue
            gbar = CONV * vb * vb / r
            gobs = CONV * vo * vo / r
            pts.append([round(math.log10(gbar), 3), round(math.log10(gobs), 3)])
            gb_last.append(gbar); go_last.append(gobs)
        if len(gb_last) < 3:
            continue
        # outer dark-matter fraction (last 3 points)
        vo2 = sum(go_last[-3:]); vb2 = sum(gb_last[-3:])
        dmf = max(0.0, min(1.0, 1 - vb2 / vo2))
        gbar_out = np.mean(np.log10(gb_last[-3:]))
        names.append(f.name.replace("_rotmod.dat", ""))
        gal_feat.append([dmf, gbar_out])

    gal_feat = np.array(gal_feat); n = len(names)

    # --- relaxation-label the galaxies into free-flow / transitional / clogged ---
    def rnk(v):
        return np.argsort(np.argsort(v)) / (len(v) - 1)
    dmf_r = rnk(gal_feat[:, 0])
    # ordinal prior: low dmf -> free-flow, high -> clogged
    OM = np.clip(1 - 2 * dmf_r, 0, 1)                       # free-flow
    CL = np.clip(2 * dmf_r - 1, 0, 1)                       # clogged
    TR = 1 - np.abs(2 * dmf_r - 1)                          # transitional
    prior = np.stack([OM, TR, CL], 1) + 1e-3
    prior /= prior.sum(1, keepdims=True)
    R3 = np.array([[1.0, 0.5, 0.05], [0.5, 1.0, 0.5], [0.05, 0.5, 1.0]])   # ordinal affinity
    d2 = (dmf_r[:, None] - dmf_r[None, :]) ** 2
    W = np.exp(-d2 / 0.02); np.fill_diagonal(W, 0.0)
    C = np.einsum("ik,lm->ilkm", W, R3); C /= C.max()
    res = RelaxationLabeler(C, prior, noise=False, prior_strength=0.45,
                            max_iterations=30, record_history=False).run()
    from collections import Counter
    cls = res.assignments
    counts = Counter(LABELS[a] for a in cls)

    # exemplar galaxies per class (most confident)
    exemplars = {}
    for lab in range(3):
        idx = [i for i in range(n) if cls[i] == lab]
        idx.sort(key=lambda i: -res.confidence[i])
        exemplars[LABELS[lab]] = [{"name": names[i], "dmf": round(float(gal_feat[i, 0]), 2)} for i in idx[:6]]

    # RAR fit curve (McGaugh): g_obs = g_bar / (1 - exp(-sqrt(g_bar/g_dagger)))
    curve = []
    for lg in np.linspace(-12.2, -8.0, 60):
        gb = 10 ** lg
        go = gb / (1 - math.exp(-math.sqrt(gb / G_DAGGER)))
        curve.append([round(lg, 3), round(math.log10(go), 3)])

    data = dict(points=pts, curve=curve, g_dagger_log=round(math.log10(G_DAGGER), 3),
                n_gal=n, n_pts=len(pts), counts=dict(counts), exemplars=exemplars)
    (HERE / "data.json").write_text(json.dumps(data))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)))
    print(f"{len(pts)} real (g_bar,g_obs) points from {n} galaxies")
    print(f"HRL galaxy classes: {dict(counts)}")
    print(f"wrote {HERE/'index.html'}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Clog Threshold — the Radial Acceleration Relation (real data)</title>
<style>
:root{--bg:#05060c;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;--free:#e8c170;--clog:#c060ff;--fit:#37e6ff}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#101830,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:940px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--clog);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:750px;margin:0 auto 12px;font-size:14.5px}.lede b{color:var(--ink)}.lede i{color:var(--clog)}
.stage{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;margin:14px auto;align-items:flex-start}
#rar{background:#02030a;border:1px solid var(--line);border-radius:12px;flex:1 1 500px;max-width:560px}
.side{flex:1 1 250px;max-width:320px;text-align:left}
.cls{background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:10px;font-size:12.5px}
.cls h3{margin:0 0 6px;font:600 13px ui-serif,Georgia,serif}
.cls .row{display:flex;justify-content:space-between;color:var(--dim);padding:2px 0;font:11.5px ui-monospace,monospace}
.bar{height:7px;border-radius:4px;margin:5px 0 9px}
.leg{display:flex;gap:15px;justify-content:center;margin:8px auto;font:12px ui-monospace,monospace;color:var(--dim);flex-wrap:wrap}
.leg span{display:inline-flex;align-items:center;gap:6px}.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.note{color:var(--dim);font-size:12.5px;max-width:800px;margin:20px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--clog)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--free);font-size:12px}
a{color:var(--fit);text-decoration:none}
</style></head><body><div class="wrap">
<h1>The Clog Threshold</h1><div class="sub">the radial acceleration relation · real SPARC data</div>
<p class="lede">Every dot is one real measurement in one real galaxy: the pull the <b>visible matter</b> can source (horizontal)
versus the pull actually <b>measured</b> (vertical). Where the flow is fast they sit on the 1:1 line — light explains everything.
But below a critical acceleration <i>g&dagger; &asymp; 1.2&times;10<sup>&minus;10</sup> m/s&sup2;</i> they peel upward: the
<b>free‑flowing whirlpool clogs</b>, and pull appears with no light behind it. <i>Your clog threshold is a measured number.</i></p>
<div class="stage">
  <canvas id="rar" width="560" height="500"></canvas>
  <div class="side" id="side"></div>
</div>
<div class="leg">
  <span><i class="dot" style="background:var(--free)"></i>free flow (g_obs&asymp;g_bar)</span>
  <span><i class="dot" style="background:var(--clog)"></i>clogged (dark-dominated)</span>
  <span><i class="dot" style="background:var(--fit)"></i>RAR fit &amp; 1:1 line</span>
</div>
<div class="note">
<b>What's real vs. what's interpreted.</b> The dots and the tight relation are <i>real</i> — this is the actual SPARC RAR, one of the
most reproduced results in galaxy dynamics. The acceleration scale <code>g† ≈ 1.2e-10 m/s²</code> is measured. What's <i>interpreted</i>
is the story: standard cosmology reads the upturn as dark-matter halos; <i>MOND</i> reads the very same curve as gravity changing below
g†; Manny's model reads it as <i>geodesic flow clogging into stagnation</i>. The data does not yet decide between them — but any theory
must reproduce <b>this curve</b>. The side panel shows the engine relaxation-labeling the real galaxies into free-flow / transitional /
clogged regimes — <a href="../ontology/">HRL</a> on real data.
</div>
<p style="margin-top:14px"><a href="../sparc/">← rotation curves</a> · <a href="../ontology/">The Four Poles</a> · <a href="../">Genesis</a> · <span style="color:var(--dim)">data: SPARC / McGaugh et&nbsp;al. 2016</span></p>
</div>
<script>
const D = /*DATA*/;
const cv=document.getElementById('rar'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
const PAD={l:58,r:14,t:16,b:46};
const XMIN=-12.2, XMAX=-8.2, YMIN=-12.2, YMAX=-8.2;
const X=g=>PAD.l+(g-XMIN)/(XMAX-XMIN)*(W-PAD.l-PAD.r);
const Y=g=>H-PAD.b-(g-YMIN)/(YMAX-YMIN)*(H-PAD.t-PAD.b);
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle='rgba(120,140,190,.16)'; ctx.fillStyle='#7f8bb0'; ctx.font='10px ui-monospace,monospace';
  for(let g=-12;g<=-8;g++){ ctx.textAlign='right'; ctx.beginPath();ctx.moveTo(PAD.l,Y(g));ctx.lineTo(W-PAD.r,Y(g));ctx.stroke();
    ctx.fillText('10'+g, PAD.l-5, Y(g)+3);
    ctx.textAlign='center'; ctx.fillText('10'+g, X(g), H-PAD.b+15); }
  ctx.fillStyle='#9aa6c8'; ctx.textAlign='center';
  ctx.fillText('g_bar  — pull from visible matter  (m/s²)', W/2, H-8);
  ctx.save();ctx.translate(14,H/2);ctx.rotate(-Math.PI/2);ctx.fillText('g_obs — measured pull  (m/s²)',0,0);ctx.restore();
  // 1:1 line
  ctx.strokeStyle='rgba(55,230,255,.45)'; ctx.setLineDash([5,4]); ctx.lineWidth=1.4;
  ctx.beginPath();ctx.moveTo(X(XMIN),Y(YMIN));ctx.lineTo(X(-8.2),Y(-8.2));ctx.stroke(); ctx.setLineDash([]);
  // g_dagger threshold marker
  ctx.strokeStyle='rgba(192,96,255,.4)'; ctx.setLineDash([3,4]);
  ctx.beginPath();ctx.moveTo(X(D.g_dagger_log),Y(YMIN));ctx.lineTo(X(D.g_dagger_log),Y(YMAX));ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle='#c060ff'; ctx.font='italic 11px ui-serif,Georgia'; ctx.textAlign='left';
  ctx.fillText('g† clog threshold', X(D.g_dagger_log)+4, Y(YMAX)+14);
  // points, colored by discrepancy (distance above 1:1)
  for(const p of D.points){ const disc=p[1]-p[0];      // log g_obs - log g_bar
    const t=Math.max(0,Math.min(1,disc/1.1));
    const r=Math.round(232+(192-232)*t), gg=Math.round(193+(96-193)*t), b=Math.round(112+(255-112)*t);
    ctx.fillStyle=`rgba(${r},${gg},${b},.5)`;
    ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),1.7,0,7);ctx.fill(); }
  // RAR fit curve
  ctx.strokeStyle='#37e6ff'; ctx.lineWidth=2; ctx.beginPath();
  D.curve.forEach((c,i)=>{const x=X(c[0]),y=Y(c[1]); i?ctx.lineTo(x,y):ctx.moveTo(x,y);}); ctx.stroke();
}
draw();
// side panel: HRL classification of real galaxies
const COL={'free-flow':'#e8c170','transitional':'#9a8fd0','clogged':'#c060ff'};
let html='';
for(const lab of ['free-flow','transitional','clogged']){
  const c=D.counts[lab]||0, pct=(100*c/D.n_gal).toFixed(0);
  html+=`<div class="cls"><h3 style="color:${COL[lab]}">${lab} · ${c} galaxies (${pct}%)</h3>`;
  html+=`<div class="bar" style="background:${COL[lab]};width:${pct}%"></div>`;
  for(const g of (D.exemplars[lab]||[])) html+=`<div class="row"><span>${g.name}</span><span>${(g.dmf*100).toFixed(0)}% dark</span></div>`;
  html+='</div>';
}
document.getElementById('side').innerHTML=
  `<div style="font:12.5px ui-monospace,monospace;color:#8a97b8;margin-bottom:8px">the engine sorted <b style="color:#e8f0ff">${D.n_gal}</b> real galaxies by their dark-matter signature:</div>`+html;
</script></body></html>
"""


if __name__ == "__main__":
    main()
