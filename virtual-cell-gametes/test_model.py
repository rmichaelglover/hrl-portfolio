import unittest
from model import Fertilization


class FertilizationChecks(unittest.TestCase):
    def test_dna_conservation_with_polar_body(self):
        cell = Fertilization()
        self.assertEqual(cell.snapshot()["maternal_nuclear_dna_C"], 2)
        for event in ("fusion", "activation", "meiosis_II_completion", "pronuclear_formation"):
            state = cell.apply(event, "s1" if event == "fusion" else None)
            self.assertEqual(sum(state[key] for key in (
                "maternal_nuclear_dna_C", "paternal_nuclear_dna_C",
                "second_polar_body_dna_C")), state["total_accounted_nuclear_dna_C"])
        self.assertEqual(state["maternal_nuclear_dna_C"] + state["paternal_nuclear_dna_C"], 2)
        self.assertEqual(state["second_polar_body_dna_C"], 1)

    def test_rejected_events_do_not_mutate(self):
        cell = Fertilization()
        for event in ("activation", "meiosis_II_completion", "pronuclear_formation", "unknown"):
            before = cell.snapshot()
            with self.assertRaises(ValueError):
                cell.apply(event)
            self.assertEqual(cell.snapshot(), before)
            self.assertEqual(cell.history, [])

    def test_block_and_duplicate_fusion(self):
        cell = Fertilization()
        cell.apply("fusion", "s1")
        with self.assertRaises(ValueError):
            cell.apply("fusion", "s1")
        cell.apply("activation")
        cell.apply("block_established")
        with self.assertRaises(ValueError):
            cell.apply("fusion", "s2")
        self.assertEqual(len(cell.fused_sperm), 1)

    def test_polyspermy_before_block_is_preserved(self):
        cell = Fertilization()
        cell.apply("fusion", "s1")
        cell.apply("activation")
        cell.apply("fusion", "s2")
        cell.apply("meiosis_II_completion")
        self.assertEqual(cell.snapshot()["status"], "polyspermy")
        with self.assertRaises(ValueError):
            cell.apply("pronuclear_formation")


if __name__ == "__main__":
    unittest.main()
