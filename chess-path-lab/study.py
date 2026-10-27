from pathlib import Path
import json,time,importlib.metadata
import chess,chess.pgn
from PIL import Image
from paths import solve,endpoint_bound,budget
from tracking import observations,evaluate_tracking,observed_squares
ROOT=Path(__file__).resolve().parent

def main():
 with (ROOT/'witness.pgn').open() as f:game=chess.pgn.read_game(f)
 assert not game.errors
 boards=[game.board()];b=game.board();moves=list(game.mainline_moves())
 for move in moves:assert move in b.legal_moves;b.push(move);boards.append(b.copy(stack=False))
 frames,keys,truth=observations(game);metrics,geometry,constrained=evaluate_tracking(frames,keys,truth,game)
 print('Tracking',metrics,flush=True)
 for idx in [0,len(frames)//2,len(frames)-1]:Image.fromarray(frames[idx]).save(ROOT/f'frame-{idx}.png')
 small=[Image.fromarray(frames[i]).resize((256,256)) for i in range(len(frames))]
 small[0].save(ROOT/'tracking.gif',save_all=True,append_images=small[1:],duration=65,loop=0)
 results=[]
 for start,depth in [(0,4),(8,3),(20,3),(38,3),(len(moves)-4,4)]:
  for method in ['legal','material','bound']:
   record={'start_ply':start,'end_ply':start+depth,'start_fen':boards[start].fen(),'target_fen':boards[start+depth].fen(),'witness_uci':[m.uci() for m in moves[start:start+depth]],**solve(boards[start],boards[start+depth],depth,method)}
   results.append(record);print('Search',start,depth,method,record['nodes'],record['paths'],record['complete'],round(record['seconds'],2),flush=True)
  completed=[r['paths'] for r in results if r['start_ply']==start and r['complete']];assert len(set(completed))<=1
  midpoint=depth//2
  if len(constrained[start+midpoint])==1:
   checkpoint=constrained[start+midpoint][0][0]
   results.append({'start_ply':start,'end_ply':start+depth,**solve(boards[start],boards[start+depth],depth,'bound',checkpoints={midpoint:checkpoint}),'method':'bound+observed-midpoint'})
 # Observed identities are measurements, not assumptions about every endpoint-compatible path.
 endpoints=[]
 for ply in range(len(moves)+1):
  geo={i:xy.tolist() for i,xy in geometry[keys[ply]].items()}
  endpoints.append({'observed':{('white' if c else 'black'):[chess.square_name(s) for s in sorted(squares)] for c,squares in observed_squares(frames[keys[ply]]).items()},'ply':ply,'fen':boards[ply].fen(),'truth_ids':{chess.square_name(s):i for s,i in truth[ply].items()},'geometry_tracks':geo,'legal_hypotheses':len(constrained[ply]),'legal_ids':{chess.square_name(s):i for s,i in constrained[ply][0][1].items()} if len(constrained[ply])==1 else None})
 payload={'game':dict(game.headers),'tracking':metrics,'searches':results,'positions':endpoints,'environment':{n:importlib.metadata.version(n) for n in ['chess','numpy','scipy','Pillow']}}
 (ROOT/'results.json').write_text(json.dumps(payload,indent=2)+'\n')
if __name__=='__main__':main()
