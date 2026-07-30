(function(){
  const R={ok:[],fail:[]};
  const chk=(n,c,extra)=>{ (c?R.ok:R.fail).push(n+(extra?" — "+extra:"")); };
  try{
    // the real producer, at the real default game
    const w = buildWorld();
    chk("buildWorld format", w.format==="chess-world" && w.version===1, w.format+" v"+w.version);
    chk("has frames", w.frames && w.frames.length>1, (w.frames||[]).length+" frames");
    chk("has pieces", w.pieces && w.pieces.length===32, (w.pieces||[]).length+" pieces");
    chk("height is 8x8", w.frames[0].height.length===8 && w.frames[0].height[0].length===8);
    chk("WorldKit loaded", !!window.WorldKit);

    R.meta = w.meta;
    R.plies = w.frames.length-1;

    // WorldKit accepts it
    const fr = WorldKit.readFrame(w, w.frames.length-1);
    chk("readFrame gives 64 cells", fr.cells.length===64, fr.cells.length+"");
    chk("readFrame found pieces", fr.pieces.length>0, fr.pieces.length+" on board");
    R.land  = fr.cells.filter(c=>c.kind==="land").length;
    R.water = fr.cells.filter(c=>c.kind==="water").length;
    R.waterKinds = Array.from(new Set(fr.cells.filter(c=>c.kind==="water").map(c=>c.water)));
    R.elevs = Array.from(new Set(fr.cells.filter(c=>c.kind==="land").map(c=>c.elev))).sort();
    R.roles = {}; fr.pieces.forEach(p=>R.roles[p.role]=(R.roles[p.role]||0)+1);
    R.sample = fr.pieces.slice(0,4).map(p=>({sq:p.square,name:p.name,emoji:p.emoji,role:p.role,team:p.team,h:p.height}));

    // Minecraft
    const mc = WorldKit.toMinecraftZip(w, {ply:"final"});
    chk("zip has PK magic", mc.bytes[0]===0x50 && mc.bytes[1]===0x4B);
    chk("zip non-trivial", mc.bytes.length>10000, mc.bytes.length+" bytes");
    chk("one function per ply", mc.stats.functions >= R.plies, mc.stats.functions+" functions");
    R.mc = mc.stats; R.mcBytes = mc.bytes.length;
    const build = mc.files["data/maestro/function/build.mcfunction"];
    chk("build.mcfunction present", !!build);
    chk("build has fills", (build.match(/^fill /gm)||[]).length>64, (build.match(/^fill /gm)||[]).length+" fills");
    chk("build has nameplates", (build.match(/^summon /gm)||[]).length>0, (build.match(/^summon /gm)||[]).length+" summons");
    chk("no undefined leaked into commands", build.indexOf("undefined")<0);
    chk("no NaN leaked into commands", build.indexOf("NaN")<0);
    R.mcSampleSummon = (build.match(/^summon .*$/m)||[""])[0].slice(0,180);

    // Roblox
    const rb = WorldKit.toRoblox(w, {ply:"final"});
    chk("lua non-trivial", rb.lua.length>3000, rb.lua.length+" chars");
    chk("lua has no undefined", rb.lua.indexOf("undefined")<0);
    chk("lua has no NaN", rb.lua.indexOf("NaN")<0);
    chk("lua terrain rows = 64", rb.stats.terrain===64, rb.stats.terrain+"");
    R.rb = rb.stats;

    // a mid-game ply must differ from the final one
    const mid = WorldKit.toRoblox(w, {ply:Math.floor(R.plies/2)});
    chk("mid-game differs from final", mid.lua!==rb.lua);

    // stem naming
    R.stem = WorldKit.stem(w,{ply:"final"});
    chk("stem is filename-safe", /^[a-z0-9-]+$/.test(R.stem), R.stem);
  }catch(e){
    R.fail.push("THREW: "+e.message);
    R.stack=String(e.stack).split("\n").slice(0,4).join(" | ");
  }
  document.getElementById("TESTOUT").textContent = "@@"+JSON.stringify(R,null,1)+"@@";
})();
