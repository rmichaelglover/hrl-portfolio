/*
 * Maestro chess visualizer core.
 * Works as a Node module and in the browser (no imports, no DOM).
 * Board rep: board[rank][file], rank 0 = rank 1, file 0 = a-file.
 * Pieces are single-char FEN-style: uppercase = white, lowercase = black.
 */
const Maestro = {};

Maestro.FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

// ---- Board construction ----------------------------------------------------
Maestro.startBoard = function () {
  const b = [];
  for (let r = 0; r < 8; r++) b.push([null, null, null, null, null, null, null, null]);
  const back = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'];
  for (let f = 0; f < 8; f++) {
    b[0][f] = back[f];
    b[1][f] = 'P';
    b[6][f] = 'p';
    b[7][f] = back[f].toLowerCase();
  }
  return b;
};

Maestro.cloneBoard = function (board) {
  return board.map(function (row) { return row.slice(); });
};

Maestro.colorOf = function (piece) {
  return piece === piece.toUpperCase() ? 'w' : 'b';
};

// ---- Attack patterns -------------------------------------------------------
// Squares a piece "influences" (attacks/defends), sliders blocked by occupancy.
Maestro.pieceAttacks = function (board, file, rank) {
  const piece = board[rank][file];
  if (!piece) return [];
  const type = piece.toLowerCase();
  const color = Maestro.colorOf(piece);
  const res = [];
  const add = function (f, r) { if (f >= 0 && f < 8 && r >= 0 && r < 8) res.push([f, r]); };

  if (type === 'p') {
    const dir = color === 'w' ? 1 : -1;
    add(file - 1, rank + dir);
    add(file + 1, rank + dir);
  } else if (type === 'n') {
    const d = [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]];
    for (let i = 0; i < d.length; i++) add(file + d[i][0], rank + d[i][1]);
  } else if (type === 'k') {
    for (let df = -1; df <= 1; df++) for (let dr = -1; dr <= 1; dr++) if (df || dr) add(file + df, rank + dr);
  } else {
    let dirs = [];
    if (type === 'b' || type === 'q') dirs = dirs.concat([[1, 1], [1, -1], [-1, 1], [-1, -1]]);
    if (type === 'r' || type === 'q') dirs = dirs.concat([[1, 0], [-1, 0], [0, 1], [0, -1]]);
    for (let i = 0; i < dirs.length; i++) {
      let f = file + dirs[i][0];
      let r = rank + dirs[i][1];
      while (f >= 0 && f < 8 && r >= 0 && r < 8) {
        res.push([f, r]);
        if (board[r][f]) break;
        f += dirs[i][0];
        r += dirs[i][1];
      }
    }
  }
  return res;
};

// ---- Check detection -------------------------------------------------------
Maestro.findKing = function (board, color) {
  const k = color === 'w' ? 'K' : 'k';
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) if (board[r][f] === k) return [f, r];
  return null;
};

Maestro.isAttackedBy = function (board, file, rank, byColor) {
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) {
    const p = board[r][f];
    if (!p || Maestro.colorOf(p) !== byColor) continue;
    const atk = Maestro.pieceAttacks(board, f, r);
    for (let i = 0; i < atk.length; i++) if (atk[i][0] === file && atk[i][1] === rank) return true;
  }
  return false;
};

Maestro.inCheck = function (board, color) {
  const k = Maestro.findKing(board, color);
  if (!k) return false;
  return Maestro.isAttackedBy(board, k[0], k[1], color === 'w' ? 'b' : 'w');
};

// ---- SAN applier -----------------------------------------------------------
Maestro.parseSquare = function (s) {
  return [s.charCodeAt(0) - 97, parseInt(s[1], 10) - 1];
};

// Apply one SAN move for `color`, returning a new board.
Maestro.applySAN = function (board, color, san) {
  let m = san.replace(/[+#!?]+$/, '');
  const nb = Maestro.cloneBoard(board);

  // Castling (stubbed but functional for standard cases).
  if (m === 'O-O' || m === 'O-O-O' || m === '0-0' || m === '0-0-0') {
    const r = color === 'w' ? 0 : 7;
    if (m === 'O-O' || m === '0-0') {
      nb[r][6] = nb[r][4]; nb[r][4] = null;
      nb[r][5] = nb[r][7]; nb[r][7] = null;
    } else {
      nb[r][2] = nb[r][4]; nb[r][4] = null;
      nb[r][3] = nb[r][0]; nb[r][0] = null;
    }
    return nb;
  }

  // Promotion suffix (e.g. e8=Q).
  let promo = null;
  const pm = m.match(/=([QRBN])$/);
  if (pm) { promo = pm[1]; m = m.replace(/=([QRBN])$/, ''); }

  let type, rest;
  if (/^[NBRQK]/.test(m)) { type = m[0].toLowerCase(); rest = m.slice(1); }
  else { type = 'p'; rest = m; }

  rest = rest.replace('x', '');
  const dest = Maestro.parseSquare(rest.slice(-2));
  const disamb = rest.slice(0, -2);

  let from = null;
  let epCapture = null; // en passant: the taken pawn is not on the destination square

  if (type === 'p') {
    const dir = color === 'w' ? 1 : -1;
    const pchar = color === 'w' ? 'P' : 'p';
    if (disamb) {
      // capture: source file from disambiguation
      const sf = disamb.charCodeAt(0) - 97;
      from = [sf, dest[1] - dir];
      // A pawn capture onto an empty square can only be en passant; the victim
      // sits alongside the mover, one rank back from the destination.
      const victim = nb[dest[1] - dir] && nb[dest[1] - dir][dest[0]];
      if (!nb[dest[1]][dest[0]] && victim && Maestro.colorOf(victim) !== color && victim.toLowerCase() === 'p') {
        epCapture = [dest[0], dest[1] - dir];
      }
    } else {
      const f = dest[0];
      const one = dest[1] - dir;
      if (one >= 0 && one < 8 && nb[one][f] === pchar) from = [f, one];
      else from = [f, dest[1] - 2 * dir];
    }
  } else {
    const pchar = color === 'w' ? type.toUpperCase() : type;
    let cands = [];
    for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) {
      if (nb[r][f] !== pchar) continue;
      const atk = Maestro.pieceAttacks(nb, f, r);
      for (let i = 0; i < atk.length; i++) {
        if (atk[i][0] === dest[0] && atk[i][1] === dest[1]) { cands.push([f, r]); break; }
      }
    }
    if (disamb) {
      for (let i = 0; i < disamb.length; i++) {
        const ch = disamb[i];
        if (ch >= 'a' && ch <= 'h') {
          const df = ch.charCodeAt(0) - 97;
          cands = cands.filter(function (c) { return c[0] === df; });
        } else if (ch >= '1' && ch <= '8') {
          const dr = parseInt(ch, 10) - 1;
          cands = cands.filter(function (c) { return c[1] === dr; });
        }
      }
    }
    if (cands.length > 1) {
      // Resolve remaining ambiguity by legality (don't leave own king in check).
      const legal = cands.filter(function (c) {
        const tb = Maestro.cloneBoard(nb);
        tb[dest[1]][dest[0]] = tb[c[1]][c[0]];
        tb[c[1]][c[0]] = null;
        return !Maestro.inCheck(tb, color);
      });
      if (legal.length >= 1) cands = legal;
    }
    from = cands[0];
  }

  if (!from) return nb; // defensive: do not crash on an unhandled move

  const moving = nb[from[1]][from[0]];
  nb[dest[1]][dest[0]] = promo ? (color === 'w' ? promo : promo.toLowerCase()) : moving;
  nb[from[1]][from[0]] = null;
  if (epCapture) nb[epCapture[1]][epCapture[0]] = null;
  return nb;
};

// ---- Influence -------------------------------------------------------------
Maestro.computeInfluence = function (board) {
  const cells = [];
  for (let i = 0; i < 64; i++) cells.push({ white: 0, black: 0, net: 0, terrain: 'contested', height: 0, water: false });
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) {
    const piece = board[r][f];
    if (!piece) continue;
    const color = Maestro.colorOf(piece);
    const atk = Maestro.pieceAttacks(board, f, r);
    for (let i = 0; i < atk.length; i++) {
      const idx = atk[i][1] * 8 + atk[i][0];
      if (color === 'w') cells[idx].white++; else cells[idx].black++;
    }
  }
  for (let i = 0; i < 64; i++) {
    const c = cells[i];
    c.net = c.white - c.black;
    c.terrain = c.net > 0 ? 'white' : (c.net < 0 ? 'black' : 'contested');
    c.height = Math.min(4, Math.abs(c.net));
    c.water = (c.net === 0 && (c.white + c.black) > 0);
  }
  return cells;
};

// ---- Roles -----------------------------------------------------------------
Maestro.piecesList = function (board) {
  const arr = [];
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) {
    const p = board[r][f];
    if (!p) continue;
    arr.push({ file: f, rank: r, type: p.toLowerCase(), color: Maestro.colorOf(p) });
  }
  return arr;
};

Maestro.defendedByPawn = function (board, file, rank, color) {
  const pchar = color === 'w' ? 'P' : 'p';
  const dir = color === 'w' ? 1 : -1;
  const sr = rank - dir;
  const offs = [-1, 1];
  for (let i = 0; i < offs.length; i++) {
    const sf = file + offs[i];
    if (sf >= 0 && sf < 8 && sr >= 0 && sr < 8 && board[sr][sf] === pchar) return true;
  }
  return false;
};

Maestro.computeRoles = function (board) {
  const pieces = Maestro.piecesList(board);
  const central = [[3, 3], [4, 3], [3, 4], [4, 4]]; // d4,e4,d5,e5
  return pieces.map(function (pc) {
    const file = pc.file, rank = pc.rank, type = pc.type, color = pc.color;
    const atk = Maestro.pieceAttacks(board, file, rank);

    const attacksEnemy = atk.some(function (sq) {
      const t = board[sq[1]][sq[0]];
      return t && Maestro.colorOf(t) !== color;
    });
    const defendsFriend = atk.some(function (sq) {
      const t = board[sq[1]][sq[0]];
      return t && Maestro.colorOf(t) === color;
    });
    const advanced = (color === 'w' && rank >= 4) || (color === 'b' && rank <= 3);
    const enemyTerritory = (color === 'w' && rank >= 5) || (color === 'b' && rank <= 2);
    const touchesCenter = atk.some(function (sq) {
      return central.some(function (c) { return c[0] === sq[0] && c[1] === sq[1]; });
    }) || central.some(function (c) { return c[0] === file && c[1] === rank; });

    let role;
    if (attacksEnemy) role = 'attacker';
    else if ((type === 'n' || type === 'b') && advanced && Maestro.defendedByPawn(board, file, rank, color)) role = 'outpost';
    else if ((type === 'p' && advanced) || enemyTerritory) role = 'runner';
    else if (touchesCenter) role = 'controller';
    else if (defendsFriend) role = 'defender';
    else role = 'noise';

    return { file: file, rank: rank, type: type, color: color, role: role };
  });
};

// ---- Snapshot + PGN --------------------------------------------------------
Maestro.snapshot = function (board, ply, san) {
  return {
    ply: ply,
    san: san,
    board: Maestro.cloneBoard(board),
    pieces: Maestro.piecesList(board),
    influence: Maestro.computeInfluence(board),
    roles: Maestro.computeRoles(board)
  };
};

Maestro.applyPGN = function (movesString) {
  let board = Maestro.startBoard();
  const positions = [Maestro.snapshot(board, 0, '')];
  const tokens = movesString.trim().split(/\s+/);
  let ply = 0;
  let color = 'w';
  for (let i = 0; i < tokens.length; i++) {
    let tok = tokens[i];
    if (!tok) continue;
    if (/^(1-0|0-1|1\/2-1\/2|\*)$/.test(tok)) continue;
    const numMatch = tok.match(/^\d+\.+(.*)$/);
    if (numMatch) tok = numMatch[1];
    if (!tok) continue; // bare move number token
    board = Maestro.applySAN(board, color, tok);
    ply++;
    positions.push(Maestro.snapshot(board, ply, tok));
    color = color === 'w' ? 'b' : 'w';
  }
  return positions;
};

// ---- chess-world v1 --------------------------------------------------------
// The interchange format WorldKit consumes (whimsy-chess/worldkit.js), so a game
// stepped here can be built into Minecraft and Roblox by the same code path that
// serves maestro.html. Terrain semantics match maestro.html's: positive height is
// land elevation, negative is water depth, and the contested seam is sized by the
// area of its connected component — a lone square is a pond, a sprawl is an ocean.

Maestro.NAMES = { p: 'Pawn', n: 'Knight', b: 'Bishop', r: 'Rook', q: 'Queen', k: 'King' };

// Size each contested region pond→ocean, the way maestro.html does.
Maestro.waterBodies = function (influence) {
  const wet = [];
  for (let i = 0; i < 64; i++) wet.push(!!influence[i].water);
  const comp = new Array(64).fill(-1);
  const kinds = new Array(64).fill('');
  let id = 0;
  for (let start = 0; start < 64; start++) {
    if (!wet[start] || comp[start] >= 0) continue;
    const stack = [start], cells = [];
    comp[start] = id;
    while (stack.length) {
      const at = stack.pop();
      cells.push(at);
      const f = at & 7, r = at >> 3;
      for (let df = -1; df <= 1; df++) for (let dr = -1; dr <= 1; dr++) {
        if (!df && !dr) continue;
        const nf = f + df, nr = r + dr;
        if (nf < 0 || nf > 7 || nr < 0 || nr > 7) continue;
        const ni = nr * 8 + nf;
        if (wet[ni] && comp[ni] < 0) { comp[ni] = id; stack.push(ni); }
      }
    }
    const fs = cells.map(c => c & 7), rs = cells.map(c => c >> 3);
    const w = Math.max.apply(null, fs) - Math.min.apply(null, fs) + 1;
    const h = Math.max.apply(null, rs) - Math.min.apply(null, rs) + 1;
    const n = cells.length;
    const thin = Math.min(w, h) === 1 || n <= Math.max(w, h) + 1;
    let kind;
    if (n <= 1) kind = 'pond';
    else if (n <= 2) kind = 'creek';
    else if (thin && Math.max(w, h) >= 3) kind = 'river';
    else if (n <= 5) kind = 'lake';
    else if (n <= 12) kind = 'sea';
    else kind = 'ocean';
    for (let i = 0; i < cells.length; i++) kinds[cells[i]] = kind;
    id++;
  }
  return kinds;
};

const WATER_DEPTH = { pond: 1, creek: 1, river: 1, lake: 2, sea: 3, ocean: 4 };

// A stable piece id per starting square, so a piece keeps its identity across plies.
Maestro.identify = function (positions) {
  const ids = {}; // "file,rank" -> id, tracked forward through each move
  const start = positions[0];
  const seen = {};
  for (const p of start.pieces) {
    const n = (seen[p.color + p.type] = (seen[p.color + p.type] || 0) + 1);
    ids[p.file + ',' + p.rank] = p.color + p.type + n;
  }
  const perPly = [Object.assign({}, ids)];
  let live = Object.assign({}, ids);
  for (let i = 1; i < positions.length; i++) {
    const prev = positions[i - 1], cur = positions[i];
    const was = {}, now = {};
    for (const p of prev.pieces) was[p.file + ',' + p.rank] = p;
    for (const p of cur.pieces) now[p.file + ',' + p.rank] = p;
    const vacated = [], filled = [];
    for (const k in was) if (!now[k] || now[k].color !== was[k].color || now[k].type !== was[k].type) vacated.push(k);
    for (const k in now) if (!was[k] || was[k].color !== now[k].color || was[k].type !== now[k].type) filled.push(k);
    const next = {};
    for (const k in live) if (now[k] && vacated.indexOf(k) < 0) next[k] = live[k];
    // Move each id from the square it left to the square its own colour arrived on.
    for (const to of filled) {
      const arriving = now[to];
      let bestFrom = null;
      for (const from of vacated) {
        const left = was[from];
        if (!left || left.color !== arriving.color) continue;
        if (!live[from] || next[from]) continue;
        // prefer same type (promotion changes type, so fall back to any same-colour mover)
        if (left.type === arriving.type) { bestFrom = from; break; }
        if (!bestFrom) bestFrom = from;
      }
      next[to] = bestFrom && live[bestFrom] ? live[bestFrom] : arriving.color + arriving.type + 'x';
    }
    live = next;
    perPly.push(Object.assign({}, live));
  }
  return perPly;
};

/**
 * Emit a chess-world v1 document for a whole game.
 * @param {Array} positions  output of Maestro.applyPGN
 * @param {Object} meta      {label, white, black, result, hero}
 */
Maestro.toWorld = function (positions, meta) {
  meta = meta || {};
  const hero = meta.hero || 'w';
  const idsPerPly = Maestro.identify(positions);

  const pieces = [];
  const declared = {};
  for (let i = 0; i < positions.length; i++) {
    const ids = idsPerPly[i];
    for (const p of positions[i].pieces) {
      const id = ids[p.file + ',' + p.rank];
      if (!id || declared[id]) continue;
      declared[id] = true;
      pieces.push({
        id: id, color: p.color, team: p.color === hero ? 'woodland' : 'misfit',
        type: p.type, startSquare: Maestro.FILES[p.file] + (p.rank + 1),
        name: Maestro.NAMES[p.type] || p.type, emoji: ''
      });
    }
  }

  const frames = positions.map(function (P, i) {
    const kinds = Maestro.waterBodies(P.influence);
    const height = [], water = [];
    for (let r = 0; r < 8; r++) {
      const hr = [], wr = [];
      for (let f = 0; f < 8; f++) {
        const idx = r * 8 + f, c = P.influence[idx], kind = kinds[idx];
        if (kind) { hr.push(-(WATER_DEPTH[kind] || 1)); wr.push(kind); }
        else { hr.push(Math.max(1, Math.min(8, Math.abs(c.net) || 1))); wr.push(''); }
      }
      height.push(hr); water.push(wr);
    }

    const ids = idsPerPly[i];
    const placement = {}, roles = {};
    for (const r of P.roles) {
      const id = ids[r.file + ',' + r.rank];
      if (!id) continue;
      placement[Maestro.FILES[r.file] + (r.rank + 1)] = id;
      roles[id] = { role: r.role, strength: 1 };
    }

    return {
      ply: i, move: i === 0 ? null : { san: P.san, from: null, to: null, moverId: null },
      placement: placement, roles: roles, height: height, water: water,
      beat: i, onset: i, coherence: 1, advantage: 0
    };
  });

  return {
    format: 'chess-world', version: 1,
    meta: {
      label: meta.label || 'Chess Maestro', white: meta.white || 'White',
      black: meta.black || 'Black', result: meta.result || '*', hero: hero,
      plies: positions.length - 1, generator: 'Maestro core.js'
    },
    files: 'abcdefgh',
    note: 'height[rankIndex 0..7][fileIndex 0..7]; rankIndex0=rank1, fileIndex0=file a. height<0 = water depth, >0 = land elevation. placement maps square -> piece id; pieces[] gives identity/team.',
    legend: {
      roles: ['attacker', 'defender', 'controller', 'outpost', 'runner', 'tactic', 'noise'],
      water: ['pond', 'creek', 'river', 'lake', 'sea', 'ocean'],
      elevation: ['grass', 'meadow', 'tan', 'hills', 'brown', 'rock', 'alpine', 'snow']
    },
    pieces: pieces, frames: frames
  };
};

// ---- Universal export ------------------------------------------------------
if (typeof module !== 'undefined' && module.exports) module.exports = Maestro;
if (typeof window !== 'undefined') window.Maestro = Maestro;
