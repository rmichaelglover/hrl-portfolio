"""Small deterministic two-ply chess policy with optional bounded randomness.

A demonstration player, not a claim of optimal chess or a trained engine.
"""
import copy
import chess

VALUES={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:0}


def evaluation(board,color):
    if board.is_checkmate():return -100000 if board.turn==color else 100000
    score=0.
    for square,piece in board.piece_map().items():
        file,rank=chess.square_file(square),chess.square_rank(square)
        forward=rank if piece.color else 7-rank
        central=7-abs(file-3.5)-abs(rank-3.5)
        value=VALUES[piece.piece_type]
        if piece.piece_type==chess.PAWN:value+=forward*5+(3.5-abs(file-3.5))*5
        elif piece.piece_type==chess.KNIGHT:value+=central*11
        elif piece.piece_type==chess.BISHOP:value+=central*7
        elif piece.piece_type==chess.KING and len(board.piece_map())<10:value+=central*8
        score+=value if piece.color==color else -value
    return score


def ordered_moves(board,topology,rng,randomness,position_counts):
    color=board.turn
    moves=list(board.legal_moves)
    if topology.enforced:moves=[m for m in moves if topology.permitted(m)]
    entries=[]
    for move in moves:
        child=board.copy(stack=True);field=copy.deepcopy(topology)
        field.moved(board,move);child.push(move)
        score=evaluation(child,color)
        if not child.is_checkmate():
            replies=list(child.legal_moves)
            if field.enforced:replies=[m for m in replies if field.permitted(m)]
            if replies:
                scores=[]
                for reply in replies:
                    child.push(reply);scores.append(evaluation(child,color));child.pop()
                score=min(scores)
        # Development/king safety terms remain small compared with material.
        piece=board.piece_at(move.from_square)
        if board.is_castling(move):score+=35
        elif piece.piece_type==chess.KING and board.ply()<20:score-=20
        if piece.piece_type==chess.QUEEN and board.ply()<12:score-=8
        if child.is_check():score+=8
        key=' '.join(child.fen(en_passant='legal').split()[:4])
        score-=position_counts.get(key,0)*24
        if randomness:score+=rng.uniform(-12.,12.)
        entries.append((score,move))
    return [move for _,move in sorted(entries,key=lambda item:(-item[0],item[1].uci()))]
