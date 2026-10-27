"""RelaxFish: deterministic HRL chess research prototype, inspired by M. E. Glover."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import chess
import numpy as np

ROLES = ('King-Shield', 'Infiltrator', 'Blockader', 'Open-File-Anchor',
         'Diagonal-Lurker', 'Escape-Choker', 'Null-Noise')
VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
          chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def normalize(a):
    a = np.asarray(a, dtype=float)
    if not np.all(np.isfinite(a)) or np.any(a < 0):
        raise ValueError('Weights must be finite and nonnegative')
    total = a.sum(axis=-1, keepdims=True)
    if np.any(total <= 0):
        raise ValueError('Every distribution needs positive total weight')
    return a / total


def movement_layer(board, square, legal=False):
    """8x8 matrix, row zero = rank 8. Legal mode respects turn and king safety.

    Default mode returns attacks, including defended friendly occupied squares.
    Pawn pushes are deliberately absent from attack maps.
    """
    result = np.zeros((8, 8))
    targets = (m.to_square for m in board.legal_moves if m.from_square == square) if legal else board.attacks(square)
    for target in targets:
        result[7 - chess.square_rank(target), chess.square_file(target)] = 1
    return result


def role_priors(board, squares):
    rows = []
    for square in squares:
        piece = board.piece_at(square)
        own_king = board.king(piece.color)
        enemy_king = board.king(not piece.color)
        attacks = set(board.attacks(square))
        own_distance = chess.square_distance(square, own_king) if own_king is not None else 8
        enemy_distance = chess.square_distance(square, enemy_king) if enemy_king is not None else 8
        forward_rank = chess.square_rank(square) if piece.color else 7 - chess.square_rank(square)
        pawns_on_file = any(board.piece_type_at(chess.square(chess.square_file(square), r)) == chess.PAWN for r in range(8))
        forward = square + (8 if piece.color else -8)
        blocked_pawn = piece.piece_type == chess.PAWN and 0 <= forward < 64 and board.piece_at(forward) is not None
        enemy_ring = set(board.attacks(enemy_king)) if enemy_king is not None else set()
        rows.append([
            0.2 + (3 if own_distance <= 2 else 0) + sum(board.color_at(t) == piece.color for t in attacks) / 4,
            0.2 + forward_rank / 7 + len(attacks) / 16,
            0.2 + 2 * blocked_pawn,
            0.2 + 3 * (piece.piece_type in (chess.ROOK, chess.QUEEN) and not pawns_on_file),
            0.2 + 2 * (piece.piece_type in (chess.BISHOP, chess.QUEEN)),
            0.2 + len(attacks & enemy_ring) + 1 / (1 + enemy_distance),
            0.5,
        ])
    return normalize(rows)


class ChessRelaxationLabeler:
    """Primary P(piece, role), dual D(role, actual individual piece).

    Bounded, damped updates have an explicit iteration cap. A residual below
    tolerance means numerical stationarity, not a solved chess position.
    """
    def __init__(self, board, max_iterations=40, tolerance=1e-8, damping=0.4):
        if max_iterations < 1 or tolerance <= 0 or not 0 < damping <= 1:
            raise ValueError('Invalid relaxation controls')
        self.board = board.copy(stack=True)
        self.squares = sorted(board.piece_map())
        self.pieces = [f'{board.piece_at(s).symbol()}@{chess.square_name(s)}' for s in self.squares]
        self.max_iterations, self.tolerance, self.damping = max_iterations, tolerance, damping
        self.prior = role_priors(board, self.squares)
        self.P_primary = self.prior.copy()
        self.P_dual = normalize(self.P_primary.T)
        self.history = []
        n, l = self.P_primary.shape
        self.adjacency = np.zeros((n, n))
        self.compatibility = np.zeros((n, n, l, l))
        for i, si in enumerate(self.squares):
            pi = board.piece_at(si)
            for j, sj in enumerate(self.squares):
                if i == j:
                    continue
                pj = board.piece_at(sj)
                contact = sj in board.attacks(si) or si in board.attacks(sj)
                self.adjacency[i, j] = (1 + contact) / (1 + chess.square_distance(si, sj))
                sign = 1 if pi.color == pj.color else -1
                self.compatibility[i, j] = sign * np.eye(l) * 0.3
                self.compatibility[i, j, 0, 2] = sign * 0.2
                self.compatibility[i, j, 1, 5] = sign * 0.2
                self.compatibility[i, j, 6, :] = 0
                self.compatibility[i, j, :, 6] = 0
        self.adjacency /= np.maximum(self.adjacency.sum(axis=1, keepdims=True), 1)

    def execute_dual_relaxation_step(self, compatibility_tensor=None, adjacency_weights=None):
        c = self.compatibility if compatibility_tensor is None else np.asarray(compatibility_tensor)
        a = self.adjacency if adjacency_weights is None else np.asarray(adjacency_weights)
        n, l = self.P_primary.shape
        if c.shape != (n, n, l, l) or a.shape != (n, n):
            raise ValueError('Expected compatibility (N,N,L,L) and adjacency (N,N)')
        if not np.all(np.isfinite(c)) or not np.all(np.isfinite(a)) or np.any(a < 0):
            raise ValueError('Invalid compatibility or adjacency values')
        # Row normalization bounds incoming support independently of piece count.
        a = a / np.maximum(a.sum(axis=1, keepdims=True), 1)
        support = np.einsum('ij,ijab,jb->ia', a, c, self.P_primary, optimize=True)
        feedback = self.P_dual.T * n
        weights = self.prior * np.exp(np.clip(support + 0.1 * feedback, -20, 20))
        target = normalize(weights)
        self.P_primary = normalize((1 - self.damping) * self.P_primary + self.damping * target)
        self.P_dual = normalize(self.P_primary.T)
        return self.P_primary, self.P_dual

    def solve(self):
        self.history = []
        for _ in range(self.max_iterations):
            before = self.P_primary.copy()
            self.execute_dual_relaxation_step()
            residual = float(np.max(np.abs(self.P_primary - before)))
            self.history.append(residual)
            if residual < self.tolerance:
                break
        return {'pieces': self.pieces, 'roles': ROLES,
                'primary': self.P_primary.tolist(), 'dual': self.P_dual.tolist(),
                'iterations': len(self.history), 'residual': self.history[-1],
                'converged': self.history[-1] < self.tolerance}


class QuantumTacticalSuperpositionEngine:
    """Complex-valued role model on a classical computer; no quantum speedup claim."""
    basis_roles = ROLES

    def initialize_state_vector(self):
        return np.ones(len(ROLES), dtype=complex) / np.sqrt(len(ROLES))

    def compute_probability_distribution(self, psi):
        psi = np.asarray(psi, dtype=complex)
        if psi.shape != (len(ROLES),):
            raise ValueError('Expected one amplitude per role')
        return normalize(np.abs(psi) ** 2)

    def apply_classical_field_interference(self, psi, distance_to_king, is_blocked):
        # Amplitude scaling is nonlinear renormalization, not unitary evolution.
        self.compute_probability_distribution(psi)
        out = np.array(psi, dtype=complex, copy=True)
        out[0] *= 1.8 if distance_to_king <= 2 else 0.2
        if is_blocked:
            out[2] *= np.exp(1j * np.pi / 4)
            out[1] *= 0.1
        return out / np.linalg.norm(out)

    def mix_roles(self, psi, angle=0.3):
        # A unitary two-role rotation makes relative phases observable in |psi|^2.
        self.compute_probability_distribution(psi)
        out = np.array(psi, dtype=complex, copy=True)
        out[1] = np.cos(angle) * psi[1] - np.sin(angle) * psi[2]
        out[2] = np.sin(angle) * psi[1] + np.cos(angle) * psi[2]
        return out / np.linalg.norm(out)

    def collapse_tactical_state(self, probabilities, rng):
        p = normalize(probabilities)
        if p.shape != (len(ROLES),):
            raise ValueError('Expected one probability per role')
        return ROLES[int(rng.choice(len(ROLES), p=p))]


class SubboardLedger:
    """Context-addressed heuristic records. Cropped boards are not tablebase proofs."""
    def __init__(self):
        self.records = {}

    def register(self, board, origin, size, evaluation):
        row, col = origin
        if size not in (4, 6) or not (0 <= row <= 8-size and 0 <= col <= 8-size):
            raise ValueError('Expected an in-bounds 4x4 or 6x6 window')
        if not np.isfinite(evaluation):
            raise ValueError('Evaluation must be finite')
        # Full FEN prevents conflating turn, en passant, castling and move clocks.
        # History is included because repetition is not encoded in FEN.
        key = json.dumps({'fen': board.fen(en_passant='fen'), 'origin': origin, 'size': size,
                          'root': board.root().fen(en_passant='fen'),
                          'moves': [m.uci() for m in board.move_stack]}, sort_keys=True)
        self.records[key] = {'evaluation': float(evaluation), 'certified': False,
                             'cells': [[board.piece_at(chess.square(col+c, 7-row-r)).symbol()
                                        if board.piece_at(chess.square(col+c, 7-row-r)) else '.'
                                        for c in range(size)] for r in range(size)]}
        return key

    def save(self, path):
        Path(path).write_text(json.dumps(self.records, indent=2) + '\n')


def evaluate(board):
    outcome = board.outcome(claim_draw=False)
    if outcome is not None:
        return 0.0 if outcome.winner is None else (100000.0 if outcome.winner else -100000.0)
    material = sum(VALUES[p.piece_type] * (1 if p.color else -1) for p in board.piece_map().values())
    model = ChessRelaxationLabeler(board)
    model.solve()
    role_value = 0.0
    for i, square in enumerate(model.squares):
        piece = board.piece_at(square)
        sign = 1 if piece.color else -1
        role_value += sign * float(model.P_primary[i] @ np.array([8, 10, 3, 10, 6, 12, 0]))
        role_value += sign * len(board.attacks(square)) * 0.3
    return material + role_value


def choose_move(board):
    """Rank legal successors with HRL. One ply only; no forced-win guarantee."""
    sign = 1 if board.turn else -1
    candidates = []
    for move in sorted(board.legal_moves, key=lambda m: m.uci()):
        child = board.copy(stack=True)
        child.push(move)
        candidates.append((sign * evaluate(child), move))
    return max(candidates, key=lambda pair: pair[0])[1] if candidates else None


def distributed_profiles(fens, workers=1):
    """Independent position jobs; each position retains all cross-board interactions."""
    if workers < 1:
        raise ValueError('workers must be positive')
    if workers == 1:
        return [profile(fen) for fen in fens]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(profile, fens))


def profile(fen):
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError('Invalid standard chess position')
    return ChessRelaxationLabeler(board).solve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fen', default=chess.STARTING_FEN)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--plies', type=int, default=0, help='Optional bounded self-play')
    args = parser.parse_args()
    board = chess.Board(args.fen)
    if not board.is_valid() or args.plies < 0:
        parser.error('Use a valid FEN and nonnegative plies')
    result = profile(args.fen)
    result['fen'] = board.fen()
    result['recommended_move'] = None
    move = choose_move(board)
    if move is not None:
        result['recommended_move'] = {'uci': move.uci(), 'san': board.san(move)}
    if args.plies:
        from chess import pgn
        game = pgn.Game.from_board(board)
        game.headers['Event'] = 'RelaxFish bounded prototype self-play'
        node = game
        for _ in range(args.plies):
            move = choose_move(board)
            if move is None or board.is_game_over():
                break
            node = node.add_variation(move)
            board.push(move)
        game.headers['Result'] = board.result()
        result['pgn'] = str(game)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + '\n')
    print(rendered)


if __name__ == '__main__':
    main()
