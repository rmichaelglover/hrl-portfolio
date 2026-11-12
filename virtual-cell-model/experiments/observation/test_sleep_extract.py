import tempfile, unittest
from pathlib import Path
import numpy as np
from sleep_extract import EDF, codebook, features, clock

class SleepExtractTests(unittest.TestCase):

    def test_calibrated_channel_and_record_offsets(self):

        def fields(values, width):
            return b''.join((str(v).encode().ljust(width) for v in values))
        header = b'0'.ljust(8) + b'SYNTHETIC'.ljust(80) + b'TEST'.ljust(80) + b'01.01.00' + b'12.00.00' + b'768'.ljust(8) + b''.ljust(44) + b'2'.ljust(8) + b'1'.ljust(8) + b'2'.ljust(4)
        channel = fields(['E1-M2', 'E2-M2'], 16) + fields(['', ''], 80) + fields(['uV', 'uV'], 8) + fields([-100, -100], 8) + fields([100, 100], 8) + fields([-1000, -1000], 8) + fields([1000, 1000], 8) + fields(['', ''], 80) + fields([32, 32], 8) + fields(['', ''], 32)
        samples = np.tile(np.r_[np.full(32, 100), np.full(32, -200)], 2).astype('<i2')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'test.edf'
            p.write_bytes(header + channel + samples.tobytes())
            edf = EDF(p)
            (left, fs) = edf.channel('E1-M2', 0.5, 1)
            (right, _) = edf.channel('E2-M2', 0, 2)
            np.testing.assert_allclose(left, 10)
            np.testing.assert_allclose(right, -20)
            self.assertEqual(fs, 32)
            with self.assertRaises(ValueError):
                edf.channel('E1-M2', 1.5, 1)

    def test_codebook_is_derived_not_guessed(self):
        stages = [{'Epoch': '1', 'Sleep': '5'}]
        events = [{'Epoch': '1', 'Stage': 'REM'}]
        self.assertEqual(codebook(stages, events), {'5': 'REM'})
        events.append({'Epoch': '1', 'Stage': 'N2'})
        with self.assertRaises(ValueError):
            codebook(stages, events)

    def test_filter_preserves_eye_band_and_removes_dc(self):
        fs = 100
        t = np.arange(3000) / fs
        f = features(100 + 50 * np.sin(2 * np.pi * t), fs)
        self.assertAlmostEqual(f['rms_uv'], 50 / np.sqrt(2), delta=3)
        self.assertFalse(f['flatline'])
        self.assertTrue(features(np.zeros(3000), fs)['flatline'])
        with self.assertRaises(ValueError):
            features(t, 10)

    def test_clock_crosses_midnight(self):
        self.assertEqual((clock('00:00:10') - clock('23:59:40')) % 86400, 30)
if __name__ == '__main__':
    unittest.main()
