#!/usr/bin/env python3
"""Decision-driven morphogenesis — division gated by the field, death by the noise label.

Levin Milestone 2.5. Growth is no longer geometric: cells **commit** to an identity when
confident, **divide** only at the growing front where the bioelectric setpoint wants more
tissue, and **apoptose** (the noise label) when the setpoint strongly disagrees with their
committed identity.

This unlocks REMODELLING WITHOUT INJURY: grow a one-headed body, then flip the posterior
setpoint to *head* on the intact animal — the committed tail cells die and are replaced by
head cells, and the worm becomes two-headed with no amputation. Homeostatic error-correction.

Emits morphogenesis-remodel/index.html + prints verification.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from hrl.morphogenesis import body_plan

H = W = 30
L = 3
LABELS = ["empty", "head", "trunk", "tail", "dying"]
COLORS = ["#0d0f16", "#ff8c42", "#3ddc84", "#5b8cff", "#7a1530"]   # +dying = dark red
GROW_STEPS, FLIP_STEP, REMODEL_STEPS = 16, 16, 20
COMMIT_T, APOP_T = 0.80, 0.30        # commit above this confidence; die if setpoint(committed) below this


def neighbors_of(slot):
    y, x = divmod(slot, W); out = []
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
    oh = np.zeros((H, W, L))
    for c in range(L):
        oh[..., c] = (target == c + 1)
    return blur(oh).reshape(H * W, L)


def relax(idx, nbr, eff_prior, init, prior_strength=0.62, iters=10):
    n = len(idx); s = init.copy()
    base = (1 - prior_strength) / L + prior_strength * eff_prior
    for _ in range(iters):
        support = np.zeros((n, L))
        for i in range(n):
            if nbr[i]:
                support[i] = s[nbr[i]].mean(axis=0)
        q = base * (1e-3 + support)
        s = q / q.sum(axis=1, keepdims=True)
    return s


def simulate(target, in_target, seed):
    """Grow with commitment+gated division, flip the setpoint at FLIP_STEP, remodel via apoptosis."""
    mem = setpoint_field(target)
    bipolar = target.copy(); bipolar[bipolar == 3] = 1
    mem_bp = setpoint_field(bipolar)

    occupied = {seed}
    strength = {seed: mem[seed].copy()}
    committed = {}                                    # slot -> committed body-label (0,1,2)
    frames, deaths_log = [], []
    field = mem

    for step in range(GROW_STEPS + REMODEL_STEPS):
        if step == FLIP_STEP:
            field = mem_bp                            # reprogram the setpoint of the INTACT body

        idx = sorted(occupied)
        pos = {sl: i for i, sl in enumerate(idx)}
        nbr = [[pos[nb] for nb in neighbors_of(sl) if nb in occupied] for sl in idx]
        # effective prior: committed cells hold their identity; uncommitted read the field
        eff = np.zeros((len(idx), L))
        for i, sl in enumerate(idx):
            if sl in committed:
                eff[i] = 0.04; eff[i, committed[sl]] = 0.92
            else:
                eff[i] = field[sl]
        init = np.array([strength.get(sl, field[sl]) for sl in idx])
        s = relax(idx, nbr, eff, init)
        for i, sl in enumerate(idx):
            strength[sl] = s[i]

        # commitment: confident uncommitted cells lock in
        for i, sl in enumerate(idx):
            if sl not in committed and s[i].max() >= COMMIT_T:
                committed[sl] = int(s[i].argmax())

        # apoptosis (noise label): committed cells whose CURRENT setpoint gives their
        # committed identity < APOP_T are incompatible with the field. They die most-
        # posterior-first, capped per step, so resorption sweeps as a wave from the tip.
        conflicted = [sl for sl in idx if sl in committed and field[sl][committed[sl]] < APOP_T]
        conflicted.sort(key=lambda sl: -(sl // W))      # posterior (large y) first
        dying = set(conflicted[: max(6, len(conflicted) // 4)])
        deaths_log.append(len(dying))

        # record frame BEFORE removal, marking dying cells distinctly
        frame = np.zeros(H * W, dtype=int)
        for i, sl in enumerate(idx):
            frame[sl] = 4 if sl in dying else int(s[i].argmax()) + 1
        frames.append(frame.tolist())

        for sl in dying:                              # remove dead cells
            occupied.discard(sl); strength.pop(sl, None); committed.pop(sl, None)

        # field-gated division: a confident cell divides into an empty in-target neighbour
        # only where the setpoint there still wants tissue (under-filled front).
        recruits = set()
        for sl in occupied:
            conf = strength[sl].max()
            if conf < 0.45:
                continue
            for nb in neighbors_of(sl):
                if nb not in occupied and in_target[nb] and field[nb].max() > 0.20:
                    recruits.add(nb)
        for sl in recruits:
            occupied.add(sl); strength[sl] = field[sl].copy()

    return frames, deaths_log


def heads_at(frame):
    arr = np.array(frame).reshape(H, W)
    ys = np.where(arr == 1)[0]
    if not len(ys): return (False, False)
    return (ys.min() < H * 0.34, ys.max() > H * 0.66)


def tails(frame):
    return int((np.array(frame) == 3).sum())


def main():
    target = body_plan(H, W)
    in_target = (target.reshape(-1) > 0)
    seed = (H // 2) * W + (W // 2)
    frames, deaths = simulate(target, in_target, seed)

    pre = frames[FLIP_STEP - 1]; post = frames[-1]
    print("VERIFICATION — remodelling without injury (decision-driven division + apoptosis)")
    print(f"  before flip: heads(ant,post)={heads_at(pre)}  tail-cells={tails(pre)}  ({'one head' if heads_at(pre)==(True,False) else '??'})")
    print(f"  after  flip: heads(ant,post)={heads_at(post)} tail-cells={tails(post)}  ({'TWO HEADS' if heads_at(post)==(True,True) else '??'})")
    print(f"  total apoptotic-cell events: {sum(deaths)} (peak {max(deaths)}/step) — no amputation")

    data = {"h": H, "w": W, "labels": LABELS, "colors": COLORS,
            "flip": FLIP_STEP, "frames": frames, "deaths": deaths}
    (HERE / "morphogenesis_remodel_data.json").write_text(json.dumps(data), encoding="utf-8")
    out = HERE / "morphogenesis-remodel" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)), encoding="utf-8")
    print(f"wrote {out} ({len(frames)} frames, setpoint flip at {FLIP_STEP})")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Remodelling Without Injury — decision-driven morphogenesis</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--line:#2b2740;--cyan:#37e6ff;--red:#ff476f}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);font:16px/1.5 ui-serif,Georgia,serif;text-align:center}
.wrap{max-width:760px;margin:0 auto;padding:36px 18px 70px}
h1{font-size:clamp(22px,4vw,38px);margin:0 0 6px}
h1 small{display:block;color:var(--cyan);font-size:.42em;letter-spacing:3px;text-transform:uppercase;margin-top:12px}
.lede{color:var(--dim);max-width:680px;margin:12px auto 18px;font-size:15px}
canvas{background:#0d0f16;border:1px solid var(--line);border-radius:12px;image-rendering:pixelated;width:360px;height:360px}
.ctl{display:flex;gap:14px;align-items:center;justify-content:center;margin:18px 0}
button{background:#1d1933;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 18px;font:15px ui-serif,Georgia,serif;cursor:pointer}
button:hover{background:#2a2444} input[type=range]{width:280px;accent-color:var(--gold)} .it{font:13px ui-monospace,monospace;color:var(--dim);min-width:170px}
.legend{color:var(--dim);font-size:13px;margin-top:8px}.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:middle;margin:0 4px}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:13px}
.flag{color:var(--red);font-weight:600}
</style></head><body><div class="wrap">
<h1>Remodelling Without Injury<small>decision-driven division · death by the noise label</small></h1>
<p class="lede">A one-headed body grows by relaxation, cells <b>committing</b> to an identity and <b>dividing</b> only at the front where the
bioelectric <b>setpoint</b> wants tissue. Then — with <b>no amputation</b> — we <b>flip the posterior setpoint to head</b> on the intact
animal. The committed tail cells now conflict with the field, <b class="flag">apoptose</b> (dark red), and are replaced by head cells.
It becomes <b>two-headed</b>. Homeostatic error-correction, driven by the field.</p>
<canvas id="c" width="30" height="30"></canvas>
<div class="ctl"><button id="play">⏸ Pause</button><button id="replay">⟲ Replay</button>
  <input id="scrub" type="range" min="0" max="100" value="0"><span class="it" id="it">t 0</span></div>
<div class="legend"><span><i style="background:#ff8c42"></i>head</span><span><i style="background:#3ddc84"></i>trunk</span><span><i style="background:#5b8cff"></i>tail</span><span><i style="background:#7a1530"></i>apoptosing</span><span><i style="background:#0d0f16;border:1px solid #2b2740"></i>empty</span></div>
<p style="margin-top:18px"><a href="../bible-hrl/">← to the HRL gallery</a> · the engine reads the Bible, grows a body, and now remodels one — no scalpel.</p>
</div>
<script>
const D=/*DATA*/, COL=D.colors, T=D.frames.length;
const ctx=document.getElementById('c').getContext('2d');
function draw(flat){ const img=ctx.createImageData(D.w,D.h);
  for(let i=0;i<flat.length;i++){ const c=COL[flat[i]]||'#0d0f16';
    img.data[i*4]=parseInt(c.slice(1,3),16);img.data[i*4+1]=parseInt(c.slice(3,5),16);img.data[i*4+2]=parseInt(c.slice(5,7),16);img.data[i*4+3]=255;}
  ctx.putImageData(img,0,0);}
function render(t){ const i=Math.min(Math.round(t),T-1); draw(D.frames[i]);
  const phase=i<D.flip?'growing (one head)':(i===D.flip?'⚡ setpoint flipped':'remodelling → two heads');
  document.getElementById('it').textContent='t '+i+' · '+phase; document.getElementById('scrub').value=Math.round(i/(T-1)*100);}
let t=0,playing=true,last=null;
function tick(ts){ if(last==null)last=ts; const dt=(ts-last)/1000; last=ts;
  if(playing){ t+=dt*5; if(t>T-1){t=T-1;playing=false;document.getElementById('play').textContent='▶ Play';} render(t);} requestAnimationFrame(tick);}
render(0); requestAnimationFrame(tick);
document.getElementById('play').onclick=function(){if(t>=T-1)t=0;playing=!playing;this.textContent=playing?'⏸ Pause':'▶ Play';last=null;};
document.getElementById('replay').onclick=function(){t=0;playing=true;last=null;document.getElementById('play').textContent='⏸ Pause';};
document.getElementById('scrub').oninput=function(){playing=false;document.getElementById('play').textContent='▶ Play';t=this.value/100*(T-1);render(t);};
</script></body></html>"""


if __name__ == "__main__":
    main()
