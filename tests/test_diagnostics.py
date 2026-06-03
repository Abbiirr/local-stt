import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from local_dictation.diagnostics import load_wav_mono_float32, repeat_audio_to_duration


class DiagnosticsTests(unittest.TestCase):
    def test_load_wav_mono_float32(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.wav"
            samples = np.array([0, 16384, -16384, 0], dtype="<i2")
            with wave.open(str(path), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(16000)
                handle.writeframes(samples.tobytes())

            audio = load_wav_mono_float32(path, target_sample_rate=16000)

        self.assertEqual(audio.dtype, np.float32)
        self.assertEqual(audio.shape, (4,))
        self.assertAlmostEqual(float(audio[1]), 0.5, places=4)
        self.assertAlmostEqual(float(audio[2]), -0.5, places=4)

    def test_repeat_audio_to_duration(self):
        audio = np.array([0.1, -0.1], dtype=np.float32)
        repeated = repeat_audio_to_duration(audio, sample_rate=4, duration_seconds=1.0)

        np.testing.assert_array_equal(repeated, np.array([0.1, -0.1, 0.1, -0.1], dtype=np.float32))


if __name__ == "__main__":
    unittest.main()
