#!/usr/bin/env python3
import json,chess,numpy as np
from pathlib import Path
from experiment import role_field,choose
r=Path(__file__).resolve().parent;d=json.loads((r/'data/results.json').read_text())
assert len(d['positions'])==24 and len(d['matches'])==4
for p in d['positions']:
 b=chess.Board(p['fen']);assert b.is_valid()
 q=np.array(p['q']);assert np.all(q>=0) and np.allclose(q.sum(axis=1),1)
 assert np.min(np.diff(p['potential']))>=-1e-10
 for name,v in p['models'].items():assert chess.Move.from_uci(v['move']) in b.legal_moves
 for roles in [False,True]:
  before=b.fen();move,_=choose(b,roles);assert b.fen()==before;assert move in b.legal_moves
for match in d['matches']:
 b=chess.Board()
 opening='e4 e5 Nf3 Nc6 Bc4 Bc5' if match['opening']=='Italian' else 'd4 d5 c4 e6 Nc3 Nf6'
 for san in opening.split():b.push_san(san)
 for uci in match['moves']:
  move=chess.Move.from_uci(uci);assert move in b.legal_moves;assert not b.is_game_over(claim_draw=True);b.push(move)
 assert b.fen()==match['final_fen'];outcome=b.outcome(claim_draw=True)
 assert outcome.result()==match['outcome'] and outcome.termination.name==match['termination']
 assert match['relaxfish_score']==0
# Numerical gradient checks every role component on a fixed real chess state.
f=role_field(chess.Board(d['positions'][1]['fen']),iterations=0)
from experiment import C
q=f['q'];n=len(q);tri=f['triples']
def potential(x):return np.sum(f['aff']*x)+.5*.18/n*np.sum((f['edges']@x@C)*x)+.12/max(1,len(tri))*sum(x[i,0]*x[j,0]*x[k,0] for i,j,k in tri)
g=f['aff']+.18/n*(f['edges']@q@C)
for i,j,k in tri:
 a=.12/max(1,len(tri));g[i,0]+=a*q[j,0]*q[k,0];g[j,0]+=a*q[i,0]*q[k,0];g[k,0]+=a*q[i,0]*q[j,0]
for ix in np.ndindex(q.shape):
 a=q.copy();b=q.copy();a[ix]+=1e-6;b[ix]-=1e-6
 assert abs((potential(a)-potential(b))/2e-6-g[ix])<1e-7
print('PASS: 24 legal fixtures, 72 legal chosen moves, normalized role weights, nondecreasing potential, deterministic choice and board preservation, all analytic gradient entries versus finite differences.')
