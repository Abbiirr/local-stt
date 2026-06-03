from __future__ import annotations

import time

import keyboard
import pyperclip

from .config import AppConfig


class TextInserter:
    def __init__(self, config: AppConfig):
        self.config = config

    def insert(self, text: str) -> None:
        if not text:
            return

        payload = text + " " if self.config.append_trailing_space else text

        if self.config.type_text_instead_of_paste:
            keyboard.write(payload)
            return

        if not self.config.auto_paste:
            pyperclip.copy(payload)
            return

        previous_clipboard: str | None = None
        if self.config.restore_clipboard_after_paste:
            try:
                previous_clipboard = pyperclip.paste()
            except Exception:
                previous_clipboard = None

        pyperclip.copy(payload)
        time.sleep(self.config.paste_delay_seconds)
        keyboard.press_and_release("ctrl+v")

        if self.config.restore_clipboard_after_paste and previous_clipboard is not None:
            time.sleep(self.config.clipboard_restore_delay_seconds)
            pyperclip.copy(previous_clipboard)
