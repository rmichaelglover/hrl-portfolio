"""Reproduce a finite-node engine audit of the supplied tournament export.

Install python-chess and make Stockfish available at /usr/games/stockfish,
then run python3 analyze.py. No network requests or changes to original.pgn.
"""
from pathlib import Path
import collections
import hashlib
import json
import statistics
import time
import chess
import chess.engine
import chess.pgn

HERE = Path(__file__).resolve().parent
USER = 'mannyfresher'
NODES = 40_000


def score_dict(score):
    white = score.white()
    return {'cp_white': white.score(), 'mate_white': white.mate()}


def pv_san(board, moves, maximum=9):
    b = board.copy()
    out = []
    for move in moves[:maximum]:
        if move not in b.legal_moves:
            raise ValueError('Engine supplied an illegal PV')
        prefix = f'{b.fullmove_number}.' if b.turn else f'{b.fullmove_number}...'
        out.append(prefix + b.san(move))
        b.push(move)
    return ' '.join(out)


def audit():
    start = time.time()
    source = HERE / 'original.pgn'
    games = []
    with source.open() as f:
        while (game := chess.pgn.read_game(f)) is not None:
            if game.errors:
                raise ValueError(game.errors)
            games.append(game)
    games.sort(key=lambda g: (g.headers.get('UTCDate', ''), g.headers.get('UTCTime', '')))
    engine = chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish')
    engine.configure({'Threads': 1, 'Hash': 64})
    report = {
        'source': 'original.pgn', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'user': USER, 'engine': engine.id, 'python_chess': chess.__version__,
        'settings': {'nodes_per_position': NODES, 'threads': 1, 'hash_mib': 64,
                     'tablebases': 'none configured', 'multipv': 1},
        'scope': 'Finite-node position searches with normal transposition-table reuse, not proof of optimal play. No clock annotations present.',
        'games': [],
    }
    outcomes = collections.Counter()
    ratings = []
    for number, game in enumerate(games, 1):
        headers = dict(game.headers)
        if USER not in (headers.get('White'), headers.get('Black')):
            raise ValueError('Unexpected non-user game')
        side = chess.WHITE if headers['White'] == USER else chess.BLACK
        opponent_side = 'Black' if side else 'White'
        opponent = headers[opponent_side]
        ratings.append(int(headers[opponent_side + 'Elo']))
        result = headers['Result']
        outcome = 'draw' if result == '1/2-1/2' else (
            'win' if (result == '1-0') == side else 'loss')
        outcomes[outcome] += 1
        b = game.board()
        moves = list(game.mainline_moves())
        positions = []
        for ply in range(len(moves)+1):
            terminal = b.is_game_over(claim_draw=False)
            if terminal:
                outcome_on_board = b.outcome(claim_draw=False)
                cp = 0 if outcome_on_board.winner is None else None
                mate = (1 if outcome_on_board.winner else -1) if b.is_checkmate() else None
                # Store mate-in-zero explicitly by the winning color, not Mate(0)'s sign.
                record = {'fen': b.fen(), 'cp_white': cp, 'mate_white': 0 if b.is_checkmate() else mate,
                          'mate_winner': ('white' if outcome_on_board.winner else 'black') if b.is_checkmate() else None,
                          'depth': None, 'nodes': 0, 'best_uci': None, 'pv': [], 'pv_san': '',
                          'board_outcome': outcome_on_board.result()}
            else:
                info = engine.analyse(b, chess.engine.Limit(nodes=NODES), game=game)
                pv = info.get('pv', [])
                record = {'fen': b.fen(), **score_dict(info['score']), 'mate_winner': None,
                          'depth': info.get('depth'), 'nodes': info.get('nodes'),
                          'best_uci': pv[0].uci() if pv else None, 'pv': [m.uci() for m in pv[:12]],
                          'pv_san': pv_san(b, pv)}
            positions.append(record)
            if ply < len(moves):
                b.push(moves[ply])
        b = game.board()
        move_records = []
        for ply, move in enumerate(moves, 1):
            mover = b.turn
            before, after = positions[ply-1], positions[ply]
            cp_loss = None
            if before['cp_white'] is not None and after['cp_white'] is not None:
                cp_loss = max(0, (before['cp_white']-after['cp_white']) * (1 if mover else -1))
            record = {'ply': ply, 'move_number': b.fullmove_number, 'side': 'white' if mover else 'black',
                      'user_move': mover == side, 'san': b.san(move), 'uci': move.uci(),
                      'estimated_cp_loss': cp_loss}
            move_records.append(record)
            b.push(move)
        ending = {'fen': b.fen(), 'is_checkmate': b.is_checkmate(), 'is_stalemate': b.is_stalemate(),
                  'white_material': {chess.piece_name(p): len(b.pieces(p, chess.WHITE)) for p in chess.PIECE_TYPES},
                  'black_material': {chess.piece_name(p): len(b.pieces(p, chess.BLACK)) for p in chess.PIECE_TYPES}}
        report['games'].append({'number': number, 'id': headers['GameId'], 'headers': headers,
                               'side': 'white' if side else 'black', 'opponent': opponent,
                               'outcome': outcome, 'moves': move_records, 'positions': positions,
                               'ending': ending})
        (HERE/'analysis.json').write_text(json.dumps(report, indent=2)+'\n')
        print(f'{number:02}/{len(games)} {opponent}: {outcome}; {len(moves)} legal plies', flush=True)
    engine.quit()
    report['summary'] = {'games': len(games), **outcomes,
                         'opponent_rating_mean': statistics.mean(ratings),
                         'opponent_rating_median': statistics.median(ratings),
                         'opponent_rating_range': [min(ratings),max(ratings)],
                         'total_plies': sum(len(g['moves']) for g in report['games']),
                         'elapsed_seconds': round(time.time()-start, 2)}
    (HERE/'analysis.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['summary']),flush=True)


if __name__ == '__main__':
    audit()
