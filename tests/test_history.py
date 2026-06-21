import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from local_dictation.config import AppConfig
from local_dictation.history import (
    create_history_entry,
    list_history_entries,
    load_history_entry,
    update_history_error,
    update_history_status,
    update_history_transcript,
)


class HistoryTests(unittest.TestCase):
    def test_create_history_entry_writes_audio_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                audio = np.array([0.0, 0.5, -0.5], dtype=np.float32)
                entry = create_history_entry(audio, AppConfig(sample_rate=16000, model_name="tiny"))

                self.assertIsNotNone(entry)
                self.assertEqual(entry.status, "recorded")
                self.assertEqual(entry.model_name, "tiny")
                self.assertTrue(Path(entry.audio_path).exists())
                self.assertTrue((Path(tmp) / "history" / entry.id / "metadata.json").exists())

                loaded = load_history_entry(entry.id)
                self.assertEqual(loaded.id, entry.id)
                self.assertEqual(loaded.duration_seconds, 3 / 16000)

    def test_history_can_update_transcript_error_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                entry = create_history_entry(np.array([0.1], dtype=np.float32), AppConfig())

                update_history_transcript(entry, "hello")
                loaded = load_history_entry(entry.id)
                self.assertEqual(loaded.status, "transcribed")
                self.assertEqual(Path(loaded.transcript_path).read_text(encoding="utf-8"), "hello")

                update_history_error(loaded, "failure")
                failed = load_history_entry(entry.id)
                self.assertEqual(failed.status, "failed")
                self.assertEqual(Path(failed.error_path).read_text(encoding="utf-8"), "failure")

                update_history_status(failed, "too_short")
                short = load_history_entry(entry.id)
                self.assertEqual(short.status, "too_short")

    def test_list_history_entries_newest_first_and_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                first = create_history_entry(np.array([0.1], dtype=np.float32), AppConfig())
                second = create_history_entry(np.array([0.2], dtype=np.float32), AppConfig())

                entries = list_history_entries(limit=1)

                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0].id, second.id)
                self.assertNotEqual(first.id, second.id)

    def test_history_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                entry = create_history_entry(np.array([0.1], dtype=np.float32), AppConfig(history_enabled=False))

                self.assertIsNone(entry)
                self.assertEqual(list_history_entries(), [])


if __name__ == "__main__":
    unittest.main()
