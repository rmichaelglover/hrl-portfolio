#!/usr/bin/env python3
"""Editable anatomical memory, in silico — Levin's two-headed planaria as HRL.

Same compatibility kernel, same label set (the "genome"); we edit ONLY the prior
(the bioelectric setpoint / pattern memory). The wild-type setpoint regenerates a
head + a tail; the reprogrammed setpoint (posterior memory flipped head) regenerates
TWO heads — and the change is heritable across re-cuts because it lives in the prior,
not the genome. This reproduces Levin's signature result with the relaxation engine.

Emits morphogenesis.html (a side-by-side animation) + prints a verification.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import numpy as np
from hrl.morphogenesis import (body_plan, bioelectric_compatibility,
                               pattern_memory_prior, LABELS, COLORS)
from hrl.core import RelaxationLabeler

H = W = 28
HEAD, TRUNK, TAIL = 1, 2, 3


def run(target, wound, compat, *, prior_strength=0.55, iters=70):
    prior = pattern_memory_prior(target, wound, len(LABELS))
    res = RelaxationLabeler(compat, prior, prior_strength=prior_strength,
                            max_iterations=iters, record_history=True).run()
    grids = [s[:, :len(LABELS)].argmax(axis=1).reshape(target.shape) for s in res.history]
    return grids


def main():
    target = body_plan(H, W)                 # head (top) / trunk / tail (bottom)
    bipolar = target.copy()
    bipolar[bipolar == TAIL] = HEAD          # EDIT THE SETPOINT ONLY: posterior memory -> head
    wound = (target == TAIL)                 # amputate the posterior in BOTH cases
    compat = bioelectric_compatibility(H, W, len(LABELS))   # identical "genome"

    grids_wt = run(target, wound, compat)
    grids_bp = run(bipolar, wound, compat)

    def heads_at(grid):
        ys = np.where(grid == HEAD)[0]
        if len(ys) == 0:
            return (False, False)
        return (ys.min() < H * 0.34, ys.max() > H * 0.66)   # head present anterior / posterior

    wt_ant, wt_post = heads_at(grids_wt[-1])
    bp_ant, bp_post = heads_at(grids_bp[-1])
    print("VERIFICATION — final morphology")
    print(f"  wild-type   : head anterior={wt_ant}  head posterior={wt_post}  "
          f"({'one head' if wt_ant and not wt_post else 'unexpected'})")
    print(f"  reprogrammed: head anterior={bp_ant}  head posterior={bp_post}  "
          f"({'TWO HEADS' if bp_ant and bp_post else 'unexpected'})")
    print(f"  same kernel & labels in both: only the prior (setpoint) differed.")

    def pack(grids, stride=2):
        return [g.astype(int).flatten().tolist() for g in grids[::stride]] + [grids[-1].astype(int).flatten().tolist()]

    data = {"h": H, "w": W, "labels": LABELS, "colors": COLORS,
            "wt": pack(grids_wt), "bp": pack(grids_bp),
            "wound": wound.astype(int).flatten().tolist()}
    (HERE / "morphogenesis_data.json").write_text(json.dumps(data), encoding="utf-8")

    html = TEMPLATE.replace("/*DATA*/", json.dumps(data))
    out = HERE / "morphogenesis" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}  ({len(data['wt'])} frames/panel)")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Editable Anatomical Memory — HRL × Levin</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--line:#2b2740;--cyan:#37e6ff}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);
     font:16px/1.5 ui-serif,Georgia,serif;text-align:center}
.wrap{max-width:980px;margin:0 auto;padding:36px 18px 70px}
h1{font-size:clamp(22px,4vw,38px);margin:0 0 6px}
h1 small{display:block;color:var(--cyan);font-size:.42em;letter-spacing:3px;text-transform:uppercase;margin-top:12px}
.lede{color:var(--dim);max-width:720px;margin:12px auto 18px;font-size:15px}
.panels{display:flex;gap:30px;justify-content:center;flex-wrap:wrap}
.panel h3{margin:0 0 8px;font-size:17px}.panel .cap{color:var(--dim);font-size:13px;margin-top:8px;max-width:300px}
canvas{background:#0d0f16;border:1px solid var(--line);border-radius:10px;image-rendering:pixelated;width:300px;height:300px}
.ctl{display:flex;gap:14px;align-items:center;justify-content:center;margin:18px 0}
button{background:#1d1933;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 18px;font:15px ui-serif,Georgia,serif;cursor:pointer}
button:hover{background:#2a2444} input[type=range]{width:260px;accent-color:var(--gold)} .it{font:13px ui-monospace,monospace;color:var(--dim)}
.legend{color:var(--dim);font-size:13px;margin-top:8px}.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:middle;margin:0 4px}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:13px}
</style></head><body><div class="wrap">
<h1>Editable Anatomical Memory<small>Levin's two-headed planaria, as relaxation labeling</small></h1>
<p class="lede">Both creatures are amputated at the posterior, then regrow by <code>hrl.consensus</code> relaxation — cells (objects) settling onto an
anatomical identity (label) via gap-junction coupling (the compatibility kernel). The <b>only</b> difference is the <b>prior</b> — the bioelectric
<b>setpoint</b>. The kernel and labels (the "genome") are identical. Watch the wound heal.</p>
<div class="panels">
  <div class="panel"><h3 style="color:var(--gold)">Wild-type setpoint</h3><canvas id="cwt" width="28" height="28"></canvas>
    <div class="cap">memory says <b>tail</b> at the posterior → regrows a tail. <b>One head.</b></div></div>
  <div class="panel"><h3 style="color:var(--cyan)">Reprogrammed setpoint</h3><canvas id="cbp" width="28" height="28"></canvas>
    <div class="cap">edit the prior so posterior memory says <b>head</b> → regrows a head. <b>Two heads.</b> No genomic change.</div></div>
</div>
<div class="ctl"><button id="play">⏸ Pause</button><button id="replay">⟲ Replay</button>
  <input id="scrub" type="range" min="0" max="100" value="0"><span class="it" id="it">t 0</span></div>
<div class="legend"><span><i style="background:#ff8c42"></i>head</span><span><i style="background:#3ddc84"></i>trunk</span><span><i style="background:#5b8cff"></i>tail</span><span><i style="background:#0d0f16;border:1px solid #2b2740"></i>background</span></div>
<p style="margin-top:18px"><a href="../bible-hrl/">← to the HRL gallery</a> · same engine that reads the Bible, here growing a body.</p>
</div>
<script>
const D=/*DATA*/, COL=D.colors, T=Math.min(D.wt.length,D.bp.length);
const cwt=document.getElementById('cwt').getContext('2d'), cbp=document.getElementById('cbp').getContext('2d');
function draw(ctx,flat){ const img=ctx.createImageData(D.w,D.h);
  for(let i=0;i<flat.length;i++){ const c=COL[flat[i]]||'#0d0f16';
    const r=parseInt(c.slice(1,3),16),g=parseInt(c.slice(3,5),16),b=parseInt(c.slice(5,7),16);
    img.data[i*4]=r;img.data[i*4+1]=g;img.data[i*4+2]=b;img.data[i*4+3]=255;}
  ctx.putImageData(img,0,0);}
function render(t){ const i=Math.min(Math.round(t),T-1); draw(cwt,D.wt[i]); draw(cbp,D.bp[i]);
  document.getElementById('it').textContent='t '+i; document.getElementById('scrub').value=Math.round(i/(T-1)*100);}
let t=0,playing=true,last=null;
function tick(ts){ if(last==null)last=ts; const dt=(ts-last)/1000; last=ts;
  if(playing){ t+=dt*12; if(t>T-1){t=T-1;playing=false;document.getElementById('play').textContent='▶ Play';} render(t);} requestAnimationFrame(tick);}
render(0); requestAnimationFrame(tick);
document.getElementById('play').onclick=function(){if(t>=T-1)t=0;playing=!playing;this.textContent=playing?'⏸ Pause':'▶ Play';last=null;};
document.getElementById('replay').onclick=function(){t=0;playing=true;last=null;document.getElementById('play').textContent='⏸ Pause';};
document.getElementById('scrub').oninput=function(){playing=false;document.getElementById('play').textContent='▶ Play';t=this.value/100*(T-1);render(t);};
</script></body></html>"""


if __name__ == "__main__":
    main()
