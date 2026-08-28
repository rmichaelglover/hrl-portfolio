/* Chess Maestro study intersections — dependency-free PGN study brancher.
 *
 * This intentionally does not pretend to be Stockfish. When a study contains
 * [%eval] annotations, those are ranked as engine evidence. Without them, the
 * fallback is study consensus (frequency), clearly labeled as such. Manny's
 * recorded moves and annotation tone remain a separate human/intuition line.
 */
(function (global) {
  "use strict";

  function headers(text) {
    const out = {};
    for (const m of text.matchAll(/^\s*\[([^\s]+)\s+"((?:[^"\\]|\\.)*)"\]\s*$/gm)) {
      out[m[1]] = m[2].replace(/\\(["\\])/g, "$1");
    }
    return out;
  }

  function evalValue(raw) {
    if (!raw) return null;
    if (raw[0] === "#") return (raw[1] === "-" ? -1 : 1) * 99;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  }

  function parseGame(chunk, index) {
    const h = headers(chunk);
    const body = chunk.replace(/^\s*\[[^\n]+\]\s*$/gm, "");
    const plies = [];
    let variation = 0, pendingEval = null, pendingComment = "";
    const tokens = body.match(/\{[^}]*\}|\([^)]*\)|\$\d+|\d+\.(?:\.\.)?|[^\s]+/g) || [];
    for (const token of tokens) {
      if (token[0] === "(") continue; // simple variation blocks are skipped below
      if (token[0] === "{") {
        const comment = token.slice(1, -1);
        const e = token.match(/\[%eval\s+(-?#?\d+(?:\.\d+)?)\]/);
        if (plies.length) {
          const last = plies[plies.length - 1];
          last.comment += " " + comment;
          if (e) last.eval = evalValue(e[1]);
          last.intuition = last.intuition || (!/(?:blunder|inaccuracy|mistake|\?\?)/i.test(last.comment) &&
            /(?:!|best|good|great|idea|plan|attack|patient|intuition|manny)/i.test(last.comment));
        } else {
          pendingComment += " " + comment;
          if (e) pendingEval = evalValue(e[1]);
        }
        continue;
      }
      if (token === "(") { variation++; continue; }
      if (token === ")") { variation = Math.max(0, variation - 1); continue; }
      if (variation) continue;
      if (/^(?:\d+\.(?:\.\.)?|\.\.\.)$/.test(token)) continue;
      if (/^(?:1-0|0-1|1\/2-1\/2|\*)$/.test(token)) continue;
      if (/^\$\d+$/.test(token)) continue;
      const san = token.replace(/[!?]+$/, "");
      if (!/^(?:O-O(?:-O)?|0-0(?:-0)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|[a-h]x?[a-h][1-8](?:=[QRBN])?[+#]?)$/.test(san)) continue;
      const ply = plies.length;
      const side = ply % 2 === 0 ? "w" : "b";
      const actor = side === "w" ? (h.White || "") : (h.Black || "");
      const mood = pendingComment;
      plies.push({ san, side, eval: pendingEval, comment: mood,
        human: /mannyfresher/i.test(actor),
        intuition: !/(?:blunder|inaccuracy|mistake|\?\?)/i.test(mood) &&
          /(?:!|best|good|great|idea|plan|attack|patient|intuition|manny)/i.test(mood) });
      pendingEval = null; pendingComment = "";
    }
    return { index, headers: h, plies };
  }

  function parseStudy(text) {
    const chunks = String(text || "").replace(/\r/g, "").split(/(?=^\s*\[Event\b)/m).filter(x => /\[Event\b/.test(x));
    return chunks.map(parseGame).filter(g => g.plies.length);
  }

  function node(san, ply) {
    return { san, ply, count: 0, games: new Set(), children: new Map(),
      evals: [], human: 0, intuition: 0 };
  }

  function build(study) {
    const root = node("START", -1);
    for (const game of study) {
      let parent = root;
      game.plies.forEach((move, ply) => {
        if (!parent.children.has(move.san)) parent.children.set(move.san, node(move.san, ply));
        const child = parent.children.get(move.san);
        child.count++; child.games.add(game.index);
        if (move.eval !== null) child.evals.push(move.side === "w" ? move.eval : -move.eval);
        if (move.human) child.human++;
        if (move.intuition) child.intuition++;
        parent = child;
      });
    }
    return root;
  }

  function average(a) { return a.length ? a.reduce((x, y) => x + y, 0) / a.length : null; }
  function rank(children, mode) {
    return [...children].sort((a, b) => {
      const av = average(a.evals), bv = average(b.evals);
      if (mode === "engine" && av !== null && bv !== null) return bv - av;
      if (mode === "human") return (b.human * 2 + b.intuition + b.count) - (a.human * 2 + a.intuition + a.count);
      return b.count - a.count;
    });
  }

  function intersection(root, maxPly) {
    const out = [];
    let parent = root;
    for (let ply = 0; ply < maxPly; ply++) {
      const children = [...parent.children.values()];
      if (!children.length) break;
      const best = children.sort((a, b) => b.games.size - a.games.size || b.count - a.count)[0];
      out.push(best); parent = best;
      if (best.games.size < 2) break;
    }
    return out;
  }

  function fmtEval(n) { return n === null ? "—" : (n > 98 ? "#" : n < -98 ? "−#" : (n >= 0 ? "+" : "") + n.toFixed(2)); }
  function esc(s) { return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c])); }

  function analyze(text, limit) {
    const games = parseStudy(text), root = build(games), maxPly = limit || 24;
    const common = intersection(root, maxPly);
    const rows = [];
    let parent = root;
    for (let ply = 0; ply < maxPly; ply++) {
      const children = [...parent.children.values()]; if (!children.length) break;
      const engine = rank(children, "engine")[0], human = rank(children, "human")[0];
      const shared = common[ply];
      rows.push({ ply: ply + 1, shared: shared ? shared.san : "—", sharedCount: shared ? shared.games.size : 0,
        engine: engine.san, engineEval: fmtEval(average(engine.evals)), engineEvidence: engine.evals.length ? "eval" : "consensus",
        human: human.san, humanCount: human.human, branchCount: children.length,
        branches: rank(children, "engine").slice(0, 6).map(x => x.san) });
      parent = shared || engine;
    }
    return { games, rows, commonLength: common.length };
  }

  function render(text, target, limit) {
    const result = analyze(text, limit);
    if (!target) return result;
    if (!result.games.length) { target.innerHTML = "<div class=\"loadhint\">No complete PGN games found.</div>"; return result; }
    const rows = result.rows.map(r => `<tr><td>${r.ply}</td><td><b>${esc(r.shared)}</b> <small>${r.sharedCount}/${result.games.length}</small></td><td>${esc(r.engine)} <small>${r.engineEval} · ${r.engineEvidence}</small></td><td>${esc(r.human)} <small>${r.humanCount} Manny</small></td><td>${r.branchCount}</td><td>${r.branches.map(esc).join(" · ")}</td></tr>`).join("");
    target.innerHTML = `<div class="card2"><b>Study intersection</b> — ${result.games.length} games; common route ${result.commonLength} plies.
      <div class="loadhint">Engine column uses annotated <code>[%eval]</code> when present; otherwise it uses study consensus. Human column follows Manny's recorded moves and positive annotation cues. Neither column claims an engine was run in-browser.</div>
      <div style="overflow:auto"><table class="studytable"><thead><tr><th>Ply</th><th>Intersection</th><th>Engine / consensus</th><th>Manny / intuition</th><th>#</th><th>Branch moves</th></tr></thead><tbody>${rows}</tbody></table></div></div>`;
    return result;
  }

  global.StudyBranches = { parseStudy, analyze, render };
})(window);
