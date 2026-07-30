#!/usr/bin/env node
/* Regression tests for the Maestro board engine (core.js).
   Run:  node test_core.js        (exit 0 = all passing)
   By Manny Glover. */
const M = require("./core.js");

let fail = 0, pass = 0;
function chk(name, got, want) {
  const ok = String(got) === String(want);
  ok ? pass++ : fail++;
  console.log((ok ? "  ok   " : "  FAIL ") + name + ": " + got + (ok ? "" : "  (want " + want + ")"));
}
const sq = (b, f, r) => b[r][f] || ".";
const total = b => { let n = 0; for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) if (b[r][f]) n++; return n; };
const last = pgn => M.applyPGN(pgn).pop().board;

console.log("start position");
{
  const b = M.startBoard();
  chk("32 pieces", total(b), 32);
  chk("e1 white king", sq(b, 4, 0), "K");
  chk("d8 black queen", sq(b, 3, 7), "q");
}

console.log("en passant — white captures (3. exf6)");
{
  const b = last("1. e4 d5 2. e5 f5 3. exf6");
  chk("pawn lands on f6", sq(b, 5, 5), "P");
  chk("victim on f5 removed", sq(b, 5, 4), ".");
  chk("31 pieces remain", total(b), 31);
}

console.log("en passant — black captures (3... hxg3)");
{
  const b = last("1. e4 h5 2. Nf3 h4 3. g4 hxg3");
  chk("pawn lands on g3", sq(b, 6, 2), "p");
  chk("victim on g4 removed", sq(b, 6, 3), ".");
  chk("31 pieces remain", total(b), 31);
}

console.log("ordinary pawn capture is untouched (2. exd5)");
{
  const b = last("1. e4 d5 2. exd5");
  chk("pawn on d5", sq(b, 3, 4), "P");
  chk("31 pieces remain", total(b), 31);
}

console.log("castling");
{
  const b = last("1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O");
  chk("king to g1", sq(b, 6, 0), "K");
  chk("rook to f1", sq(b, 5, 0), "R");
  chk("h1 empty", sq(b, 7, 0), ".");
}

console.log("promotion");
{
  const b = last("1. e4 d5 2. exd5 c6 3. dxc6 Nf6 4. cxb7 Ng4 5. bxa8=Q");
  chk("white queen on a8", sq(b, 0, 7), "Q");
}

console.log("King Me — mannyfresher, the Creepy Crawly mate");
{
  const p = M.applyPGN("1. h3 d5 2. a3 e5 3. c3 Nc6 4. e3 Nf6 5. g4 Ne4 6. b4 Nxb4 7. axb4 Qh4 8. Rh2 Bxg4 9. hxg4 Qxh2 10. Qa4+ c6 11. Bb5 a6 12. Bxc6+ bxc6 13. Qxc6+ Kd8 14. Qxd5+ Kc8 15. Qxa8+ Kc7 16. Qxe4 Qxg1+ 17. Ke2 Qxc1 18. b5 axb5 19. Ra7+ Kb8 20. Qa8#");
  chk("39 plies", p.length - 1, 39);
  chk("final move is Qa8#", p[39].san, "Qa8#");
  chk("black king is in check (mate)", M.inCheck(p[39].board, "b"), true);
  chk("white king is not", M.inCheck(p[39].board, "w"), false);
  chk("influence covers 64 squares", p[39].influence.length, 64);
  chk("every piece got a role", p[39].roles.every(r => !!r.role), true);
}

console.log("\n" + pass + " passing" + (fail ? ", " + fail + " FAILING" : ""));
process.exit(fail ? 1 : 0);
