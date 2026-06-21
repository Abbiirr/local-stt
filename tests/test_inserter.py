import unittest
import subprocess
from unittest.mock import patch

from local_dictation.config import AppConfig
from local_dictation.inserter import TextInserter


class TextInserterTests(unittest.TestCase):
    def test_type_text_mode_uses_keyboard_write_without_clipboard(self):
        config = AppConfig(type_text_instead_of_paste=True)
        inserter = TextInserter(config)

        with (
            patch("local_dictation.inserter._is_linux", return_value=False),
            patch("local_dictation.inserter.keyboard.write") as keyboard_write,
            patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy,
        ):
            inserter.insert("hello")

        keyboard_write.assert_called_once_with("hello ")
        clipboard_copy.assert_not_called()

    def test_linux_paste_uses_xdotool_when_display_is_available(self):
        inserter = TextInserter(AppConfig())

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", side_effect=lambda command: "/usr/bin/xdotool" if command == "xdotool" else None),
            patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy"),
            patch("local_dictation.inserter.pyperclip.paste", return_value="old"),
            patch("local_dictation.inserter.subprocess.run") as run,
            patch("local_dictation.inserter.keyboard.press_and_release") as press,
        ):
            inserter.insert("hello")

        run.assert_any_call(["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=True)
        press.assert_not_called()

    def test_linux_paste_without_injection_tool_leaves_clipboard_only(self):
        inserter = TextInserter(AppConfig(restore_clipboard_after_paste=False))

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", return_value=None),
            patch.dict("os.environ", {}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy,
            patch("local_dictation.inserter.keyboard.press_and_release") as press,
        ):
            inserter.insert("hello")

        clipboard_copy.assert_called_once_with("hello ")
        press.assert_not_called()

    def test_linux_paste_injection_failure_is_nonfatal(self):
        inserter = TextInserter(AppConfig(restore_clipboard_after_paste=False))

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", side_effect=lambda command: "/usr/bin/xdotool" if command == "xdotool" else None),
            patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy,
            patch("local_dictation.inserter.subprocess.run", side_effect=subprocess.CalledProcessError(1, "xdotool")),
            patch("local_dictation.inserter.keyboard.press_and_release") as press,
        ):
            inserter.insert("hello")

        clipboard_copy.assert_called_once_with("hello ")
        press.assert_not_called()

    def test_linux_paste_uses_ctrl_shift_v_for_terminal_windows(self):
        inserter = TextInserter(AppConfig(restore_clipboard_after_paste=False))

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", side_effect=lambda command: "/usr/bin/xdotool" if command == "xdotool" else None),
            patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy"),
            patch("local_dictation.inserter._active_window_wm_classes", return_value={"dev.warp.warp"}),
            patch("local_dictation.inserter.subprocess.run") as run,
        ):
            inserter.insert("hello")

        run.assert_any_call(["xdotool", "key", "--clearmodifiers", "ctrl+shift+v"], check=True)

    def test_linux_paste_uses_ctrl_v_for_non_terminal_windows(self):
        inserter = TextInserter(AppConfig(restore_clipboard_after_paste=False))

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", side_effect=lambda command: "/usr/bin/xdotool" if command == "xdotool" else None),
            patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy"),
            patch("local_dictation.inserter._active_window_wm_classes", return_value={"firefox"}),
            patch("local_dictation.inserter.subprocess.run") as run,
        ):
            inserter.insert("hello")

        run.assert_any_call(["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=True)

    def test_linux_paste_falls_back_to_ctrl_v_when_window_class_unknown(self):
        inserter = TextInserter(AppConfig(restore_clipboard_after_paste=False))

        with (
            patch("local_dictation.inserter._is_linux", return_value=True),
            patch("local_dictation.inserter.shutil.which", side_effect=lambda command: "/usr/bin/xdotool" if command == "xdotool" else None),
            patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True),
            patch("local_dictation.inserter.pyperclip.copy"),
            patch("local_dictation.inserter._active_window_wm_classes", return_value=set()),
            patch("local_dictation.inserter.subprocess.run") as run,
        ):
            inserter.insert("hello")

        run.assert_any_call(["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=True)

    def test_auto_paste_disabled_copies_payload(self):
        config = AppConfig(auto_paste=False, append_trailing_space=False)
        inserter = TextInserter(config)

        with patch("local_dictation.inserter.pyperclip.copy") as clipboard_copy:
            inserter.insert("hello")

        clipboard_copy.assert_called_once_with("hello")


if __name__ == "__main__":
    unittest.main()
