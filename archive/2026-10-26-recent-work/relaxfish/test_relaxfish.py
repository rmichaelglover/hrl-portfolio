import unittest
import chess
import numpy as np
from relaxfish import (ChessRelaxationLabeler, QuantumTacticalSuperpositionEngine,
                       SubboardLedger, choose_move, distributed_profiles, movement_layer, normalize)

class RelaxFishTests(unittest.TestCase):
    def test_primary_dual_dimensions_and_normalization(self):
        for fen in [chess.STARTING_FEN, '7k/8/8/8/8/8/8/K7 w - - 0 1']:
            m = ChessRelaxationLabeler(chess.Board(fen))
            result = m.solve()
            self.assertEqual(m.P_dual.shape, (7, len(m.squares)))
            np.testing.assert_allclose(m.P_primary.sum(1), 1)
            np.testing.assert_allclose(m.P_dual.sum(1), 1)
            self.assertTrue(np.all(m.P_primary >= 0))
            self.assertLessEqual(result['iterations'], 40)
            self.assertTrue(result['converged'])

    def test_bounded_nonconvergence_is_reported(self):
        result = ChessRelaxationLabeler(chess.Board(), max_iterations=1).solve()
        self.assertEqual(result['iterations'], 1)
        self.assertFalse(result['converged'])

    def test_attack_and_legal_geometry(self):
        b = chess.Board()
        self.assertEqual(movement_layer(b, chess.E2).sum(), 2)  # pawn attacks
        self.assertEqual(movement_layer(b, chess.E2, legal=True).sum(), 2)  # pushes
        self.assertEqual(movement_layer(b, chess.A1).sum(), 2)  # friendly defended endpoints
        self.assertEqual(movement_layer(b, chess.A1, legal=True).sum(), 0)
        b = chess.Board('4k3/8/8/8/8/8/4R3/4K3 w - - 0 1')
        q = b.copy(); q.set_piece_at(chess.E2, chess.Piece(chess.QUEEN, chess.WHITE))
        bishop = b.copy(); bishop.set_piece_at(chess.E2, chess.Piece(chess.BISHOP, chess.WHITE))
        np.testing.assert_array_equal(movement_layer(q, chess.E2),
                                      np.maximum(movement_layer(b, chess.E2), movement_layer(bishop, chess.E2)))

    def test_pinned_piece_and_special_moves(self):
        b = chess.Board('k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1')
        self.assertEqual(movement_layer(b, chess.E2, legal=True)[6, 3], 0)
        b = chess.Board('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.assertEqual(movement_layer(b, chess.E1, legal=True)[7, 6], 1)
        b = chess.Board('4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1')
        self.assertIn(chess.Move.from_uci('e5d6'), b.legal_moves)
        b = chess.Board('7k/P7/8/8/8/8/8/7K w - - 0 1')
        self.assertEqual(len([m for m in b.legal_moves if m.from_square == chess.A7]), 4)

    def test_mate_in_one_and_terminal_positions(self):
        b = chess.Board('7k/5Q2/6K1/8/8/8/8/8 w - - 0 1')
        move = choose_move(b)
        self.assertIn(move, b.legal_moves)
        b.push(move)
        self.assertTrue(b.is_checkmate())
        self.assertIsNone(choose_move(b))
        stale = chess.Board('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
        self.assertTrue(stale.is_stalemate())
        self.assertIsNone(choose_move(stale))

    def test_complex_phase_and_rotation(self):
        q = QuantumTacticalSuperpositionEngine()
        psi = q.initialize_state_vector()
        changed = psi.copy(); changed[2] *= 1j
        np.testing.assert_allclose(q.compute_probability_distribution(psi), q.compute_probability_distribution(changed))
        self.assertFalse(np.allclose(q.compute_probability_distribution(q.mix_roles(psi)),
                                    q.compute_probability_distribution(q.mix_roles(changed))))
        out = q.apply_classical_field_interference(psi, 1.4, True)
        self.assertAlmostEqual(float(np.linalg.norm(out)), 1)
        self.assertEqual(q.collapse_tactical_state(abs(out)**2, np.random.default_rng(42)),
                         q.collapse_tactical_state(abs(out)**2, np.random.default_rng(42)))

    def test_ledger_context_and_bounds(self):
        ledger = SubboardLedger(); b = chess.Board()
        k1 = ledger.register(b, (0, 0), 4, 0)
        b.turn = not b.turn
        k2 = ledger.register(b, (0, 0), 4, 0)
        self.assertNotEqual(k1, k2)
        self.assertFalse(ledger.records[k1]['certified'])
        with self.assertRaises(ValueError): ledger.register(b, (5, 5), 4, 0)

    def test_determinism_and_parallel_equivalence(self):
        fens = [chess.STARTING_FEN, '7k/8/8/8/8/8/8/K7 w - - 0 1']
        self.assertEqual(distributed_profiles(fens), distributed_profiles(fens, workers=2))

    def test_bad_inputs(self):
        for values in [[0, 0], [-1, 2], [float('nan'), 1]]:
            with self.assertRaises(ValueError): normalize(values)
        m = ChessRelaxationLabeler(chess.Board())
        with self.assertRaises(ValueError): m.execute_dual_relaxation_step(np.zeros((2, 2)), np.zeros((2, 2)))

if __name__ == '__main__':
    unittest.main()
