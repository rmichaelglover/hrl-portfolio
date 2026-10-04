#!/usr/bin/env python3
"""Relaxfish pilot: executable role relaxation, paired ablation, versioned reference.
This diagnostic is not a tournament or a claim of superiority over Stockfish.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import chess, chess.engine, numpy as np, json, time, platform, hashlib, csv
from pathlib import Path
from itertools import combinations
ROOT=Path(__file__).resolve().parent; (ROOT/'data').mkdir(exist_ok=True)
ROLES=['attacker','defender','controller','outpost','runner','tactician','idle']
VAL={1:100,2:320,3:330,4:500,5:900,6:0}
C=np.full((7,7),.05);C[6,:]=0;C[:,6]=0
for i,j,w in [(0,0,.8),(0,2,.5),(1,1,.5),(4,2,.3),(4,0,.3),(3,0,.3),(5,0,.4)]: C[i,j]=C[j,i]=w
C[2,2]=0

def role_field(board,iterations=12,lam2=.18,lam3=.12):
    squares=sorted(board.piece_map());pieces=[board.piece_at(s) for s in squares];n=len(squares)
    if not n:return {'q':np.zeros((0,7)),'potential':[0.],'entropy':[0.],'score':0.,'squares':[],'aff':np.zeros((0,7)),'edges':np.zeros((0,0)),'triples':[]}
    attacks=[set(board.attacks(s)) for s in squares]
    zones={c:set(chess.SquareSet(chess.BB_KING_ATTACKS[board.king(c)]))|{board.king(c)} for c in [True,False]}
    pawn={c:set().union(*(attacks[i] for i,p in enumerate(pieces) if p.color==c and p.piece_type==1)) for c in [True,False]}
    aff=np.full((n,7),.02);edges=np.zeros((n,n));triples=[]
    for i,(s,p,cs) in enumerate(zip(squares,pieces,attacks)):
        f,r=chess.square_file(s),chess.square_rank(s);own=p.color;enemy=not own
        aff[i,0]+=min(1.,.35*len(cs&zones[enemy]))
        aff[i,1]+=min(1.,.14*len(cs&zones[own])+(.35 if p.piece_type==6 else 0))
        aff[i,2]+=min(1.,len(cs)/20.) if p.piece_type in [3,4,5] else .05
        if p.piece_type in [2,3] and ((own and r>=4) or (not own and r<=3)) and s not in pawn[enemy]:aff[i,3]+=.6+(.2 if s in pawn[own] else 0)
        if p.piece_type==1:
            ahead=[e for e in board.pieces(1,enemy) if abs(chess.square_file(e)-f)<=1 and ((own and chess.square_rank(e)>r) or (not own and chess.square_rank(e)<r))]
            aff[i,4]+=min(1.,.10*(r-1 if own else 6-r)+(.4 if not ahead else 0))
        targets=[board.piece_at(e) for e in cs if board.piece_at(e) and board.piece_at(e).color==enemy and board.piece_at(e).piece_type!=6]
        aff[i,5]+=min(1.,.25*len(targets)+(.5 if board.is_pinned(enemy,s) else 0))
        aff[i,6]+=.3 if len(cs)<=3 and max(aff[i,:6])<.25 else .02
        for j in range(i):
            if pieces[j].color==own:
                distance=chess.square_distance(s,squares[j]);edges[i,j]=edges[j,i]=1. if squares[j] in cs or s in attacks[j] else (.6 if distance<=3 else .2)
    for color in [True,False]:
        idx=[i for i,p in enumerate(pieces) if p.color==color and attacks[i]&zones[not color]]
        triples+=list(combinations(idx,3))
    # Normalize incoming pair and triple support by n and actual triple count.
    def potential(q):
        pair=.5*lam2/max(1,n)*np.sum((edges@q@C)*q)
        tri=lam3/max(1,len(triples))*sum(q[i,0]*q[j,0]*q[k,0] for i,j,k in triples)
        return float(np.sum(aff*q)+pair+tri)
    q=aff/aff.sum(axis=1,keepdims=True);trace=[potential(q)];ent=[float(-np.sum(q*np.log(q))/n)]
    for _ in range(iterations):
        support=aff+lam2/max(1,n)*(edges@q@C)
        for i,j,k in triples:
            factor=lam3/max(1,len(triples));support[i,0]+=factor*q[j,0]*q[k,0];support[j,0]+=factor*q[i,0]*q[k,0];support[k,0]+=factor*q[i,0]*q[j,0]
        eta=1.
        for _ in range(24):
            candidate=q*np.exp(eta*(support-support.max(axis=1,keepdims=True)));candidate/=candidate.sum(axis=1,keepdims=True)
            if potential(candidate)>=trace[-1]-1e-12:break
            eta*=.5
        else:candidate=q
        q=candidate;trace.append(potential(q));ent.append(float(-np.sum(q*np.log(np.maximum(q,1e-300)))/n))
    weights=np.array([.8,.7,.45,.55,.9,1.,-.3]);score=sum((1 if p.color else -1)*float(q[i]@weights) for i,p in enumerate(pieces))*18.
    return {'q':q,'potential':trace,'entropy':ent,'score':score,'squares':squares,'aff':aff,'edges':edges,'triples':triples}

def static(board):
    score=0.
    for s,p in board.piece_map().items():
        f,r=chess.square_file(s),chess.square_rank(s);central=3.5-abs(f-3.5)+3.5-abs(r-3.5)
        positional=3*central if p.piece_type in [2,3] else 2*(r if p.color else 7-r) if p.piece_type==1 else 0
        score+=(1 if p.color else -1)*(VAL[p.piece_type]+positional)
    return score

def choose(board,use_roles=True,depth=1):
    started=time.perf_counter();nodes=0
    def visit(d):
        nonlocal nodes
        nodes+=1
        terminal=board.outcome(claim_draw=True)
        if terminal:return 0. if terminal.winner is None else (100000 if terminal.winner else -100000)
        if d==0:return static(board)+(role_field(board)['score'] if use_roles else 0)
        vals=[]
        for move in sorted(board.legal_moves,key=lambda m:m.uci()):board.push(move);vals.append(visit(d-1));board.pop()
        return (max if board.turn else min)(vals)
    choices=[]
    for move in sorted(board.legal_moves,key=lambda m:m.uci()):board.push(move);value=visit(depth-1);board.pop();choices.append((move,value))
    move,value=(max if board.turn else min)(choices,key=lambda x:x[1])
    return move,{'nodes':nodes,'seconds':time.perf_counter()-started,'value':value}

def suite():
    openings=[('Italian','e4 e5 Nf3 Nc6 Bc4 Bc5'),('Sicilian','e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6'),('French','e4 e6 d4 d5 Nc3 Bb4'),('Caro-Kann','e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5'),('Queens-Gambit','d4 d5 c4 e6 Nc3 Nf6'),('Kings-Indian','d4 Nf6 c4 g6 Nc3 Bg7 e4 d6'),('English','c4 e5 Nc3 Nf6 g3 d5'),('Reti','Nf3 d5 g3 c5 Bg2 Nc6')]
    result=[]
    for name,line in openings:
        b=chess.Board()
        for san in line.split():b.push_san(san)
        result.append((name,'opening',b))
    rng=np.random.default_rng(20261003)
    for idx in range(8):
        b=chess.Board()
        for _ in range(24+idx*2):
            if b.is_game_over():break
            b.push(sorted(b.legal_moves,key=lambda m:m.uci())[int(rng.integers(b.legal_moves.count()))])
        if b.is_game_over():raise RuntimeError('Generated terminal fixture')
        result.append((f'Legal-random-{idx+1}','middlegame',b))
    endings=['7k/8/5KQ1/8/8/8/8/8 w - - 0 1','8/8/8/8/8/5kq1/8/7K b - - 0 1','7k/8/6P1/5K2/8/8/8/8 w - - 0 1','8/8/8/8/5k2/6p1/8/7K b - - 0 1','8/7k/8/8/8/2K5/3R4/8 w - - 0 1','8/3r4/2k5/8/8/8/7K/8 b - - 0 1','8/4k3/8/3p4/3P4/8/4K3/8 w - - 0 1','8/4k3/8/3p4/3P4/8/4K3/8 b - - 0 1']
    for idx,fen in enumerate(endings):
        b=chess.Board(fen);assert b.is_valid() and not b.is_game_over(),fen
        result.append((f'Endgame-{idx+1}','endgame',b))
    return result

def run():
    engine=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish');engine.configure({'Threads':1,'Hash':16})
    data={'protocol':'diagnostic-v1','seed':20261003,'stockfish':engine.id,'stockfish_sha256':hashlib.sha256(Path('/usr/games/stockfish').read_bytes()).hexdigest(),'python':platform.python_version(),'platform':platform.platform(),'positions':[],'matches':[]}
    for name,category,b in suite():
        engine.configure({'Clear Hash':None});ref=engine.analyse(b,chess.engine.Limit(nodes=20000));refmove=ref['pv'][0]
        entry={'name':name,'category':category,'fen':b.fen(),'reference_move':refmove.uci(),'reference_nodes':ref.get('nodes'),'models':{}}
        candidates={}
        for model,use in [('static',False),('relaxfish',True)]:
            move,stats=choose(b,use);candidates[model]=move
            entry['models'][model]={'move':move.uci(),'agreement':move==refmove,**stats}
        engine.configure({'Clear Hash':None});small=engine.analyse(b,chess.engine.Limit(nodes=2000));entry['models']['stockfish_2k']={'move':small['pv'][0].uci(),'agreement':small['pv'][0]==refmove,'nodes':small.get('nodes'),'seconds':small.get('time',0)}
        allmoves={refmove,*candidates.values(),small['pv'][0]};scores={}
        for move in sorted(allmoves,key=lambda m:m.uci()):
            c=b.copy();c.push(move);terminal=c.outcome(claim_draw=True)
            if terminal:cp=0 if terminal.winner is None else (10000 if terminal.winner==b.turn else -10000)
            else:
                engine.configure({'Clear Hash':None});info=engine.analyse(c,chess.engine.Limit(nodes=5000));cp=info['score'].pov(b.turn).score(mate_score=10000)
            scores[move.uci()]=cp
        entry['reference_after_move_cp']=scores[refmove.uci()]
        for model,stats in entry['models'].items():stats['after_move_cp']=scores[stats['move']];stats['reference_gap_cp']=scores[refmove.uci()]-stats['after_move_cp']
        field=role_field(b);entry['potential']=field['potential'];entry['entropy']=field['entropy'];entry['q']=field['q'].tolist();entry['squares']=field['squares'];entry['triple_count']=len(field['triples'])
        data['positions'].append(entry);print(name, 'done',flush=True)
    # Small paired diagnostic, deliberately separate from fair strength testing.
    for label,line in [('Italian','e4 e5 Nf3 Nc6 Bc4 Bc5'),('Queens-Gambit','d4 d5 c4 e6 Nc3 Nf6')]:
        for hero in [True,False]:
            b=chess.Board()
            for san in line.split():b.push_san(san)
            history=[];t0=time.perf_counter()
            for ply in range(120):
                if b.is_game_over(claim_draw=True):break
                if b.turn==hero:move,_=choose(b,True)
                else:move=engine.play(b,chess.engine.Limit(nodes=1000)).move
                history.append(move.uci());b.push(move)
            outcome=b.outcome(claim_draw=True)
            data['matches'].append({'opening':label,'relaxfish_color':'white' if hero else 'black','outcome':outcome.result() if outcome else '*','termination':outcome.termination.name if outcome else 'CENSORED_120_PLY','relaxfish_score':None if not outcome else .5 if outcome.winner is None else int(outcome.winner==hero),'moves':history,'final_fen':b.fen(),'seconds':time.perf_counter()-t0})
            print('match',label,hero,data['matches'][-1]['outcome'],flush=True)
    engine.quit()
    (ROOT/'data/results.json').write_text(json.dumps(data,indent=2)+'\n')
    rows=[]
    for p in data['positions']:
        for model,v in p['models'].items():rows.append({'position':p['name'],'category':p['category'],'model':model,**v})
    with (ROOT/'data/positions.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print('SAVED',len(data['positions']),'positions',len(data['matches']),'matches')
if __name__=='__main__':run()
