from pathlib import Path
import json,chess,chess.pgn,chess.engine,time
OUT=Path(__file__).parent
p=OUT/'games.json';games=json.loads(p.read_text())
for g in games:
 first=g['queen_moves'][0]['ply'] if g['queen_moves'] else 100000
 g['engine_supported']=g['headers'].get('Variant','Standard')!='Crazyhouse'
 g['chases']=[c for c in g['chases'] if c['ply']>first]
 for c in g['chases']:
  m=g['moves'][c['ply']-1];c['checking_move']=m['check'];c['capturing_move']=m['capture']
  response=g['moves'][c['ply']] if c['ply']<len(g['moves']) else None
  c['response']=response['move'] if response else None
  c['queen_answer']=bool(response and response['michael'] and response['piece'].upper()=='Q')
  c['forcing_queen_answer']=bool(c['queen_answer'] and (response['capture'] or response['check']))
 g['early_chases']=[c for c in g['chases'] if c['first_20_moves']]
p.write_text(json.dumps(games,indent=2))
start=time.time()
def ev(e,b):
 if b.is_game_over(claim_draw=False):
  o=b.outcome();return {'cp_white':0 if o.winner is None else 10000 if o.winner else -10000,'display':'terminal','pv':''}
 r=e.analyse(b,chess.engine.Limit(nodes=200000));v=r['score'].white();bb=b.copy();pv=[]
 for m in r.get('pv',[])[:5]:pv.append(f'{bb.fullmove_number}{"." if bb.turn else "..."}{bb.san(m)}');bb.push(m)
 return {'cp_white':v.score(mate_score=10000),'display':str(v),'pv':' '.join(pv),'depth':r.get('depth'),'nodes':r.get('nodes')}
with chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish',timeout=15) as e:
 e.configure({'Threads':1,'Hash':64})
 for i,g in enumerate(games):
  if not g['engine_supported'] or g['plies']<3 or g.get('refinements'):continue
  candidates={g['largest_own_setback']['ply'],g['largest_opponent_concession']['ply']}
  if g['early_chases']:candidates.add(max(g['early_chases'],key=lambda c:c['swing_for_michael'])['ply'])
  ref=g['references'][0]
  with (Path('/home/rmichaelglover/Documents')/ref['file']).open() as f:
   for _ in range(ref['chapter']):original=chess.pgn.read_game(f)
  b=original.board();own=g['michael_color']=='White';refinements={}
  for ply,m in enumerate(original.mainline_moves(),1):
   if ply in candidates:
    before=ev(e,b);b.push(m);after=ev(e,b)
    refinements[str(ply)]={'before':before,'after':after,'swing_for_michael':(after['cp_white']-before['cp_white'])*(1 if own else -1)}
   else:b.push(m)
  g['refinements']=refinements
  if i%5==0:print(f"Deeper checks {i+1}/{len(games)} ({time.time()-start:.1f}s)",flush=True)
  p.write_text(json.dumps(games,indent=2))
print('DEEP CHECKS DONE',flush=True)
