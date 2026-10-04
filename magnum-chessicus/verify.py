"""Read-only replay of exported fixture certificates; does not rerun search."""
from pathlib import Path
import json,copy
import chess
B=Path(__file__).resolve().parent
def check(c):
    b=chess.Board(c['root_fen'])
    assert b.is_valid()
    if c['name']=='White mate in one':
        assert b.turn==chess.WHITE and c['lower']==c['upper']==1
        m=chess.Move.from_uci(c['lower_witness']);assert m in b.legal_moves
        b.push(m);assert b.turn==chess.BLACK and b.is_checkmate()
    elif c['name']=='Stalemate':
        assert b.is_stalemate() and c['lower']==c['upper']==0
    elif c['name']=='Kings only':
        assert len(b.piece_map())==2 and b.kings.bit_count()==2 and c['lower']==c['upper']==0
    else:raise AssertionError('Unknown certificate form')
    return True
certs=json.loads((B/'data/certificates.json').read_text())
for c in certs:assert check(c)
bad=copy.deepcopy(certs[0]);bad['lower_witness']='g6g5'
try:check(bad)
except AssertionError:pass
else:raise AssertionError('False certificate accepted')
r=json.loads((B/'results.json').read_text())
assert not r['initial_position_solved']
assert [x['frontiers'] for x in r['initial_search']]==[1,20,400,8902]
assert all(x['lower']==-1 and x['upper']==1 for x in r['initial_search'])
assert r['fools_mate']['probability_exact']=='1/228000'
print('PASS: three fixture certificates replayed; corrupted witness rejected; initial root remains unresolved.')
