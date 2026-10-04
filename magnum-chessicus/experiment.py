from pathlib import Path
import json,time,hashlib,importlib.metadata
from fractions import Fraction
import chess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent
(B/'figures').mkdir(exist_ok=True)

def terminal_value(board):
    outcome=board.outcome(claim_draw=False)
    if outcome is None:return None
    if outcome.winner is None:return 0
    return 1 if outcome.winner else -1

def interval(board,depth,counter):
    counter['nodes']+=1
    value=terminal_value(board)
    if value is not None:
        counter['terminals']+=1;return value,value
    claims=board.can_claim_draw()
    if depth==0:
        counter['frontiers']+=1
        return (0,1) if claims and board.turn else (-1,0) if claims else (-1,1)
    children=[(0,0)] if claims else []
    for move in list(board.legal_moves):
        board.push(move)
        try:children.append(interval(board,depth-1,counter))
        finally:board.pop()
    assert children
    f=max if board.turn else min
    return f(v[0] for v in children),f(v[1] for v in children)

def run_search(board,depth):
    before=board.fen();counter={'nodes':0,'terminals':0,'frontiers':0};t=time.perf_counter();bounds=interval(board,depth,counter)
    assert board.fen()==before
    return {'depth':depth,'lower':bounds[0],'upper':bounds[1],**counter,'seconds':time.perf_counter()-t}

initial=[run_search(chess.Board(),d) for d in range(4)]
assert all(r['lower']==-1 and r['upper']==1 for r in initial)
matefen='7k/8/5KQ1/8/8/8/8/8 w - - 0 1';mateboard=chess.Board(matefen);assert mateboard.is_valid();mates=[m for m in mateboard.legal_moves if '#' in mateboard.san(m)];assert len(mates)==1
mate=[run_search(mateboard,d) for d in range(3)]
assert mate[1]['lower']==mate[1]['upper']==1
stalefen='7k/5K2/6Q1/8/8/8/8/8 b - - 0 1';staleboard=chess.Board(stalefen);assert staleboard.is_valid() and staleboard.is_stalemate();stalemate=run_search(staleboard,0);assert stalemate['lower']==stalemate['upper']==0
deadfen='7k/8/5K2/8/8/8/8/8 w - - 0 1';dead=run_search(chess.Board(deadfen),0);assert dead['lower']==dead['upper']==0

board=chess.Board();probability=Fraction(1);fool=[]
for san in ['f3','e5','g4','Qh4#']:
    count=board.legal_moves.count();probability/=count;move=board.parse_san(san);fool.append({'san':san,'uci':move.uci(),'legal_choices':count,'path_probability':str(probability),'fen_before':board.fen()});board.push(move)
assert board.is_checkmate() and probability==Fraction(1,228000)
foolmate=run_search(board,0);assert foolmate['lower']==foolmate['upper']==-1

board=chess.Board();repetition=[]
for ply in range(17):
    repetition.append({'ply':ply,'repetition_2':board.is_repetition(2),'repetition_3':board.is_repetition(3),'fivefold':board.is_fivefold_repetition(),'claim_threefold':board.can_claim_threefold_repetition(),'automatic_terminal':terminal_value(board)})
    if ply<16:board.push_san(['Nf3','Nf6','Ng1','Ng8'][ply%4])
assert repetition[8]['repetition_3'] and not repetition[8]['fivefold']
assert repetition[16]['fivefold'] and repetition[16]['automatic_terminal']==0
fromfen=chess.Board(board.fen());assert not fromfen.is_fivefold_repetition();assert fromfen.fen()==board.fen()

# Small exported certificates. Legality is replayed; a terminal leaf is checked anew.
certificates=[{'name':'White mate in one','root_fen':matefen,'lower':1,'upper':1,'lower_witness':mates[0].uci(),'proof':'White existential mate edge; global payoff cap supplies upper bound'}, {'name':'Stalemate','root_fen':stalefen,'lower':0,'upper':0,'proof':'No legal moves, no check'}, {'name':'Kings only','root_fen':deadfen,'lower':0,'upper':0,'proof':'Only the two kings remain; no checkmate possible'}]
def verify_certificate(c):
    b=chess.Board(c['root_fen']);assert b.is_valid()
    if c['name']=='White mate in one':
        assert b.turn==chess.WHITE
        m=chess.Move.from_uci(c['lower_witness']);assert m in b.legal_moves;b.push(m);assert b.is_checkmate() and b.turn==chess.BLACK
        assert c['lower']==c['upper']==1
    elif c['name']=='Stalemate':assert b.is_stalemate() and c['lower']==c['upper']==0
    elif c['name']=='Kings only':assert len(b.piece_map())==2 and b.kings.bit_count()==2 and c['lower']==c['upper']==0
    else:raise AssertionError('Unrecognized proof rule')
    return True
for c in certificates:assert verify_certificate(c)
bad=dict(certificates[0],lower_witness='g6g5')
try:verify_certificate(bad)
except AssertionError:pass
else:raise AssertionError('Incorrect certificate accepted')

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def save(n):
    plt.savefig(B/'figures'/f'{n}.pdf',bbox_inches='tight');plt.savefig(B/'figures'/f'{n}.png',dpi=170,bbox_inches='tight');plt.close()
plt.figure(figsize=(8,4));plt.fill_between(range(4),[-1]*4,[1]*4,alpha=.2,color='#0072B2',label='Certified enclosure');plt.plot(range(4),[-1]*4,'o-',color='#0072B2');plt.plot(range(4),[1]*4,'o-',color='#D55E00');plt.ylim(-1.2,1.2);plt.xlabel('Search depth (plies)');plt.ylabel('White outcome payoff');plt.title('Initial position: measured bounds remain [-1, +1]');plt.legend();save('initial-bounds')
plt.figure(figsize=(8,4));plt.semilogy([r['depth'] for r in initial],[r['nodes'] for r in initial],'o-',label='Visited nodes');plt.xlabel('Depth (plies)');plt.ylabel('Measured node visits');plt.title('Full enumeration without heuristic cutoffs');plt.legend();save('search-cost')
plt.figure(figsize=(8,4));d=[r['depth'] for r in mate];plt.plot(d,[r['lower'] for r in mate],'o-',label='Lower');plt.plot(d,[r['upper'] for r in mate],'s--',label='Upper');plt.xlabel('Depth (plies)');plt.ylabel('White outcome payoff');plt.ylim(-1.2,1.2);plt.title('Legal mate-in-one fixture: interval collapses exactly');plt.legend();save('mate-bounds')
plt.figure(figsize=(8,4));plt.semilogy(range(1,5),[float(Fraction(x['path_probability'])) for x in fool],'o-',color='#D55E00');plt.xticks(range(1,5),[r['san'] for r in fool]);plt.ylabel('Uniform legal-move path probability');plt.xlabel('Played move');plt.title('A positive-probability decisive path from the initial position');save('fools-mate')
plt.figure(figsize=(8,4));plt.step([r['ply'] for r in repetition],[int(r['repetition_3']) for r in repetition],where='post',label='Threefold currently present');plt.step([r['ply'] for r in repetition],[int(r['fivefold']) for r in repetition],where='post',label='Automatic fivefold');plt.xlabel('Ply in the verified knight-return line');plt.ylabel('Predicate (0 / 1)');plt.title('Claimable and automatic repetition are different conditions');plt.legend();save('repetition')
n=np.arange(1,10001);upper=1-.05**(1/n)
plt.figure(figsize=(8,4));plt.loglog(n,upper,label='Exact one-sided 95% upper bound');plt.axhline(float(probability),color='#D55E00',linestyle='--',label='One uniform-play mate path');plt.xlabel('Independent games, zero decisive outcomes observed');plt.ylabel('Decisive-event probability bound');plt.title('Hypothetical sampling precision is not a universal strategy certificate');plt.legend();save('sampling-bound')
p,q=np.meshgrid(np.linspace(0,1,80),np.linspace(0,1,80));z=(1-p)*(1-q)
fig=plt.figure(figsize=(8,5));ax=fig.add_subplot(projection='3d');ax.plot_surface(p,q,z,cmap='viridis',linewidth=0);ax.set_xlabel('Invented branch probability p');ax.set_ylabel('Invented branch probability q');ax.set_zlabel('Chance of entering unseen branch');ax.set_title('Toy sampling model: branch coverage depends on policy');save('coverage-surface')
fig,ax=plt.subplots(figsize=(8,4));ax.axvspan(-.75,.75,color='#009E73',alpha=.2,label='Illustrative certified interval');ax.scatter([-1,0,1],[0,0,0],s=100,c=['#D55E00','#009E73','#0072B2']);ax.set_xticks([-1,0,1],['Black win (-1)','Draw (0)','White win (+1)']);ax.set_yticks([]);ax.set_ylim(-1,1);ax.set_title('Discrete outcome gap: epsilon below one excludes both wins');ax.legend();save('outcome-gap')
pilot=json.loads((B/'data/relaxfish/summary.json').read_text());fig,ax=plt.subplots(figsize=(8,4));names=['static','relaxfish','stockfish_2k'];ax.bar(names,[pilot['models'][n]['agreement'] for n in names],color=['#56B4E9','#009E73','#0072B2']);ax.set_ylim(0,24);ax.set_ylabel('Reference-move agreement out of 24 positions');ax.set_title('Archived measured Relaxfish pilot; not a strength tournament');save('pilot-agreement')
result={'title':'Magnum Chessicus','chess_package':chess.__version__,'python_chess_distribution':importlib.metadata.version('python-chess'),'payoff':'White +1, draw 0, Black -1','rules':'Automatic terminal conditions plus optional correct draw claims as available actions; no clocks, resignations, or agreed draws','initial_search':initial,'mate_fixture':{'fen':matefen,'search':mate,'winning_move':mates[0].uci()},'stalemate_fixture':{'fen':stalefen,'search':stalemate},'kings_only_fixture':{'fen':deadfen,'search':dead},'fools_mate':{'moves':fool,'probability_exact':str(probability),'probability_float':float(probability),'search':foolmate},'repetition':repetition,'same_fen_different_fivefold_status':True,'certificate_checks':{'accepted':3,'incorrect_mate_witness_rejected':True},'archived_pilot':{'source':'hrl-portfolio/relaxfish/data; previously executed pilot, not rerun here','reference_agreement':{n:pilot['models'][n]['agreement'] for n in names},'positions':24,'diagnostic_match_results':[m['outcome'] for m in pilot['matches']],'file_hashes':{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((B/'data/relaxfish').glob('*'))}},'confidence_examples':{str(n):1-.05**(1/n) for n in [100,1000,10000]},'checks_passed':True,'initial_position_solved':False}
(B/'results.json').write_text(json.dumps(result,indent=2));(B/'data/certificates.json').write_text(json.dumps(certificates,indent=2));print(json.dumps({'initial_search':initial,'fools_mate_probability':str(probability),'checks_passed':True,'initial_position_solved':False},indent=2))
