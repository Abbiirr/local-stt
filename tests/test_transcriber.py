import unittest

from local_dictation.config import AppConfig
from local_dictation.transcriber import WhisperTranscriber


class WhisperTranscriberTests(unittest.TestCase):
    def test_unload_if_idle_releases_loaded_model_when_enabled(self):
        config = AppConfig(unload_model_when_idle=True, unload_after_seconds=0)
        transcriber = WhisperTranscriber(config)
        transcriber._model = object()
        transcriber.last_used_at = 0.0

        self.assertTrue(transcriber.unload_if_idle())
        self.assertFalse(transcriber.loaded)

    def test_unload_if_idle_keeps_loaded_model_when_disabled(self):
        config = AppConfig(unload_model_when_idle=False, unload_after_seconds=0)
        transcriber = WhisperTranscriber(config)
        transcriber._model = object()
        transcriber.last_used_at = 0.0

        self.assertFalse(transcriber.unload_if_idle())
        self.assertTrue(transcriber.loaded)


if __name__ == "__main__":
    unittest.main()
