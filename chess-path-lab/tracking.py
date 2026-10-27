"""Rasterize a legal witness, then track anonymous colored centers without PGN moves."""
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,center_of_mass
from scipy.optimize import linear_sum_assignment
import chess
COLORS={True:(35,135,220),False:(231,147,42)}
CELL=40

def centers(square):return np.array([(chess.square_file(square)+.5)*CELL,(7-chess.square_rank(square)+.5)*CELL])
def initial_ids(board):return {s:('w' if p.color else 'b')+p.symbol().upper()+'@'+chess.square_name(s) for s,p in board.piece_map().items()}
def advance(board,ids,move):
 ids=ids.copy();who=ids.pop(move.from_square)
 if board.is_en_passant(move):ids.pop(move.to_square+(-8 if board.turn else 8))
 ids.pop(move.to_square,None)
 if board.is_castling(move):
  rank=chess.square_rank(move.from_square);right=chess.square_file(move.to_square)>4
  rook=chess.square(7 if right else 0,rank);dest=chess.square(5 if right else 3,rank);ids[dest]=ids.pop(rook)
 ids[move.to_square]=who;return ids

def render(positions):
 im=Image.new('RGB',(320,320));d=ImageDraw.Draw(im)
 for r in range(8):
  for c in range(8):d.rectangle([c*CELL,r*CELL,(c+1)*CELL-1,(r+1)*CELL-1],fill=(236,240,233) if (r+c)%2 else (208,219,203))
 for ident,xy in positions.items():
  x,y=xy;d.ellipse((x-6,y-6,x+6,y+6),fill=COLORS[ident.startswith('w')])
 return np.array(im)
def detect(frame):
 result={}
 for color,rgb in COLORS.items():
  mask=np.all(frame==rgb,axis=2);components,n=label(mask);result[color]=np.array([(p[1],p[0]) for p in center_of_mass(mask,components,range(1,n+1))]).reshape(-1,2)
 return result

def observations(game,steps=8):
 board=game.board();ids=initial_ids(board);frames=[render({i:centers(s) for s,i in ids.items()})];keys=[0];truth=[ids.copy()]
 for move in game.mainline_moves():
  nxt=advance(board,ids,move);old={i:centers(s) for s,i in ids.items()};new={i:centers(s) for s,i in nxt.items()}
  for k in range(1,steps+1):
   fraction=k/steps;positions={i:old.get(i,xy)*(1-fraction)+xy*fraction for i,xy in new.items()}
   if k<steps:positions.update({i:xy for i,xy in old.items() if i not in new})
   frames.append(render(positions))
  board.push(move);ids=nxt;keys.append(len(frames)-1);truth.append(ids.copy())
 return frames,keys,truth

def geometry_track(frames,start_ids):
 tracks={i:{'xy':centers(s),'missed':0} for s,i in start_ids.items()}
 history=[]
 for frame in frames:
  obs=detect(frame)
  for color in chess.COLORS:
   names=[i for i in tracks if i.startswith('w' if color else 'b')];points=obs[color];matched=set()
   if names and len(points):
    cost=np.linalg.norm(np.array([tracks[i]['xy'] for i in names])[:,None,:]-points[None,:,:],axis=2);rows,cols=linear_sum_assignment(cost)
    for r,c in zip(rows,cols):
     if cost[r,c]<=50:tracks[names[r]]={'xy':points[c],'missed':0};matched.add(names[r])
   for i in names:
    if i not in matched:tracks[i]['missed']+=1
   for i in names:
    if tracks[i]['missed']>2:del tracks[i]
  history.append({i:t['xy'].copy() for i,t in tracks.items() if t['missed']==0})
 return history

def observed_squares(frame):
 out={}
 for c,points in detect(frame).items():
  out[c]=set(chess.square(int(p[0]//CELL),7-int(p[1]//CELL)) for p in points)
 return out

def constrained_track(frames,keys,start):
 # The tracker receives initial state and rendered keyframes, never witness moves.
 hypotheses=[(start.copy(stack=False),initial_ids(start))];history=[hypotheses]
 for index in keys[1:]:
  obs=observed_squares(frames[index]);new=[]
  for board,ids in hypotheses:
   for move in list(board.legal_moves):
    nxt=board.copy(stack=False);nxt_ids=advance(board,ids,move);nxt.push(move)
    if all(set(chess.SquareSet(nxt.occupied_co[c]))==obs[c] for c in chess.COLORS):new.append((nxt,nxt_ids))
  # Retain distinct identities as well as board states; ambiguity is not silently resolved.
  unique={ (b.fen(),tuple(sorted(ids.items()))):(b,ids) for b,ids in new};hypotheses=list(unique.values());history.append(hypotheses)
  if len(hypotheses)>4096:raise RuntimeError('Observation hypotheses exceed tracking cap')
 return history

def evaluate_tracking(frames,keys,truth,game):
 geom=geometry_track(frames,truth[0]);con=constrained_track(frames,keys,game.board());correct=0;total=0
 for frame_idx,expected in zip(keys,truth):
  inferred={}
  for i,xy in geom[frame_idx].items():
   sq=chess.square(min(7,max(0,int(xy[0]//CELL))),7-min(7,max(0,int(xy[1]//CELL))));inferred[sq]=i
  total+=len(expected);correct+=sum(inferred.get(s)==i for s,i in expected.items())
 unique_correct=sum(len(h)==1 and h[0][1]==ids for h,ids in zip(con,truth))
 return {'rendered_frames':len(frames),'keyframes':len(keys),'geometry_correct_identity_assignments':correct,'visible_identity_assignments':total,'geometry_identity_accuracy':correct/total,'constraint_unique_correct_keyframes':unique_correct,'constraint_keyframes':len(keys),'max_constraint_hypotheses':max(map(len,con)),'constraint_true_identity_retained':all(any(candidate==ids for _,candidate in h) for h,ids in zip(con,truth))},geom,con
