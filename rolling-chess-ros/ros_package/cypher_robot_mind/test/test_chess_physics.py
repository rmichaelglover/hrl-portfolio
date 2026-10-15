import math
import chess
import pytest
from cypher_robot_mind.chess_physics import (ChessLab, Ball, acceleration, integrate, STEP,
                                            RADIUS, G, xy, position_key)


def commit(lab,uci):
    move=chess.Move.from_uci(uci)
    if lab.source!=move.from_square:lab.select(chess.square_name(move.from_square))
    lab.promotion=chess.piece_symbol(move.promotion) if move.promotion else 'q'
    ball=lab.active
    assert ball is not None
    ball.hole=move.to_square;ball.mode='well';lab.commit(ball)


def test_solid_sphere_acceleration_and_level_rest():
    angle=math.radians(6)
    ax,ay=acceleration(angle,0,0,0,resistance=0,drag=0)
    assert ax==pytest.approx((5/7)*G*math.sin(angle)) and ay==0
    assert acceleration(0,0,0,0)==(0,0)
    ball=Ball(1,'white',.2,.2)
    for _ in range(240):integrate(ball,0,0,[],[])
    assert ball.x==.2 and ball.y==.2
    ball.vx=.1
    for _ in range(1000):integrate(ball,0,0,[],[])
    assert ball.vx>=0 and ball.vx<.002


def test_wall_collision_and_gravitational_well():
    b=Ball(1,'black',.25,.2,vx=.35)
    for _ in range(150):integrate(b,0,0,[],[(.30,.05,.02,.3)])
    assert b.x<=.30-RADIUS+1e-6 and b.collisions>0
    b=Ball(2,'white',*xy(chess.E4))
    for _ in range(120):integrate(b,0,0,[chess.E4],[])
    assert b.mode=='well' and b.z<0


def test_opening_roll_is_witness_and_does_not_delete_piece():
    lab=ChessLab()
    assert len(lab.legal())==20
    assert len(lab.snapshot()['selected'])==2
    before=lab.board.fen();trial=lab.trial(chess.Move.from_uci('e2e4'))
    assert trial['status']=='witness' and lab.board.fen()==before
    lab.drive('e2e4')
    for _ in range(300):
        lab.tick()
        if len(lab.board.move_stack):break
    assert len(lab.board.move_stack)==1
    assert lab.board.piece_at(chess.E4)==chess.Piece(chess.PAWN,chess.WHITE)
    assert lab.board.piece_at(chess.E2) is None
    assert len(lab.board.piece_map())==32
    assert lab.reserve.color=='black' and lab.reserve.mode=='reserve'
    assert lab.active and lab.active.color=='black'
    assert lab.ledger[0]['trajectory'] and lab.ledger[0]['controls']


def test_replenishment_even_if_prior_tokens_stranded():
    lab=ChessLab();old=lab.active
    old.x+=.035  # A genuinely stranded attempt, not an untouched reserve launch.
    lab.select('g1')
    assert old in lab.parked and old.mode=='stranded'
    assert lab.reserve.mode=='reserve' and lab.active.serial!=old.serial
    commit(lab,'g1f3')
    assert lab.reserve.color=='black' and old in lab.parked
    assert len(lab.board.piece_map())==32


def test_observation_filtering_preserves_promotion_ambiguity():
    lab=ChessLab()
    assert len(lab.observation_candidates())==20
    assert len(lab.observation_candidates('e2'))==2
    assert lab.observation_candidates('e2','e4')==['e2e4']
    lab=ChessLab('[SetUp "1"]\n[FEN "7k/P7/8/8/8/8/8/7K w - - 0 1"]\n\n*',maze=False)
    assert len(lab.observation_candidates('a7','a8'))==4
    assert lab.observation_candidates('a7','a8','n')==['a7a8n']
    commit(lab,'a7a8n')
    assert lab.board.piece_at(chess.A8).piece_type==chess.KNIGHT
    assert len(lab.board.piece_map())==3


def test_capture_en_passant_and_castling_material():
    lab=ChessLab(maze=False)
    for uci in ['e2e4','a7a6','e4e5','d7d5']:commit(lab,uci)
    assert lab.board.is_en_passant(chess.Move.from_uci('e5d6'))
    commit(lab,'e5d6')
    assert lab.board.piece_at(chess.D5) is None and len(lab.board.piece_map())==31
    assert lab.ledger[-1]['capture']
    lab=ChessLab('[SetUp "1"]\n[FEN "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"]\n\n*',maze=False)
    commit(lab,'e1g1')
    assert lab.board.piece_at(chess.G1).piece_type==chess.KING
    assert lab.board.piece_at(chess.F1).piece_type==chess.ROOK
    assert len(lab.board.piece_map())==6 and lab.ledger[-1]['castle']


def test_king_safety_and_no_own_piece_disposal():
    lab=ChessLab('[SetUp "1"]\n[FEN "k3r3/8/8/8/8/8/4B3/4K3 w - - 0 1"]\n\n*',maze=False)
    assert not lab.observation_candidates('e2')
    before=lab.board.fen()
    with pytest.raises(ValueError):lab.select('e2')
    assert lab.board.fen()==before
    lab=ChessLab(maze=False)
    with pytest.raises(ValueError):lab.drive('e1e2')
    assert len(lab.board.piece_map())==32


def test_repetition_keys_and_movement_counts_are_separate():
    lab=ChessLab('*',maze=False)
    for _ in range(2):
        for move in ['g1f3','g8f6','f3g1','f6g8']:commit(lab,move)
    assert lab.positions[position_key(lab.board)]==3
    assert lab.board.can_claim_threefold_repetition()
    assert lab.board.outcome() is None  # Claimable does not mean automatic.
    assert lab.movements['white:g1f3']==2
    a=chess.Board('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
    b=chess.Board('r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1')
    assert position_key(a)!=position_key(b)


def test_inaccessible_physical_maze_does_not_prune_chess():
    lab=ChessLab(maze=False)
    lab.walls=[(0,.26,.8,.025)]
    result=lab.trial(chess.Move.from_uci('e2e4'))
    assert result['status']=='unresolved'
    assert chess.Move.from_uci('e2e4') in lab.legal()
    experiment=lab.experiment_all()
    assert experiment['legal']==20 and experiment['pruned_by_rollouts']==0
    assert len(experiment['results'])==20


def test_export_and_illegal_pgn():
    lab=ChessLab(maze=False)
    with pytest.raises(ValueError):lab.load('1. e5 *')
    assert len(lab.board.piece_map())==32
    commit(lab,'e2e4')
    record=lab.export()
    assert record['format']=='glover-rolling-chess-v1'
    assert record['ledger'][0]['before']==chess.STARTING_FEN
    assert record['ledger'][0]['after']==lab.board.fen()


def test_idle_time_does_not_exhaust_a_later_controller_attempt():
    lab=ChessLab();lab.active.time=1000.
    lab.drive('e2e4')
    for _ in range(300):
        lab.tick()
        if lab.board.move_stack:break
    assert lab.board.peek().uci()=='e2e4'
