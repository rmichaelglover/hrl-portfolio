import csv
import json
from pathlib import Path
import unittest

import numpy as np
from scipy.optimize import lsq_linear
import analyze


class AssayAnalysisChecks(unittest.TestCase):
    def test_coordinate_reconstruction_and_unique_measurements(self):
        rows = analyze.read_data()
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({r['id'] for r in rows}), 30)
        for row in rows:
            x, y = row['pixel_x'], row['pixel_y']
            if row['dataset'] == 'ins1p_magnesium':
                self.assertAlmostEqual(row['magnesium_mm'], (x-495)*8/229.5)
                self.assertAlmostEqual(row['rate_abs_per_min'], (278.5-y)*.08/168.25)
            else:
                self.assertAlmostEqual(1/row['substrate_mm'], (x-509.5)*2/210)
                self.assertAlmostEqual(1/row['rate_abs_per_min'], (557.5-y)*100/154)

    def test_held_out_concentration(self):
        rows = [r for r in analyze.read_data() if r['dataset'] == 'ribose_lithium']
        self.assertEqual({r['lithium_mm'] for r in rows if r['split'] == 'train'}, {0, .5, 1})
        self.assertEqual({r['lithium_mm'] for r in rows if r['split'] == 'test'}, {1.5})

    def test_mixed_fit_matches_independent_linear_solution(self):
        # Reciprocal mixed kinetics is linear in four transformed coefficients.
        # This independently checks the nonlinear solver, rather than its output file.
        train = [r for r in analyze.read_data() if r['dataset'] == 'ribose_lithium'
                 and r['split'] == 'train']
        x = np.array([1/r['substrate_mm'] for r in train])
        li = np.array([r['lithium_mm'] for r in train])
        design = np.column_stack([np.ones(len(train)), x, li*x, li])
        coefficients = lsq_linear(design, analyze.observed(train, True), bounds=(0, np.inf)).x
        a, b, c, d = coefficients
        expected = np.array([1/a, b/a, b/c, a/d])
        fitted = np.exp(analyze.fit('mixed', train, True, starts=2).x)
        np.testing.assert_allclose(fitted, expected, rtol=1e-5)

    def test_mixed_model_can_recover_known_synthetic_constants(self):
        # Synthetic recovery tests numerical machinery, never empirical validation.
        rows = [dict(substrate_mm=s, magnesium_mm=3, lithium_mm=li)
                for s in [.2, .5, 1, 3, 8] for li in [0, .3, 1, 2]]
        truth = np.array([.12, 1.4, 2.5, .45])
        rates = analyze.predict('mixed', truth, rows)
        for row, rate in zip(rows, rates):
            row['rate_abs_per_min'] = rate
        estimate = np.exp(analyze.fit('mixed', rows, True, starts=2).x)
        np.testing.assert_allclose(estimate, truth, rtol=1e-6)

    def test_saved_predictions_and_cpp(self):
        report = json.loads((analyze.OUT/'fit-results.json').read_text())
        for dataset, entry in report['datasets'].items():
            rows = [r for r in analyze.read_data() if r['dataset'] == dataset]
            for name, model in entry['models'].items():
                p = [model['parameters'][key] for key in analyze.MODELS[name][1]]
                np.testing.assert_allclose(analyze.cpp_predictions(name, p, rows),
                                           analyze.predict(name, p, rows), rtol=2e-12)
                self.assertTrue(model['optimizer_success'])


if __name__ == '__main__':
    unittest.main()
