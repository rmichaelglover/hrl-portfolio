#!/usr/bin/env node
/* Maestro CAST -> Roblox: the emoji critters as voxel-Part standees on a chessboard.
   Reads core.js (positions + identity) and emoji_models.json (baked emoji pixels).
   Exact Color3 per pixel. Usage: node export_roblox_emoji.js [ply]  (default: the mate)
   By Manny Glover. */
const fs=require("fs"), path=require("path");
const M=require("./core.js");
const data=JSON.parse(fs.readFileSync(path.join(__dirname,"emoji_models.json"),"utf8"));
const N=data.N, MODELS=data.models;

const WOOD={Ra:"🏰",Nb:"🦄",Bc:"🛕",Qd:"🐲",Ke:"🦁",Bf:"🧙",Ng:"🐎",Rh:"🧱",Pa:"🦊",Pb:"🦡",Pc:"🦝",Pd:"🦌",Pe:"🦉",Pf:"🐸",Pg:"🦎",Ph:"🦔"};
const MISFIT={Ra:"🏯",Nb:"🦏",Bc:"🔮",Qd:"👸",Ke:"🤴",Bf:"💎",Ng:"🐘",Rh:"🗼",Pa:"🤠",Pb:"🥳",Pc:"🧔",Pd:"🔺",Pe:"📢",Pf:"💃",Pg:"🏁",Ph:"🏨"};
const BACK={0:"Ra",1:"Nb",2:"Bc",3:"Qd",4:"Ke",5:"Bf",6:"Ng",7:"Rh"};
const homeId=(f,r)=>(r===1||r===6)?"P"+"abcdefgh"[f]:(r===0||r===7)?BACK[f]:null;

const PGN="1. h3 d5 2. a3 e5 3. c3 Nc6 4. e3 Nf6 5. g4 Ne4 6. b4 Nxb4 7. axb4 Qh4 8. Rh2 Bxg4 9. hxg4 Qxh2 10. Qa4+ c6 11. Bb5 a6 12. Bxc6+ bxc6 13. Qxc6+ Kd8 14. Qxd5+ Kc8 15. Qxa8+ Kc7 16. Qxe4 Qxg1+ 17. Ke2 Qxc1 18. b5 axb5 19. Ra7+ Kb8 20. Qa8#";
const pos=M.applyPGN(PGN);
const ply=process.argv[2]!==undefined?Math.max(0,Math.min(pos.length-1,+process.argv[2])):pos.length-1;

// identity tracking (diff; King Me has no castling/EP/promotion)
const idPlies=[]; let prev=null;
for(let k=0;k<pos.length;k++){ const cur=new Map();
  for(const pc of pos[k].roles) cur.set(pc.file+","+pc.rank,{type:pc.type,color:pc.color,file:pc.file,rank:pc.rank});
  if(k===0){ for(const [sq,v] of cur){ const [f,r]=sq.split(",").map(Number); v.id=homeId(f,r)||("X"+sq); } }
  else{ const vac=[],arr=[];
    for(const sq of prev.keys()) if(!cur.has(sq)) vac.push(sq);
    for(const [sq,v] of cur){ const pv=prev.get(sq); if(pv&&pv.type===v.type&&pv.color===v.color) v.id=pv.id; else arr.push(sq); }
    for(const to of arr){ const v=cur.get(to); let from=null;
      for(const f of vac){ const pf=prev.get(f); if(pf&&pf.color===v.color&&pf.type===v.type){from=f;break;} }
      if(from===null) for(const f of vac){ const pf=prev.get(f); if(pf&&pf.color===v.color){from=f;break;} }
      if(from!==null){ v.id=prev.get(from).id; vac.splice(vac.indexOf(from),1); } else if(!v.id) v.id="X"+to; } }
  idPlies.push(cur); prev=cur;
}

const PX=2, SQ=N*PX, P=pos[ply], tiles=[], pix=[];
for(let idx=0;idx<64;idx++){ const c=P.influence[idx], f=idx&7, r=idx>>3;
  let col=c.water?[46,120,190]:c.terrain==="white"?[210,205,190]:c.terrain==="black"?[70,78,96]:[120,126,128];
  const k=(f+r)%2?1.0:0.7; tiles.push([f,r,col[0]*k|0,col[1]*k|0,col[2]*k|0]); }
for(const [sq,v] of idPlies[ply]){ const emoji=(v.color==="w"?WOOD:MISFIT)[v.id], m=emoji&&MODELS[emoji]; if(!m) continue;
  const cx=v.file*SQ, cz=v.rank*SQ, y0=1.5+PX;
  for(const p of m) pix.push([ (cx+(p[0]-(N-1)/2)*PX)|0, (y0+(N-1-p[1])*PX)|0, cz|0, p[2],p[3],p[4] ]); }

const lua=`-- ═══════════════════════════════════════════════════════════════
--  MAESTRO — THE CAST, in Roblox  (generated from core.js + emoji_models.json)
--  King Me: mannyfresher 1-0 Lerouxdu74 · ply ${ply}/${pos.length-1} (${P.san||"start"})
--  Each critter = its narration emoji, pixel-for-pixel in coloured Parts.  By Manny Glover.
--  RUN: Studio ▸ New ▸ Baseplate ▸ View ▸ Command Bar → paste → Enter (or a Script + Play)
-- ═══════════════════════════════════════════════════════════════
local PX,SQ=${PX},${SQ}
local old=workspace:FindFirstChild("MaestroCast"); if old then old:Destroy() end
local root=Instance.new("Model"); root.Name="MaestroCast"; root.Parent=workspace
local function box(x,y,z,sx,sy,sz,col)
	local p=Instance.new("Part"); p.Anchored=true; p.Size=Vector3.new(sx,sy,sz); p.Position=Vector3.new(x,y,z)
	p.Color=col; p.Material=Enum.Material.SmoothPlastic; p.TopSurface=Enum.SurfaceType.Smooth; p.Parent=root; return p end
local TILES={ ${tiles.map(t=>`{${t[0]},${t[1]},${t[2]},${t[3]},${t[4]}}`).join(",")} }
for _,t in ipairs(TILES) do box(t[1]*SQ,0,t[2]*SQ, SQ,1,SQ, Color3.fromRGB(t[3],t[4],t[5])) end
local PIX={ ${pix.map(p=>`{${p[0]},${p[1]},${p[2]},${p[3]},${p[4]},${p[5]}}`).join(",")} }
for _,p in ipairs(PIX) do box(p[1],p[2],p[3], PX,PX,PX, Color3.fromRGB(p[4],p[5],p[6])) end
local s=Instance.new("SpawnLocation"); s.Anchored=true; s.Size=Vector3.new(SQ,1,SQ)
s.Position=Vector3.new(3.5*SQ,80,-SQ); s.Neutral=true; s.Parent=root
print("Maestro cast built — "..#root:GetChildren().." objects · King Me ply ${ply} ("..${JSON.stringify(P.san||"start")}..")")
`;
const dir=path.join(__dirname,"roblox"); fs.mkdirSync(dir,{recursive:true});
fs.writeFileSync(path.join(dir,"maestro_cast.lua"),lua);
console.log(`Roblox cast written · ply ${ply} (${P.san||"start"}) · ${tiles.length} tiles · ${pix.length} pixel-parts`);
