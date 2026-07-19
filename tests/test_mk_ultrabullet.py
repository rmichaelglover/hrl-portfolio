import importlib.util
from pathlib import Path


PATH = Path(__file__).parents[1] / "mk-ultrabullet" / "prepare_lichess_ultrabullet.py"
SPEC = importlib.util.spec_from_file_location("mk_ultrabullet", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


PGN = '''[Event "rated ultrabullet game"]
[Result "1-0"]
[TimeControl "15+0"]

1. e4 { [%clk 0:00:15] } e5 { [%clk 0:00:14.8] }
2. Qh5 { [%clk 0:00:14.4] } Nc6 { [%clk 0:00:14.1] }
3. Bc4 { [%clk 0:00:13.8] } Nf6 { [%clk 0:00:13.2] }
4. Qxf7# { [%clk 0:00:13.0] } 1-0
'''


def test_extracts_anonymous_musical_features():
    game = MOD.parse_game(PGN)
    assert game["time_control"] == "15+0"
    assert game["plies"] == 7
    assert game["captures"] == [6]
    assert game["checks"] == [6]
    assert "White" not in game and "Black" not in game


def test_rejects_non_ultrabullet_control():
    assert MOD.parse_game(PGN.replace('15+0', '600+0')) is None
