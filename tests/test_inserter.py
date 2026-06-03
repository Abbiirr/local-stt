import unittest
from unittest.mock import patch

from local_dictation.config import AppConfig
from local_dictation.inserter import TextInserter


class TextInserterTests(unittest.TestCase):
    def test_type_text_mode_uses_keyboard_write_without_clipboard(self):
        config = AppConfig(type_text_instead_of_paste=True)
        inserter = TextInserter(config)

        with (
            patch("local_dictation.inserter.keyboard.write") as keyboard_write,
            patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy,
        ):
            inserter.insert("hello")

        keyboard_write.assert_called_once_with("hello ")
        clipboard_copy.assert_not_called()

    def test_auto_paste_disabled_copies_payload(self):
        config = AppConfig(auto_paste=False, append_trailing_space=False)
        inserter = TextInserter(config)

        with patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy:
            inserter.insert("hello")

        clipboard_copy.assert_called_once_with("hello")


if __name__ == "__main__":
    unittest.main()
