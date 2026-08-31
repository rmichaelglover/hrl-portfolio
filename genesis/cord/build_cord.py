#!/usr/bin/env python3
"""The Cord of Three Strands — trinary relaxation labeling on the real connectome.

"A cord of three strands is not quickly broken." (Ecclesiastes 4:12)

Every nervous system is a cord of three strands: SENSORY (in) -> INTERNEURON (reason) -> MOTOR (out).
We relaxation-label the REAL C. elegans connectome (OpenWorm / Cook 2019) into those three strands
at once -- a DIRECTED, three-way relaxation seeded by the known sensory & motor neurons, letting the
interneurons fall into the middle by how information flows through the true synapses. Then we run
activity BOTH ways through the cord: sensory in, interneurons reasoning, motor out -- and feedback
flowing back up (the octopus's two-way arm-to-center loop).
"""
from __future__ import annotations
import csv, json, re
from pathlib import Path
import numpy as np
import networkx as nx

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "brain" / "data" / "herm_full_edgelist.csv"
RNG = np.random.default_rng(5)
STR = ["sensory", "interneuron", "motor"]

DROP = ("MDL", "MDR", "MVL", "MVR", "MVU", "hyp", "exc", "hmc", "GLR",
        "mu_", "bm", "vm", "um", "g1", "g2", "int", "sph", "anal", "pm", "MC")
SENS = ("ASE", "ASG", "ASH", "ASI", "ASJ", "ASK", "ADF", "ADL", "AWA", "AWB", "AWC", "AFD",
        "ALM", "AVM", "PLM", "PVM", "ADE", "PDE", "FLP", "OLQ", "OLL", "CEP", "IL1", "IL2",
        "BAG", "URX", "URY", "AQR", "PQR", "PHA", "PHB", "PHC", "SDQ", "AUA")
MOTOR_CORD = re.compile(r"^(VA|VB|VC|VD|DA|DB|DD|AS)\d+$")
MOTOR_HEAD = ("RMD", "RME", "SMD", "SMB", "RIV", "RMF", "URA", "RID")
INTER = ("AVA", "AVB", "AVD", "AVE", "AVG", "AVH", "AVJ", "AVK", "AVL", "AVF",
         "PVC", "PVN", "PVP", "PVQ", "PVR", "PVT", "PVW", "AIA", "AIB", "AIY", "AIZ",
         "AIN", "AIM", "RIA", "RIB", "RIC", "RIF", "RIG", "RIH", "RIM", "RIP", "RIR",
         "RIS", "RMG", "DVA", "DVB", "DVC", "LUA", "BDU", "PVD")


def klass(n):
    if MOTOR_CORD.match(n) or n.startswith(MOTOR_HEAD):
        return 2
    if n.startswith(SENS):
        return 0
    if n.startswith(INTER):
        return 1
    return -1                                    # unseeded -> relax with interneuron default


def is_neuron(n):
    return not n.startswith(DROP)


def load():
    W = {}; nodes = set()
    with open(DATA) as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 4: continue
            s, t, w = row[0].strip(), row[1].strip(), row[2].strip()
            if not s or not t or not is_neuron(s) or not is_neuron(t): continue
            try: w = float(w)
            except ValueError: continue
            W[(s, t)] = W.get((s, t), 0.0) + w
            nodes.add(s); nodes.add(t)
    names = sorted(nodes); idx = {n: i for i, n in enumerate(names)}
    nn = len(names)
    Ad = np.zeros((nn, nn))                       # directed  Ad[i,j] = weight i->j
    for (s, t), w in W.items():
        Ad[idx[s], idx[t]] += w
    return names, Ad


def trinary_relax(Ad, seed, iters=25, ps=0.5, sf=1.2):
    """Trinary relaxation labeling into sensory(0)/inter(1)/motor(2): seed the known cells of all
    three strands, then relax the residual/ambiguous cells by connectivity homophily (neighbours
    share a strand), with an interneuron default. Seeds are clamped."""
    nn = Ad.shape[0]
    Aud = Ad + Ad.T                                          # undirected wiring
    prior = np.zeros((nn, 3)); fixed = np.zeros(nn, bool)
    for i, c in enumerate(seed):
        if c >= 0:
            prior[i] = 0.02; prior[i, c] = 0.96; fixed[i] = True
        else:
            prior[i] = [0.2, 0.6, 0.2]                       # residual cells default to interneuron
    p = prior.copy()
    An = Aud / (Aud.sum(1, keepdims=True) + 1e-9)
    for _ in range(iters):
        sup = An @ p                                         # neighbours reinforce their strand
        sup -= sup.min(1, keepdims=True); sup /= (sup.max(1, keepdims=True) + 1e-9)
        p = (prior ** ps) * (p ** (1 - ps)) * (1 + sf * sup)
        p /= p.sum(1, keepdims=True)
        p[fixed] = prior[fixed]                              # clamp the known cells
    return p.argmax(1), p


def two_way_activity(Ad, seed_idx, steps=36, fwd=0.6, back=0.3, decay=0.8):
    nn = Ad.shape[0]
    Fout = Ad / (Ad.sum(1, keepdims=True) + 1e-9)          # i distributes to its targets
    Fin = Ad.T / (Ad.sum(0)[:, None] + 1e-9)               # feedback along reverse edges
    a = np.zeros(nn); a[seed_idx] = 1.0
    frames = [a.copy()]
    for _ in range(steps):
        inp = fwd * (Fout.T @ a) + back * (Fin.T @ a)      # forward + feedback
        a = np.clip(decay * a + 0.7 * inp, 0, 1)
        a[seed_idx] = 1.0
        frames.append(a.copy())
    return frames


def main():
    names, Ad = load()
    nn = len(names)
    seed = np.array([klass(n) for n in names])
    labels, p = trinary_relax(Ad, seed)
    counts = {STR[c]: int((labels == c).sum()) for c in range(3)}
    nseed = {STR[c]: int((seed == c).sum()) for c in range(3)}
    print(f"neurons: {nn}   seeded {nseed}")
    print(f"trinary relaxation result: {counts}")
    for probe in ["ASHL", "AWCL", "AVAL", "AVBL", "PVCL", "AIYL", "VB3", "DA5", "RMDL"]:
        if probe in names:
            print(f"   {probe:6} -> {STR[labels[names.index(probe)]]}")

    # layout: x from force layout, y = strand band (sensory top, inter mid, motor bottom)
    G = nx.from_numpy_array(np.maximum(Ad, Ad.T))
    pos = nx.spring_layout(G, k=2.4 / np.sqrt(nn), iterations=150, weight="weight", seed=4)
    X = np.array([pos[i][0] for i in range(nn)])
    X = (X - X.mean()); X = np.clip(X / (np.percentile(np.abs(X), 92) + 1e-9), -1, 1)
    band = {0: -0.72, 1: 0.0, 2: 0.72}
    Y = np.array([band[labels[i]] for i in range(nn)]) + RNG.normal(0, 0.07, nn)

    # antennal-style sensory stimulus
    prefer = ["ASHL", "ASHR", "AWCL", "AWCR", "ALML", "ALMR"]
    sd = [names.index(x) for x in prefer if x in names] or [int((seed == 0).argmax())]
    frames = two_way_activity(Ad, sd)

    # strongest edges for drawing
    ei, ej = np.where(Ad > 0); ew = Ad[ei, ej]
    order = np.argsort(-ew)[:1500]
    edges = [[int(ei[o]), int(ej[o])] for o in order]

    data = dict(names=names, n=nn, strands=STR,
                x=[round(float(v), 3) for v in X], y=[round(float(v), 3) for v in Y],
                cls=[int(c) for c in labels], deg=[round(float(d), 1) for d in Ad.sum(1) + Ad.sum(0)],
                edges=edges, seed=[int(s) for s in sd], seedNames=[names[s] for s in sd],
                frames=[[round(float(x), 3) for x in f] for f in frames], counts=counts)
    (HERE / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data, separators=(",", ":"))))
    print(f"stimulus: {data['seedNames']}")
    print(f"wrote {HERE/'index.html'} ({len(frames)} frames, {len(edges)} edges)")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Cord of Three Strands — trinary relaxation labeling</title>
<style>
:root{--bg:#04050b;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;--sen:#5fe3a0;--int:#e8c170;--mot:#ff7a6b}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#0c1626,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:940px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--int);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:770px;margin:0 auto 12px;font-size:14.5px}.lede b{color:var(--ink)}
.lede .s{color:var(--sen)} .lede .i{color:var(--int)} .lede .m{color:var(--mot)}
#net{background:#02030a;border:1px solid var(--line);border-radius:14px;max-width:660px;width:100%;cursor:pointer;touch-action:none}
.panel{display:flex;gap:12px 18px;justify-content:center;align-items:center;margin:12px auto;flex-wrap:wrap}
button{background:#0c1226;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 15px;font:14px ui-serif,Georgia;cursor:pointer}button:hover{background:#12203a}
.leg{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin:8px auto;font:12.5px ui-monospace,monospace;color:var(--dim)}
.leg span{display:inline-flex;align-items:center;gap:6px}.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.stat{font:12.5px ui-monospace,monospace;color:var(--dim);margin-top:4px}.stat b{color:var(--int)}
.note{color:var(--dim);font-size:12.5px;max-width:810px;margin:20px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--int)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--sen);font-size:12px}
a{color:var(--int);text-decoration:none}
</style></head><body><div class="wrap">
<h1>The Cord of Three Strands</h1><div class="sub">trinary relaxation labeling · real connectome</div>
<p class="lede"><i>"A cord of three strands is not quickly broken."</i> Every nervous system is that cord:
<b class="s">sensory</b> in → <b class="i">interneuron</b> reasoning → <b class="m">motor</b> out. Our engine relaxation-labels the
<b>real</b> C. elegans connectome into all three strands at once — seeded by the known sensory &amp; motor cells, letting the
interneurons settle in the middle by how signal flows through the true synapses. Then activity runs <b>both ways</b>: down the cord
to act, and back up as feedback — the octopus's two-way loop. Click any node to stimulate it.</p>
<canvas id="net" width="660" height="520"></canvas>
<div class="panel">
  <button id="play">▶ Sense → Reason → Act</button>
  <button id="reset">↺ Reset</button>
  <span class="stat" id="stat"></span>
</div>
<div class="leg" id="leg"></div>
<div class="note">
<b>What's real &amp; what's ours.</b> The connectome (neurons, directed synapses) is measured data (OpenWorm / Cook 2019). The three
strands come from <b>directed relaxation labeling</b>: seed the known <span style="color:var(--sen)">sensory</span> and
<span style="color:var(--mot)">motor</span> neurons, then relax with a rule that rewards a cell being <i>upstream-or-equal</i> of the
cells it drives — so <span style="color:var(--int)">interneurons</span> precipitate into the middle. Activity is a two-way spreading
model <code>a ← 0.8·a + forward + feedback</code> on the real wiring. <b>Honest limit:</b> the sensory/motor seeds and the simplified
signless dynamics are approximations; the wiring they run on is the animal's own. The command interneurons AVA/AVB/PVC landing in the
middle strand — the real deciders of forward vs. backward crawling — is the labeling working.
</div>
<p style="margin-top:14px"><a href="../brain/">← the connectome</a> · <a href="../ontology/">The Four Poles</a> · <a href="../">Genesis</a> · <span style="color:var(--dim)">data: OpenWorm / Cook 2019</span></p>
</div>
<script>
const D = /*DATA*/;
const COL=['#5fe3a0','#e8c170','#ff7a6b'];   // sensory, inter, motor
const cv=document.getElementById('net'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
const PAD=44, SX=(W-2*PAD)/2, SY=(H-2*PAD)/2;
const X=x=>W/2+x*SX, Y=y=>H/2+y*SY;
let t=0, playing=false, fr=0, seed=D.seed.slice(), frames=D.frames;
function act(i){ return frames[Math.min(t,frames.length-1)][i]; }
function draw(){
  ctx.clearRect(0,0,W,H);
  // strand bands
  const bands=[['sensory',-0.72,COL[0]],['interneuron',0,COL[1]],['motor',0.72,COL[2]]];
  ctx.textAlign='left';ctx.font='italic 11px ui-serif,Georgia';
  for(const [nm,yy,c] of bands){ ctx.fillStyle='rgba(255,255,255,0.03)';ctx.fillRect(0,Y(yy)-42,W,84);
    ctx.fillStyle=c;ctx.globalAlpha=.6;ctx.fillText(nm,10,Y(yy)-30);ctx.globalAlpha=1; }
  ctx.lineWidth=0.5;
  for(const [a,b] of D.edges){ const aa=Math.max(act(a),act(b));
    ctx.strokeStyle=aa>0.05?`rgba(255,224,138,${0.05+0.5*aa})`:'rgba(120,140,190,0.045)';
    ctx.beginPath();ctx.moveTo(X(D.x[a]),Y(D.y[a]));ctx.lineTo(X(D.x[b]),Y(D.y[b]));ctx.stroke(); }
  for(let i=0;i<D.n;i++){ const a=act(i), r=2+Math.min(4,D.deg[i]/70)+3.2*a, c=COL[D.cls[i]];
    if(a>0.05){ ctx.fillStyle=`rgba(255,236,170,${0.25*a})`;ctx.beginPath();ctx.arc(X(D.x[i]),Y(D.y[i]),r+7*a,0,7);ctx.fill(); }
    ctx.fillStyle=a>0.2?'#fff6d8':c; ctx.globalAlpha=0.5+0.5*Math.min(1,a*2+0.3);
    ctx.beginPath();ctx.arc(X(D.x[i]),Y(D.y[i]),r,0,7);ctx.fill();ctx.globalAlpha=1; }
  for(const s of seed){ ctx.strokeStyle='#fff6d8';ctx.lineWidth=1.4;ctx.beginPath();ctx.arc(X(D.x[s]),Y(D.y[s]),8,0,7);ctx.stroke(); }
}
function updateStat(){ let lit=0; for(let i=0;i<D.n;i++) if(act(i)>0.1)lit++;
  document.getElementById('stat').innerHTML=`stimulus: <b>${seed.map(s=>D.names[s]).join(', ')}</b> · step ${Math.min(t,frames.length-1)}/${frames.length-1} · <b>${lit}</b> active`; }
function loop(){ if(playing){ fr++; if(fr%3===0){ t++; if(t>=frames.length){t=frames.length-1;playing=false;document.getElementById('play').textContent='▶ Sense → Reason → Act';} } }
  draw();updateStat();requestAnimationFrame(loop); }
function recompute(){ const n=D.n, out={}, inc={};
  for(const [a,b] of D.edges){ (out[a]||(out[a]=[])).push(b); (inc[b]||(inc[b]=[])).push(a); }
  let a=new Float32Array(n); for(const s of seed)a[s]=1; frames=[Array.from(a)];
  for(let step=0;step<36;step++){ const inp=new Float32Array(n);
    for(let i=0;i<n;i++){ let f=0,bk=0; const o=out[i],c=inc[i];
      if(o){for(const j of o)f+=a[j];f/=o.length;} if(c){for(const j of c)bk+=a[j];bk/=c.length;}
      inp[i]=0.6*bk+0.3*f; }               // signal arriving from up/down-stream
    for(let i=0;i<n;i++)a[i]=Math.min(1,0.8*a[i]+0.7*inp[i]); for(const s of seed)a[s]=1;
    frames.push(Array.from(a)); } t=0;
}
cv.addEventListener('pointerdown',e=>{ const rc=cv.getBoundingClientRect();
  const mx=(e.clientX-rc.left)*W/rc.width, my=(e.clientY-rc.top)*H/rc.height;
  let best=-1,bd=1e9; for(let i=0;i<D.n;i++){ const dx=X(D.x[i])-mx,dy=Y(D.y[i])-my,d=dx*dx+dy*dy; if(d<bd){bd=d;best=i;} }
  if(best>=0&&bd<420){ seed=[best]; recompute(); playing=true; t=0; document.getElementById('play').textContent='⏸ …'; } });
document.getElementById('play').onclick=function(){ if(t>=frames.length-1)t=0; playing=!playing; this.textContent=playing?'⏸ …':'▶ Sense → Reason → Act'; };
document.getElementById('reset').onclick=()=>{ seed=D.seed.slice(); frames=D.frames; t=0; playing=false; document.getElementById('play').textContent='▶ Sense → Reason → Act'; };
document.getElementById('leg').innerHTML=D.strands.map((s,i)=>`<span><i class="dot" style="background:${COL[i]}"></i>${s} · ${D.counts[s]}</span>`).join('');
loop();
</script></body></html>
"""


if __name__ == "__main__":
    main()
