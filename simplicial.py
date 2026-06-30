#!/usr/bin/env python3
"""The virtual body as a SIMPLICIAL COMPLEX — the topological substrate for the hierarchy.

A labelled body (cells with anatomical identities) is lifted from a graph to a 2D simplicial
complex: cells = 0-simplices, gap junctions = 1-simplices, triangulated tissue patches =
2-simplices. We compute its homology (Euler characteristic chi = V-E+F; Betti b0 = connected
pieces via union-find; b1 = b0 - chi, since b2=0 for a planar 2-complex) and extract the
anatomical-boundary sub-complex (edges where two cells carry different labels = the seams).

Key demonstrations:
  * a healthy body is a disk: b0=1, b1=0
  * punch an interior hole (a wound): b1=1 — a loop appears. Topology detects the wound.

Emits simplicial/index.html (interactive) + prints the topology.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from hrl.morphogenesis import body_plan, LABELS, COLORS

H = W = 28


def slot(y, x): return y * W + x


class DSU:
    def __init__(self, items):
        self.p = {i: i for i in items}
    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]; a = self.p[a]
        return a
    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def build_complex(occupied, label):
    """occupied: set of slots; label: dict slot->anatomical label (1,2,3)."""
    edges, faces = set(), []
    for y in range(H - 1):
        for x in range(W - 1):
            tl, tr, bl, br = slot(y, x), slot(y, x + 1), slot(y + 1, x), slot(y + 1, x + 1)
            if all(s in occupied for s in (tl, tr, bl, br)):
                # two triangles sharing the tl-br diagonal
                for tri in ((tl, tr, br), (tl, bl, br)):
                    faces.append(tri)
                    a, b, c = tri
                    edges |= {frozenset((a, b)), frozenset((b, c)), frozenset((a, c))}
    verts = set()
    for e in edges:
        verts |= set(e)
    V, E, F = len(verts), len(edges), len(faces)
    chi = V - E + F
    dsu = DSU(verts)
    for e in edges:
        a, b = tuple(e); dsu.union(a, b)
    b0 = len({dsu.find(v) for v in verts}) if verts else 0
    b1 = b0 - chi                                  # b2 = 0 for a planar 2-complex
    seams = [e for e in edges if label.get(tuple(e)[0]) != label.get(tuple(e)[1])]
    return {"verts": verts, "edges": edges, "faces": faces, "seams": seams,
            "V": V, "E": E, "F": F, "chi": chi, "b0": b0, "b1": b1}


def body(holed=False):
    target = body_plan(H, W)
    occupied = {slot(y, x) for y in range(H) for x in range(W) if target[y, x] > 0}
    label = {slot(y, x): int(target[y, x]) for y in range(H) for x in range(W) if target[y, x] > 0}
    if holed:                                       # punch an interior wound (a topological hole)
        cy, cx = H // 2, W // 2
        for y in range(cy - 2, cy + 3):
            for x in range(cx - 2, cx + 3):
                if (y - cy) ** 2 + (x - cx) ** 2 <= 4:
                    occupied.discard(slot(y, x)); label.pop(slot(y, x), None)
    return occupied, label


def export(occupied, label, cx):
    def xy(s): return (s % W, s // W)
    return {
        "verts": [{"s": s, "x": xy(s)[0], "y": xy(s)[1], "l": label.get(s, 0)} for s in sorted(cx["verts"])],
        "edges": [[*sorted(e)] for e in cx["edges"]],
        "seams": [[*sorted(e)] for e in cx["seams"]],
        "faces": [[*f] for f in cx["faces"]],
        "stats": {k: cx[k] for k in ("V", "E", "F", "chi", "b0", "b1")},
    }


def main():
    occ_h, lab_h = body(holed=False); cx_h = build_complex(occ_h, lab_h)
    occ_w, lab_w = body(holed=True);  cx_w = build_complex(occ_w, lab_w)
    print("TOPOLOGY of the virtual body (simplicial complex)")
    print(f"  healthy : V={cx_h['V']} E={cx_h['E']} F={cx_h['F']}  chi={cx_h['chi']}  "
          f"b0={cx_h['b0']} b1={cx_h['b1']}  ({'disk ✓' if cx_h['b1']==0 else '??'})  seams={len(cx_h['seams'])}")
    print(f"  wounded : V={cx_w['V']} E={cx_w['E']} F={cx_w['F']}  chi={cx_w['chi']}  "
          f"b0={cx_w['b0']} b1={cx_w['b1']}  ({'HOLE detected ✓' if cx_w['b1']>=1 else '??'})")

    data = {"w": W, "h": H, "labels": LABELS, "colors": COLORS,
            "healthy": export(occ_h, lab_h, cx_h), "wounded": export(occ_w, lab_w, cx_w)}
    (HERE / "simplicial_data.json").write_text(json.dumps(data), encoding="utf-8")
    out = HERE / "simplicial" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)), encoding="utf-8")
    print(f"wrote {out}")


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Body as a Simplicial Complex — HRL × topology</title>
<style>
:root{--bg:#0e0c16;--ink:#ece7f5;--dim:#9b93b8;--gold:#e8c170;--line:#2b2740;--cyan:#37e6ff;--seam:#ffffff}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#231b3a,var(--bg));color:var(--ink);font:16px/1.5 ui-serif,Georgia,serif;text-align:center}
.wrap{max-width:1000px;margin:0 auto;padding:36px 18px 70px}
h1{font-size:clamp(22px,4vw,38px);margin:0 0 6px}
h1 small{display:block;color:var(--cyan);font-size:.42em;letter-spacing:3px;text-transform:uppercase;margin-top:12px}
.lede{color:var(--dim);max-width:760px;margin:12px auto 16px;font-size:15px}
.row{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;align-items:flex-start}
svg.cx{width:440px;height:440px;background:#0b0d15;border:1px solid var(--line);border-radius:12px}
.side{width:300px;text-align:left}
.toggles{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:10px 0}
button{background:#1d1933;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 14px;font:14px ui-serif,Georgia,serif;cursor:pointer}
button.on{border-color:var(--cyan);color:var(--cyan)} button:hover{background:#2a2444}
.stat{background:#0b1022;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px;font:14px ui-monospace,monospace}
.stat b{color:var(--gold)} .stat .big{font-size:22px;color:var(--cyan)}
.ladder{display:flex;gap:8px;align-items:flex-end;height:90px;margin-top:8px}
.ladder .bar{flex:1;background:linear-gradient(#37e6ff,#5b8cff);border-radius:4px 4px 0 0;position:relative}
.ladder .bar span{position:absolute;bottom:-20px;left:0;right:0;color:var(--dim);font:11px ui-monospace,monospace}
.ladder .bar b{position:absolute;top:-18px;left:0;right:0;color:var(--ink);font:11px ui-monospace,monospace}
.legend{color:var(--dim);font-size:13px;margin-top:6px}.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:middle;margin:0 4px}
a{color:var(--cyan);text-decoration:none} code{background:#1d1933;padding:1px 6px;border-radius:5px;color:var(--gold);font-size:13px}
</style></head><body><div class="wrap">
<h1>The Body as a Simplicial Complex<small>the topological substrate for hierarchical relaxation</small></h1>
<p class="lede">The virtual body, lifted from a graph to a 2-complex: cells are <b>0-simplices</b>, gap junctions <b>1-simplices</b>,
triangulated tissue patches <b>2-simplices</b>. Its <b>homology</b> is a signature of morphological integrity — a healthy body is a
disk (b₁=0); a wound is a <b>hole</b> (b₁=1). The white <b>seams</b> are the anatomical-boundary sub-complex.</p>
<div class="toggles">
  <button id="bHealthy" class="on">healthy body</button>
  <button id="bWounded">wounded body (a hole)</button>
  <span style="width:18px"></span>
  <button id="tFaces" class="on">2-simplices</button>
  <button id="tEdges" class="on">1-simplices</button>
  <button id="tVerts" class="on">0-simplices</button>
  <button id="tSeams" class="on">seams</button>
</div>
<div class="row">
  <svg id="cx" class="cx" viewBox="0 0 28 28"></svg>
  <div class="side">
    <div class="stat" id="stat"></div>
    <div class="stat"><b>simplices by dimension</b><div class="ladder" id="ladder"></div></div>
    <div class="legend"><span><i style="background:#ff8c42"></i>head</span><span><i style="background:#3ddc84"></i>trunk</span><span><i style="background:#5b8cff"></i>tail</span><span><i style="background:#fff"></i>seam</span></div>
  </div>
</div>
<p style="margin-top:18px"><a href="../bible-hrl/">← to the HRL gallery</a> · the substrate for Milestone 3 — relaxation across simplex dimensions.</p>
</div>
<script>
const D=/*DATA*/, COL=D.colors, ns="http://www.w3.org/2000/svg";
const svg=document.getElementById('cx');
let which="healthy", show={faces:true,edges:true,verts:true,seams:true};
const mk=(t,a)=>{const e=document.createElementNS(ns,t);for(const k in a)e.setAttribute(k,a[k]);return e;};
function render(){
  const G=D[which]; while(svg.firstChild) svg.removeChild(svg.firstChild);
  const pos={}; G.verts.forEach(v=>pos[v.s]=[v.x+0.5,v.y+0.5]); const lab={}; G.verts.forEach(v=>lab[v.s]=v.l);
  if(show.faces) G.faces.forEach(f=>{ const pts=f.map(s=>pos[s]); if(pts.some(p=>!p))return;
    const ls=f.map(s=>lab[s]); const m=ls.sort((a,b)=>ls.filter(x=>x===a).length-ls.filter(x=>x===b).length).pop();
    svg.appendChild(mk('polygon',{points:pts.map(p=>p.join(',')).join(' '),fill:COL[m]||'#222','fill-opacity':0.55,stroke:'none'}));});
  if(show.edges) G.edges.forEach(e=>{ const a=pos[e[0]],b=pos[e[1]]; if(!a||!b)return;
    svg.appendChild(mk('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:'#5566aa','stroke-width':0.06,'stroke-opacity':0.5}));});
  if(show.seams) G.seams.forEach(e=>{ const a=pos[e[0]],b=pos[e[1]]; if(!a||!b)return;
    svg.appendChild(mk('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:'#ffffff','stroke-width':0.16,'stroke-linecap':'round'}));});
  if(show.verts) G.verts.forEach(v=>svg.appendChild(mk('circle',{cx:v.x+0.5,cy:v.y+0.5,r:0.16,fill:COL[v.l]||'#fff'})));
  const s=G.stats;
  document.getElementById('stat').innerHTML=
    `<b>homology</b><br>V−E+F = χ = <span class="big">${s.chi}</span><br>
     b₀ (pieces) = <b>${s.b0}</b> · b₁ (holes) = <span class="big">${s.b1}</span><br>
     <span style="color:var(--dim)">${s.b1===0?'a disk — no holes ✓':'a hole — the wound is topologically real ✓'}</span>`;
  const mx=Math.max(s.V,s.E,s.F);
  document.getElementById('ladder').innerHTML=
    [['0·cells',s.V],['1·junctions',s.E],['2·patches',s.F]].map(([n,v])=>
      `<div class="bar" style="height:${100*v/mx}%"><b>${v}</b><span>${n}</span></div>`).join('');
}
function tog(id,key){const b=document.getElementById(id);b.onclick=()=>{show[key]=!show[key];b.classList.toggle('on',show[key]);render();};}
tog('tFaces','faces');tog('tEdges','edges');tog('tVerts','verts');tog('tSeams','seams');
document.getElementById('bHealthy').onclick=function(){which="healthy";this.classList.add('on');document.getElementById('bWounded').classList.remove('on');render();};
document.getElementById('bWounded').onclick=function(){which="wounded";this.classList.add('on');document.getElementById('bHealthy').classList.remove('on');render();};
render();
</script></body></html>"""


if __name__ == "__main__":
    main()
