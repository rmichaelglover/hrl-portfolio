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

  if (type === 'p') {
    const dir = color === 'w' ? 1 : -1;
    const pchar = color === 'w' ? 'P' : 'p';
    if (disamb) {
      // capture: source file from disambiguation
      const sf = disamb.charCodeAt(0) - 97;
      from = [sf, dest[1] - dir];
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

// ---- Universal export ------------------------------------------------------
if (typeof module !== 'undefined' && module.exports) module.exports = Maestro;
if (typeof window !== 'undefined') window.Maestro = Maestro;
