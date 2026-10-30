"""Independent integrity checks for the published PGN review and teaching lines."""
from pathlib import Path
import collections,hashlib,json,re
import chess,chess.pgn
from editorial import GAMES
HERE=Path(__file__).resolve().parent

def load_pgn(name):
    result=[]
    with (HERE/name).open() as f:
        while (game:=chess.pgn.read_game(f)) is not None:
            assert not game.errors
            result.append(game)
    return result

original=load_pgn('original.pgn');original.sort(key=lambda g:g.headers['UTCTime'])
reviewed=load_pgn('reviewed.pgn');data=json.loads((HERE/'review.json').read_text())
audit=json.loads((HERE/'analysis.json').read_text());deep=json.loads((HERE/'selected-analysis.json').read_text());manifest=json.loads((HERE/'manifest.json').read_text())
assert hashlib.sha256((HERE/'original.pgn').read_bytes()).hexdigest()==manifest['sha256']==audit['source_sha256']
assert len(original)==len(reviewed)==len(data['games'])==29
plies=0
for game,annotated,record,engine in zip(original,reviewed,data['games'],audit['games']):
    assert dict(game.headers)==dict(annotated.headers)==record['headers']
    moves=list(game.mainline_moves());assert moves==list(annotated.mainline_moves())
    assert game.headers['TimeControl']=='60+0' and game.headers['Date']=='2026.10.30'
    assert len(record['frames'])==len(moves)+1
    b=game.board();hero=record['side']=='white'
    for ply,frame in enumerate(record['frames']):
        assert frame['fen']==b.fen()==engine['positions'][ply]['fen']
        assert len(frame['wood'])==len(b.pieces(chess.KING,hero))+sum(len(b.pieces(piece,hero)) for piece in [chess.PAWN,chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN])
        assert all(b.piece_at(chess.parse_square(sq)).color==hero for sq in frame['wood'])
        pv=b.copy()
        for uci in engine['positions'][ply]['pv']:
            move=chess.Move.from_uci(uci);assert move in pv.legal_moves;pv.push(move)
        if ply<len(moves):
            assert moves[ply] in b.legal_moves and b.san(moves[ply])==record['moves'][ply]
            b.push(moves[ply]);plies+=1
    for beat in GAMES[record['number']]['beats']:
        assert record['moves'][beat['ply']-1]==beat['san']
assert plies==1621
assert collections.Counter(g['outcome'] for g in data['games'])=={'win':4,'draw':1,'loss':24}
assert sum(len(g['queen_departures']) for g in data['games'])==15
assert all(g['outcome']=='loss' for g in data['games'] if g['queen_departures'])
for c in data['checkpoints']:
    b=chess.Board(c['fen']);legal={b.san(m) for m in b.legal_moves}
    assert set(c['options'])<=legal and c['answer']==c['line_san'][0]
    for uci in c['line']:
        move=chess.Move.from_uci(uci);assert move in b.legal_moves;b.push(move)
for selected in deep['positions']:
    for line in selected['lines']:
        b=chess.Board(selected['fen'])
        for uci in line['uci']:
            move=chess.Move.from_uci(uci);assert move in b.legal_moves;b.push(move)
# The knight really forks the king and queen; this is more than a PV label.
b=chess.Board(data['checkpoints'][1]['fen']);b.push_san('Nxf3+')
assert b.is_check() and chess.D4 in b.attacks(chess.F3) and b.piece_at(chess.D4)==chess.Piece(chess.QUEEN,chess.WHITE)
# The c-file resource really takes a queen with check.
b=chess.Board(data['checkpoints'][0]['fen']);assert b.piece_at(chess.C3)==chess.Piece(chess.QUEEN,chess.WHITE);b.push_san('Rxc3+');assert b.is_check()
# The timeout draw's recorded final board has a bare black king.
b=original[9].end().board();assert set(b.piece_map().values())>=set([chess.Piece(chess.KING,chess.BLACK)])
assert sum(len(b.pieces(piece,chess.BLACK)) for piece in chess.PIECE_TYPES)==1
assert len(b.pieces(chess.ROOK,chess.WHITE))==1 and len(b.pieces(chess.PAWN,chess.WHITE))>0
assert '[%clk' not in (HERE/'original.pgn').read_text()
print('PASS: 29 unchanged mainlines, 1,621 legal plies, all replay frames and cast identities, 107 anchored beats, legal engine PVs, 3 checkpoints and timeout-draw material.')
