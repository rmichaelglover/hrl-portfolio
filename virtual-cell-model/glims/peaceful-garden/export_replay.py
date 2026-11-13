"""Regenerate the PGN profile, C++ constants and deterministic garden replay."""
import argparse
import json
from pathlib import Path
from peaceful import Garden, chess_profile
parser=argparse.ArgumentParser()
parser.add_argument('--pgn',type=Path,default=Path(__file__).with_name('source-game.pgn'))
parser.add_argument('--output',type=Path,default=Path(__file__).parent)
parser.add_argument('--turns',type=int,default=40)
args=parser.parse_args()
if not 0 <= args.turns <= 1000: parser.error('turns must be between 0 and 1000')
text=args.pgn.read_text();profile=chess_profile(text);world=Garden(profile)
states=[world.snapshot()]
for _ in range(args.turns): states.append(world.step())
args.output.mkdir(parents=True,exist_ok=True)
for name,data in [('chess-profile.json',profile),('replay.json',{'profile':profile,'states':states})]:
 (args.output/name).write_text(json.dumps(data,indent=2)+'\n')
(args.output/'chess_preferences.hpp').write_text('// Generated from PGN geometry; designed transfer, not psychological inference.\n#pragma once\nnamespace chess_preferences {\ninline constexpr double anticipation = '+repr(profile['weights']['anticipation'])+';\ninline constexpr double progress = '+repr(profile['weights']['progress'])+';\n}\n')
print(f"Exported {profile['plies']} legal plies and {args.turns} joint turns")
