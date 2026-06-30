#!/usr/bin/env python3
"""Growing-graph morphogenesis — a body that builds AND heals itself by relaxation.

Levin Milestone 2. The substrate is now a DYNAMIC graph: a single seed-cell grows by
recruiting empty in-target neighbours (division), every cell labels itself each step by
relaxation over gap-junction coupling + a bioelectric setpoint field (the prior). The
relaxation update is the engine's persistent-prior Hummel-Zucker rule, in sparse form so
it scales on the changing graph.

We grow a creature from one cell, amputate the posterior, and watch it regrow — wild-type
(regrows a tail) vs a setpoint reprogrammed posterior->head (regrows a second head).

Emits morphogenesis-grow/index.html (animation) + prints verification.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from hrl.morphogenesis import body_plan          # 0=bg,1=head,2=trunk,3=tail over a grid

H = W = 30
L = 3                                            # body labels: head, trunk, tail (0,1,2)
LABELS = ["background", "head", "trunk", "tail"]
COLORS = ["#0d0f16", "#ff8c42", "#3ddc84", "#5b8cff"]
GROW_STEPS, INJURY_STEP, HEAL_STEPS = 17, 17, 16


def neighbors_of(slot):
    y, x = divmod(slot, W)
    out = []
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W:
            out.append(ny * W + nx)
    return out


def blur(field, iters=10):
    f = field.astype(float)
    for _ in range(iters):
        acc = 4 * f.copy()
        acc[1:] += f[:-1]; acc[:-1] += f[1:]
        acc[:, 1:] += f[:, :-1]; acc[:, :-1] += f[:, 1:]
        s = acc.sum(axis=-1, keepdims=True); s[s == 0] = 1
        f = acc / s
    return f


def setpoint_field(target):
    """Coarse blurred one-hot over the 3 body labels = the bioelectric setpoint memory."""
    oh = np.zeros((H, W, L))
    for c in range(L):
        oh[..., c] = (target == c + 1)
    return blur(oh).reshape(H * W, L)


def relax(idx, nbr, prior, init, prior_strength=0.6, iters=10):
    """Sparse persistent-prior relaxation (the engine's update on the current graph)."""
    n = len(idx)
    s = init.copy()
    base = (1 - prior_strength) / L + prior_strength * prior     # respected prior, refolded each iter
    for _ in range(iters):
        support = np.zeros((n, L))
        for i in range(n):
            if nbr[i]:
                support[i] = s[nbr[i]].mean(axis=0)
        q = base * (1e-3 + support)
        s = q / q.sum(axis=1, keepdims=True)
    return s


def grow(target, in_target, mem, *, seed):
    occupied = {seed}
    strength = {seed: mem[seed].copy()}
    frames = []
    for step in range(GROW_STEPS + HEAL_STEPS):
        if step == INJURY_STEP:                                   # amputate the posterior third
            ys = sorted({sl // W for sl in occupied})
            cut = ys[int(len(ys) * 0.62)]
            for sl in [s for s in occupied if s // W >= cut]:
                occupied.discard(sl); strength.pop(sl, None)

        idx = sorted(occupied)
        pos = {sl: i for i, sl in enumerate(idx)}
        nbr = [[pos[nb] for nb in neighbors_of(sl) if nb in occupied] for sl in idx]
        prior = np.array([mem[sl] for sl in idx])
        init = np.array([strength.get(sl, mem[sl]) for sl in idx])
        s = relax(idx, nbr, prior, init)
        for i, sl in enumerate(idx):
            strength[sl] = s[i]

        frame = np.zeros(H * W, dtype=int)
        for i, sl in enumerate(idx):
            frame[sl] = int(s[i].argmax()) + 1                   # 1=head,2=trunk,3=tail; 0=empty
        frames.append(frame.tolist())

        # recruitment = division into empty in-target neighbours (the graph grows)
        recruits = set()
        for sl in occupied:
            for nb in neighbors_of(sl):
                if nb not in occupied and in_target[nb]:
                    recruits.add(nb)
        for sl in recruits:
            occupied.add(sl); strength[sl] = mem[sl].copy()
    return frames


def heads_at(frame):
    arr = np.array(frame).reshape(H, W)
    ys = np.where(arr == 1)[0]
    if not len(ys):
        return (False, False)
    return (ys.min() < H * 0.34, ys.max() > H * 0.66)


def main():
    target = body_plan(H, W)
    in_target = (target.reshape(-1) > 0)
    seed = (H // 2) * W + (W // 2)

    mem_wt = setpoint_field(target)
    bipolar = target.copy(); bipolar[bipolar == 3] = 1            # reprogram posterior memory -> head
    mem_bp = setpoint_field(bipolar)

    frames_wt = grow(target, in_target, mem_wt, seed=seed)
    frames_bp = grow(target, in_target, mem_bp, seed=seed)

    wt = heads_at(frames_wt[-1]); bp = heads_at(frames_bp[-1])
    print("VERIFICATION — growing-graph morphogenesis")
    print(f"  cells grown (wt): {sum(1 for v in frames_wt[GROW_STEPS-1] if v)} / {int(in_target.sum())} target slots")
    print(f"  wild-type    final: head_ant={wt[0]} head_post={wt[1]}  ({'one head' if wt[0] and not wt[1] else '??'})")
    print(f"  reprogrammed final: head_ant={bp[0]} head_post={bp[1]}  ({'TWO HEADS' if bp[0] and bp[1] else '??'})")

    data = {"h": H, "w": W, "labels": LABELS, "colors": COLORS,
            "injury": INJURY_STEP, "wt": frames_wt, "bp": frames_bp}
    (HERE / "morphogenesis_grow_data.json").write_text(json.dumps(data), encoding="utf-8")
    out = HERE / "morphogenesis-grow" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)), encoding="utf-8")
    print(f"wrote {out}  ({len(frames_wt)} frames/panel, injury at {INJURY_STEP})")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Body Grows Itself — growing-graph morphogenesis</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--line:#2b2740;--cyan:#37e6ff}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);font:16px/1.5 ui-serif,Georgia,serif;text-align:center}
.wrap{max-width:980px;margin:0 auto;padding:36px 18px 70px}
h1{font-size:clamp(22px,4vw,38px);margin:0 0 6px}
h1 small{display:block;color:var(--cyan);font-size:.42em;letter-spacing:3px;text-transform:uppercase;margin-top:12px}
.lede{color:var(--dim);max-width:740px;margin:12px auto 18px;font-size:15px}
.panels{display:flex;gap:30px;justify-content:center;flex-wrap:wrap}
.panel h3{margin:0 0 8px;font-size:17px}.panel .cap{color:var(--dim);font-size:13px;margin-top:8px;max-width:300px}
canvas{background:#0d0f16;border:1px solid var(--line);border-radius:10px;image-rendering:pixelated;width:300px;height:300px}
.ctl{display:flex;gap:14px;align-items:center;justify-content:center;margin:18px 0}
button{background:#1d1933;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 18px;font:15px ui-serif,Georgia,serif;cursor:pointer}
button:hover{background:#2a2444} input[type=range]{width:280px;accent-color:var(--gold)} .it{font:13px ui-monospace,monospace;color:var(--dim);min-width:150px}
.legend{color:var(--dim);font-size:13px;margin-top:8px}.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:middle;margin:0 4px}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:13px}
.phase{color:var(--gold);font:13px ui-monospace,monospace}
</style></head><body><div class="wrap">
<h1>A Body Grows Itself<small>growing-graph morphogenesis — relaxation on a living substrate</small></h1>
<p class="lede">From a single <b>seed-cell</b>, the body grows by recruiting neighbours (division); every cell labels itself each step by
<code>relaxation</code> over gap-junction coupling and a bioelectric <b>setpoint field</b>. Watch it grow, suffer an <b>amputation</b>, and
<b>regrow</b>. The only difference between the two: the posterior <b>setpoint</b> — wild-type remembers <b>tail</b>, the reprogrammed remembers <b>head</b>.</p>
<div class="panels">
  <div class="panel"><h3 style="color:var(--gold)">Wild-type setpoint</h3><canvas id="cwt" width="30" height="30"></canvas>
    <div class="cap">grows, is amputated, regrows a <b>tail</b>. One head.</div></div>
  <div class="panel"><h3 style="color:var(--cyan)">Reprogrammed setpoint</h3><canvas id="cbp" width="30" height="30"></canvas>
    <div class="cap">same kernel & labels — posterior memory says <b>head</b>, so it regrows a head. <b>Two heads.</b></div></div>
</div>
<div class="ctl"><button id="play">⏸ Pause</button><button id="replay">⟲ Replay</button>
  <input id="scrub" type="range" min="0" max="100" value="0"><span class="it" id="it">t 0</span></div>
<div class="legend"><span><i style="background:#ff8c42"></i>head</span><span><i style="background:#3ddc84"></i>trunk</span><span><i style="background:#5b8cff"></i>tail</span><span><i style="background:#0d0f16;border:1px solid #2b2740"></i>empty</span></div>
<p style="margin-top:18px"><a href="../bible-hrl/">← to the HRL gallery</a> · the same engine that reads the Bible, here growing a body from one cell.</p>
</div>
<script>
const D=/*DATA*/, COL=D.colors, T=Math.min(D.wt.length,D.bp.length);
const cwt=document.getElementById('cwt').getContext('2d'), cbp=document.getElementById('cbp').getContext('2d');
function draw(ctx,flat){ const img=ctx.createImageData(D.w,D.h);
  for(let i=0;i<flat.length;i++){ const c=COL[flat[i]]||'#0d0f16';
    img.data[i*4]=parseInt(c.slice(1,3),16);img.data[i*4+1]=parseInt(c.slice(3,5),16);img.data[i*4+2]=parseInt(c.slice(5,7),16);img.data[i*4+3]=255;}
  ctx.putImageData(img,0,0);}
function render(t){ const i=Math.min(Math.round(t),T-1); draw(cwt,D.wt[i]); draw(cbp,D.bp[i]);
  const phase = i<D.injury?'growing':(i===D.injury?'✂ amputation':'regrowing');
  document.getElementById('it').textContent='t '+i+' · '+phase; document.getElementById('scrub').value=Math.round(i/(T-1)*100);}
let t=0,playing=true,last=null;
function tick(ts){ if(last==null)last=ts; const dt=(ts-last)/1000; last=ts;
  if(playing){ t+=dt*6; if(t>T-1){t=T-1;playing=false;document.getElementById('play').textContent='▶ Play';} render(t);} requestAnimationFrame(tick);}
render(0); requestAnimationFrame(tick);
document.getElementById('play').onclick=function(){if(t>=T-1)t=0;playing=!playing;this.textContent=playing?'⏸ Pause':'▶ Play';last=null;};
document.getElementById('replay').onclick=function(){t=0;playing=true;last=null;document.getElementById('play').textContent='⏸ Pause';};
document.getElementById('scrub').oninput=function(){playing=false;document.getElementById('play').textContent='▶ Play';t=this.value/100*(T-1);render(t);};
</script></body></html>"""


if __name__ == "__main__":
    main()
