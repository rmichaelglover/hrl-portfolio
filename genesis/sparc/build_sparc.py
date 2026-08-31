#!/usr/bin/env python3
"""SPARC galaxy rotation curves -> the real fingerprint of dark matter.

REAL DATA: the SPARC database (Lelli, McGaugh & Schombert 2016, AJ 152, 157) — 175 nearby
galaxies with high-quality HI/Halpha rotation curves and Spitzer 3.6um photometry. For each
galaxy we have the *measured* rotation speed V_obs(R) and the speed the *visible* matter
(gas + stellar disk + bulge) can account for, V_bar(R). Where V_obs races ahead of V_bar, the
extra pull has no luminous source: that gap is the dark matter.

    V_bar^2 = Vgas|Vgas| + Y_disk*Vdisk^2 + Y_bul*Vbul^2      (Y_disk=0.5, Y_bul=0.7 at 3.6um)
    V_dm    = sqrt(max(V_obs^2 - V_bar^2, 0))

No fitting, no simulation — just the arithmetic of what light can and cannot explain.
"""
from __future__ import annotations
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAT = HERE / "rotmod"
Y_DISK, Y_BUL = 0.5, 0.7


def parse(path):
    dist, R, Vobs, eV, Vgas, Vdisk, Vbul = None, [], [], [], [], [], []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            if "Distance" in line:
                try: dist = float(line.split("=")[1].split("Mpc")[0])
                except Exception: pass
            continue
        p = line.split()
        if len(p) < 6:
            continue
        R.append(float(p[0])); Vobs.append(float(p[1])); eV.append(float(p[2]))
        Vgas.append(float(p[3])); Vdisk.append(float(p[4])); Vbul.append(float(p[5]))
    Vbar, Vdm = [], []
    for g, d, b in zip(Vgas, Vdisk, Vbul):
        vb2 = g * abs(g) + Y_DISK * d * d + Y_BUL * b * b
        vb = math.sqrt(vb2) if vb2 > 0 else 0.0
        Vbar.append(vb)
    return dict(dist=dist, R=R, Vobs=Vobs, eV=eV, Vbar=Vbar)


def dm_fraction(gal):
    """Fraction of the outer (last 3 points) centripetal pull with no luminous source."""
    n = len(gal["R"])
    idx = range(max(0, n - 3), n)
    vo2 = sum(gal["Vobs"][i] ** 2 for i in idx)
    vb2 = sum(gal["Vbar"][i] ** 2 for i in idx)
    return max(0.0, min(1.0, 1 - vb2 / vo2)) if vo2 > 0 else 0.0


def main():
    gals = {}
    for f in sorted(DAT.glob("*_rotmod.dat")):
        name = f.name.replace("_rotmod.dat", "")
        g = parse(f)
        if len(g["R"]) >= 6 and max(g["Vobs"]) > 10:
            g["name"] = name
            g["dmf"] = dm_fraction(g)
            g["vmax"] = max(g["Vobs"])
            g["npts"] = len(g["R"])
            gals[name] = g
    allg = list(gals.values())
    n = len(allg)
    mean_dmf = sum(g["dmf"] for g in allg) / n

    # curated set: well-measured, spanning dwarf -> giant.  Prefer iconic names when present.
    iconic = ["NGC3198", "NGC2403", "NGC6503", "DDO154", "NGC7814", "UGC02885",
              "NGC2841", "NGC5055", "NGC1560", "IC2574", "UGC128", "F571-8",
              "NGC0247", "DDO170", "NGC3521", "UGCA442"]
    well = [g for g in allg if g["npts"] >= 8]
    well.sort(key=lambda g: g["vmax"])
    pick, seen = [], set()
    for nm in iconic:
        if nm in gals and nm not in seen:
            pick.append(gals[nm]); seen.add(nm)
    # fill to 16 spanning the velocity range
    if len(pick) < 16 and well:
        step = max(1, len(well) // (16 - len(pick)))
        for i in range(0, len(well), step):
            g = well[i]
            if g["name"] not in seen:
                pick.append(g); seen.add(g["name"])
            if len(pick) >= 16:
                break
    pick.sort(key=lambda g: g["vmax"])

    def slim(g):
        r = 2
        return dict(name=g["name"], dist=round(g["dist"], 1) if g["dist"] else None,
                    dmf=round(g["dmf"], 3), vmax=round(g["vmax"], 1),
                    R=[round(x, 2) for x in g["R"]],
                    Vobs=[round(x, 1) for x in g["Vobs"]],
                    eV=[round(x, 1) for x in g["eV"]],
                    Vbar=[round(x, 1) for x in g["Vbar"]])

    # summary scatter: every galaxy's baryon-dominance vs dark-dominance (outer)
    scatter = [dict(name=g["name"], dmf=round(g["dmf"], 3), vmax=round(g["vmax"], 1)) for g in allg]

    data = dict(n=n, mean_dmf=round(mean_dmf, 3),
                galaxies=[slim(g) for g in pick], scatter=scatter)
    out = HERE / "data.json"
    out.write_text(json.dumps(data))
    (HERE / "index.html").write_text(TEMPLATE.replace("/*DATA*/", json.dumps(data)))
    print(f"parsed {n} real SPARC galaxies; mean outer dark-matter fraction = {mean_dmf:.1%}")
    print(f"curated {len(pick)} for the gallery; wrote {out} and index.html")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Fingerprint of Dark Matter — real galaxy rotation curves</title>
<style>
:root{--bg:#05060c;--ink:#e8f0ff;--dim:#8a97b8;--line:#18213c;
 --obs:#37e6ff;--bar:#e8c170;--dm:#c060ff}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1100px 700px at 50% -8%,#101830,var(--bg));color:var(--ink);
 font:15px/1.55 ui-sans-serif,system-ui;text-align:center}
.wrap{max-width:940px;margin:0 auto;padding:30px 16px 70px}
h1{font:700 clamp(21px,3.6vw,34px)/1.12 ui-serif,Georgia,serif;margin:0 0 4px}
.sub{color:var(--dm);letter-spacing:2.5px;text-transform:uppercase;font-size:12px;margin-bottom:12px}
.lede{color:var(--dim);max-width:740px;margin:0 auto 12px;font-size:14.5px}.lede b{color:var(--ink)}
.badge{display:inline-block;background:#0c1226;border:1px solid var(--line);border-radius:20px;
 padding:5px 14px;margin:6px auto 2px;font:12.5px ui-monospace,monospace;color:var(--dm)}
.badge b{color:var(--ink)}
.stage{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin:14px auto;max-width:900px}
#plot{background:#02030a;border:1px solid var(--line);border-radius:12px;flex:1 1 520px;max-width:600px}
.side{flex:1 1 240px;max-width:300px;text-align:left}
.gsel{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
.gsel button{background:#0c1226;color:var(--dim);border:1px solid var(--line);border-radius:6px;
 padding:4px 8px;font:11px ui-monospace,monospace;cursor:pointer}
.gsel button.on{background:#1a1236;color:#fff;border-color:var(--dm)}
.gcap{background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:13px;color:var(--dim)}
.gcap b{color:var(--ink)} .gcap .big{font:700 26px ui-serif,Georgia,serif;color:var(--dm)}
.leg{display:flex;gap:16px;justify-content:center;margin:8px auto;font:12px ui-monospace,monospace;color:var(--dim);flex-wrap:wrap}
.leg span{display:inline-flex;align-items:center;gap:6px} .swatch{width:14px;height:4px;border-radius:2px;display:inline-block}
.note{color:var(--dim);font-size:12.5px;max-width:800px;margin:20px auto 0;text-align:left;
 background:#0a1020;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.note b{color:var(--dm)} code{background:#141d3a;padding:1px 6px;border-radius:5px;color:var(--bar);font-size:12px}
a{color:var(--obs);text-decoration:none}
</style></head><body><div class="wrap">
<h1>The Fingerprint of Dark Matter</h1><div class="sub">175 real galaxies · SPARC rotation curves</div>
<p class="lede">This is <b>real measured data</b> — not a simulation. For each galaxy we plot how fast it actually spins
(<span style="color:var(--obs)">V<sub>obs</sub></span>, from Doppler shifts) against how fast the <span style="color:var(--bar)">visible
matter</span> — gas, stars, bulge — could <i>ever</i> make it spin. The stars should fall off at the edge like planets past
Neptune. They don't. The <span style="color:var(--dm)">gap</span> is pull with no light behind it: <b>dark matter</b>.</p>
<div class="badge">across all <b id="nn"></b> galaxies, the outer spin is on average <b id="mdf"></b> unexplained by visible matter</div>
<div class="stage">
  <canvas id="plot" width="600" height="440"></canvas>
  <div class="side">
    <div class="gsel" id="gsel"></div>
    <div class="gcap" id="gcap"></div>
  </div>
</div>
<div class="leg">
  <span><i class="swatch" style="background:var(--obs)"></i>V<sub>obs</sub> — measured spin</span>
  <span><i class="swatch" style="background:var(--bar)"></i>V<sub>bar</sub> — visible matter</span>
  <span><i class="swatch" style="background:var(--dm);height:10px"></i>dark-matter gap</span>
</div>
<div class="note">
<b>How the gap is computed (honest, standard).</b> V<sub>bar</sub> is the Newtonian speed from the measured gas + stellar mass:
<code>V_bar² = Vgas·|Vgas| + 0.5·Vdisk² + 0.7·Vbul²</code> (the 0.5/0.7 are standard 3.6µm mass-to-light ratios). The dark-matter
curve is simply <code>√(V_obs² − V_bar²)</code>. No fitting. <b>An honest alternative</b> exists — <i>MOND</i> reads the same gap as
modified gravity rather than unseen mass; SPARC is a battleground for both. Either way the <i>data</i> is real and the discrepancy
is undeniable.
<br><br>
<b>Where this meets our model.</b> In Manny's picture the gap is where matter/energy geodesics get too <i>cluttered</i> to carry a
clean luminous label — the <a href="../ontology/">noise / dark-matter pole</a> made of real starlight's shortfall. The same data forms
the <a href="../rar/">Radial Acceleration Relation</a> — the "clog threshold" — where the engine sorts these 165 galaxies into
free-flow / clogged regimes.
</div>
<p style="margin-top:14px"><a href="../rar/">The Clog Threshold →</a> · <a href="../ontology/">The Four Poles</a> · <a href="../">Project Genesis</a> · <span style="color:var(--dim)">data: SPARC, Lelli et&nbsp;al. 2016</span></p>
</div>
<script>
const D = /*DATA*/;
document.getElementById('nn').textContent=D.n;
document.getElementById('mdf').textContent=(D.mean_dmf*100).toFixed(0)+'%';
const cv=document.getElementById('plot'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
const PAD={l:56,r:16,t:18,b:42}; let sel=0;
function plot(g){
  ctx.clearRect(0,0,W,H);
  const rmax=Math.max(...g.R)*1.05, vmax=Math.max(Math.max(...g.Vobs),Math.max(...g.Vbar))*1.15;
  const X=r=>PAD.l+(r/rmax)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/vmax)*(H-PAD.t-PAD.b);
  // axes + grid
  ctx.strokeStyle='rgba(120,140,190,.18)'; ctx.fillStyle='#7f8bb0'; ctx.font='10px ui-monospace,monospace';
  ctx.lineWidth=1; ctx.textAlign='right';
  for(let v=0;v<=vmax;v+=50){ ctx.beginPath();ctx.moveTo(PAD.l,Y(v));ctx.lineTo(W-PAD.r,Y(v));ctx.stroke();
    ctx.fillText(v, PAD.l-6, Y(v)+3); }
  ctx.textAlign='center';
  for(let r=0;r<=rmax;r+=Math.ceil(rmax/6)){ ctx.fillText(r, X(r), H-PAD.b+16); }
  ctx.fillStyle='#9aa6c8'; ctx.fillText('radius (kpc)', W/2, H-6);
  ctx.save();ctx.translate(14,H/2);ctx.rotate(-Math.PI/2);ctx.fillText('rotation speed (km/s)',0,0);ctx.restore();
  // dark-matter gap fill (between Vbar and Vobs)
  ctx.beginPath(); ctx.moveTo(X(g.R[0]),Y(g.Vobs[0]));
  for(let i=0;i<g.R.length;i++) ctx.lineTo(X(g.R[i]),Y(g.Vobs[i]));
  for(let i=g.R.length-1;i>=0;i--) ctx.lineTo(X(g.R[i]),Y(g.Vbar[i]));
  ctx.closePath(); ctx.fillStyle='rgba(192,96,255,.16)'; ctx.fill();
  // Vbar curve
  ctx.strokeStyle='#e8c170'; ctx.lineWidth=2; ctx.beginPath();
  g.R.forEach((r,i)=>{const x=X(r),y=Y(g.Vbar[i]); i?ctx.lineTo(x,y):ctx.moveTo(x,y);}); ctx.stroke();
  // Vobs error bars + points
  ctx.strokeStyle='rgba(55,230,255,.5)'; ctx.lineWidth=1;
  g.R.forEach((r,i)=>{const x=X(r); ctx.beginPath();ctx.moveTo(x,Y(g.Vobs[i]-g.eV[i]));ctx.lineTo(x,Y(g.Vobs[i]+g.eV[i]));ctx.stroke();});
  ctx.fillStyle='#37e6ff';
  g.R.forEach((r,i)=>{ctx.beginPath();ctx.arc(X(r),Y(g.Vobs[i]),3,0,7);ctx.fill();});
  // title
  ctx.fillStyle='#e8f0ff'; ctx.font='600 15px ui-serif,Georgia,serif'; ctx.textAlign='left';
  ctx.fillText(g.name, PAD.l+4, PAD.t+6);
}
function showCap(g){
  document.getElementById('gcap').innerHTML=
    `<b>${g.name}</b>${g.dist?` · ${g.dist} Mpc away`:''}<br>peak spin ${g.vmax} km/s`+
    `<div style="margin-top:8px">at the outer edge, visible matter explains only <b>${(100*(1-g.dmf)).toFixed(0)}%</b> of the pull:</div>`+
    `<div class="big">${(g.dmf*100).toFixed(0)}% dark</div>`;
}
function select(i){ sel=i; plot(D.galaxies[i]); showCap(D.galaxies[i]);
  [...document.querySelectorAll('#gsel button')].forEach((b,j)=>b.classList.toggle('on',j===i)); }
const gs=document.getElementById('gsel');
D.galaxies.forEach((g,i)=>{const b=document.createElement('button');b.textContent=g.name;b.onclick=()=>select(i);gs.appendChild(b);});
// default to a galaxy with a clear, iconic gap
let def=D.galaxies.findIndex(g=>g.name==='NGC3198'); if(def<0)def=Math.floor(D.galaxies.length/2);
select(def);
</script></body></html>
"""


if __name__ == "__main__":
    main()
