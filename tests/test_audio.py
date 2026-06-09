import unittest

import numpy as np

from local_dictation.audio import AudioRecorder, rms_to_level
from local_dictation.config import AppConfig


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

    def test_pause_discards_audio_until_resume(self):
        levels = []
        recorder = AudioRecorder(AppConfig(), level_callback=levels.append)
        recorder._recording = True

        kept_before_pause = np.full((2, 1), 0.1, dtype=np.float32)
        discarded_while_paused = np.full((2, 1), 0.7, dtype=np.float32)
        kept_after_resume = np.full((2, 1), 0.2, dtype=np.float32)

        recorder._callback(kept_before_pause, 2, None, None)
        recorder.pause()
        recorder._callback(discarded_while_paused, 2, None, None)
        recorder.resume()
        recorder._callback(kept_after_resume, 2, None, None)

        recorder._recording = False
        with recorder._lock:
            audio = np.concatenate(recorder._frames, axis=0).flatten()

        np.testing.assert_array_equal(audio, np.array([0.1, 0.1, 0.2, 0.2], dtype=np.float32))
        self.assertIn(0.0, levels)


if __name__ == "__main__":
    unittest.main()
