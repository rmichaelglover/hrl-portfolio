from pathlib import Path
import json,chess,chess.pgn,collections
O=Path(__file__).parent;games=json.loads((O/'games.json').read_text())
for g in games:
 ref=g['references'][0]
 with (Path('/home/rmichaelglover/Documents')/ref['file']).open() as f:
  for _ in range(ref['chapter']):game=chess.pgn.read_game(f)
 b=game.board();g['initial_fen']=b.fen();g['custom_start']=g['headers'].get('Variant')=='From Position';own=g['michael_color']=='White';firstq=g['queen_moves'][0]['ply'] if g['queen_moves'] else 100000;chases=[]
 for entry in g['moves']:
  move=chess.Move.from_uci(entry['uci']);side=b.turn;queen=b.queen if False else next(iter(b.pieces(chess.QUEEN,own)),None)
  def legal_attackers(board,target,color):
   if target is None:return set()
   probe=board.copy();probe.turn=color
   return {sq for sq in board.attackers(color,target) if probe.is_legal(chess.Move(sq,target))}
  old=legal_attackers(b,queen,side) if side!=own else set()
  b.push(move)
  if side!=own and entry['ply']>firstq and queen is not None and b.piece_at(queen)==chess.Piece(chess.QUEEN,own):
   attacks=legal_attackers(b,queen,side)
   if attacks-old:
    piece=entry['piece'].upper();kind='piece drop' if move.drop else 'minor-piece development' if piece in ['N','B'] and entry['piece_prior_moves']==0 else 'pawn commitment' if piece=='P' else 'repeat-piece move' if entry['piece_prior_moves']>0 else 'other piece move'
    following=g['moves'][entry['ply']] if entry['ply']<len(g['moves']) else None
    qanswer=bool(following and following['piece'].upper()=='Q')
    chases.append({'ply':entry['ply'],'move':entry['move'],'kind':kind,'first_20_moves':int(entry['move'].split('.')[0])<=20,
      'checking_move':entry['check'],'capturing_move':entry['capture'],'response':following['move'] if following else None,
      'queen_answer':qanswer,'forcing_queen_answer':bool(qanswer and (following['capture'] or following['check'])),
      'swing_for_michael':entry['swing_for_michael'],'new_attackers':[chess.square_name(s) for s in sorted(attacks-old)]})
 g['chases']=chases;g['early_chases']=[c for c in chases if c['first_20_moves']]
 def early(m):return int(m['move'].split('.')[0])<=10
 g['queen_moves_first10']=[m for m in g['queen_moves'] if m['own_move_number']<=10]
 g['own_minor_development_first10']=[m['move'] for m in g['moves'] if m['michael'] and early(m) and m['piece'].upper() in ['B','N'] and m['piece_prior_moves']==0]
 g['opponent_minor_development_first10']=[m['move'] for m in g['moves'] if not m['michael'] and early(m) and m['piece'].upper() in ['B','N'] and m['piece_prior_moves']==0]
 g['early_uncastled_king_moves']=[m['move'] for m in g['moves'] if m['michael'] and early(m) and m['piece'].upper()=='K' and not m['san'].startswith('O-O')]
(O/'games.json').write_text(json.dumps(games,indent=2))
counts=collections.Counter(g['outcome'] for g in games)
qs=[g for g in games if g['early_queen']];episodes=[c for g in games for c in g['early_chases']]
stats={'unique_games':len(games),'outcomes':dict(counts),'early_queen_games':len(qs),'early_queen_results':dict(collections.Counter(g['outcome'] for g in qs)),
 'queen_first5_games':sum(bool(g['queen_moves'] and g['queen_moves'][0]['own_move_number']<=5) for g in games),
 'queen_pressure_games':sum(bool(g['early_chases']) for g in games),'early_queen_pressure_games':sum(bool(g['early_chases']) for g in qs),
 'queen_pressure_episodes':len(episodes),'episode_kinds':dict(collections.Counter(c['kind'] for c in episodes)),
 'queen_answers':sum(c['queen_answer'] for c in episodes),'forcing_queen_answers':sum(c['forcing_queen_answer'] for c in episodes),
 'checking_queen_pressure_episodes':sum(c['checking_move'] for c in episodes),
 'early_king_move_games':sum(bool(g['early_uncastled_king_moves']) for g in games),
 'standard_games':sum(g['engine_supported'] for g in games),'crazyhouse_games':sum(not g['engine_supported'] for g in games)}
(O/'summary.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
