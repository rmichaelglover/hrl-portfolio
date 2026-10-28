"""Extract verified sole-legal-move exercises from the user's real standard games."""
from pathlib import Path
import argparse,json,hashlib,collections
import chess,chess.pgn
ROOT=Path(__file__).resolve().parent
NAMES={chess.PAWN:'pawn',chess.KNIGHT:'knight',chess.BISHOP:'bishop',chess.ROOK:'rook',chess.QUEEN:'queen',chess.KING:'king'}

def classify(board,move):
 piece=board.piece_at(move.from_square);target=board.piece_at(move.to_square)
 if target and target.color==piece.color:return 'own'
 if board.is_pseudo_legal(move):
  if board.is_legal(move):return 'legal'
  if piece.piece_type==chess.KING:return 'king-danger'
  return 'check-remains' if board.is_check() else 'pin'
 dx=chess.square_file(move.to_square)-chess.square_file(move.from_square);dy=chess.square_rank(move.to_square)-chess.square_rank(move.from_square)
 if piece.piece_type==chess.PAWN:
  sign=1 if piece.color else -1
  if dx==0 and dy*sign in (1,2) and (target or (dy*sign==2 and board.piece_at(move.from_square+8*sign))):return 'pawn-blocked'
  if abs(dx)==1 and dy*sign==1 and not target and move.to_square!=board.ep_square:return 'pawn-diagonal'
 if piece.piece_type==chess.KING and abs(dx)==2 and dy==0:return 'castle'
 if (piece.piece_type in [chess.ROOK,chess.QUEEN] and (dx==0 or dy==0)) or (piece.piece_type in [chess.BISHOP,chess.QUEEN] and abs(dx)==abs(dy)):
  if chess.between(move.from_square,move.to_square) & board.occupied:return 'blocked'
 return 'geometry'

def record(board):
 moves=list(board.legal_moves);assert board.is_valid() and not board.is_game_over() and len(moves)==1
 move=moves[0];p=board.piece_at(move.from_square);next_board=board.copy();san=board.san(move);capture=board.is_capture(move);next_board.push(move)
 reasons={}
 for sq,piece in board.piece_map().items():
  if piece.color!=board.turn:continue
  for dest in chess.SQUARES:
   if sq==dest:continue
   m=chess.Move(sq,dest);reasons[m.uci()]=classify(board,m)
 return {'fen':board.fen(),'turn':'white' if board.turn else 'black','in_check':board.is_check(),'checkers':[chess.square_name(s) for s in board.checkers()],'pieces':{chess.square_name(s):p.symbol() for s,p in board.piece_map().items()},'move':{'uci':move.uci(),'from':chess.square_name(move.from_square),'to':chess.square_name(move.to_square),'san':san,'piece':NAMES[p.piece_type],'capture':capture},'reasons':reasons,'after_fen':next_board.fen(),'next_legal_count':len(list(next_board.legal_moves)),'next_game_over':next_board.is_game_over(),'next_outcome':next_board.outcome().result() if next_board.is_game_over() else None}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pgn',type=Path,action='append');args=parser.parse_args()
 paths=args.pgn or sorted(Path('/home/rmichaelglover/Documents').glob('*.pgn'),key=lambda p:p.stat().st_mtime,reverse=True)[:30]+sorted(Path('/home/rmichaelglover/Downloads').glob('*.pgn'),key=lambda p:p.stat().st_mtime,reverse=True)[:2]
 candidates=[];games=0;forced=0;seen=set();total_ply=0
 for path in paths:
  with path.open(errors='replace') as f:
   for index in range(1000):
    game=chess.pgn.read_game(f)
    if game is None:break
    if game.errors or game.headers.get('Variant','Standard')!='Standard' or not any('mannyfresher' in game.headers.get(side,'').lower() for side in ['White','Black']):continue
    games+=1;b=game.board()
    for ply,move in enumerate(game.mainline_moves()):
     if move not in b.legal_moves:raise ValueError('Illegal witness')
     total_ply+=1
     if b.is_valid() and not b.is_game_over() and len(list(b.legal_moves))==1:
      forced+=1
      if 'mannyfresher' in game.headers.get('White' if b.turn else 'Black','').lower():
       key=' '.join(b.fen().split()[:4])
       if key not in seen:
        seen.add(key);own=sum(p.color==b.turn for p in b.piece_map().values());candidates.append({'board':b.copy(),'game':game,'ply':ply,'key':key,'own':own,'pieces':len(b.piece_map())})
     b.push(move)
 # Sparse positions first, but at most two from each game and diverse move types.
 candidates.sort(key=lambda c:(c['own'],c['pieces'],c['ply']))
 selected=[];per_game=collections.Counter();types=collections.Counter()
 for candidate in candidates:
  site=candidate['game'].headers.get('Site','');m=next(iter(candidate['board'].legal_moves));kind=candidate['board'].piece_at(m.from_square).piece_type
  if per_game[site]>=2:continue
  if kind==chess.KING and types[kind]>=12:continue
  selected.append(candidate);per_game[site]+=1;types[kind]+=1
  if len(selected)==20:break
 selected.sort(key=lambda c:not(c['own']==2 and {p.piece_type for p in c['board'].piece_map().values() if p.color==c['board'].turn}=={chess.KING,chess.PAWN} and c['board'].piece_at(next(iter(c['board'].legal_moves)).from_square).piece_type==chess.KING))
 exercises=[];sources={}
 for i,c in enumerate(selected):
  g=c['game'];url=g.headers.get('Site','');ident=hashlib.sha256(str(g).encode()).hexdigest()[:12]
  if ident not in sources:
   path=ROOT/'sources'/f'{ident}.pgn';path.write_text(str(g)+'\n');sources[ident]={'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'site':url}
  steps=[];b=c['board'].copy()
  while not b.is_game_over() and len(list(b.legal_moves))==1 and len(steps)<24:
   steps.append(record(b));b.push(next(iter(b.legal_moves)))
  exercises.append({'id':f'only-{i+1:02d}','title':('Just a king and a pawn' if c['own']==2 and {p.piece_type for p in c['board'].piece_map().values() if p.color==c['board'].turn}=={chess.KING,chess.PAWN} else 'A little breathing room' if c['own']<=2 else 'One step is enough'),'source':sources[ident]['file'],'source_url':url,'white':g.headers.get('White'),'black':g.headers.get('Black'),'date':g.headers.get('Date'),'start_ply':c['ply'],'own_pieces':c['own'],'steps':steps,'end_reason':'game-over' if b.is_game_over() else 'choice-returns' if len(list(b.legal_moves))>1 else 'preview-limit','next_legal_count':len(list(b.legal_moves))})
 summary={'scanned_user_games':games,'scanned_plies':total_ply,'forced_positions_either_side':forced,'unique_user_to_move_positions':len(candidates),'exercises':len(exercises),'longest_selected_corridor':max(len(e['steps']) for e in exercises),'rules':'Standard chess; exactly one legal move, not one best move; automatic game-over stops exercises; optional draw claims are not played automatically.'}
 (ROOT/'exercises.json').write_text(json.dumps({'version':1,'summary':summary,'sources':list(sources.values()),'exercises':exercises},indent=2)+'\n');print(json.dumps(summary,indent=2));print('Move types:',dict(types))
if __name__=='__main__':main()
