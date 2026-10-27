import unittest,random
import chess
from paths import solve,endpoint_bound,budget,state
class PathTests(unittest.TestCase):
 def test_transposed_histories_count_separately(self):
  b=chess.Board();t=b.copy()
  for u in ['g1f3','g8f6','b1c3','b8c6']:t.push_uci(u)
  results=[solve(b,t,4,m) for m in ['legal','material','bound']]
  self.assertTrue(all(x['complete'] for x in results));self.assertEqual([x['paths'] for x in results],[4,4,4])
 def test_castle_promotion_capture_and_en_passant_bounds(self):
  cases=[('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',['e1g1','e8c8']),('7k/P7/8/8/8/8/8/7K w - - 0 1',['a7a8n']),('7k/8/8/3pP3/8/8/8/7K w - d6 0 1',['e5d6']),('7k/8/8/8/8/8/r7/R6K w - - 0 1',['a1a2'])]
  for fen,moves in cases:
   b=chess.Board(fen);t=b.copy()
   for u in moves:self.assertIn(chess.Move.from_uci(u),t.legal_moves);t.push_uci(u)
   for c in chess.COLORS:self.assertLessEqual(endpoint_bound(b,t,c),budget(b,len(moves),c),(fen,c))
   a=solve(b,t,len(moves),'legal');z=solve(b,t,len(moves),'bound');self.assertEqual(a['paths'],z['paths']);self.assertGreater(z['paths'],0)
 def test_bound_never_exceeds_known_random_witness_budget(self):
  rng=random.Random(71);b=chess.Board();states=[b.copy()]
  for _ in range(75):
   moves=list(b.legal_moves)
   if not moves:break
   b.push(rng.choice(moves));states.append(b.copy())
  for i in range(len(states)-6):
   for c in chess.COLORS:self.assertLessEqual(endpoint_bound(states[i],states[i+6],c),budget(states[i],6,c))
 def test_limits_are_not_reported_as_exhaustive(self):
  r=solve(chess.Board(),chess.Board(),6,'legal',max_nodes=10);self.assertFalse(r['complete']);self.assertIsNone(r['paths'])
 def test_castling_rights_in_state(self):
  b=chess.Board();t=b.copy();t.castling_rights=0;self.assertNotEqual(state(b),state(t))

class CheckpointTests(unittest.TestCase):
 def test_checkpoint_changes_problem_and_retains_witness(self):
  b=chess.Board();t=b.copy();mid=None
  for i,u in enumerate(['g1f3','g8f6','b1c3','b8c6']):
   t.push_uci(u)
   if i==1:mid=t.copy()
  a=solve(b,t,4,'bound');z=solve(b,t,4,'bound',checkpoints={2:mid})
  self.assertEqual(a['paths'],4);self.assertEqual(z['paths'],1);self.assertEqual(z['examples'][0],['g1f3','g8f6','b1c3','b8c6'])

class TrackingTests(unittest.TestCase):
 def test_special_moves_and_promotion_ambiguity(self):
  import chess.pgn
  from tracking import observations,constrained_track
  for fen,uci,expected in [('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1','e1g1',1),('7k/8/8/3pP3/8/8/8/7K w - d6 0 1','e5d6',1),('7k/P7/8/8/8/8/8/7K w - - 0 1','a7a8q',4)]:
   g=chess.pgn.Game();g.setup(chess.Board(fen));g.add_variation(chess.Move.from_uci(uci))
   frames,keys,truth=observations(g);inferred=constrained_track(frames,keys,g.board());self.assertEqual(len(inferred[-1]),expected);self.assertTrue(any(ids==truth[-1] for _,ids in inferred[-1]))

if __name__=='__main__':unittest.main()
