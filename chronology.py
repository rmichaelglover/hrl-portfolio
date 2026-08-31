#!/usr/bin/env python3
"""Career-and-contribution timeline — resume roles vs. real commit activity.

Resume positions (the NewIDByConstraints / hierarchical-relaxation-labeling thread is
highlighted) on one track; the real monthly commit histogram of the `relaxation-labeling`
engine on another. The October-2023 body-position burst stands out. Self-contained page.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent

# (label, start_year, end_year, uses_the_algorithm, short note)
ROLES = [
    ("Siemens (forecasting)", 2009.40, 2009.70, False, "VBA, economic forecasting"),
    ("Motion Reality", 2010.00, 2014.00, True, "optical mocap ID+tracking — invented the noise label"),
    ("Cardlytics", 2014.00, 2016.00, True, "NLP transaction parsing — 'hierarchical' idea"),
    ("Beena Vision", 2014.75, 2015.00, True, "train-brake ID via NewIDByConstraints"),
    ("MiRus", 2016.00, 2018.00, False, "stereo cameras, AprilTag, CMake"),
    ("General Assembly", 2016.40, 2016.70, False, "data-science instructor"),
    ("Stanley B&D", 2018.00, 2019.00, False, "weld-defect CV, blob detector"),
    ("Google ML Intensive", 2019.40, 2019.70, False, "curriculum dev"),
    ("TechMah Medical", 2019.75, 2020.05, False, "Qt/C++ imaging"),
    ("FocusedCryo", 2022.35, 2023.10, True, "CT bead detection + registration ($20k license)"),
    ("Huxley Medical", 2023.00, 2026.50, True, "body-position from accelerometer"),
]

# real monthly commit counts of relaxation-labeling (git log --all)
COMMITS = {
    "2021-02": 1, "2021-04": 23, "2021-05": 9, "2021-09": 7, "2021-10": 29, "2021-11": 23,
    "2021-12": 1, "2022-06": 9, "2022-07": 5, "2022-08": 22, "2022-09": 14, "2022-10": 10,
    "2023-01": 8, "2023-02": 3, "2023-03": 2, "2023-04": 16, "2023-09": 1, "2023-10": 74,
    "2023-11": 3, "2024-01": 2, "2025-02": 2, "2026-06": 15,
}
BODYPOS = {"2023-09": 1, "2023-10": 64, "2023-11": 1, "2026-06": 1}


def ym_to_year(ym):
    y, m = ym.split("-")
    return int(y) + (int(m) - 0.5) / 12.0


def lanes(roles):
    out, lane_end = [], []
    for r in sorted(roles, key=lambda x: x[1]):
        placed = False
        for i, e in enumerate(lane_end):
            if r[1] >= e - 0.02:
                lane_end[i] = r[2]; out.append((i, r)); placed = True; break
        if not placed:
            lane_end.append(r[2]); out.append((len(lane_end) - 1, r))
    return out, len(lane_end)


def main():
    placed, nlanes = lanes(ROLES)
    data = {
        "roles": [{"lane": ln, "label": r[0], "s": r[1], "e": r[2], "algo": r[3], "note": r[4]} for ln, r in placed],
        "nlanes": nlanes,
        "commits": [{"x": round(ym_to_year(k), 3), "n": v, "bp": BODYPOS.get(k, 0), "ym": k} for k, v in sorted(COMMITS.items())],
        "xmin": 2009, "xmax": 2026.7,
    }
    html = TEMPLATE.replace("/*DATA*/", json.dumps(data))
    out = HERE / "chronology" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(ROLES)} roles, {len(COMMITS)} commit-months)")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Career & Contribution Timeline — one algorithm, thirteen years</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--cyan:#37e6ff;--line:#2b2740;--bar:#5b8cff;--hot:#ff5470}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,sans-serif;text-align:center}
.wrap{max-width:1040px;margin:0 auto;padding:34px 16px 70px}
h1{font:700 clamp(22px,4vw,36px)/1.1 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--cyan);letter-spacing:3px;text-transform:uppercase;font-size:12px;margin-bottom:14px}
.lede{color:var(--dim);max-width:760px;margin:0 auto 16px;font-size:14.5px}
svg{width:100%;max-width:1010px;background:#0a0c14;border:1px solid var(--line);border-radius:12px}
.legend{color:var(--dim);font-size:13px;margin-top:10px}.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:middle;margin:0 5px}
.note{color:var(--dim);font-size:12.5px;margin-top:14px;max-width:780px;margin-left:auto;margin-right:auto}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:12.5px}
</style></head><body><div class="wrap">
<h1>One Algorithm, Thirteen Years</h1><div class="sub">career roles · vs · real commit activity</div>
<p class="lede">A single distinctive method — <b>NewIDByConstraints</b>, i.e. hierarchical relaxation labeling — runs through a 13-year career.
Roles that applied it are <span style="color:var(--gold)">highlighted gold</span>. Below, the real monthly commit histogram of the
<code>relaxation-labeling</code> engine: note the <span style="color:var(--hot)">October-2023 spike</span> — the Huxley body-position work.</p>
<svg id="tl"></svg>
<div class="legend"><span><i style="background:var(--gold)"></i>uses NewIDByConstraints</span><span><i style="background:#444a63"></i>other role</span>
  &nbsp;·&nbsp; commits: <span><i style="background:var(--bar)"></i>engine</span><span><i style="background:var(--hot)"></i>body-position</span></div>
<p class="note">Commit data exists only from 2021 (when the public engine repo began); earlier roles are from the CV. Bars are monthly commit
counts (<code>git log --all</code>). Timestamps are author/committer dates. A neutral professional record — one method, many applications.</p>
<p style="margin-top:14px"><a href="bible-hrl/">← HRL gallery</a></p>
</div>
<script>
const D=/*DATA*/, ns="http://www.w3.org/2000/svg";
const W=1010,H=540,L=46,R=16,xmin=D.xmin,xmax=D.xmax;
const svg=document.getElementById('tl'); svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
const mk=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
const X=y=>L+(W-L-R)*(y-xmin)/(xmax-xmin);
// year gridlines
for(let y=2009;y<=2026;y++){ svg.appendChild(mk('line',{x1:X(y),y1:24,x2:X(y),y2:H-26,stroke:'#171a2b'}));
  if(y%2===1){const t=mk('text',{x:X(y),y:H-10,fill:'#7d89b0','font-size':10,'text-anchor':'middle','font-family':'ui-monospace'});t.textContent="'"+String(y).slice(2);svg.appendChild(t);} }
// roles band
const rTop=40, laneH=26, rH=20;
D.roles.forEach(r=>{ const x1=X(r.s),x2=X(r.e),y=rTop+r.lane*laneH;
  svg.appendChild(mk('rect',{x:x1,y:y,width:Math.max(3,x2-x1),height:rH,rx:5,
    fill:r.algo?'#e8c170':'#444a63','fill-opacity':r.algo?0.92:0.6,stroke:r.algo?'#f0d488':'#566','stroke-width':r.algo?1:0.5}));
  const lab=mk('text',{x:x1+4,y:y+14,fill:r.algo?'#1a1206':'#cfd6ee','font-size':10.5,'font-family':'ui-sans-serif','font-weight':r.algo?'700':'400'});
  lab.textContent=r.label; svg.appendChild(lab);
  const tt=mk('title',{}); tt.textContent=r.label+" — "+r.note; svg.appendChild(tt); });
// divider + commit band
const cTop=rTop+D.nlanes*laneH+24, cBot=H-30, cH=cBot-cTop;
svg.appendChild(mk('line',{x1:L,y1:cBot,x2:W-R,y2:cBot,stroke:'#2b2740'}));
const lab2=mk('text',{x:L,y:cTop-6,fill:'#9b93b8','font-size':11,'font-family':'ui-monospace'});lab2.textContent='relaxation-labeling commits / month';svg.appendChild(lab2);
const maxN=Math.max(...D.commits.map(c=>c.n));
const bw=(W-L-R)/((xmax-xmin)*12)*0.8;
D.commits.forEach(c=>{ const h=cH*c.n/maxN, x=X(c.x)-bw/2;
  svg.appendChild(mk('rect',{x:x,y:cBot-h,width:bw,height:h,fill:'#5b8cff'}));
  if(c.bp){ const hb=cH*c.bp/maxN; svg.appendChild(mk('rect',{x:x,y:cBot-hb,width:bw,height:hb,fill:'#ff5470'})); }
  const tt=mk('title',{}); tt.textContent=`${c.ym}: ${c.n} commits`+(c.bp?` (${c.bp} body-position)`:''); svg.appendChild(tt); });
// annotate the Oct-2023 spike
const spike=D.commits.find(c=>c.ym==='2023-10');
if(spike){ const x=X(spike.x);
  const t=mk('text',{x:x+6,y:cTop+22,fill:'#ff8095','font-size':11,'font-family':'ui-sans-serif'});
  t.textContent='Oct 2023 — 74 commits (64 body-position)'; svg.appendChild(t);
  svg.appendChild(mk('line',{x1:x,y1:cTop+26,x2:x,y2:cBot-cH*0.9,stroke:'#ff5470','stroke-dasharray':'3 3','stroke-opacity':0.6})); }
</script></body></html>"""


if __name__ == "__main__":
    main()
