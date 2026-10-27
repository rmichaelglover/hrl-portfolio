"""Exact bounded legal-move sequence counts, with conservative endpoint bounds."""
from functools import lru_cache
import time
import chess
import numpy as np
from scipy.optimize import linear_sum_assignment


def state(board):
    return (board.board_fen(),board.turn,board.castling_rights,board.ep_square if board.has_legal_en_passant() else None)


def budget(board,remaining,color):
    return (remaining+1)//2 if board.turn==color else remaining//2


@lru_cache(None)
def distance(kind,source,target,color,other_kind,castle):
    if kind==chess.PAWN:
        sign=1 if color else -1
        if other_kind==chess.PAWN:
            dy=(chess.square_rank(target)-chess.square_rank(source))*sign;dx=abs(chess.square_file(target)-chess.square_file(source))
            if dy<0 or dx>dy:return 999
            initial=chess.square_rank(source)==(1 if color else 6)
            return max(dx,dy-int(initial and dy>=2))
        if other_kind==chess.KING:return 999
        dy=(7-chess.square_rank(source)) if color else chess.square_rank(source)
        initial=chess.square_rank(source)==(1 if color else 6)
        promotion=max(0,dy-int(initial and dy>=2))
        return promotion+min(distance(other_kind,chess.square(f,7 if color else 0),target,color,other_kind,False) for f in range(8))
    if kind!=other_kind:return 999
    dx=abs(chess.square_file(source)-chess.square_file(target));dy=abs(chess.square_rank(source)-chess.square_rank(target))
    if dx==dy==0:return 0
    if kind==chess.KNIGHT:
        queue=[source];seen={source}
        for d in range(1,8):
            nxt=[]
            for sq in queue:
                for t in chess.SquareSet(chess.BB_KNIGHT_ATTACKS[sq]):
                    if t==target:return d
                    if t not in seen:seen.add(t);nxt.append(t)
            queue=nxt
        return 999
    if kind==chess.BISHOP:
        if (sum(divmod(source,8))-sum(divmod(target,8)))%2:return 999
        return 1 if dx==dy else 2
    if kind==chess.ROOK:return 1 if dx==0 or dy==0 else 2
    if kind==chess.QUEEN:return 1 if dx==0 or dy==0 or dx==dy else 2
    if kind==chess.KING:
        direct=max(dx,dy)
        if castle and source==chess.E1+(0 if color else 56):
            rank=0 if color else 7
            direct=min([direct]+[1+max(abs(chess.square_file(target)-f),abs(chess.square_rank(target)-rank)) for f in [2,6]])
        return direct
    raise ValueError(kind)


def material_possible(board,target,remaining):
    if board.turn != (target.turn if remaining%2==0 else not target.turn):return False
    if target.castling_rights & ~board.castling_rights:return False
    for color in chess.COLORS:
        current=sum(len(board.pieces(p,color)) for p in chess.PIECE_TYPES);final=sum(len(target.pieces(p,color)) for p in chess.PIECE_TYPES)
        if current<final or len(board.pieces(chess.PAWN,color))<len(target.pieces(chess.PAWN,color)):return False
        if current-final>budget(board,remaining,not color):return False
    return True


def endpoint_bound(board,target,color):
    sources=[(s,p.piece_type) for s,p in board.piece_map().items() if p.color==color]
    goals=[(s,p.piece_type) for s,p in target.piece_map().items() if p.color==color]
    if len(sources)<len(goals):return 999
    if not goals:return 0
    rights=bool(board.clean_castling_rights() & board.occupied_co[color])
    costs=np.array([[distance(k,s,t,color,j,rights) for s,k in sources] for t,j in goals])
    rows,cols=linear_sum_assignment(costs)
    raw=int(costs[rows,cols].sum())
    # Castling moves king and rook in one turn, while the assignment sums both.
    # At most one castle per color is possible. Subtracting one even when unused
    # weakens the bound, but cannot exclude a valid path.
    return max(0,raw-int(rights))


def solve(start,target,plies,method='bound',max_nodes=300000,checkpoints=None):
    if method not in {'legal','material','bound'}:raise ValueError(method)
    board=start.copy(stack=False);target_key=state(target);checkpoints=checkpoints or {};cache={};stats={'nodes':0,'edges':0,'cache_hits':0,'pruned':0};t=time.perf_counter()
    class Limit(Exception):pass
    def count(left):
        key=(state(board),left)
        if key in cache:stats['cache_hits']+=1;return cache[key]
        stats['nodes']+=1
        if stats['nodes']>max_nodes:raise Limit
        if plies-left in checkpoints and key[0]!=state(checkpoints[plies-left]):stats['pruned']+=1;answer=0
        elif left==0:answer=int(key[0]==target_key)
        elif method!='legal' and not material_possible(board,target,left):stats['pruned']+=1;answer=0
        elif method=='bound' and any(endpoint_bound(board,target,c)>budget(board,left,c) for c in chess.COLORS):stats['pruned']+=1;answer=0
        else:
            answer=0
            for move in list(board.legal_moves):
                stats['edges']+=1;board.push(move)
                try:answer+=count(left-1)
                finally:board.pop()
        cache[key]=answer;return answer
    try:total=count(plies);complete=True
    except Limit:total=None;complete=False
    examples=[]
    def collect(left,path):
        if len(examples)>=12:return
        if left==0:
            if state(board)==target_key:examples.append(path)
            return
        for move in list(board.legal_moves):
            board.push(move)
            try:
                if cache.get((state(board),left-1),0):collect(left-1,path+[move.uci()])
            finally:board.pop()
            if len(examples)>=12:return
    if complete and total:collect(plies,[])
    return {**stats,'method':method,'plies':plies,'complete':complete,'paths':total,'examples':examples,'seconds':time.perf_counter()-t,'checkpoint_plies':sorted(checkpoints),'state_model':'piece placement, turn, castling rights, legal en-passant; draw claims/counters excluded; standard chess'}
