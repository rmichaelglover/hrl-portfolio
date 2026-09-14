"""Author and verify the bounded lesson tree. Build dependency: python-chess.
No game engine, package download, or network request is used by the browser.
"""
import json
from pathlib import Path
import chess
HERE = Path(__file__).parent
specs = [
 dict(id='defender',skill='defense',title='The offered rook',fen='4r1k1/5ppp/8/8/r7/8/5PPP/3Q2K1 w - - 0 1',line=['d1a4','e8e1'],take=False,
 prompt='Your queen can take the rook on a4. Would you accept?',question='After Qxa4, which reply must you notice?',
 options=['Re1#: the rook reaches the back rank.','h6: Black makes a pawn move.','Kf8: Black moves the king.'],answer=0,
 hint='Your queen has a defensive job on the first rank. What happens when it leaves?',
 explanation='Qxa4 wins a rook but removes the queen from d1. Black plays Re1 checkmate. The pawns block the king from escaping. The immediate mate outweighs the material gain.',
 takeaway='Before moving a defender, name the square or line it protects.',checks=['e8e1','h7h6','g8f8']),
 dict(id='recapture',skill='count',title='The pawn on the open file',fen='3r2k1/5ppp/8/3p4/8/8/5PPP/3Q2K1 w - - 0 1',line=['d1d5','d8d5'],take=False,
 prompt='Your queen can take the pawn on d5. Would you accept?',question='After Qxd5 Rxd5, what did the capturing side gain or lose?',
 options=['Gained 1 point.','Lost 8 points: queen for pawn.','An equal exchange.'],answer=1,
 hint='Follow the d-file beyond the pawn. Count both captures: pawn = 1, queen = 9.',
 explanation='The first capture wins a pawn, but the rook then takes the queen. That is 1 gained and 9 lost: a net loss of 8 material points. This lesson only needs the immediate recapture.',
 takeaway='Count the complete visible exchange, not just its first move.',checks=[]),
 dict(id='free',skill='reply',title='The bishop in the center',fen='6k1/5ppp/8/4b3/8/8/5PPP/4R1K1 w - - 0 1',line=['e1e5','h7h6'],take=True,
 prompt='Your rook can take the bishop on e5. Would you accept?',question='After Rxe5, which description fits Black\'s immediate legal replies?',
 options=['Black can recapture the rook immediately.','Black has mate in one.','Black has no check or capture; you won a bishop.'],answer=2,
 hint='Check every black piece, including the king and pawns. What could take e5 or check your king?',
 explanation='Rxe5 wins the undefended bishop. Black has no immediate legal check or capture. The replay shows h6 as one quiet reply, not a uniquely best move. For this short-horizon exercise, accept the bishop.',
 takeaway='When no concrete immediate refutation appears, do not invent a trap.',checks=[]),
]
lessons=[]
def material(b,color):
 return sum(len(b.pieces(p,color))*v for p,v in [(chess.PAWN,1),(chess.KNIGHT,3),(chess.BISHOP,3),(chess.ROOK,5),(chess.QUEEN,9)])
for spec in specs:
 for mirror in [False,True]:
  d={k:v for k,v in spec.items() if k not in ('checks','line')}
  b=chess.Board(spec['fen']);assert b.is_valid(),spec['id']
  if mirror:b=b.mirror()
  mover=b.turn;initial=material(b,mover)-material(b,not mover)
  moves=[chess.Move.from_uci(m) for m in spec['line']]
  if mirror:moves=[chess.Move(chess.square_mirror(m.from_square),chess.square_mirror(m.to_square)) for m in moves]
  d['id']+= '-black' if mirror else '-white';d['side']='Black' if mirror else 'White'
  d['frames']=[b.fen()];d['moves']=[]
  for i,m in enumerate(moves):
   assert m in b.legal_moves,(d['id'],m)
   d['moves'].append({'uci':m.uci(),'san':b.san(m)});b.push(m);d['frames'].append(b.fen())
   if i==0:
    if spec['id']=='free':assert not any(b.is_capture(r) or b.gives_check(r) for r in b.legal_moves)
    for uci in spec['checks']:
     r=chess.Move.from_uci(uci)
     if mirror:r=chess.Move(chess.square_mirror(r.from_square),chess.square_mirror(r.to_square))
     assert r in b.legal_moves
  if spec['id']=='defender':assert b.is_checkmate()
  if spec['id']=='recapture':assert material(b,mover)-material(b,not mover)-initial==-8
  if spec['id']=='free':assert material(b,mover)-material(b,not mover)-initial==3
  if mirror:
   d['title']+=' (Black to move)'
   if spec['id']=='defender':
    d.update(prompt='Your queen can take the rook on a5. Would you accept?',question='After Qxa5, which reply must you notice?',options=['Re8#: the rook reaches the back rank.','h3: White makes a pawn move.','Kf1: White moves the king.'],hint='Your queen has a defensive job on the eighth rank. What happens when it leaves?',explanation='Qxa5 wins a rook but removes the queen from d8. White plays Re8 checkmate. The pawns block your king from escaping. The immediate mate outweighs the material gain.')
   if spec['id']=='recapture':
    d.update(prompt='Your queen can take the pawn on d4. Would you accept?',question='After Qxd4 Rxd4, what did the capturing side gain or lose?',explanation=spec['explanation'])
   if spec['id']=='free':
    d.update(prompt='Your rook can take the bishop on e4. Would you accept?',question="After Rxe4, which description fits White's immediate legal replies?",options=['White can recapture the rook immediately.','White has mate in one.','White has no check or capture; you won a bishop.'],hint='Check every white piece, including the king and pawns. What could take e4 or check your king?',explanation='Rxe4 wins the undefended bishop. White has no immediate legal check or capture. The replay shows h3 as one quiet reply, not a uniquely best move. For this short-horizon exercise, accept the bishop.')
  d['fen']=d['frames'][0];lessons.append(d)
(HERE/'lessons.js').write_text('/* Generated by build_lessons.py; authored positions, not historical games. */\nglobalThis.CaptureLessons = '+json.dumps(lessons,indent=2)+';\n')
print(f'Verified {len(lessons)} legal positions and lines, both mates, material losses, and safe-capture replies.')
