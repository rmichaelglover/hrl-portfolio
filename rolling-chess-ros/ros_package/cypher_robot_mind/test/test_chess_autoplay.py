import random
import chess
from cypher_robot_mind.chess_autoplay import ordered_moves
from cypher_robot_mind.chess_physics import ChessLab


def test_randomness_off_is_independent_of_rng_state():
    lab=ChessLab('*')
    a=ordered_moves(lab.board,lab.topology,random.Random(1),False,lab.positions)
    b=ordered_moves(lab.board,lab.topology,random.Random(999),False,lab.positions)
    assert a==b and len(a)==20
    assert set(a)==set(lab.board.legal_moves)


def test_seeded_randomness_reproducible_and_never_changes_legality():
    lab=ChessLab('*')
    a=ordered_moves(lab.board,lab.topology,random.Random(2026),True,lab.positions)
    b=ordered_moves(lab.board,lab.topology,random.Random(2026),True,lab.positions)
    assert a==b and set(a)==set(lab.board.legal_moves)


def test_complete_physical_game_and_easy_noise_switch():
    # A short complete game exercises captures, terminal adjudication and playback.
    lab=ChessLab('1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7# *')
    lab.randomness=True;lab.set_playing(True)
    for _ in range(6000):
        lab.tick()
        if not lab.playing:break
    assert lab.board.is_checkmate(),(lab.playback_status,lab.board.fen())
    assert len(lab.ledger)==7
    assert lab.board.outcome().winner==chess.WHITE
    assert len(lab.board.piece_map())==31
    assert 'Game complete' in lab.playback_status
    old_fen=lab.board.fen();lab.randomness=False
    assert lab.board.fen()==old_fen


def test_configured_live_loop_restarts_and_pause_cancels_it():
    lab=ChessLab('1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7# *')
    lab.loop_games=True;lab.randomness=False;lab.set_playing(True)
    for _ in range(6000):
        lab.tick()
        if not lab.playing:break
    assert lab.loop_pending and lab.board.is_checkmate()
    lab.set_playing(False)
    assert not lab.loop_pending
    lab.set_playing(True);lab.tick()
    assert lab.loop_pending
    for _ in range(310):lab.tick()
    assert lab.playing and not lab.board.is_checkmate()
    assert lab.randomness is False and lab.loop_games
