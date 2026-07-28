#!/usr/bin/env node
/* Maestro CAST -> Minecraft Java: the emoji critters as wool standees on a chessboard.
   Reads core.js (positions + identity) and emoji_models.json (baked emoji pixels);
   maps each pixel to the nearest wool colour. Usage: node export_minecraft_emoji.js [ply]
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

const PAL=[["white_wool",233,236,236],["light_gray_wool",142,142,134],["gray_wool",62,68,71],["black_wool",20,21,25],
  ["red_wool",160,39,34],["orange_wool",240,118,19],["yellow_wool",248,197,39],["lime_wool",112,185,25],
  ["green_wool",84,109,27],["cyan_wool",21,137,145],["light_blue_wool",58,175,217],["blue_wool",44,46,143],
  ["purple_wool",122,42,173],["magenta_wool",189,68,179],["pink_wool",237,141,172],["brown_wool",114,71,40]];
function nearest(r,g,b){ let bp=PAL[0],bd=1e9; for(const p of PAL){ const d=(r-p[1])**2+(g-p[2])**2+(b-p[3])**2; if(d<bd){bd=d;bp=p;} } return bp[0]; }

const Y=-60, P=pos[ply], L=[];
L.push("# ═══════════════════════════════════════════════════════════════");
L.push("#  MAESTRO — THE CAST, in Minecraft  (generated from core.js + emoji_models.json)");
L.push(`#  King Me: mannyfresher 1-0 Lerouxdu74 · ply ${ply}/${pos.length-1} (${P.san||"start"})`);
L.push("#  Each critter = its narration emoji, pixel-for-pixel in nearest-colour wool.  By Manny Glover.");
L.push("#  RUN in a CREATIVE superflat world:  /reload  ·  /function maestrocast:build  ·  /tp @s "+(4*N)+" -54 "+(4*N));
L.push("# ═══════════════════════════════════════════════════════════════");
L.push("");
L.push("# --- board (nearest-wool of the influence terrain), one flat square per tile ---");
for(let idx=0;idx<64;idx++){ const c=P.influence[idx], f=idx&7, r=idx>>3;
  let col=c.water?[46,120,190]:c.terrain==="white"?[210,205,190]:c.terrain==="black"?[70,78,96]:[120,126,128];
  const k=(f+r)%2?1.0:0.72; const blk=nearest(col[0]*k|0,col[1]*k|0,col[2]*k|0);
  L.push(`fill ${f*N} ${Y} ${r*N} ${f*N+N-1} ${Y} ${r*N+N-1} minecraft:${blk}`); }
L.push("");
L.push("# --- the cast, each emoji as a standing wool billboard on its square ---");
for(const [sq,v] of idPlies[ply]){ const emoji=(v.color==="w"?WOOD:MISFIT)[v.id], m=emoji&&MODELS[emoji]; if(!m) continue;
  const cx=v.file*N+((N/2)|0), z=v.rank*N+((N/2)|0);
  for(const p of m){ const x=cx+(p[0]-((N-1)/2))|0, y=Y+1+(N-1-p[1]); L.push(`setblock ${x} ${y} ${z} minecraft:${nearest(p[2],p[3],p[4])}`); } }
L.push("");
L.push(`tellraw @a ["",{"text":"\\u265f Maestro — the Cast · ","color":"gold","bold":true},{"text":"King Me, played by the critters","color":"gray"}]`);

const base=path.join(__dirname,"minecraft-cast","maestrocast");
const fn=path.join(base,"data","maestrocast","function"); fs.mkdirSync(fn,{recursive:true});
fs.writeFileSync(path.join(fn,"build.mcfunction"),L.join("\n")+"\n");
fs.writeFileSync(path.join(base,"pack.mcmeta"),JSON.stringify({pack:{pack_format:48,description:"Maestro — the Cast (emoji wool standees). Generated from core.js. By Manny Glover."}},null,2)+"\n");
const cmds=L.filter(x=>/^(fill|setblock)/.test(x)).length;
console.log(`Minecraft cast written · ply ${ply} (${P.san||"start"}) · ${cmds} build commands`);
