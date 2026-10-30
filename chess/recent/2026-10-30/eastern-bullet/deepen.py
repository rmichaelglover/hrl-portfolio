"""Recheck selected teaching positions at a larger, fixed node budget."""
from pathlib import Path
import json
import chess,chess.engine
from analyze import pv_san,score_dict
HERE=Path(__file__).resolve().parent
requests=[(1,7),(1,15),(3,7),(3,8),(12,25),(14,38),(26,63),(28,49),(29,31)]
r=json.loads((HERE/'analysis.json').read_text());e=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish');e.configure({'Threads':1,'Hash':64})
result=[]
for number,ply in requests:
 g=r['games'][number-1];b=chess.Board()
 for m in g['moves'][:ply]:b.push_uci(m['uci'])
 infos=e.analyse(b,chess.engine.Limit(nodes=500_000),multipv=3,game=f'{number}-{ply}')
 lines=[]
 for info in infos:
  pv=info.get('pv',[])
  lines.append({**score_dict(info['score']),'depth':info['depth'],'nodes':info['nodes'],
                'uci':[m.uci() for m in pv[:12]],'san':pv_san(b,pv,12)})
 result.append({'game':number,'id':g['id'],'after_ply':ply,'fen':b.fen(),'lines':lines})
 print(number,ply,lines[0]['san'],flush=True)
e.quit();(HERE/'selected-analysis.json').write_text(json.dumps({'engine':r['engine'],'nodes_per_position':500_000,'multipv':3,'positions':result},indent=2)+'\n')
