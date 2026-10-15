import chess
import pytest
from cypher_robot_mind.chess_physics import ChessLab,position_key
from cypher_robot_mind.hole_topology import HoleTopology


def move(lab,uci):
    m=chess.Move.from_uci(uci)
    if lab.source!=m.from_square:lab.select(chess.square_name(m.from_square))
    lab.promotion=chess.piece_symbol(m.promotion) if m.promotion else 'q'
    lab.active.hole=m.to_square;lab.active.mode='well';lab.commit(lab.active)


def test_black_merger_imprisons_after_entry_without_disposal():
    lab=ChessLab(maze=False)
    lab.topology.merge('B:e3','B:e4','imprison')
    move(lab,'e2e4')
    pawn=lab.topology.pieces['w-p-e2']
    assert pawn['existence']=='on-board' and pawn['square']=='e4'
    assert pawn['mobility']=='imprisoned' and pawn['horizon']=='entered'
    assert len(lab.board.piece_map())==32
    assert lab.topology.pieces['w-p-e2']['topology']=='singularity-associated'
    move(lab,'a7a6')
    assert chess.Move.from_uci('e4e5') in lab.legal()  # Standard mode preserves chess.
    lab.topology.enforced=True
    assert chess.Move.from_uci('e4e5') not in lab.legal()
    assert chess.Move.from_uci('e4e5') in lab.standard_legal()
    lab.topology.release('w-p-e2')
    assert chess.Move.from_uci('e4e5') in lab.legal()


def test_white_merger_groups_sources_and_releases_without_fusing():
    lab=ChessLab(maze=False);before=lab.board.fen()
    lab.topology.merge('W:w-n-b1','W:w-n-g1','imprison')
    assert lab.board.fen()==before
    lab.topology.enforced=True
    assert len(lab.legal())==16  # Four knight moves excluded by declared rule.
    assert len(lab.standard_legal())==20
    lab.topology.release('w-n-g1')
    assert len(lab.legal())==18
    assert len(lab.board.piece_map())==32


def test_mixed_merger_is_directed_release_not_teleport():
    lab=ChessLab(maze=False)
    lab.topology.merge('W:w-n-b1','W:w-n-g1','imprison')
    lab.topology.merge('B:e4','W:w-n-b1')
    lab.topology.enforced=True
    move(lab,'e2e4')
    for identifier in ['w-n-b1','w-n-g1']:
        assert lab.topology.pieces[identifier]['mobility']=='free'
    assert lab.board.piece_at(chess.B1).piece_type==chess.KNIGHT
    assert lab.board.piece_at(chess.G1).piece_type==chess.KNIGHT
    assert lab.topology.links[0]['black']=='B:e4'


def test_constrained_destination_and_promotion_keep_identity():
    lab=ChessLab(maze=False)
    lab.topology.merge('B:e3','B:e4','constrain')
    move(lab,'e2e4');move(lab,'a7a6');lab.topology.enforced=True
    assert not lab.topology.permitted(chess.Move.from_uci('e4e5'))
    assert lab.topology.pieces['w-p-e2']['allowed']==['e3','e4']
    lab=ChessLab('[SetUp "1"]\n[FEN "7k/P7/8/8/8/8/8/7K w - - 0 1"]\n\n*',maze=False)
    move(lab,'a7a8q')
    assert lab.topology.pieces['w-p-a7']['type']=='q'
    assert lab.topology.at[chess.A8]=='w-p-a7'


def test_captured_piece_is_retained_as_record_and_cannot_be_resurrected():
    lab=ChessLab(maze=False)
    for uci in ['e2e4','d7d5','e4d5']:move(lab,uci)
    victim=lab.topology.pieces['b-p-d7']
    assert victim['existence']=='captured' and victim['horizon']=='capture-completed'
    assert len(lab.board.piece_map())==31
    with pytest.raises(ValueError):lab.topology.release('b-p-d7')
    assert victim['captured_by']=='w-p-e2'


def test_castling_rook_constraints_count():
    board=chess.Board('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
    t=HoleTopology(board)
    t.merge('W:w-r-a1','W:w-r-h1','imprison')
    assert not t.permitted(chess.Move.from_uci('e1g1'))
    assert not t.permitted(chess.Move.from_uci('e1c1'))


def test_canonical_merger_signature_and_variant_repetition_context():
    board=chess.Board();a=HoleTopology(board);b=HoleTopology(board)
    a.merge('B:e3','B:e4');a.merge('B:e4','B:e5')
    b.merge('B:e5','B:e3');b.merge('B:e4','B:e3')
    assert a.signature(board)==b.signature(board)
    old=a.signature(board);a.enforced=True
    assert a.signature(board)!=old
    unchanged=position_key(board)
    a.release('w-n-g1')
    assert position_key(board)==unchanged and a.signature(board)!=b.signature(board)


def test_current_capture_and_imprisonment_are_different():
    board=chess.Board('7k/8/8/8/8/8/rP6/7K b - - 0 1')
    t=HoleTopology(board)
    piece=next(p for p in t.snapshot(board,[])['pieces'] if p['id']=='w-p-b2')
    assert piece['existence']=='on-board'
    assert piece['attacked_now']
    assert piece['capture_available_now']==['a2b2']
    result=t.forecast(board,'w-p-b2',depth=1)
    assert result['status']=='forced within horizon' and result['probability'] is None
    assert board.piece_at(chess.B2) is not None  # Forecast never executes the capture.


def test_no_probability_or_capture_guarantee_from_prison_alone():
    lab=ChessLab(maze=False)
    lab.topology.merge('W:w-n-g1','W:w-n-b1','imprison');lab.topology.enforced=True
    forecast=lab.topology.forecast(lab.board,'w-n-g1',depth=1)
    assert forecast['status']=='not forced within horizon'
    assert forecast['probability'] is None
    assert 'never king capture' in lab.topology.forecast(lab.board,'w-k-e1')['status']
    limited=lab.topology.forecast(lab.board,'w-n-g1',depth=4,max_nodes=1)
    assert limited['status']=='unresolved budget'


def test_apparatus_key_contains_geometry_velocity_and_mobility():
    lab=ChessLab(maze=False);baseline=lab.apparatus_key();fen=lab.board.fen()
    lab.active.vx=.1
    assert lab.apparatus_key()!=baseline and lab.board.fen()==fen
    lab.active.vx=0.;assert lab.apparatus_key()==baseline
    lab.walls.append((.1,.3,.3,.02));assert lab.apparatus_key()!=baseline
    lab.walls=[];lab.topology.merge('B:e3','B:e4')
    assert lab.apparatus_key()!=baseline and lab.board.fen()==fen


def test_variant_does_not_use_baseline_threefold_as_full_state_draw():
    lab=ChessLab(maze=False)
    for _ in range(4):
        for uci in ['g1f3','g8f6','f3g1','f6g8']:move(lab,uci)
    assert lab.board.is_fivefold_repetition() and lab.legal()==[]
    lab.topology.merge('B:e3','B:e4');lab.topology.enforced=True
    assert lab.legal()  # Variant repetition is not adjudicated from FEN-only history.
    assert lab.snapshot()['outcome'] is None
    assert lab.snapshot()['baseline_outcome']=='FIVEFOLD_REPETITION'
