#!/usr/bin/env node
/* Chess Maestro → Roblox Luau builder.  Single source of truth: core.js.
   Emits roblox/maestro_build.lua — paste into Studio's Command Bar (or a Script)
   and the influence-terrain board with role-colored piece totems appears.
   Usage:  node export_roblox.js [ply]   (default: final position / the mate)
   By Manny Glover. */
const fs = require("fs"), path = require("path");
const M = require("./core.js");

const PGN = "1. h3 d5 2. a3 e5 3. c3 Nc6 4. e3 Nf6 5. g4 Ne4 6. b4 Nxb4 7. axb4 Qh4 8. Rh2 Bxg4 9. hxg4 Qxh2 10. Qa4+ c6 11. Bb5 a6 12. Bxc6+ bxc6 13. Qxc6+ Kd8 14. Qxd5+ Kc8 15. Qxa8+ Kc7 16. Qxe4 Qxg1+ 17. Ke2 Qxc1 18. b5 axb5 19. Ra7+ Kb8 20. Qa8#";
const pos = M.applyPGN(PGN);
const ply = process.argv[2] !== undefined ? Math.max(0, Math.min(pos.length - 1, +process.argv[2])) : pos.length - 1;
const P = pos[ply];

const terrRGB = c => c.water ? [46,150,205]
  : c.terrain === "white" ? [228,228,220]
  : c.terrain === "black" ? [70,78,96] : [120,130,128];
const roleRGB = { attacker:[224,84,70], defender:[74,120,224], controller:[245,197,66],
  outpost:[92,200,112], runner:[96,224,224], noise:[132,142,152] };
const pieceH = t => t === "p" ? 1 : (t === "q" || t === "k") ? 3 : 2;
const rgb = a => `Color3.fromRGB(${a[0]},${a[1]},${a[2]})`;

const terr = [];
for (let idx = 0; idx < 64; idx++) {
  const c = P.influence[idx], file = idx & 7, rank = idx >> 3, h = c.water ? 1 : Math.max(1, c.height);
  terr.push(`{${file},${rank},${h},${rgb(terrRGB(c))}}`);
}
const pcs = [];
for (const r of P.roles) {
  const c = P.influence[r.rank * 8 + r.file], base = c.water ? 1 : Math.max(1, c.height), ph = pieceH(r.type);
  pcs.push(`{${r.file},${r.rank},${base},${ph},${rgb(roleRGB[r.role] || roleRGB.noise)},${rgb(r.color === "w" ? [232,238,244] : [38,42,52])}}`);
}

const lua = `-- ═══════════════════════════════════════════════════════════════
--  CHESS MAESTRO — the board as a Roblox world  (generated from core.js)
--  King Me: mannyfresher 1-0 Lerouxdu74 · ply ${ply}/${pos.length - 1} (${P.san || "start"})
--  HRL influence terrain + tactical-role piece totems.  By Manny Glover.
--
--  RUN: Roblox Studio ▸ New ▸ Baseplate ▸ View ▸ Command Bar → paste → Enter
--       (or drop into a Script in ServerScriptService and press Play)
-- ═══════════════════════════════════════════════════════════════
local SIZE, LV = 8, 4
local old = workspace:FindFirstChild("ChessMaestro"); if old then old:Destroy() end
local root = Instance.new("Model"); root.Name = "ChessMaestro"; root.Parent = workspace

local function blk(fx, y, fz, color)
	local p = Instance.new("Part")
	p.Anchored = true
	p.Size = Vector3.new(SIZE, LV, SIZE)
	p.Position = Vector3.new(fx * SIZE + SIZE/2, y * LV + LV/2, fz * SIZE + SIZE/2)
	p.Color = color
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.Parent = root
	return p
end

-- influence terrain: {file, rank, height, color}
local TERR = { ${terr.join(", ")} }
for _, t in ipairs(TERR) do
	for y = 0, t[3] - 1 do blk(t[1], y, t[2], t[4]) end
end

-- pieces: {file, rank, base, height, roleColor, capColor}
local PCS = { ${pcs.join(", ")} }
for _, p in ipairs(PCS) do
	for y = 0, p[4] - 1 do blk(p[1], p[3] + y, p[2], p[5]) end
	blk(p[1], p[3] + p[4], p[2], p[6])
end

local spawn = Instance.new("SpawnLocation")
spawn.Anchored = true
spawn.Size = Vector3.new(SIZE, 1, SIZE)
spawn.Position = Vector3.new(4 * SIZE, 60, -SIZE)
spawn.Neutral = true
spawn.Parent = root

print("Chess Maestro built — " .. #root:GetChildren() .. " objects · King Me (Qa8#)")
`;

const dir = path.join(__dirname, "roblox");
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, "maestro_build.lua"), lua);
console.log(`Roblox builder written · ply ${ply} (${P.san || "start"}) · ${terr.length} terrain cells · ${pcs.length} pieces`);
