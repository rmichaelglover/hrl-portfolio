#!/usr/bin/env node
/*
 * Chess Maestro → chess-world v1 → Minecraft datapack + Roblox builder.
 *
 * The same WorldKit that powers maestro.html's export buttons, driven from the
 * command line so worlds can be generated in bulk (and checked into a repo).
 *
 *   node export_world.js                             # King Me, final position
 *   node export_world.js --ply 12                     # a single moment
 *   node export_world.js --pgn game.pgn --out ./dist
 *   node export_world.js --pgn game.pgn --label "Creepy Crawly" --white mannyfresher
 *
 * Writes:  <out>/<stem>.world.json          the spec — single source of truth
 *          <out>/<stem>.datapack.zip        drop into saves/<world>/datapacks/
 *          <out>/<stem>.roblox.lua          paste into Studio's Command Bar
 *
 * By Manny Glover.
 */
const fs = require("fs");
const path = require("path");
const Maestro = require("./core.js");
const WorldKit = require("../../whimsy-chess/worldkit.js");

const KING_ME = "1. h3 d5 2. a3 e5 3. c3 Nc6 4. e3 Nf6 5. g4 Ne4 6. b4 Nxb4 7. axb4 Qh4 8. Rh2 Bxg4 9. hxg4 Qxh2 10. Qa4+ c6 11. Bb5 a6 12. Bxc6+ bxc6 13. Qxc6+ Kd8 14. Qxd5+ Kc8 15. Qxa8+ Kc7 16. Qxe4 Qxg1+ 17. Ke2 Qxc1 18. b5 axb5 19. Ra7+ Kb8 20. Qa8#";

/* ---- args ---- */
const argv = process.argv.slice(2);
const arg = (name, dflt) => {
  const i = argv.indexOf("--" + name);
  return i >= 0 && argv[i + 1] !== undefined ? argv[i + 1] : dflt;
};
const has = name => argv.indexOf("--" + name) >= 0;

if (has("help")) {
  console.log(fs.readFileSync(__filename, "utf8").split("*/")[0].replace(/^\/\*\n?/, "").replace(/^ \* ?/gm, ""));
  process.exit(0);
}

/* ---- read the game ---- */
// Strip PGN headers, comments and annotations down to bare SAN.
function movesOf(text) {
  return text
    .replace(/\[[^\]]*\]/g, " ")          // [Event "..."] headers
    .replace(/\{[^}]*\}/g, " ")           // { commentary }
    .replace(/;[^\n]*/g, " ")             // ; rest-of-line comments
    .replace(/\$\d+/g, " ")               // $1 NAG annotations
    .replace(/\.\.\./g, " ")              // black-move ellipses
    .replace(/\s+/g, " ")
    .trim();
}

const pgnPath = arg("pgn", null);
let raw = KING_ME, meta = { label: "King Me", white: "mannyfresher", black: "Lerouxdu74", result: "1-0", hero: "w" };
if (pgnPath) {
  raw = fs.readFileSync(pgnPath, "utf8");
  const tag = (name, dflt) => {
    const m = raw.match(new RegExp('\\[' + name + '\\s+"([^"]*)"\\]'));
    return m ? m[1] : dflt;
  };
  meta = {
    label: arg("label", tag("Event", path.basename(pgnPath, path.extname(pgnPath)))),
    white: arg("white", tag("White", "White")),
    black: arg("black", tag("Black", "Black")),
    result: arg("result", tag("Result", "*")),
    hero: arg("hero", "w")
  };
} else {
  meta.label = arg("label", meta.label);
  meta.white = arg("white", meta.white);
  meta.black = arg("black", meta.black);
  meta.result = arg("result", meta.result);
  meta.hero = arg("hero", meta.hero);
}

const positions = Maestro.applyPGN(movesOf(raw));
if (positions.length < 2) {
  console.error("No moves parsed. Check the PGN.");
  process.exit(1);
}

const world = Maestro.toWorld(positions, meta);
const plyOpt = has("ply") ? +arg("ply") : "final";
const opts = { ply: plyOpt, allPlies: !has("single") };

/* ---- write ---- */
const outDir = path.resolve(arg("out", path.join(__dirname, "dist")));
fs.mkdirSync(outDir, { recursive: true });
const stem = WorldKit.stem(world, opts);

const worldPath = path.join(outDir, stem + ".world.json");
fs.writeFileSync(worldPath, JSON.stringify(world, null, 1) + "\n");

const mc = WorldKit.toMinecraftZip(world, opts);
const zipPath = path.join(outDir, stem + ".datapack.zip");
fs.writeFileSync(zipPath, Buffer.from(mc.bytes));

const rb = WorldKit.toRoblox(world, opts);
const luaPath = path.join(outDir, stem + ".roblox.lua");
fs.writeFileSync(luaPath, rb.lua);

/* ---- report ---- */
const kb = n => (n / 1024).toFixed(1) + " KB";
const rel = p => path.relative(process.cwd(), p);
console.log(meta.label + " — " + meta.white + " " + meta.result + " " + meta.black
  + "  ·  " + (positions.length - 1) + " plies, exported at ply " + mc.stats.ply);
console.log("  spec      " + rel(worldPath) + "  (" + kb(fs.statSync(worldPath).size) + ")");
console.log("  minecraft " + rel(zipPath) + "  (" + kb(mc.bytes.length) + ", "
  + mc.stats.functions + " functions, " + mc.stats.commands + " commands)");
console.log("  roblox    " + rel(luaPath) + "  (" + kb(rb.lua.length) + ", "
  + rb.stats.terrain + " terrain cells, " + rb.stats.pieces + " pieces)");
console.log("\nMinecraft:  copy the .zip into saves/<world>/datapacks/ then  /reload  ·  /function maestro:build  ·  /function maestro:home");
console.log("Roblox:     Studio ▸ Baseplate ▸ Command Bar ▸ paste the .lua");
