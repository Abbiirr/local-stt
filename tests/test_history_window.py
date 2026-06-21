import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

from local_dictation.config import AppConfig
from local_dictation.history import (
    create_history_entry,
    history_dir,
    update_history_error,
    update_history_transcript,
)
from local_dictation.history_window import HistoryWindow


class HistoryWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_history_shows_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                window = HistoryWindow(AppConfig())

                self.assertEqual(window.list_widget.count(), 0)
                self.assertIn("No recordings yet", window.meta_label.text())
                self.assertFalse(window.copy_button.isEnabled())

    def test_lists_entries_newest_first_and_shows_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(model_name="tiny")
                create_history_entry(np.array([0.1], dtype=np.float32), config)
                second = create_history_entry(np.array([0.2], dtype=np.float32), config)
                update_history_transcript(second, "hello world")

                window = HistoryWindow(config)

                self.assertEqual(window.list_widget.count(), 2)
                # Newest entry is first and selected by default.
                self.assertEqual(window._current_entry().id, second.id)
                self.assertIn("hello world", window.detail.toPlainText())
                self.assertTrue(window.copy_button.isEnabled())
                self.assertTrue(window.insert_button.isEnabled())

    def test_copy_button_sets_clipboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(model_name="tiny")
                entry = create_history_entry(np.array([0.1], dtype=np.float32), config)
                update_history_transcript(entry, "copy me")

                window = HistoryWindow(config)
                window._on_copy()

                self.assertEqual(QApplication.clipboard().text(), "copy me")

    def test_failed_entry_shows_error_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(model_name="tiny")
                entry = create_history_entry(np.array([0.1], dtype=np.float32), config)
                update_history_error(entry, "kaboom")

                window = HistoryWindow(config)

                self.assertIn("kaboom", window.detail.toPlainText())
                self.assertFalse(window.copy_button.isEnabled())
                # Retry is available for every entry, including failed ones.
                self.assertTrue(window.retry_button.isEnabled())

    def test_delete_removes_entry_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("local_dictation.history.config_dir", return_value=Path(tmp)):
                config = AppConfig(model_name="tiny")
                entry = create_history_entry(np.array([0.1], dtype=np.float32), config)
                entry_dir = history_dir() / entry.id
                self.assertTrue(entry_dir.exists())

                window = HistoryWindow(config)
                with patch(
                    "local_dictation.history_window.QMessageBox.question",
                    return_value=QMessageBox.StandardButton.Yes,
                ):
                    window._on_delete()

                self.assertFalse(entry_dir.exists())
                self.assertEqual(window.list_widget.count(), 0)


if __name__ == "__main__":
    unittest.main()
