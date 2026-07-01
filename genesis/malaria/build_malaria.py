#!/usr/bin/env python3
"""Opening the Escape Valves — malaria & waterborne-disease mitigation with HRL + water infrastructure.

HONEST FRAMING. This is a CONCEPTUAL / educational model on a synthetic watershed — not medical
advice and not a claim to cure anything. But the strategy it illustrates is real and evidence-based:
  * Larval Source Management (LSM) — draining, channeling or biologically treating the STANDING water
    where Anopheles mosquitoes breed. Environmental water management eliminated malaria from the US
    South and the Panama Canal zone. WHO recognizes LSM as a supplementary vector-control tool.
  * Permaculture water design — keep water MOVING and infiltrating (swales, keyline) rather than
    ponding, denying mosquitoes their nursery while still serving people and crops.
  * WASH — protecting water sources from faecal contamination breaks the dysentery cycle.

The engine's job here is the one it was born for: SPATIAL LABELING. Relaxation labeling segments the
landscape into eco-hydrological classes (upland / flowing water / standing water / wetland / village)
from terrain features + neighbourhood coherence. Then we model the malaria risk each village carries
from nearby breeding habitat, and let a greedy planner open 'escape valves' (drain the worst breeding
sites) and watch the risk fall.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "/home/rmichaelglover/Code/hrl-portfolio")

HERE = Path(__file__).resolve().parent
GN = 100
RNG = np.random.default_rng(11)
LABELS = ["upland", "flowing water", "standing water", "wetland", "village"]
FLIGHT = 7          # mosquito flight radius (cells)


def blur(a, r=2, it=1):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    out = a.astype(float)
    for _ in range(it):
        for ax in (0, 1):
            out = np.apply_along_axis(
                lambda m: np.convolve(np.r_[m[:r][::-1], m, m[-r:][::-1]], k, "same")[r:-r], ax, out)
    return out


def make_terrain():
    e = RNG.normal(0, 1, (GN, GN))
    e = blur(e, 3, 4)
    yy, xx = np.mgrid[0:GN, 0:GN]
    e += (yy / GN) * 2.2                       # a regional tilt -> a valley to the north
    e += 0.9 * np.sin(xx / GN * 3.1) * np.cos(yy / GN * 2.2)
    e -= e.min(); e /= e.max()
    return e


def flow_accumulation(e):
    """D8 flow accumulation: each cell sends its water to its lowest neighbour."""
    acc = np.ones((GN, GN))
    order = np.argsort(e.ravel())[::-1]        # high -> low
    nbr = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    lowest = np.full((GN, GN, 2), -1, int)
    for idx in order:
        y, x = divmod(int(idx), GN)
        best, bv = None, e[y, x]
        for dy, dx in nbr:
            ny, nx = y + dy, x + dx
            if 0 <= ny < GN and 0 <= nx < GN and e[ny, nx] < bv:
                bv = e[ny, nx]; best = (ny, nx)
        if best:
            acc[best] += acc[y, x]
            lowest[y, x] = best
    return acc, lowest


def classify(e, acc, slope):
    """Hydrology masks -> class priors, then a spatial relaxation pass (image-segmentation HRL)."""
    la = np.log1p(acc)
    twi = np.log(acc / (slope + 0.02))                    # topographic wetness index
    stream = la >= np.percentile(la, 90)                  # channels
    flat = slope <= np.percentile(slope, 42)
    wet = twi >= np.percentile(twi, 66)
    low = e <= np.percentile(e, 58)
    standing = (~stream) & flat & wet & low               # ponds / marsh: flat, wet, low, not a torrent
    wetland = (~stream) & (~standing) & flat & (twi >= np.percentile(twi, 52))
    P = np.full((GN, GN, 5), 0.05)
    P[..., 0] = 0.35                                       # upland base
    P[stream, 1] = 3.0
    P[standing, 2] = 3.0
    P[wetland, 3] = 1.4
    P /= P.sum(2, keepdims=True)
    # relaxation labeling: neighbours reinforce the same class (Potts smoothing)
    p = P.copy()
    for _ in range(8):
        sup = np.zeros_like(p)
        for l in range(5):
            sup[..., l] = blur(p[..., l], 1, 1)
        p = (P ** 0.5) * (p ** 0.5) * (1 + 1.5 * sup)
        p /= p.sum(2, keepdims=True)
    lab = p.argmax(2)
    return lab, p


def main():
    e = make_terrain()
    acc, lowest = flow_accumulation(e)
    gy, gx = np.gradient(e)
    slope = np.hypot(gy, gx)
    lab, p = classify(e, acc, slope)

    breeding = (lab == 2).astype(float)                # standing water = Anopheles nursery
    streams = (lab == 1)

    # place villages: moderate elevation, near water, spread out
    from scipy import ndimage
    near_water = ndimage.distance_transform_edt(~(streams | (lab == 2) | (lab == 3)))
    good = (e > 0.35) & (e < 0.72) & (near_water < 5) & (near_water > 1)
    cand = list(zip(*np.where(good)))
    RNG.shuffle(cand)
    villages = []
    for (vy, vx) in cand:
        if all((vy - uy) ** 2 + (vx - ux) ** 2 > 15 ** 2 for uy, ux, _ in villages):
            villages.append((int(vy), int(vx), int(RNG.integers(200, 2000))))
        if len(villages) >= 7:
            break

    def village_risk(breed):
        risks = []
        for (vy, vx, pop) in villages:
            y0, y1 = max(0, vy - FLIGHT), min(GN, vy + FLIGHT + 1)
            x0, x1 = max(0, vx - FLIGHT), min(GN, vx + FLIGHT + 1)
            b = breed[y0:y1, x0:x1].sum()
            risks.append(1 - np.exp(-0.03 * b))
        return np.array(risks)

    # connected breeding clusters -> intervention candidates
    clab, nc = ndimage.label(breeding)
    clusters = []
    for c in range(1, nc + 1):
        ys, xs = np.where(clab == c)
        if len(ys) < 4:
            continue
        clusters.append(dict(id=c, cy=int(ys.mean()), cx=int(xs.mean()), size=int(len(ys)),
                             cells=list(zip(ys.tolist(), xs.tolist()))))

    # GREEDY 'escape valves': repeatedly drain the cluster that cuts total (pop-weighted) risk most
    pops = np.array([v[2] for v in villages], float); pw = pops / pops.sum()
    breed = breeding.copy()
    base_risk = float((village_risk(breed) * pw).sum())
    steps = [dict(applied=0, risk=round(base_risk, 4), site=None)]
    applied = []
    remaining = {c["id"]: c for c in clusters}
    dist_to_stream = ndimage.distance_transform_edt(~streams)
    for k in range(10):
        cur = village_risk(breed)
        best, bg = None, -1
        for cid, c in remaining.items():
            trial = breed.copy()
            for (yy, xx) in c["cells"]:
                trial[yy, xx] = 0
            g = float((cur * pw).sum()) - float((village_risk(trial) * pw).sum())
            if g > bg:
                bg = g; best = cid
        if best is None or bg < 1e-4:
            break
        c = remaining.pop(best)
        for (yy, xx) in c["cells"]:
            breed[yy, xx] = 0
        d = float(np.mean([dist_to_stream[yy, xx] for (yy, xx) in c["cells"]]))
        kind = "drainage / swale" if d < 6 else "larvicide (Bti)"
        applied.append(dict(cy=c["cy"], cx=c["cx"], size=c["size"], type=kind,
                            reduced=round(bg, 4), dist=round(d, 1)))
        steps.append(dict(applied=k + 1, risk=round(float((village_risk(breed) * pw).sum()), 4),
                          site=[c["cy"], c["cx"]]))

    final_risk = steps[-1]["risk"]
    # per-step per-village risk fields (for the map glow)
    breed2 = breeding.copy(); vrisk_steps = [village_risk(breed2).round(3).tolist()]
    for a in applied:
        cid = None
        # re-apply by matching centroid (rebuild): simpler — recompute from steps' sites
    # recompute village risk at each step properly
    breed2 = breeding.copy(); vrisk_steps = [village_risk(breed2).round(3).tolist()]
    apply_cells = []
    # map each applied site back to its cluster cells
    for a in applied:
        # find the cluster nearest this centroid still in original clusters
        cc = min(clusters, key=lambda c: (c["cy"] - a["cy"]) ** 2 + (c["cx"] - a["cx"]) ** 2)
        for (yy, xx) in cc["cells"]:
            breed2[yy, xx] = 0
        vrisk_steps.append(village_risk(breed2).round(3).tolist())

    # ---- DYSENTERY: faecal contamination flows downstream from a source ----
    # pick an upstream village as the (accidental) contamination source
    up_idx = int(np.argmax([e[vy, vx] for vy, vx, _ in villages]))
    sy, sx, _ = villages[up_idx]
    def downstream(sy, sx):
        path = set(); y, x = sy, sx
        for _ in range(400):
            path.add((y, x))
            ny, nx = lowest[y, x]
            if ny < 0 or (ny, nx) in path:
                break
            y, x = ny, nx
        # spread a little around the channel
        grid = np.zeros((GN, GN))
        for (yy, xx) in path:
            grid[max(0, yy - 1):yy + 2, max(0, xx - 1):xx + 2] = 1
        return grid
    contam = downstream(sy, sx)
    def dys_affected(cgrid):
        aff = []
        for i, (vy, vx, pop) in enumerate(villages):
            near = cgrid[max(0, vy - 3):vy + 4, max(0, vx - 3):vx + 4].sum()
            aff.append(1 if near > 0 else 0)
        return aff
    dys_before = dys_affected(contam)
    contam_after = np.zeros((GN, GN))                  # source protected -> latrine sealed, no discharge
    dys_after = dys_affected(contam_after)

    def q(a):                                          # quantize a [0,1]-ish grid to 0..9 for compact JSON
        return (np.clip(a, 0, 1) * 9).astype(int).tolist()

    shade = ((e - e.min()) / (e.max() - e.min()) * 9).astype(int)
    data = dict(
        GN=GN, labels=LABELS,
        shade=shade.tolist(), label=lab.tolist(), streams=streams.astype(int).tolist(),
        breeding=breeding.astype(int).tolist(),
        villages=[dict(y=v[0], x=v[1], pop=v[2]) for v in villages],
        vrisk_steps=vrisk_steps,
        steps=steps, interventions=applied,
        base_risk=round(base_risk, 4), final_risk=final_risk,
        reduction_pct=round(100 * (base_risk - final_risk) / base_risk, 1),
        dysentery=dict(source=[sy, sx], contam=contam.astype(int).tolist(),
                       before=dys_before, after=dys_after,
                       affected_before=int(sum(dys_before))),
    )
    (HERE / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data, separators=(",", ":"))))
    print(f"villages: {len(villages)}  breeding cells: {int(breeding.sum())}  clusters: {len(clusters)}")
    print(f"baseline pop-weighted malaria risk: {base_risk:.3f}")
    print(f"after {len(applied)} escape valves: {final_risk:.3f}  ({data['reduction_pct']}% reduction)")
    print(f"dysentery: {sum(dys_before)} villages on the contaminated channel -> {sum(dys_after)} after source protection")
    print(f"wrote {HERE/'index.html'}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Opening the Escape Valves — malaria & water mitigation</title>
<style>
:root{--bg:#04050b;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;--water:#37b6e6;--breed:#ff7a4d;--risk:#ff4d6d;--good:#5fe3a0}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#0c1626,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:960px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,33px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--good);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:760px;margin:0 auto 12px;font-size:14px}.lede b{color:var(--ink)}.lede i{color:var(--good)}
.warn{max-width:760px;margin:10px auto 16px;background:#1a1206;border:1px solid #5e3a1e;border-left:4px solid #e8a020;border-radius:0 10px 10px 0;padding:10px 14px;color:#e8cfa0;font-size:12.5px}.warn b{color:#ffcf5e}
.stage{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;align-items:flex-start}
#map{background:#02030a;border:1px solid var(--line);border-radius:12px;image-rendering:pixelated;width:100%;max-width:520px;aspect-ratio:1}
.side{flex:1 1 260px;max-width:340px;text-align:left}
.panel{display:flex;gap:10px 16px;justify-content:center;align-items:center;margin:12px auto;flex-wrap:wrap}
button{background:#0c1226;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 14px;font:13px ui-serif,Georgia;cursor:pointer}button:hover{background:#12203a}
button.on{border-color:var(--good);color:var(--good)}
input[type=range]{width:200px;accent-color:var(--good)}
.big{font:700 30px ui-serif,Georgia;color:var(--good)}
.stat{background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:13px;color:var(--dim)}
.stat b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px}
th,td{border-bottom:1px solid var(--line);padding:5px 7px;text-align:left}th{color:#fff}td{color:var(--dim)}
.leg{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:8px auto;font:11.5px ui-monospace,monospace;color:var(--dim)}
.leg span{display:inline-flex;align-items:center;gap:5px}.sw{width:11px;height:11px;border-radius:3px;display:inline-block}
.note{color:var(--dim);font-size:12.5px;max-width:800px;margin:16px auto 0;text-align:left;background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--good)} a{color:var(--water);text-decoration:none}
</style></head><body><div class="wrap">
<h1>Opening the Escape Valves</h1><div class="sub">malaria &amp; waterborne-disease mitigation · HRL + water infrastructure</div>
<p class="lede">The lethal tango: <b>water</b> and <b>people</b> settle together, and their tension breeds a deadly third —
<b>malaria</b>, from mosquitoes nursed in <b style="color:var(--breed)">standing water</b>. The relaxation engine first labels the
watershed into eco-hydrological classes; then a planner opens <i>escape valves</i> — draining or treating the worst breeding sites
(<b>Larval Source Management</b>) — and the village risk falls. Drag the slider to open valves one by one.</p>
<div class="warn"><b>Honest framing.</b> A conceptual, educational model on a <i>synthetic</i> watershed — <b>not medical advice</b> and
not a claim to cure malaria. The <i>strategy</i> is real &amp; evidence-based (LSM eliminated malaria from the US South &amp; the Panama
Canal; permaculture keeps water moving; WASH breaks the dysentery cycle). The engine's role is honest: spatial labeling + prioritization.</p>
<div class="panel">
  <button id="mMal" class="on">🦟 Malaria</button><button id="mDys">💧 Dysentery</button>
  <label style="font:12px ui-monospace,monospace;color:var(--dim)">escape valves opened <input id="sl" type="range" min="0" max="1" value="0"></label>
</div>
<div class="stage">
  <canvas id="map" width="100" height="100"></canvas>
  <div class="side" id="side"></div>
</div>
<div class="leg" id="leg"></div>
<div class="note" id="note"></div>
<p style="margin-top:14px"><a href="../ontology/">← The Four Poles</a> · <a href="../">Genesis</a> · <a href="../../">HRL portfolio</a></p>
</div>
<script>
const D = /*DATA*/;
const GN=D.GN, cv=document.getElementById('map'), ctx=cv.getContext('2d');
const off=document.createElement('canvas'); off.width=off.height=GN; const octx=off.getContext('2d');
const img=octx.createImageData(GN,GN);
let mode='mal', step=0;
document.getElementById('sl').max=D.steps.length-1;
function breedingAt(k){ // breeding grid after k interventions: start from D.breeding, remove applied cluster cells
  const g=D.breeding.map(r=>r.slice());
  return g; // handled via vrisk_steps + drained markers; map shows original breeding minus drained
}
function draw(){
  const d=img.data;
  for(let y=0;y<GN;y++)for(let x=0;x<GN;x++){ const i=(y*GN+x); const l=D.label[y][x]; const sh=D.shade[y][x];
    let r,g,b; const base=40+sh*10;
    if(l===1||D.streams[y][x]){ r=40;g=140;b=200; }         // flowing water
    else if(l===3){ r=40;g=90;b=90; }                        // wetland
    else if(l===2){ r=base*0.7;g=base*0.75;b=base*0.6; }     // land under standing (recolored below)
    else { r=base*0.9;g=base*0.85;b=base*0.6; }              // upland/land
    d[i*4]=r; d[i*4+1]=g; d[i*4+2]=b; d[i*4+3]=255;
  }
  // standing-water breeding sites (orange) — drained ones (first `step`) shown green
  const drained=new Set(); for(let k=0;k<step;k++){ const s=D.steps[k+1].site; if(s) drained.add(s[0]+','+s[1]); }
  octx.putImageData(img,0,0);
  ctx.imageSmoothingEnabled=false; ctx.clearRect(0,0,cv.width,cv.height);
  ctx.drawImage(off,0,0,cv.width,cv.height); const S=cv.width/GN;
  // breeding cells
  for(let y=0;y<GN;y++)for(let x=0;x<GN;x++){ if(D.breeding[y][x]){ ctx.fillStyle='rgba(255,122,77,.9)'; ctx.fillRect(x*S,y*S,S,S);} }
  if(mode==='dys'){
    for(let y=0;y<GN;y++)for(let x=0;x<GN;x++){ if(D.dysentery.contam[y][x] && step>0===false){ } }
    // contamination shown when valves=0 (before), cleared when slider>0 (source protected)
    if(step===0){ for(let y=0;y<GN;y++)for(let x=0;x<GN;x++){ if(D.dysentery.contam[y][x]){ ctx.fillStyle='rgba(200,60,230,.75)'; ctx.fillRect(x*S,y*S,S,S);} } }
    const s=D.dysentery.source; ctx.fillStyle='#ff2d7d'; ctx.beginPath(); ctx.arc(s[1]*S+S/2,s[0]*S+S/2,7,0,7); ctx.fill();
    ctx.fillStyle='#fff'; ctx.font='9px sans-serif'; ctx.fillText('☣ source',s[1]*S-8,s[0]*S-6);
  }
  // drained/treated interventions (green ✚)
  ctx.strokeStyle='#5fe3a0'; ctx.lineWidth=2;
  for(let k=0;k<step;k++){ const s=D.steps[k+1].site; if(!s)continue; const cx=s[1]*S+S/2, cy=s[0]*S+S/2;
    ctx.beginPath();ctx.moveTo(cx-5,cy);ctx.lineTo(cx+5,cy);ctx.moveTo(cx,cy-5);ctx.lineTo(cx,cy+5);ctx.stroke(); }
  // villages with risk halo
  const vr = mode==='mal' ? D.vrisk_steps[Math.min(step,D.vrisk_steps.length-1)] : null;
  D.villages.forEach((v,i)=>{ const cx=v.x*S+S/2, cy=v.y*S+S/2;
    if(mode==='mal'){ const rk=vr[i]; const g=ctx.createRadialGradient(cx,cy,0,cx,cy,6+rk*22);
      g.addColorStop(0,`rgba(255,77,109,${0.55*rk+0.12})`); g.addColorStop(1,'rgba(255,77,109,0)');
      ctx.fillStyle=g; ctx.beginPath();ctx.arc(cx,cy,6+rk*22,0,7);ctx.fill(); }
    else { const aff=step>0?D.dysentery.after[i]:D.dysentery.before[i];
      ctx.fillStyle=aff?'rgba(200,60,230,.5)':'rgba(95,227,160,.4)'; ctx.beginPath();ctx.arc(cx,cy,12,0,7);ctx.fill(); }
    ctx.fillStyle='#fff'; ctx.beginPath();ctx.arc(cx,cy,3,0,7);ctx.fill();
  });
}
function updateSide(){
  const s=D.steps[step];
  if(mode==='mal'){
    const rr=100*(D.base_risk - s.risk)/D.base_risk;
    let html=`<div class="stat">pop-weighted malaria risk<div class="big">${(s.risk*100).toFixed(0)}%</div>`+
      `<b>${step}</b> of ${D.interventions.length} escape valves opened · <b style="color:var(--good)">${rr.toFixed(0)}% reduction</b> from baseline ${(D.base_risk*100).toFixed(0)}%</div>`;
    html+='<table><tr><th>#</th><th>site</th><th>action</th><th>risk cut</th></tr>';
    D.interventions.forEach((a,i)=>{ const on=i<step;
      html+=`<tr style="opacity:${on?1:.4}"><td>${i+1}</td><td>(${a.cx},${a.cy}) ·${a.size}</td><td>${a.type}</td><td style="color:var(--good)">−${(a.reduced*100).toFixed(1)}%</td></tr>`;});
    html+='</table>';
    document.getElementById('side').innerHTML=html;
  } else {
    const aff = step>0? D.dysentery.after : D.dysentery.before;
    const n=aff.reduce((a,b)=>a+b,0);
    document.getElementById('side').innerHTML=`<div class="stat">waterborne dysentery<div class="big" style="color:${n?'#c83ce6':'var(--good)'}">${n} village${n===1?'':'s'}</div>`+
      `drawing from the faecally-contaminated channel.<br><br>${step>0?'<b style="color:var(--good)">Source protected</b> — the upstream latrine is sealed (WASH), and the downstream channel runs clean.':'Slide right to <b>protect the source</b> (seal the upstream latrine).'}</div>`+
      `<div style="font-size:12px;color:var(--dim);margin-top:8px">Dysentery is fecal–oral: contamination rides the flow <i>downstream</i>. The fix isn\'t draining water — it\'s keeping filth out of it.</div>`;
  }
}
function render(){ draw(); updateSide(); }
document.getElementById('sl').oninput=function(){ step=+this.value; render(); };
document.getElementById('mMal').onclick=function(){ mode='mal'; this.classList.add('on'); document.getElementById('mDys').classList.remove('on');
  document.getElementById('sl').max=D.steps.length-1; if(step>1&&false)step=step; render(); };
document.getElementById('mDys').onclick=function(){ mode='dys'; this.classList.add('on'); document.getElementById('mMal').classList.remove('on');
  document.getElementById('sl').max=1; if(step>1)step=1; document.getElementById('sl').value=step; render(); };
document.getElementById('leg').innerHTML=
  '<span><i class="sw" style="background:#37b6e6"></i>flowing water</span>'+
  '<span><i class="sw" style="background:#ff7a4d"></i>standing water (breeding)</span>'+
  '<span><i class="sw" style="background:#5fe3a0"></i>escape valve opened</span>'+
  '<span><i class="sw" style="background:#ff4d6d"></i>village malaria risk</span>'+
  '<span><i class="sw" style="background:#c83ce6"></i>contaminated channel</span>';
document.getElementById('note').innerHTML=
  '<b>What the engine does &amp; what it can\'t.</b> Relaxation labeling segments the terrain into water/land classes (the same image-'+
  'segmentation task it was invented for), and a greedy planner ranks which breeding sites to open first for the biggest drop in '+
  'population-weighted risk. What it <i>cannot</i> do is replace entomology, hydrology, or clinicians — real LSM needs ground surveys, '+
  'community consent, and integration with bed-nets &amp; treatment. This shows the <i>shape</i> of the strategy: move the water, and the '+
  'fever loses its nursery. The tango only breeds the deadly third when no escape valve is open.';
render();
</script></body></html>
"""


if __name__ == "__main__":
    main()
