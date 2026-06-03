import unittest

import numpy as np

from local_dictation.audio import rms_to_level


class AudioTests(unittest.TestCase):
    def test_empty_level(self):
        self.assertEqual(rms_to_level(np.array([], dtype=np.float32), 14.0), 0.0)

    def test_level_clamps(self):
        data = np.ones((16,), dtype=np.float32)
        self.assertEqual(rms_to_level(data, 14.0), 1.0)

    def test_level_scales(self):
        data = np.full((16,), 0.01, dtype=np.float32)
        self.assertGreater(rms_to_level(data, 14.0), 0.0)
        self.assertLess(rms_to_level(data, 14.0), 1.0)


if __name__ == "__main__":
    unittest.main()
