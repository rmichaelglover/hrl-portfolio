#!/usr/bin/env node
/* Chess Maestro → Minecraft Java datapack.  Single source of truth: core.js.
   The HRL influence field becomes terrain (water on the contested seam, land
   rising by control), each piece a role-colored wool totem with a side cap.
   Usage:  node export_minecraft.js [ply]   (default: final position / the mate)
   By Manny Glover. */
const fs = require("fs"), path = require("path");
const M = require("./core.js");

const PGN = "1. h3 d5 2. a3 e5 3. c3 Nc6 4. e3 Nf6 5. g4 Ne4 6. b4 Nxb4 7. axb4 Qh4 8. Rh2 Bxg4 9. hxg4 Qxh2 10. Qa4+ c6 11. Bb5 a6 12. Bxc6+ bxc6 13. Qxc6+ Kd8 14. Qxd5+ Kc8 15. Qxa8+ Kc7 16. Qxe4 Qxg1+ 17. Ke2 Qxc1 18. b5 axb5 19. Ra7+ Kb8 20. Qa8#";
const pos = M.applyPGN(PGN);
const ply = process.argv[2] !== undefined ? Math.max(0, Math.min(pos.length - 1, +process.argv[2])) : pos.length - 1;
const P = pos[ply];

const Y0 = -60; // superflat ground
const terr = c => c.water ? "light_blue_concrete"
  : c.terrain === "white" ? "white_concrete"
  : c.terrain === "black" ? "gray_concrete" : "light_gray_concrete";
const wool = { attacker:"red_wool", defender:"blue_wool", controller:"yellow_wool",
  outpost:"lime_wool", runner:"light_blue_wool", noise:"gray_wool" };
const pieceH = t => t === "p" ? 1 : (t === "q" || t === "k") ? 3 : 2;

const L = [];
L.push("# ═══════════════════════════════════════════════════════════════");
L.push("#  CHESS MAESTRO — the board as a Minecraft world  (generated from core.js)");
L.push(`#  King Me: mannyfresher 1-0 Lerouxdu74 · ply ${ply}/${pos.length-1} (${P.san || "start"})`);
L.push("#  HRL influence terrain + tactical-role wool totems.  By Manny Glover.");
L.push("#  RUN in a CREATIVE superflat world:  /reload  ·  /function maestro:build  ·  /tp @s 4 -55 4");
L.push("# ═══════════════════════════════════════════════════════════════");
L.push("");
L.push("# --- influence terrain (water = contested seam, height = control strength) ---");
for (let idx = 0; idx < 64; idx++) {
  const c = P.influence[idx], file = idx & 7, rank = idx >> 3, h = c.water ? 1 : Math.max(1, c.height);
  L.push(`fill ${file} ${Y0} ${rank} ${file} ${Y0 + h - 1} ${rank} minecraft:${terr(c)}`);
}
L.push("");
L.push("# --- pieces, tinted by relaxed tactical role, capped by side ---");
for (const r of P.roles) {
  const c = P.influence[r.rank * 8 + r.file], base = Y0 + (c.water ? 1 : Math.max(1, c.height)), ph = pieceH(r.type);
  L.push(`fill ${r.file} ${base} ${r.rank} ${r.file} ${base + ph - 1} ${r.rank} minecraft:${wool[r.role] || "gray_wool"}`);
  L.push(`setblock ${r.file} ${base + ph} ${r.rank} minecraft:${r.color === "w" ? "white_wool" : "black_wool"}`);
}
L.push("");
L.push(`tellraw @a ["",{"text":"\\u265f Chess Maestro — ","color":"gold","bold":true},{"text":"the board as a world · King Me (Qa8#)","color":"gray"}]`);

const base = path.join(__dirname, "minecraft", "maestro");
const fnDir = path.join(base, "data", "maestro", "function");
fs.mkdirSync(fnDir, { recursive: true });
fs.writeFileSync(path.join(fnDir, "build.mcfunction"), L.join("\n") + "\n");
fs.writeFileSync(path.join(base, "pack.mcmeta"),
  JSON.stringify({ pack: { pack_format: 48, description: "Chess Maestro — the board as a world. Generated from core.js. By Manny Glover." } }, null, 2) + "\n");
console.log(`Minecraft datapack written · ply ${ply} (${P.san || "start"}) · ${L.length} commands · ${P.roles.length} pieces`);
