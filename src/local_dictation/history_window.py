from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig
from .history import HistoryEntry, history_dir, list_history_entries
from .inserter import TextInserter
from .log import get_logger

_STATUS_COLORS = {
    "failed": "#d2453f",
    "empty": "#c98a1b",
    "too_short": "#c98a1b",
    "recorded": "#8a8f98",
}

_LIST_LIMIT = 200


class HistoryWindow(QWidget):
    """Minimal window to browse, retry, copy, insert, and delete dictation history."""

    def __init__(self, config: AppConfig, controller=None, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.controller = controller
        self.logger = get_logger()
        self.inserter = TextInserter(config)
        self._entries: list[HistoryEntry] = []

        self.setWindowTitle("Dictation History")
        self.resize(780, 460)

        layout = QHBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        layout.addWidget(self.list_widget, 1)

        right = QVBoxLayout()
        self.meta_label = QLabel("Select an entry.")
        self.meta_label.setWordWrap(True)
        right.addWidget(self.meta_label)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        right.addWidget(self.detail, 1)

        buttons = QHBoxLayout()
        self.copy_button = QPushButton("Copy")
        self.insert_button = QPushButton("Insert")
        self.retry_button = QPushButton("Retry")
        self.delete_button = QPushButton("Delete")
        self.folder_button = QPushButton("Open folder")
        self.refresh_button = QPushButton("Refresh")
        for button in (
            self.copy_button,
            self.insert_button,
            self.retry_button,
            self.delete_button,
            self.folder_button,
            self.refresh_button,
        ):
            buttons.addWidget(button)
        right.addLayout(buttons)
        layout.addLayout(right, 2)

        self.copy_button.clicked.connect(self._on_copy)
        self.insert_button.clicked.connect(self._on_insert)
        self.retry_button.clicked.connect(self._on_retry)
        self.delete_button.clicked.connect(self._on_delete)
        self.folder_button.clicked.connect(self._on_open_folder)
        self.refresh_button.clicked.connect(self.refresh)

        if controller is not None and hasattr(controller, "history_retry_done"):
            controller.history_retry_done.connect(self._on_retry_done)

        self.refresh()

    # --- data loading ---

    def refresh(self) -> None:
        current = self._current_entry()
        selected_id = current.id if current else None

        self._entries = list_history_entries(limit=_LIST_LIMIT)
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for entry in self._entries:
            item = QListWidgetItem(self._row_label(entry))
            color = _STATUS_COLORS.get(entry.status)
            if color:
                item.setForeground(QColor(color))
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)

        if not self._entries:
            self.meta_label.setText("No recordings yet.")
            self.detail.clear()
            self._set_buttons_enabled(False)
            return

        target_row = 0
        if selected_id:
            for index, entry in enumerate(self._entries):
                if entry.id == selected_id:
                    target_row = index
                    break
        self.list_widget.setCurrentRow(target_row)
        # setCurrentRow fires currentRowChanged only if the row actually changes;
        # force a detail refresh to cover the same-row case.
        self._on_row_changed(target_row)

    def show_window(self) -> None:
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()

    # --- helpers ---

    def _row_label(self, entry: HistoryEntry) -> str:
        snippet = self._transcript_text(entry).strip().replace("\n", " ")
        if len(snippet) > 40:
            snippet = snippet[:40] + "…"
        time_part = entry.created_at[11:16] if len(entry.created_at) >= 16 else entry.id
        label = f"{time_part} · {entry.status} · {entry.duration_seconds:.1f}s"
        if snippet:
            label += f' · "{snippet}"'
        return label

    def _current_entry(self) -> HistoryEntry | None:
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None

    @staticmethod
    def _read_text(path_str: str | None) -> str:
        if not path_str:
            return ""
        path = Path(path_str)
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def _transcript_text(self, entry: HistoryEntry) -> str:
        return self._read_text(entry.transcript_path)

    def _error_text(self, entry: HistoryEntry) -> str:
        return self._read_text(entry.error_path)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for button in (
            self.copy_button,
            self.insert_button,
            self.retry_button,
            self.delete_button,
            self.folder_button,
        ):
            button.setEnabled(enabled)

    # --- selection ---

    def _on_row_changed(self, _row: int) -> None:
        entry = self._current_entry()
        if entry is None:
            self.detail.clear()
            self.meta_label.setText("Select an entry.")
            self._set_buttons_enabled(False)
            return

        self.meta_label.setText(
            f"{entry.created_at}  ·  {entry.status}  ·  "
            f"{entry.duration_seconds:.2f}s  ·  {entry.model_name} / {entry.device}"
        )
        transcript = self._transcript_text(entry)
        error = self._error_text(entry)
        if transcript:
            self.detail.setPlainText(transcript)
        elif error:
            self.detail.setPlainText(f"[error]\n{error}")
        else:
            self.detail.setPlainText("(no transcript)")

        has_text = bool(transcript)
        self.copy_button.setEnabled(has_text)
        self.insert_button.setEnabled(has_text)
        self.retry_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.folder_button.setEnabled(True)

    # --- actions ---

    def _on_copy(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        text = self._transcript_text(entry)
        if text:
            QApplication.clipboard().setText(text)

    def _on_insert(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        text = self._transcript_text(entry)
        if not text:
            return
        self.hide()
        QTimer.singleShot(200, lambda: self._do_insert(text))

    def _do_insert(self, text: str) -> None:
        try:
            self.inserter.insert(text)
        except Exception:
            self.logger.exception("History insert failed.")

    def _on_retry(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        if self.controller is None or not hasattr(self.controller, "retry_history_entry"):
            QMessageBox.warning(self, "Retry", "Retry is unavailable.")
            return
        self.retry_button.setEnabled(False)
        self.detail.setPlainText("Retrying transcription…")
        self.controller.retry_history_entry(entry)

    def _on_retry_done(self, entry_id: str, _text: str, _error: str) -> None:
        self.refresh()
        self.retry_button.setEnabled(True)
        for index, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self.list_widget.setCurrentRow(index)
                break

    def _on_delete(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        confirm = QMessageBox.question(
            self,
            "Delete recording",
            f"Delete history entry {entry.id} and its audio?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        entry_dir = history_dir() / entry.id
        try:
            shutil.rmtree(entry_dir)
        except Exception:
            self.logger.exception("Failed to delete history entry.")
            QMessageBox.warning(self, "Delete", "Could not delete the recording.")
            return
        self.refresh()

    def _on_open_folder(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        entry_dir = history_dir() / entry.id
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(entry_dir)))
