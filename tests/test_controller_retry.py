import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from local_dictation.config import AppConfig
from local_dictation.controller import DictationController
from local_dictation.history import create_history_entry, load_history_entry


class ControllerRetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_retry_worker_success_updates_transcript_and_clears_busy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(preload_model=False, model_name="tiny")
                entry = create_history_entry(np.array([0.1, 0.2], dtype=np.float32), config)
                controller = DictationController(config)

                results = []
                controller.history_retry_done.connect(
                    lambda eid, text, err: results.append((eid, text, err))
                )

                with (
                    patch(
                        "local_dictation.diagnostics.load_wav_mono_float32",
                        return_value=np.array([0.1], dtype=np.float32),
                    ),
                    patch.object(controller.transcriber, "transcribe", return_value="recovered text"),
                ):
                    controller._retry_worker(entry)

                self.assertEqual(results, [(entry.id, "recovered text", "")])
                self.assertEqual(load_history_entry(entry.id).status, "transcribed")
                self.assertFalse(controller.transcribing)

    def test_retry_worker_failure_records_error_and_clears_busy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(preload_model=False)
                entry = create_history_entry(np.array([0.1], dtype=np.float32), config)
                controller = DictationController(config)

                results = []
                controller.history_retry_done.connect(
                    lambda eid, text, err: results.append((eid, text, err))
                )

                with (
                    patch(
                        "local_dictation.diagnostics.load_wav_mono_float32",
                        return_value=np.array([0.1], dtype=np.float32),
                    ),
                    patch.object(
                        controller.transcriber, "transcribe", side_effect=RuntimeError("boom")
                    ),
                ):
                    controller._retry_worker(entry)

                self.assertEqual(len(results), 1)
                self.assertEqual(results[0][0], entry.id)
                self.assertEqual(results[0][2], "boom")
                self.assertEqual(load_history_entry(entry.id).status, "failed")
                self.assertFalse(controller.transcribing)

    def test_retry_is_rejected_when_busy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(preload_model=False)
                entry = create_history_entry(np.array([0.1], dtype=np.float32), config)
                controller = DictationController(config)
                controller.transcribing = True

                messages = []
                controller.tray_message.connect(messages.append)

                with patch("threading.Thread") as thread:
                    controller.retry_history_entry(entry)
                    thread.assert_not_called()

                self.assertTrue(any("Busy" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
