import unittest,json,hashlib
from pathlib import Path
import chess,chess.pgn
from build_exercises import record,classify
ROOT=Path(__file__).resolve().parent
class ExercisesTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=json.loads((ROOT/'exercises.json').read_text())
 def test_each_start_reached_by_complete_legal_source_game(self):
  for e in self.data['exercises']:
   with (ROOT/e['source']).open() as f:g=chess.pgn.read_game(f)
   self.assertFalse(g.errors);b=g.board();start=None
   for ply,m in enumerate(g.mainline_moves()):
    if ply==e['start_ply']:start=b.fen()
    self.assertIn(m,b.legal_moves);b.push(m)
   self.assertEqual(start,e['steps'][0]['fen']);self.assertTrue(e['source_url'].startswith('https://lichess.org/'))
 def test_sole_moves_followups_and_reason_matrix(self):
  for e in self.data['exercises']:
   for s in e['steps']:
    b=chess.Board(s['fen']);moves=list(b.legal_moves);self.assertEqual(len(moves),1);self.assertFalse(b.is_game_over());self.assertTrue(b.is_valid())
    self.assertEqual(moves[0].uci(),s['move']['uci']);self.assertEqual([u for u,r in s['reasons'].items() if r=='legal'],[moves[0].uci()])
    for u,r in s['reasons'].items():self.assertEqual(r,classify(b,chess.Move.from_uci(u)))
    b.push(moves[0]);self.assertEqual(b.fen(),s['after_fen']);self.assertEqual(len(list(b.legal_moves)),s['next_legal_count']);self.assertEqual(b.is_game_over(),s['next_game_over'])
 def test_source_hashes_and_unique_starting_states(self):
  for source in self.data['sources']:self.assertEqual(hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest(),source['sha256'])
  states=[' '.join(e['steps'][0]['fen'].split()[:4]) for e in self.data['exercises']];self.assertEqual(len(states),len(set(states)))
 def test_pin_and_pawn_block_explanations(self):
  b=chess.Board('k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1');self.assertEqual(classify(b,chess.Move.from_uci('e2d2')),'pin')
  b=chess.Board('7k/8/8/8/8/4p3/4P3/K7 w - - 0 1');self.assertEqual(classify(b,chess.Move.from_uci('e2e3')),'pawn-blocked')
 def test_record_does_not_change_position_or_history(self):
  b=chess.Board(self.data['exercises'][0]['steps'][0]['fen']);before=(b.fen(),len(b.move_stack));record(b);self.assertEqual((b.fen(),len(b.move_stack)),before)
 def test_default_is_king_and_pawn_and_no_engine_score_required(self):
  e=self.data['exercises'][0];self.assertEqual(e['title'],'Just a king and a pawn');self.assertEqual(e['steps'][0]['move']['piece'],'king');self.assertNotIn('score',e)
if __name__=='__main__':unittest.main()
