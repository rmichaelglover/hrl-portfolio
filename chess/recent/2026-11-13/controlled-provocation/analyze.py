"""Recorded-game evaluation of Michael Emanuel Glover's controlled-provocation thesis."""
from pathlib import Path
import chess,chess.pgn,chess.engine
import json,hashlib,collections,time,sys
OUT=Path(__file__).parent
SOURCES=[
'lichess_study_kings-gambit_by_mannyfresher_2026.08.03.pgn',
'lichess_study_the-queens-gambit-netflix_by_mannyfresher_2026.10.05 (1).pgn',
'lichess_study_van-mieses_mannyfresher-936-kusal2022-1034_by_mannyfresher_2026.11.12.pgn',
'lichess_study_rancid-randi_by_mannyfresher_2026.09.09 (1).pgn',
'lichess_study_pircerson-parks_by_mannyfresher_2026.09.09.pgn',
'lichess_study_vant-kruijsing_by_mannyfresher_2026.09.08 (1).pgn']
NODES=20000

def sanline(board,pv,limit=5):
 b=board.copy();out=[]
 for m in pv[:limit]:
  if m not in b.legal_moves:break
  out.append(f'{b.fullmove_number}{"." if b.turn else "..."} {b.san(m)}');b.push(m)
 return ' '.join(out)

def evaluation(engine,board):
 if board.uci_variant!='chess':return {'cp_white':0,'display':'Not evaluated: Crazyhouse','pv':'','depth':0,'nodes':0,'unsupported_variant':True}
 if board.is_game_over(claim_draw=False):
  o=board.outcome();score=0 if o.winner is None else 10000 if o.winner else -10000
  return {'cp_white':score,'display':str(score),'pv':'','depth':0,'nodes':0,'terminal':True}
 a=engine.analyse(board,chess.engine.Limit(nodes=NODES))
 v=a['score'].white()
 return {'cp_white':v.score(mate_score=10000),'display':str(v),'pv':sanline(board,a.get('pv',[])),
         'depth':a.get('depth'),'nodes':a.get('nodes'),'terminal':False}

allgames=[];studies=[];lookup={};source_records=[]
for name in SOURCES:
 p=Path('/home/rmichaelglover/Documents')/name
 source_records.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 study=[]
 with p.open() as f:
  chapter=0
  while (g:=chess.pgn.read_game(f)) is not None:
   chapter+=1
   if g.errors:raise ValueError((name,chapter,g.errors))
   identity=g.headers.get('GameId') or g.headers.get('Site','').split('/')[-1]
   reference={'file':name,'chapter':chapter,'study':g.headers.get('StudyName'),'chapter_url':g.headers.get('ChapterURL')}
   fingerprint=hashlib.sha256(' '.join(m.uci() for m in g.mainline_moves()).encode()).hexdigest()
   key=(identity,fingerprint)
   if key in lookup:
    lookup[key]['references'].append(reference);study.append(lookup[key]['id']);continue
   item={'id':identity,'headers':dict(g.headers),'references':[reference],'game':g,'index':len(allgames)+1}
   lookup[key]=item;allgames.append(item);study.append(identity)
 studies.append({'name':g.headers.get('StudyName') if g else reference['study'],'file':name,'chapters':chapter,'ids':study})

completed={g['id']:g for g in json.loads((OUT/'games.json').read_text())} if (OUT/'games.json').exists() else {}
start=time.time()
with chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish',timeout=15) as engine:
 engine.configure({'Threads':1,'Hash':64})
 meta={'engine':engine.id,'nodes_per_position':NODES,'source_files':source_records,'studies':studies,
       'unique_games':len(allgames),'chapters':sum(s['chapters'] for s in studies),
       'framework_originator':'Michael Emanuel Glover','assistant_contribution':'Operational definitions, engine screening, legal replay, aggregation and writing.'}
 (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
 for item in allgames:
  if item['id'] in completed:
   item.pop('game');item.update(completed[item['id']]);continue
  g=item.pop('game');b=g.board();item['engine_supported']=b.uci_variant=='chess';own=chess.WHITE if g.headers['White']=='mannyfresher' else chess.BLACK
  item['michael_color']='White' if own else 'Black'
  result=g.headers.get('Result');item['outcome']='Draw' if result=='1/2-1/2' else 'Win' if result==('1-0' if own else '0-1') else 'Loss' if result in ('1-0','0-1') else 'Unfinished'
  engine.configure({'Clear Hash':None})
  scores=[evaluation(engine,b)];moves=[];chases=[];q_moves=[];own_queen_lost=[]
  identities={sq:[sq,0] for sq in b.piece_map()}
  for node in g.mainline():
   m=node.move;side=b.turn;piece=chess.Piece(m.drop,side) if m.drop else b.piece_at(m.from_square);ply=b.ply()+1
   prefix=f'{b.fullmove_number}{"." if side else "..."}';san=b.san(m)
   entry={'ply':ply,'move':prefix+san,'san':san,'uci':m.uci(),'side':'White' if side else 'Black',
          'michael':side==own,'capture':b.is_capture(m),'check':b.gives_check(m),'piece':piece.symbol(),
          'clock':node.clock(),'fen_before':b.fen()}
   token=identities.get(m.from_square,[m.from_square,0]);entry['piece_prior_moves']=token[1]
   queen=b.king(own) # overwritten explicitly; queen is allowed to be absent.
   queen=next(iter(b.pieces(chess.QUEEN,own)),None)
   old_attackers=set(b.attackers(side,queen)) if queen is not None and side!=own else set()
   if side==own and piece.piece_type==chess.QUEEN:q_moves.append({'move':entry['move'],'ply':ply,'own_move_number':b.fullmove_number,'forcing':entry['capture'] or entry['check']})
   if side!=own and queen is not None and m.to_square==queen:own_queen_lost.append(entry['move'])
   identities.pop(m.to_square,None);identities.pop(m.from_square,None);identities[m.to_square]=[token[0],token[1]+1]
   b.push(m)
   if side!=own and queen is not None and b.piece_at(queen)==chess.Piece(chess.QUEEN,own):
    attackers=set(b.attackers(side,queen))
    if attackers and attackers-old_attackers:
     kind='minor-piece development' if piece.piece_type in [chess.KNIGHT,chess.BISHOP] and token[1]==0 else 'pawn commitment' if piece.piece_type==chess.PAWN else 'repeat-piece move' if token[1]>0 else 'other piece move'
     chases.append({'ply':ply,'move':entry['move'],'kind':kind,'first_20_moves':int(prefix.rstrip('.'))<=20,'new_attackers':[chess.square_name(x) for x in sorted(attackers-old_attackers)]})
   moves.append(entry);scores.append(evaluation(engine,b))
  item.update({'plies':len(moves),'moves':moves,'evaluations':scores,'queen_moves':q_moves,'chases':chases,'queen_captures_by_opponent':own_queen_lost,'final_fen':b.fen(),'checkmate':b.is_checkmate()})
  for i,m in enumerate(moves):
   before=scores[i]['cp_white'];after=scores[i+1]['cp_white'];m['swing_for_michael']=(after-before)*(1 if own else -1)
   m['swing_for_mover']=(after-before)*(1 if m['side']=='White' else -1)
  for c in chases:c['swing_for_michael']=moves[c['ply']-1]['swing_for_michael']
  early=[c for c in chases if c['first_20_moves']]
  item['early_queen']=bool(q_moves and q_moves[0]['own_move_number']<=10)
  item['early_chases']=early
  item['opening_cp_for_michael']=scores[min(len(moves),20)]['cp_white']*(1 if own else -1)
  ownerrors=sorted([m for m in moves if m['michael']],key=lambda m:m['swing_for_michael'])
  chances=sorted([m for m in moves if not m['michael']],key=lambda m:-m['swing_for_michael'])
  item['largest_own_setback']=ownerrors[0] if ownerrors else None
  item['largest_opponent_concession']=chances[0] if chances else None
  (OUT/'games.json').write_text(json.dumps(allgames[:item['index']],indent=2))
  print(f"{item['index']}/{len(allgames)} {item['id']} {item['michael_color']} {item['outcome']} {item['plies']} plies ({time.time()-start:.1f}s)",flush=True)
print('DONE',flush=True)
