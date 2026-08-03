/*
 * WorldKit — turn a Chess Maestro `chess-world` v1 export into playable worlds.
 *
 * One source of truth in, two platforms out:
 *     buildWorld()  →  chess-world v1 JSON  →  Minecraft datapack + Roblox builder
 *
 * The terrain is Maestro's own relaxation-labeling output: elevation is how hard a
 * square is held, water is the contested seam (sized pond→ocean by its area), and
 * every piece is tinted by its relaxed role. Nothing here re-derives chess — it
 * only renders what the labeling already decided.
 *
 * Runs unchanged in the browser (for the export buttons) and in Node (for the CLI).
 * No dependencies, including no zip library — the store-only zip writer is below,
 * so a one-click download is a datapack Minecraft will actually load.
 *
 * By Manny Glover.
 */
(function (root) {
  "use strict";

  const WorldKit = { FORMAT: "chess-world", VERSION: 1 };

  /* ===================== shared vocabulary =====================
     These mirror maestro.html's ROLE_COLOR / LANDRAMP / WATERCOL so the
     Minecraft and Roblox worlds read as the same world as the web board. */

  const ROLES = ["attacker", "defender", "controller", "outpost", "runner", "tactic", "noise"];

  const ROLE = {
    attacker:   { rgb: [224,  72,  58], mc: "red_concrete",        emoji: "⚔️", label: "Attacker" },
    defender:   { rgb: [ 63, 127, 208], mc: "blue_concrete",       emoji: "🛡️", label: "Defender" },
    controller: { rgb: [122,  85, 192], mc: "purple_concrete",     emoji: "📏", label: "Line-controller" },
    outpost:    { rgb: [ 46, 158, 107], mc: "emerald_block",       emoji: "⛳", label: "Outpost" },
    runner:     { rgb: [217, 154,   0], mc: "yellow_concrete",     emoji: "🏁", label: "Runner" },
    tactic:     { rgb: [210,  59, 176], mc: "magenta_concrete",    emoji: "🎯", label: "Tactician" },
    noise:      { rgb: [154, 160, 166], mc: "light_gray_concrete", emoji: "💤", label: "Idle" }
  };
  const roleOf = r => ROLE[r] || ROLE.noise;

  // Elevation 1..8, matching LANDRAMP: green → khaki → brown → rock → snow.
  const LAND = [
    { name: "grass",  rgb: [126, 197, 107], mc: "grass_block" },
    { name: "meadow", rgb: [170, 203,  93], mc: "moss_block" },
    { name: "tan",    rgb: [207, 197, 111], mc: "sand" },
    { name: "hills",  rgb: [193, 159,  99], mc: "dirt" },
    { name: "brown",  rgb: [163, 131,  87], mc: "granite" },
    { name: "rock",   rgb: [143, 127, 113], mc: "stone" },
    { name: "alpine", rgb: [172, 162, 152], mc: "diorite" },
    { name: "snow",   rgb: [228, 231, 235], mc: "snow_block" }
  ];
  const landOf = e => LAND[Math.min(Math.max((e | 0) - 1, 0), LAND.length - 1)];

  // Contested water, sized by the connected area of the seam.
  const WATER = {
    pond:  { depth: 1, rgb: [122, 201, 236], floor: "sand" },
    creek: { depth: 1, rgb: [ 96, 182, 228], floor: "sand" },
    river: { depth: 1, rgb: [ 72, 160, 220], floor: "sand" },
    lake:  { depth: 2, rgb: [ 54, 138, 204], floor: "clay" },
    sea:   { depth: 3, rgb: [ 40, 108, 176], floor: "gravel" },
    ocean: { depth: 4, rgb: [ 24,  78, 148], floor: "gravel" }
  };
  const waterOf = w => WATER[w] || WATER.pond;

  const PIECE_H = { p: 2, n: 3, b: 3, r: 3, q: 4, k: 4 };
  const pieceH = t => PIECE_H[t] || 2;
  const TYPE_NAME = { p: "Pawn", n: "Knight", b: "Bishop", r: "Rook", q: "Queen", k: "King" };

  /* ===================== world reading ===================== */

  function requireWorld(world) {
    if (!world || world.format !== WorldKit.FORMAT) {
      throw new Error("WorldKit: expected a " + WorldKit.FORMAT + " export, got " + (world && world.format));
    }
    if (!world.frames || !world.frames.length) throw new Error("WorldKit: world has no frames");
    return world;
  }

  // Resolve opts.ply ("final" | number) against the frame list.
  function pickPly(world, ply) {
    const last = world.frames.length - 1;
    if (ply === undefined || ply === null || ply === "final") return last;
    const n = Math.round(+ply);
    return Number.isFinite(n) ? Math.min(Math.max(n, 0), last) : last;
  }

  const FILES = "abcdefgh";
  const sqToFR = s => [FILES.indexOf(s[0]), parseInt(s.slice(1), 10) - 1]; // -> [file 0..7, rank 0..7]

  // A flat, render-ready description of one ply: 64 cells + the pieces standing on them.
  function readFrame(world, ply) {
    const fr = world.frames[ply];
    const byId = {};
    (world.pieces || []).forEach(p => { byId[p.id] = p; });

    const cells = [];
    for (let r = 0; r < 8; r++) {
      for (let f = 0; f < 8; f++) {
        const h = fr.height[r][f], wname = (fr.water && fr.water[r][f]) || "";
        const hydro = fr.hydro || {}, earth = hydro.earth && hydro.earth[r] ? +hydro.earth[r][f] : Math.max(0, h);
        const waterLevel = hydro.water && hydro.water[r] ? +hydro.water[r][f] : Math.max(0, -h);
        const ice = hydro.ice && hydro.ice[r] ? +hydro.ice[r][f] : 0;
        const sky = hydro.sky && hydro.sky[r] ? +hydro.sky[r][f] : 0.5;
        if (h < 0 || wname) {
          const w = waterOf(wname);
          cells.push({ file: f, rank: r, kind: "water", water: wname || "pond",
                       depth: h < 0 ? -h : w.depth, earth, waterLevel, ice, sky,
                       rgb: w.rgb, mc: "water", floor: w.floor, top: 0 });
        } else {
          const e = Math.max(1, h), L = landOf(e);
          cells.push({ file: f, rank: r, kind: "land", elev: e, terrain: L.name,
                       earth, waterLevel, ice, sky, rgb: L.rgb, mc: L.mc, top: e });
        }
      }
    }

    const pieces = [];
    for (const square in fr.placement) {
      const id = fr.placement[square];
      if (!id) continue;
      const meta = byId[id] || { id, color: id[0], type: (id[1] || "p").toLowerCase(), team: "", name: id, emoji: "" };
      const [f, r] = sqToFR(square);
      if (f < 0 || r < 0 || r > 7) continue;
      const rr = (fr.roles && fr.roles[id]) || { role: "noise", strength: 0 };
      pieces.push({
        id, square, file: f, rank: r,
        color: meta.color, type: meta.type, team: meta.team,
        name: meta.name || TYPE_NAME[meta.type] || id, emoji: meta.emoji || "",
        role: ROLES.indexOf(rr.role) >= 0 ? rr.role : "noise",
        strength: +rr.strength || 0,
        height: pieceH(meta.type)
      });
    }

    return { ply, cells, pieces, move: fr.move || null, hydro: fr.hydro || null,
             coherence: fr.coherence, advantage: fr.advantage, beat: fr.beat };
  }
  WorldKit.readFrame = readFrame;

  function label(world, ply) {
    const m = world.meta || {};
    const fr = world.frames[ply];
    const san = fr && fr.move && fr.move.san ? fr.move.san : (ply === 0 ? "start position" : "ply " + ply);
    return {
      game: (m.white || "White") + " " + (m.result || "") + " " + (m.black || "Black"),
      title: m.label || "Chess Maestro",
      san, ply, plies: world.frames.length - 1
    };
  }

  /* ===================== Minecraft ===================== */

  const BASE = -55;      // first land layer; leaves headroom below for ocean depth
  const PLINTH_TOP = BASE - 1;
  const PLINTH_BOT = -59; // superflat surface
  const S = 3;            // blocks per square — wide enough to walk on

  const x0 = f => f * S, z0 = r => r * S;
  const cx = f => f * S + ((S - 1) >> 1), cz = r => r * S + ((S - 1) >> 1);
  const surfaceY = c => c.kind === "land" ? BASE + c.top - 1 : BASE - 1;

  function jsonText(s) { return JSON.stringify(String(s)); }

  function mcPlyFunction(world, ply, opts) {
    const fr = readFrame(world, ply);
    const L = label(world, ply);
    const out = [];
    const say = s => out.push(s);

    say("# " + L.title + " — ply " + ply + "/" + L.plies + "  (" + L.san + ")");
    say("# " + L.game);
    say("# Terrain is the relaxation-labeling field: height = control, water = the contested seam.");
    say("");

    // Wipe the build volume so stepping between plies never leaves debris behind.
    say("# clear the previous position");
    say("fill " + x0(0) + " " + BASE + " " + z0(0) + " " + (x0(7) + S - 1) + " " + (BASE + 14) + " " + (z0(7) + S - 1) + " minecraft:air");
    say("kill @e[type=minecraft:armor_stand,tag=maestro_label]");
    say("");

    say("# plinth, so the board sits on something solid in any world type");
    say("fill " + x0(0) + " " + PLINTH_BOT + " " + z0(0) + " " + (x0(7) + S - 1) + " " + PLINTH_TOP + " " + (z0(7) + S - 1) + " minecraft:stone");
    say("");

    say("# --- terrain: " + fr.cells.filter(c => c.kind === "land").length + " land squares, "
        + fr.cells.filter(c => c.kind === "water").length + " contested (water) ---");
    for (const c of fr.cells) {
      const xa = x0(c.file), xb = xa + S - 1, za = z0(c.rank), zb = za + S - 1;
      if (c.kind === "land") {
        say("fill " + xa + " " + BASE + " " + za + " " + xb + " " + (BASE + c.top - 1) + " " + zb + " minecraft:" + c.mc);
      } else {
        const d = Math.max(1, Math.min(4, c.depth));
        say("fill " + xa + " " + (BASE - d - 1) + " " + za + " " + xb + " " + (BASE - d - 1) + " " + zb + " minecraft:" + c.floor);
        say("fill " + xa + " " + (BASE - d) + " " + za + " " + xb + " " + (BASE - 1) + " " + zb + " minecraft:water");
        if (c.ice > 0.55) say("fill " + xa + " " + BASE + " " + za + " " + xb + " " + BASE + " " + zb + " minecraft:ice");
      }
    }
    say("");

    say("# --- the pieces: one column per piece, tinted by its relaxed role ---");
    for (const p of fr.pieces) {
      const c = fr.cells[p.rank * 8 + p.file];
      const y = surfaceY(c) + 1, R = roleOf(p.role);
      const x = cx(p.file), z = cz(p.rank);
      say("fill " + x + " " + y + " " + z + " " + x + " " + (y + p.height - 1) + " " + z + " minecraft:" + R.mc);
      say("setblock " + x + " " + (y + p.height) + " " + z + " minecraft:"
          + (p.color === "w" ? "white_concrete" : "black_concrete"));
      // A floating nameplate: who this piece is, and what the labeling made of it.
      // No emoji here — Minecraft's font has no glyphs above the BMP and would draw
      // empty boxes. Roblox renders them fine, so the emoji live in that exporter.
      const text = p.name + " · " + R.label + " (" + p.square + ")";
      say("summon minecraft:armor_stand " + (x + 0.5) + " " + (y + p.height + 1.2) + " " + (z + 0.5)
          + " {Marker:1b,Invisible:1b,NoGravity:1b,Silent:1b,Invulnerable:1b,CustomNameVisible:1b,"
          + "Tags:[\"maestro_label\"],CustomName:'" + JSON.stringify({ text: text, color: p.color === "w" ? "white" : "gray" }) + "'}");
    }
    say("");

    const water = fr.cells.filter(c => c.kind === "water").length;
    say("tellraw @a [\"\",{\"text\":\"♟ " + L.title + " \",\"color\":\"gold\",\"bold\":true},"
        + "{\"text\":\"ply " + ply + "/" + L.plies + " — " + L.san.replace(/"/g, "") + "\",\"color\":\"white\"},"
        + "{\"text\":\"  ·  contested seam " + water + " sq\",\"color\":\"aqua\"}]");
    return out.join("\n") + "\n";
  }

  /**
   * Build a Minecraft Java datapack from a chess-world export.
   * @returns {{files: Object, stats: Object}} files maps zip-relative path -> text
   */
  WorldKit.toMinecraft = function (world, opts) {
    requireWorld(world);
    opts = opts || {};
    const ns = opts.namespace || "maestro";
    const last = world.frames.length - 1;
    const chosen = pickPly(world, opts.ply);
    const allPlies = opts.allPlies !== false;

    const fn = {};
    fn["build.mcfunction"] = mcPlyFunction(world, chosen, opts);
    if (allPlies) {
      for (let p = 0; p <= last; p++) fn["ply/" + p + ".mcfunction"] = mcPlyFunction(world, p, opts);
    }

    const spawnX = cx(4), spawnZ = z0(0) - 4;
    fn["home.mcfunction"] = [
      "# stand at the near edge, looking up the board",
      "tp @s " + (spawnX + 0.5) + " " + (BASE + 2) + " " + (spawnZ + 0.5) + " 0 20",
      "gamemode creative @s"
    ].join("\n") + "\n";

    fn["clear.mcfunction"] = [
      "# take the whole board back out again",
      "fill " + x0(0) + " " + (PLINTH_BOT - 5) + " " + z0(0) + " " + (x0(7) + S - 1) + " " + (BASE + 14) + " " + (z0(7) + S - 1) + " minecraft:air",
      "kill @e[type=minecraft:armor_stand,tag=maestro_label]",
      "tellraw @a {\"text\":\"Chess Maestro — board cleared.\",\"color\":\"gray\"}"
    ].join("\n") + "\n";

    const L = label(world, chosen);
    fn["help.mcfunction"] = [
      "tellraw @a [\"\",{\"text\":\"♟ " + L.title + "\",\"color\":\"gold\",\"bold\":true}]",
      "tellraw @a {\"text\":\"  /function " + ns + ":build      — the position this pack was exported at\",\"color\":\"white\"}",
      allPlies ? "tellraw @a {\"text\":\"  /function " + ns + ":ply/0 … ply/" + last + "  — step the whole game\",\"color\":\"white\"}" : "",
      "tellraw @a {\"text\":\"  /function " + ns + ":home       — teleport to the near edge\",\"color\":\"white\"}",
      "tellraw @a {\"text\":\"  /function " + ns + ":clear      — remove the board\",\"color\":\"gray\"}"
    ].filter(Boolean).join("\n") + "\n";

    const readme = [
      L.title + " — a Minecraft Java datapack",
      "=".repeat(L.title.length + 32),
      "",
      "Game:   " + L.game,
      "Export: ply " + chosen + "/" + last + "  (" + L.san + ")",
      world.meta && world.meta.key ? "Key:    " + world.meta.key + "  ·  " + world.meta.tempo + " bpm" : "",
      "",
      "The board is Chess Maestro's relaxation-labeling field, built as terrain:",
      "  · land elevation = how firmly a square is held (grass → snow, 1 → 8)",
      "  · water          = the contested seam, sized pond → ocean by its area",
      "  · piece colour   = the role the labeling relaxed it into",
      "                     (attacker red, defender blue, line-controller purple,",
      "                      outpost emerald, runner yellow, tactician magenta, idle grey)",
      "  · nameplates     = which character stands there, and its role",
      "",
      "INSTALL",
      "  1. Make a new world: game mode Creative, world type Superflat.",
      "  2. Drop this .zip (do not unzip it) into that world's datapacks folder:",
      "       .minecraft/saves/<world>/datapacks/",
      "  3. In game:  /reload",
      "",
      "PLAY",
      "  /function " + ns + ":build     the exported position",
      allPlies ? "  /function " + ns + ":ply/0     … through ply/" + last + " — step the whole game" : "",
      "  /function " + ns + ":home      teleport onto the board",
      "  /function " + ns + ":clear     take it back out",
      "  /function " + ns + ":help      this list, in chat",
      "",
      "The board occupies x 0.." + (x0(7) + S - 1) + ", z 0.." + (z0(7) + S - 1) + ", from y " + (BASE - 5) + " up.",
      "Each ply rebuilds in place, so you can step forward and back freely.",
      "",
      "VERSIONS",
      "  Built for Minecraft 1.21+ (pack_format 48). Function files are shipped in both",
      "  data/" + ns + "/function/ (1.21+) and data/" + ns + "/functions/ (1.20.x), so the pack",
      "  loads either way. On 1.20.x, Minecraft may warn the pack is 'newer' — it still works;",
      "  to silence it, edit pack.mcmeta and set pack_format to 26.",
      "",
      "Nothing in this pack spawns a hostile mob. The nameplates are marker armor stands.",
      "",
      "Generated by WorldKit from a chess-world v" + WorldKit.VERSION + " export. By Manny Glover."
    ].filter(x => x !== "").join("\n") + "\n";

    const files = {
      "pack.mcmeta": JSON.stringify({
        pack: {
          pack_format: 48,
          supported_formats: { min_inclusive: 18, max_inclusive: 61 },
          description: L.title + " — " + L.game + " · ply " + chosen + "/" + last
        }
      }, null, 2) + "\n",
      "README.txt": readme
    };
    // Ship both folder spellings so one pack covers 1.20.x and 1.21+.
    for (const name in fn) {
      files["data/" + ns + "/function/" + name] = fn[name];
      files["data/" + ns + "/functions/" + name] = fn[name];
    }

    let commands = 0;
    for (const k in fn) commands += fn[k].split("\n").filter(l => l && l[0] !== "#").length;

    return { files, stats: { ply: chosen, plies: last, namespace: ns, commands, functions: Object.keys(fn).length } };
  };

  /* ===================== Roblox ===================== */

  const rgb3 = a => "Color3.fromRGB(" + a[0] + "," + a[1] + "," + a[2] + ")";
  const luaStr = s => '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';

  /**
   * Build a Roblox Studio (Luau) builder script from a chess-world export.
   * @returns {{lua: string, stats: Object}}
   */
  WorldKit.toRoblox = function (world, opts) {
    requireWorld(world);
    opts = opts || {};
    const chosen = pickPly(world, opts.ply);
    const fr = readFrame(world, chosen);
    const L = label(world, chosen);

    // One part per terrain column keeps the object count low enough for Studio.
    const terr = fr.cells.map(c => {
      const h = c.kind === "land" ? c.top : -Math.max(1, Math.min(4, c.depth));
      return "{" + c.file + "," + c.rank + "," + h + "," + rgb3(c.rgb) + "," + luaStr(c.kind === "land" ? c.terrain : c.water)
        + "," + (+c.ice || 0).toFixed(3) + "," + (+c.sky || 0.5).toFixed(3) + "}";
    });

    const pcs = fr.pieces.map(p => {
      const c = fr.cells[p.rank * 8 + p.file];
      const base = c.kind === "land" ? c.top : 0;
      const R = roleOf(p.role);
      return "{" + p.file + "," + p.rank + "," + base + "," + p.height + "," + rgb3(R.rgb) + ","
        + rgb3(p.color === "w" ? [236, 240, 244] : [38, 42, 52]) + ","
        + luaStr((p.emoji ? p.emoji + " " : "") + p.name) + "," + luaStr(R.emoji + " " + R.label) + "}";
    });

    const lua = `--[[
  ${L.title} — the board as a Roblox world
  ${L.game}
  ply ${chosen}/${L.plies}  (${L.san})

  Terrain is Chess Maestro's relaxation-labeling field: elevation is how firmly a
  square is held, water is the contested seam, and each piece is tinted by the role
  the labeling relaxed it into. Every part is Anchored — nothing can fall on anyone.

  RUN: Roblox Studio ▸ New ▸ Baseplate ▸ View ▸ Command Bar → paste this → Enter
       (or drop it into a Script under ServerScriptService and press Play)

  Generated by WorldKit from a chess-world v${WorldKit.VERSION} export. By Manny Glover.
]]

local SQ, LV = 8, 4          -- studs per square, studs per elevation level
local NAME = "ChessMaestro"

local old = workspace:FindFirstChild(NAME)
if old then old:Destroy() end

local root = Instance.new("Model")
root.Name = NAME
root.Parent = workspace

local Lighting = game:GetService("Lighting")
Lighting.ClockTime = ${+(11+((fr.cells.reduce((s,c)=>s+(+c.sky||.5),0)/64)-.5)*6).toFixed(2)}
Lighting.Brightness = ${+(1.8+(fr.cells.reduce((s,c)=>s+(+c.sky||.5),0)/64)).toFixed(2)}

local function part(cf, size, color, material)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = true
	p.Size = size
	p.CFrame = cf
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = root
	return p
end

local function centre(file, rank)
	return Vector3.new(file * SQ + SQ / 2, 0, rank * SQ + SQ / 2)
end

local function nameplate(adornee, title, subtitle)
	local bb = Instance.new("BillboardGui")
	bb.Size = UDim2.fromScale(9, 2.6)
	bb.StudsOffsetWorldSpace = Vector3.new(0, 3.4, 0)
	bb.AlwaysOnTop = false
	bb.MaxDistance = 220
	bb.Adornee = adornee
	bb.Parent = adornee

	local top = Instance.new("TextLabel")
	top.Size = UDim2.fromScale(1, 0.6)
	top.BackgroundTransparency = 1
	top.Font = Enum.Font.GothamBold
	top.TextScaled = true
	top.TextColor3 = Color3.new(1, 1, 1)
	top.TextStrokeTransparency = 0.35
	top.Text = title
	top.Parent = bb

	local bot = Instance.new("TextLabel")
	bot.Position = UDim2.fromScale(0, 0.6)
	bot.Size = UDim2.fromScale(1, 0.4)
	bot.BackgroundTransparency = 1
	bot.Font = Enum.Font.Gotham
	bot.TextScaled = true
	bot.TextColor3 = Color3.fromRGB(210, 216, 226)
	bot.TextStrokeTransparency = 0.5
	bot.Text = subtitle
	bot.Parent = bb
end

-- terrain: {file, rank, levels, colour, name, ice, sky}
local TERR = {
	${terr.join(",\n\t")}
}

for _, t in ipairs(TERR) do
	local file, rank, lv, colour, kind, ice = t[1], t[2], t[3], t[4], t[5], t[6]
	local c = centre(file, rank)
	if lv > 0 then
		local h = lv * LV
		local p = part(CFrame.new(c.X, h / 2, c.Z), Vector3.new(SQ, h, SQ), colour)
		p.Name = string.format("%s_%d%d", kind, file, rank)
	else
		local d = -lv * LV
		-- a solid bed, then translucent water sitting flush with the shoreline
		part(CFrame.new(c.X, -d - LV / 2, c.Z), Vector3.new(SQ, LV, SQ), Color3.fromRGB(150, 140, 120))
		local w = part(CFrame.new(c.X, -d / 2, c.Z), Vector3.new(SQ, d, SQ), colour, Enum.Material.Glass)
		w.Transparency = 0.45
		w.CanCollide = false
		w.Name = string.format("%s_%d%d", kind, file, rank)
		if ice > 0.55 then
			local cap = part(CFrame.new(c.X, LV * 0.08, c.Z), Vector3.new(SQ, LV * 0.16, SQ), Color3.fromRGB(205, 235, 245), Enum.Material.Ice)
			cap.Transparency = 0.18
			cap.Name = string.format("ice_%d%d", file, rank)
		end
	end
end

-- pieces: {file, rank, baseLevels, heightLevels, roleColour, capColour, title, role}
local PCS = {
	${pcs.join(",\n\t")}
}

for _, p in ipairs(PCS) do
	local file, rank, base, hLv = p[1], p[2], p[3], p[4]
	local c = centre(file, rank)
	local y0 = base * LV
	local h = hLv * LV
	local body = part(CFrame.new(c.X, y0 + h / 2, c.Z), Vector3.new(SQ * 0.5, h, SQ * 0.5), p[5])
	body.Name = p[7]
	local cap = part(CFrame.new(c.X, y0 + h + LV * 0.3, c.Z), Vector3.new(SQ * 0.62, LV * 0.6, SQ * 0.62), p[6])
	cap.Name = "cap"
	nameplate(cap, p[7], p[8])
end

local spawn = Instance.new("SpawnLocation")
spawn.Anchored = true
spawn.Size = Vector3.new(SQ, 1, SQ)
spawn.CFrame = CFrame.new(4 * SQ, LV * 9 + 1, -SQ * 1.5)
spawn.Neutral = true
spawn.Duration = 0
spawn.Parent = root

print(string.format("${L.title.replace(/"/g, "")} built — ply ${chosen}/${L.plies} (${L.san.replace(/"/g, "")}) · %d parts", #root:GetDescendants()))
`;

    return { lua, stats: { ply: chosen, plies: L.plies, terrain: terr.length, pieces: pcs.length } };
  };

  /* ===================== store-only zip =====================
     Minecraft loads a zipped datapack directly, so the browser can hand the
     user one file instead of a folder tree. No compression: a datapack is a few
     hundred KB of text and correctness beats bytes here. */

  const CRC_TABLE = (function () {
    const t = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      t[n] = c;
    }
    return t;
  })();

  function crc32(bytes) {
    let c = 0 ^ (-1);
    for (let i = 0; i < bytes.length; i++) c = (c >>> 8) ^ CRC_TABLE[(c ^ bytes[i]) & 0xFF];
    return (c ^ (-1)) >>> 0;
  }

  const utf8 = (function () {
    if (typeof TextEncoder !== "undefined") {
      const enc = new TextEncoder();
      return s => enc.encode(s);
    }
    return s => new Uint8Array(Buffer.from(s, "utf8")); // Node without TextEncoder
  })();

  /**
   * Pack {path: text} into a store-only zip.
   * @returns {Uint8Array}
   */
  WorldKit.zip = function (files) {
    const names = Object.keys(files);
    const DOS_TIME = 0x6000, DOS_DATE = 0x5CE1; // fixed stamp → byte-identical rebuilds
    const parts = [], central = [];
    let offset = 0;

    const u16 = v => [v & 0xFF, (v >>> 8) & 0xFF];
    const u32 = v => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];

    for (const name of names) {
      const nameBytes = utf8(name);
      const data = utf8(files[name]);
      const crc = crc32(data);

      const local = [].concat(
        u32(0x04034b50), u16(20), u16(0x0800), u16(0),  // 0x0800 = names are UTF-8
        u16(DOS_TIME), u16(DOS_DATE),
        u32(crc), u32(data.length), u32(data.length),
        u16(nameBytes.length), u16(0)
      );
      parts.push(new Uint8Array(local), nameBytes, data);

      central.push([].concat(
        u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(0),
        u16(DOS_TIME), u16(DOS_DATE),
        u32(crc), u32(data.length), u32(data.length),
        u16(nameBytes.length), u16(0), u16(0),
        u16(0), u16(0), u32(0),
        u32(offset)
      ));
      central.push(nameBytes);

      offset += local.length + nameBytes.length + data.length;
    }

    const cdParts = [];
    let cdSize = 0;
    for (const c of central) {
      const b = c instanceof Uint8Array ? c : new Uint8Array(c);
      cdParts.push(b);
      cdSize += b.length;
    }

    const eocd = new Uint8Array([].concat(
      u32(0x06054b50), u16(0), u16(0),
      u16(names.length), u16(names.length),
      u32(cdSize), u32(offset), u16(0)
    ));

    const all = parts.concat(cdParts, [eocd]);
    let total = 0;
    for (const p of all) total += p.length;
    const zip = new Uint8Array(total);
    let at = 0;
    for (const p of all) { zip.set(p, at); at += p.length; }
    return zip;
  };

  /** Convenience: chess-world → a ready-to-drop datapack zip. */
  WorldKit.toMinecraftZip = function (world, opts) {
    const built = WorldKit.toMinecraft(world, opts);
    return { bytes: WorldKit.zip(built.files), stats: built.stats, files: built.files };
  };

  /** A filename stem like "king-me-ply39". */
  WorldKit.stem = function (world, opts) {
    const m = (world && world.meta) || {};
    const ply = pickPly(world, (opts || {}).ply);
    const base = String(m.label || m.white || "chess-maestro")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48) || "chess-maestro";
    return base + "-ply" + ply;
  };

  WorldKit.ROLES = ROLES;
  WorldKit.ROLE = ROLE;
  WorldKit.LAND = LAND;
  WorldKit.WATER = WATER;

  if (typeof module !== "undefined" && module.exports) module.exports = WorldKit;
  if (root) root.WorldKit = WorldKit;
})(typeof window !== "undefined" ? window : null);
