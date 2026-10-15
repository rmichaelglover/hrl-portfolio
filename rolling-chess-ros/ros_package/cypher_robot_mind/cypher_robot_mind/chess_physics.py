"""A legal-chess/rolling-sphere test bench, independent of ROS and HTTP.

Physics is evidence about this apparatus, never a proof about chess outcomes.
"""
from collections import Counter
from dataclasses import dataclass, field
import copy
import heapq
import hashlib
import io
import json
import math
import random
import chess
import chess.pgn
from .hole_topology import HoleTopology
from .chess_autoplay import ordered_moves

SQUARE=.1
SIDE=8*SQUARE
RADIUS=.012
HOLE=.034
G=9.81
STEP=1/240
MAX_TILT=math.radians(10)
# Wooden partitions; coordinates in metres. Chess symbols are painted markers.
MAZE=[(.395,.10,.010,.20),(.20,.495,.30,.010),(.595,.30,.010,.15)]
SAMPLE='1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 *'


def xy(square):
    return ((chess.square_file(square)+.5)*SQUARE,(chess.square_rank(square)+.5)*SQUARE)


def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])


def position_key(board):
    # Legal en-passant rights, castling rights and turn matter; move clocks do not.
    return ' '.join(board.fen(en_passant='legal').split()[:4])


def acceleration(roll,pitch,vx,vy,resistance=.006,drag=.22):
    """Solid sphere no-slip rolling: I=2mr²/5, a=(5/7)g_t.

    Roll slopes across files; pitch slopes along ranks. Angles use the stated
    board-forward convention. Quasi-static board: actuator/rotating-frame
    inertial effects and high-speed hole-rim impacts are omitted.
    """
    ax=(5/7)*G*math.sin(roll)*math.cos(pitch)
    ay=(5/7)*G*math.sin(pitch)
    normal=G*math.cos(roll)*math.cos(pitch)
    speed=math.hypot(vx,vy)
    threshold=resistance*normal
    if speed<1e-5 and math.hypot(ax,ay)<=threshold:return (0.,0.)
    if speed>1e-5:ax-=threshold*vx/speed;ay-=threshold*vy/speed
    else:
        force=math.hypot(ax,ay)
        if force:ax*=max(0,1-threshold/force);ay*=max(0,1-threshold/force)
    return ax-drag*vx,ay-drag*vy


@dataclass
class Ball:
    serial:int
    color:str
    x:float
    y:float
    vx:float=0.
    vy:float=0.
    z:float=RADIUS
    vz:float=0.
    mode:str='rolling'
    hole:int|None=None
    time:float=0.
    collisions:int=0
    trail:list=field(default_factory=list)
    controls:list=field(default_factory=list)

    def record(self):
        if self.trail and max(abs(self.x-self.trail[-1][1]),abs(self.y-self.trail[-1][2]),
                              abs(self.z-self.trail[-1][3]))<1e-5:return
        self.trail.append([round(self.time,4),round(self.x,5),round(self.y,5),round(self.z,5)])


def blocked(point,walls,balls=(),radius=RADIUS):
    x,y=point
    if min(x,y)<radius or max(x,y)>SIDE-radius:return True
    for xx,yy,w,h in walls:
        qx=max(xx,min(xx+w,x));qy=max(yy,min(yy+h,y))
        if math.hypot(x-qx,y-qy)<radius:return True
    return any(b.mode in {'stranded','rolling'} and distance(point,(b.x,b.y))<2*radius for b in balls)


def collision(ball,walls,others):
    # Stationary maze and retained stuck balls, damped normal restitution.
    for _ in range(2):
        for xx,yy,w,h in walls:
            qx=max(xx,min(xx+w,ball.x));qy=max(yy,min(yy+h,ball.y))
            dx,dy=ball.x-qx,ball.y-qy;d=math.hypot(dx,dy)
            if d>=RADIUS:continue
            if d<1e-10:
                choices=[(abs(ball.x-xx),-1,0),(abs(ball.x-xx-w),1,0),
                         (abs(ball.y-yy),0,-1),(abs(ball.y-yy-h),0,1)]
                depth,nx,ny=min(choices);penetration=RADIUS+depth
            else:nx,ny=dx/d,dy/d;penetration=RADIUS-d
            ball.x+=nx*penetration;ball.y+=ny*penetration
            vn=ball.vx*nx+ball.vy*ny
            if vn<0:ball.vx-=1.15*vn*nx;ball.vy-=1.15*vn*ny;ball.collisions+=1
        for other in others:
            if other.mode not in {'stranded','rolling'}:continue
            dx,dy=ball.x-other.x,ball.y-other.y;d=math.hypot(dx,dy)
            if d>=2*RADIUS:continue
            nx,ny=(dx/d,dy/d) if d>1e-10 else (1.,0.)
            ball.x+=nx*(2*RADIUS-d);ball.y+=ny*(2*RADIUS-d)
            vn=ball.vx*nx+ball.vy*ny
            if vn<0:ball.vx-=1.15*vn*nx;ball.vy-=1.15*vn*ny;ball.collisions+=1
    for axis,velocity in [('x','vx'),('y','vy')]:
        v=getattr(ball,axis)
        if v<RADIUS:setattr(ball,axis,RADIUS);setattr(ball,velocity,abs(getattr(ball,velocity))*.15)
        if v>SIDE-RADIUS:setattr(ball,axis,SIDE-RADIUS);setattr(ball,velocity,-abs(getattr(ball,velocity))*.15)


def integrate(ball,roll,pitch,holes,walls,others=(),dt=STEP):
    if ball.mode not in {'rolling','falling'}:return
    ball.time+=dt
    if not ball.controls or (roll,pitch)!=tuple(ball.controls[-1][1:]):
        ball.controls.append([ball.time-dt,roll,pitch])
    if ball.mode=='falling':
        ball.vz-=G*math.cos(roll)*math.cos(pitch)*dt
        ball.z+=ball.vz*dt
        # The capture well retains the token below the board. Not a chess piece.
        if ball.z<-.05:ball.mode='well';ball.vx=ball.vy=0.
    else:
        ax,ay=acceleration(roll,pitch,ball.vx,ball.vy)
        old=(ball.vx,ball.vy)
        ball.vx+=ax*dt;ball.vy+=ay*dt
        if math.hypot(roll,pitch)<1e-8 and old[0]*ball.vx+old[1]*ball.vy<0:ball.vx=ball.vy=0.
        speed=math.hypot(ball.vx,ball.vy)
        if speed>.55:ball.vx*=.55/speed;ball.vy*=.55/speed
        ball.x+=ball.vx*dt;ball.y+=ball.vy*dt
        collision(ball,walls,others)
        for square in holes:
            if distance((ball.x,ball.y),xy(square))<=HOLE-RADIUS:
                ball.hole=square;ball.mode='falling';ball.vz=0.;break
    if len(ball.trail)==0 or ball.time-ball.trail[-1][0]>=.025:ball.record()


def route(start,end,holes,walls,others=()):
    """Finite-grid controller route. No path here is NOT an impossibility proof."""
    n=80;step=SIDE/n
    def node(p):return (max(1,min(n-2,round(p[0]/step))),max(1,min(n-2,round(p[1]/step))))
    def point(v):return (v[0]*step,v[1]*step)
    source,target=node(start),node(end)
    pits=[xy(h) for h in holes if distance(xy(h),end)>.001]
    def valid(p):
        return not blocked(p,walls,others,RADIUS+.002) and all(distance(p,h)>HOLE-RADIUS+.006 for h in pits)
    if not valid(start):return []
    queue=[(0.,source)];cost={source:0.};parents={};closed=set()
    while queue:
        _,v=heapq.heappop(queue)
        if v in closed:continue
        closed.add(v)
        if v==target:
            path=[end];u=v
            while u in parents:path.append(point(u));u=parents[u]
            path.append(start);path.reverse()
            # Visibility smoothing, checked at finer than the collision radius.
            smooth=[path[0]];i=0
            while i<len(path)-1:
                j=len(path)-1
                while j>i+1:
                    samples=max(1,math.ceil(distance(path[i],path[j])/.004))
                    if all(valid((path[i][0]+(path[j][0]-path[i][0])*k/samples,
                                  path[i][1]+(path[j][1]-path[i][1])*k/samples)) for k in range(1,samples+1)):break
                    j-=1
                smooth.append(path[j]);i=j
            return smooth
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nxt=(v[0]+dx,v[1]+dy)
            if not (1<=nxt[0]<n-1 and 1<=nxt[1]<n-1):continue
            if not valid(point(nxt)):continue
            if dx and dy and (not valid(point((v[0]+dx,v[1]))) or not valid(point((v[0],v[1]+dy)))):continue
            c=cost[v]+math.hypot(dx,dy)
            if c<cost.get(nxt,math.inf):
                cost[nxt]=c;parents[nxt]=v
                heapq.heappush(queue,(c+distance(nxt,target),nxt))
    return []


def steering(ball,path,index):
    if not path:return (0.,0.,index)
    while index<len(path)-1 and distance((ball.x,ball.y),path[index])<.009:index+=1
    target=path[index]
    ax=15*(target[0]-ball.x)-7*ball.vx
    ay=15*(target[1]-ball.y)-7*ball.vy
    # Feed-forward compensates the illustrative rolling resistance.
    if distance((ball.x,ball.y),target)>.004:
        d=distance((ball.x,ball.y),target)
        ax+=.065*(target[0]-ball.x)/d;ay+=.065*(target[1]-ball.y)/d
    pitch=max(-MAX_TILT,min(MAX_TILT,math.asin(max(-1,min(1,ay/((5/7)*G))))))
    roll=max(-MAX_TILT,min(MAX_TILT,math.asin(max(-1,min(1,ax/((5/7)*G*math.cos(pitch)))))))
    return roll,pitch,index


class ChessLab:
    def __init__(self,pgn=SAMPLE,maze=True):
        self.walls=copy.deepcopy(MAZE if maze else [])
        self.load(pgn)

    def load(self,text):
        if len(text)>65536:raise ValueError('PGN is limited to 64 KiB in this test bench.')
        game=chess.pgn.read_game(io.StringIO(text))
        if game is None or game.errors:raise ValueError('PGN could not be parsed as legal chess.')
        board=game.board()
        if not board.is_valid():raise ValueError('The PGN starting position is invalid.')
        self.board=board
        self.topology=HoleTopology(board)
        self.expected=list(game.mainline_moves())
        if len(self.expected)>1024:raise ValueError('Use at most 1,024 plies per experiment.')
        self.initial_fen=self.board.fen();self.imported_pgn=text;self.pgn_index=0
        self.serial=0;self.parked=[];self.active=None;self.source=None;self.promotion='q'
        self.roll=self.pitch=0.;self.autopilot=False;self.path=[];self.path_index=0
        self.drive_start=0.
        self.playing=False;self.randomness=True;self.seed=2026
        self.choice_rng=random.Random(self.seed);self.tilt_rng=random.Random(self.seed+1)
        self.playback_status='Ready for manual control or whole-game autoplay.'
        self.auto_failed=set();self.auto_target=None;self.auto_ply=-1
        self.loop_games=False;self.loop_pending=False;self.loop_elapsed=0.
        self.ledger=[];self.movements=Counter();self.positions=Counter({position_key(self.board):1})
        self.trace_repeats=Counter()
        self.variant_positions=Counter({self.topology.signature(self.board):1})
        self.experiment=None;self.message='Fresh white or black metal token supplied at every ply.'
        self.begin_ply()

    def standard_legal(self):return list(self.board.legal_moves)

    def legal(self):
        moves=self.standard_legal()
        if not self.topology.enforced and self.board.is_game_over():return []
        return [m for m in moves if self.topology.permitted(m)] if self.topology.enforced else moves

    def topology_changed(self):
        self.playing=False
        self.loop_pending=False
        self.variant_positions[self.topology.signature(self.board)]+=1
        self.autopilot=False;self.roll=self.pitch=0.;self.path=[];self.experiment=None
        if self.active:
            moved=math.hypot(self.active.vx,self.active.vy)>.001 or (
                self.source is not None and distance((self.active.x,self.active.y),xy(self.source))>.015)
            if moved:self.active.mode='stranded';self.parked.append(self.active)
            self.active=None
        available=self.legal()
        self.source=None
        if available:self.select(chess.square_name(available[0].from_square))
        else:self.message='No move under the declared variant constraints. This is not automatically chess checkmate.'

    def begin_ply(self):
        self.serial+=1
        self.reserve=Ball(self.serial,'white' if self.board.turn else 'black',-.06,.04,mode='reserve')
        self.active=None;self.source=None;self.autopilot=False;self.roll=self.pitch=0.;self.path=[]
        if not self.topology.enforced and self.board.is_game_over():
            self.message='Chess game ended; a fresh token remains available.';return
        candidates=self.legal()
        next_move=self.expected[self.pgn_index] if self.pgn_index<len(self.expected) else None
        source=next_move.from_square if next_move in candidates else (candidates[0].from_square if candidates else None)
        if source is not None:self.select(chess.square_name(source))

    def select(self,square):
        sq=chess.parse_square(square);piece=self.board.piece_at(sq)
        if piece is None or piece.color!=self.board.turn:raise ValueError('Select a piece belonging to the mover.')
        if not any(m.from_square==sq for m in self.legal()):raise ValueError('That piece has no legal move.')
        if self.active and self.active.mode=='rolling':
            moved=math.hypot(self.active.vx,self.active.vy)>.001 or (
                self.source is not None and distance((self.active.x,self.active.y),xy(self.source))>.015)
            if moved:self.active.mode='stranded';self.parked.append(self.active)
        elif self.active and self.active.mode in {'falling','well'}:
            raise ValueError('Wait for the current ball to finish falling.')
        self.source=sq;self.roll=self.pitch=0.;self.autopilot=False;self.path=[]
        self.serial+=1
        launch=None;origin=xy(sq)
        for dx,dy in [(0,0),(-.025,0),(.025,0),(0,-.025),(0,.025),(-.025,-.025),(.025,.025)]:
            p=(origin[0]+dx,origin[1]+dy)
            if not blocked(p,self.walls,self.parked):launch=p;break
        if launch is None:
            self.active=None;self.message='Source fixture obstructed. A fresh reserve token is still available.';return
        self.active=Ball(self.serial,'white' if self.board.turn else 'black',*launch)
        self.active.record();self.message='White source = selected piece. Dark wells = its legal destinations.'

    def holes(self):return sorted({m.to_square for m in self.legal() if m.from_square==self.source})

    def tilt(self,roll,pitch):
        self.playing=False
        self.loop_pending=False
        if not math.isfinite(roll) or not math.isfinite(pitch):raise ValueError('Tilt must be finite.')
        self.roll=max(-MAX_TILT,min(MAX_TILT,math.radians(roll)))
        self.pitch=max(-MAX_TILT,min(MAX_TILT,math.radians(pitch)));self.autopilot=False

    def drive(self,uci=None):
        moves=self.legal()
        move=chess.Move.from_uci(uci) if uci else (self.expected[self.pgn_index] if self.pgn_index<len(self.expected) else None)
        if move not in moves:raise ValueError('Choose a legal move or load a PGN with another ply.')
        if self.source!=move.from_square:self.select(chess.square_name(move.from_square))
        if self.active is None or self.active.mode!='rolling':raise ValueError('Source is obstructed or the ball is not rolling.')
        self.promotion=chess.piece_symbol(move.promotion) if move.promotion else 'q'
        self.path=route((self.active.x,self.active.y),xy(move.to_square),self.holes(),self.walls,self.parked)
        self.path_index=1;self.autopilot=bool(self.path)
        self.drive_start=self.active.time
        self.message='Controller rolling toward '+self.board.san(move) if self.path else 'No sampled controller route. Chess move remains legal and unresolved.'

    def tick(self,dt=1/30):
        if self.loop_pending and self.loop_games:
            self.loop_elapsed+=dt
            if self.loop_elapsed>=10:
                noise=self.randomness;self.load('*');self.randomness=noise
                self.loop_games=True;self.set_playing(True)
        if self.playing:self.manage_autoplay()
        if not self.active:return
        ball=self.active
        for _ in range(max(1,round(dt/STEP))):
            if self.autopilot and ball.mode=='rolling':
                self.roll,self.pitch,self.path_index=steering(ball,self.path,self.path_index)
                if self.playing and self.randomness:
                    self.roll=max(-MAX_TILT,min(MAX_TILT,self.roll+self.tilt_rng.uniform(-.0015,.0015)))
                    self.pitch=max(-MAX_TILT,min(MAX_TILT,self.pitch+self.tilt_rng.uniform(-.0015,.0015)))
            integrate(ball,self.roll,self.pitch,self.holes(),self.walls,self.parked)
            if ball.mode=='well':self.commit(ball);break
            if ball.time-self.drive_start>25 and self.autopilot:
                self.autopilot=False;self.roll=self.pitch=0.
                self.message='Controller budget exhausted; no chess move was pruned.'

    def set_playing(self,enabled):
        self.playing=bool(enabled)
        if not self.playing:
            self.loop_pending=False
            self.autopilot=False;self.roll=self.pitch=0.
            self.playback_status='Autoplay paused; manual physics remains live.'
        else:self.playback_status='Whole-game autoplay enabled.'

    def manage_autoplay(self):
        if not self.topology.enforced and self.auto_ply!=len(self.board.move_stack):
            outcome=self.board.outcome(claim_draw=True)
            if outcome is not None:
                self.playing=False;self.autopilot=False;self.roll=self.pitch=0.
                self.loop_pending=self.loop_games;self.loop_elapsed=0.
                self.playback_status=f'Game complete: {outcome.result()} · {outcome.termination.name} (draw claimed where applicable).'
                return
        if not self.legal():
            self.playing=False;self.playback_status='No move under current rules. Variant blocked; no unsupported checkmate claim.';return
        if self.auto_ply!=len(self.board.move_stack):
            self.auto_failed=set();self.auto_target=None;self.auto_ply=len(self.board.move_stack)
        if self.autopilot:
            if self.active and self.active.time-self.drive_start>12:
                if self.auto_target:self.auto_failed.add(self.auto_target)
                self.autopilot=False;self.roll=self.pitch=0.
            else:return
        if self.active and self.active.mode=='falling':return
        candidates=ordered_moves(self.board,self.topology,self.choice_rng,self.randomness,self.positions)
        # A loaded reference is replayed first; play continues after its main line.
        if self.pgn_index<len(self.expected) and self.expected[self.pgn_index] in candidates:
            expected=self.expected[self.pgn_index];candidates.remove(expected);candidates.insert(0,expected)
        for move in candidates:
            if move.uci() in self.auto_failed:continue
            result=self.trial(move)
            if result['status']!='witness':
                self.auto_failed.add(move.uci());continue
            if self.active and self.active.mode=='rolling' and self.source==move.from_square and self.active.time-self.drive_start>12:
                self.select(chess.square_name(move.from_square))
            self.drive(move.uci())
            if self.autopilot:
                self.auto_target=move.uci()
                self.playback_status='Playing '+self.board.san(move)+' · '+('small seeded randomness' if self.randomness else 'deterministic policy; no injected tilt noise')
                return
        self.playing=False;self.autopilot=False;self.roll=self.pitch=0.
        self.playback_status='Paused: no physical witness found by this controller. Remaining chess moves stay unresolved.'

    def commit(self,ball):
        candidates=[m for m in self.legal() if m.from_square==self.source and m.to_square==ball.hole]
        promotion=chess.PIECE_SYMBOLS.index(self.promotion)
        move=next((m for m in candidates if m.promotion==promotion),None) or next((m for m in candidates if m.promotion is None),None)
        if move is None:raise RuntimeError('Physics tried to commit an illegal move.')
        before=self.board.fen();san=self.board.san(move);pieces_before=len(self.board.piece_map())
        capture=self.board.is_capture(move);castle=self.board.is_castling(move)
        previous=self.board.copy(stack=False)
        self.board.push(move)
        piece_id,captured_id=self.topology.moved(previous,move)
        self.variant_positions[self.topology.signature(self.board)]+=1
        if len(self.board.piece_map())!=pieces_before-int(capture):raise RuntimeError('Material conservation invariant failed.')
        if self.pgn_index<len(self.expected) and self.expected[self.pgn_index]==move:self.pgn_index+=1
        else:self.expected=self.expected[:self.pgn_index]  # Explicit deviation ends reference replay.
        signature=f'{ball.color}:{move.uci()}'
        bins=[]
        for row in ball.trail:
            point=(round(row[1]/.01),round(row[2]/.01))
            if not bins or point!=bins[-1]:bins.append(point)
        trace_key=hashlib.sha256(repr((ball.color,bins)).encode()).hexdigest()
        self.trace_repeats[trace_key]+=1
        self.movements[signature]+=1;self.positions[position_key(self.board)]+=1
        self.ledger.append({'ply':len(self.board.move_stack),'uci':move.uci(),'san':san,'ball':ball.serial,
                            'piece_id':piece_id,'captured_id':captured_id,
                            'topology_state':self.topology.signature(self.board),
                            'color':ball.color,'seconds':round(ball.time,3),'collisions':ball.collisions,
                            'capture':capture,'castle':castle,'before':before,'after':self.board.fen(),
                            'movement_repeat':self.movements[signature],
                            'trace_repeat':self.trace_repeats[trace_key],'trace_key':trace_key,
                            'trajectory':ball.trail.copy(),'controls':ball.controls.copy()})
        self.parked.append(ball);self.message=f'{san}: legal move committed; metal token retained below the board.'
        self.begin_ply()

    def trial(self,move,seconds=9.):
        # A rollout needs current physics/chess state, not copies of every
        # archived trajectory. Keep its mutations isolated without that cost.
        clone=copy.copy(self)
        clone.board=self.board.copy(stack=True);clone.topology=copy.deepcopy(self.topology)
        clone.parked=[copy.copy(b) for b in self.parked if b.mode=='stranded']
        # A trial starts with a fresh ball at the selected source, retaining old stuck tokens.
        clone.active=None;clone.select(chess.square_name(move.from_square))
        if clone.active is None:return {'uci':move.uci(),'status':'unresolved','reason':'source obstructed'}
        ball=clone.active;holes=clone.holes()
        path=route((ball.x,ball.y),xy(move.to_square),holes,clone.walls,clone.parked)
        if not path:return {'uci':move.uci(),'status':'unresolved','reason':'no grid controller route'}
        index=1
        for _ in range(round(seconds/STEP)):
            roll,pitch,index=steering(ball,path,index)
            integrate(ball,roll,pitch,holes,clone.walls,clone.parked)
            if ball.mode=='well':
                return {'uci':move.uci(),'status':'witness' if ball.hole==move.to_square else 'other legal hole',
                        'seconds':round(ball.time,3),'hole':chess.square_name(ball.hole),'collisions':ball.collisions}
        return {'uci':move.uci(),'status':'unresolved','reason':'finite simulation budget','collisions':ball.collisions}

    def experiment_all(self):
        moves=self.legal()
        results=[self.trial(m) for m in moves]
        # Witness ordering only. Simulation misses never remove a legal chess branch.
        self.experiment={'legal':len(moves),'witnesses':sum(r['status']=='witness' for r in results),
                         'unresolved':sum(r['status']!='witness' for r in results),'pruned_by_rollouts':0,
                         'results':results,'claim':'Ordering evidence only; all legal branches retained.'}
        return self.experiment

    def observation_candidates(self,source=None,destination=None,promotion=None):
        """Exact symbolic constraints from an observed fixture/entry event.

        This is PGN reconstruction with exact square evidence, not a proof of
        future chess value. Uncertain measurements must retain alternatives.
        """
        return [m.uci() for m in self.legal()
                if (source is None or m.from_square==chess.parse_square(source))
                and (destination is None or m.to_square==chess.parse_square(destination))
                and (promotion is None or m.promotion==chess.PIECE_SYMBOLS.index(promotion))]

    def apparatus_key(self):
        """Exact diagnostic key for future physical search; no quantized pruning.

        Ignore metal serial numbers and inert below-board tokens: supplies are
        unlimited, and those tokens exert no forces. Keep stranded colliders,
        velocity, controller state, chess history and all mobility rights.
        """
        ball=None if self.active is None else {key:getattr(self.active,key) for key in
             ['color','x','y','z','vx','vy','vz','mode','hole']}
        payload={'model':'rolling-chess-v2','fen':self.board.fen(),
                 'position_counts':sorted(self.positions.items()),'topology':self.topology.signature(self.board),
                 'walls':self.walls,'ball':ball,'source':self.source,'promotion':self.promotion,
                 'stranded':sorted((b.x,b.y,b.z) for b in self.parked if b.mode=='stranded'),
                 'roll':self.roll,'pitch':self.pitch,'autopilot':self.autopilot,
                 'player':[self.playing,self.randomness,self.loop_games,self.loop_pending,self.loop_elapsed,
                           hashlib.sha256(repr(self.choice_rng.getstate()).encode()).hexdigest(),
                           hashlib.sha256(repr(self.tilt_rng.getstate()).encode()).hexdigest()],
                 'controller':None if not self.autopilot else [self.path,self.path_index,self.active.time-self.drive_start]}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def snapshot(self):
        moves=self.legal();selected=[m for m in moves if m.from_square==self.source]
        def ball_data(b):
            return {k:getattr(b,k) for k in ['serial','color','x','y','z','vx','vy','mode','collisions']}|{
                'trail':[] if b.mode=='well' else b.trail[-300:]}
        topology=self.topology.snapshot(self.board,self.holes())
        return {'fen':self.board.fen(),'turn':'White' if self.board.turn else 'Black','ply':len(self.board.move_stack),
                'playback':{'playing':self.playing,'randomness':self.randomness,'seed':self.seed,
                            'loop':self.loop_games,'restart_in':round(max(0,10-self.loop_elapsed),1) if self.loop_pending else None,
                            'status':self.playback_status+(f' Next game in {max(0,10-self.loop_elapsed):.0f}s.' if self.loop_pending else '')},
                'apparatus_key':self.apparatus_key(),
                'topology':topology,'variant_position_occurrences':self.variant_positions[topology['signature']],
                'source':None if self.source is None else chess.square_name(self.source),
                'pieces':[{'square':chess.square_name(sq),'x':chess.square_file(sq),'y':chess.square_rank(sq),
                           'symbol':p.symbol(),'glyph':p.unicode_symbol()} for sq,p in self.board.piece_map().items()],
                'legal':[{'uci':m.uci(),'san':self.board.san(m)} for m in moves],
                'selected':[{'uci':m.uci(),'san':self.board.san(m)} for m in selected],
                'holes':[{'square':chess.square_name(h),'position':xy(h)} for h in self.holes()],
                'ball':None if self.active is None else ball_data(self.active),
                'parked':[ball_data(b) for b in self.parked], 'reserve':{'color':self.reserve.color,'available':True},
                'roll':math.degrees(self.roll),'pitch':math.degrees(self.pitch),'path':self.path,'walls':self.walls,
                'autopilot':self.autopilot,'message':self.message,'experiment':self.experiment,
                'pgn_next':self.expected[self.pgn_index].uci() if self.pgn_index<len(self.expected) else None,
                'position_repetitions':self.positions[position_key(self.board)],
                'threefold_claimable':self.board.can_claim_threefold_repetition(),
                'fivefold_automatic':self.board.is_fivefold_repetition(),
                'outcome':None if self.topology.enforced or self.board.outcome() is None else str(self.board.outcome().termination.name),
                'baseline_outcome':None if self.board.outcome() is None else str(self.board.outcome().termination.name),
                'ledger':[{k:v for k,v in entry.items() if k not in {'trajectory','controls'}} for entry in self.ledger[-100:]],
                'branch_counts':{'legal':len(moves),'standard_legal':len(self.standard_legal()),
                                 'variant_excluded':len(self.standard_legal())-len(moves) if self.topology.enforced else 0,
                                 'source_known':len(selected)},
                'material':dict(Counter(p.symbol() for p in self.board.piece_map().values()))}

    def export(self):
        return {'format':'glover-rolling-chess-v1','initial_fen':self.initial_fen,'reference_pgn':self.imported_pgn,
                'fen':self.board.fen(),'ledger':self.ledger,'walls':self.walls,
                'topology':self.topology.snapshot(self.board,self.holes()),
                'playback_configuration':{'seed':self.seed,'randomness':self.randomness,'loop':self.loop_games,
                    'choice_rng_state':self.choice_rng.getstate(),'tilt_rng_state':self.tilt_rng.getstate()},
                'model':{'solid_sphere_radius':RADIUS,'hole_radius':HOLE,'square_size':SQUARE,
                         'dt':STEP,'rolling_resistance':.006,'linear_drag':.22,
                         'hole_model':'absorbing capture well; high-speed rim dynamics omitted'}}
