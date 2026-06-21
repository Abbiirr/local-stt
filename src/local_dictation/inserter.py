from __future__ import annotations

import os
import platform
import shutil
import subprocess
import time

import keyboard
import pyperclip

from .config import AppConfig

TERMINAL_WM_CLASSES = {
    "alacritty",
    "com.mitchellh.ghostty",
    "cool-retro-term",
    "deepin-terminal",
    "dev.warp.warp",
    "eterm",
    "foot",
    "footclient",
    "ghostty",
    "gnome-terminal",
    "gnome-terminal-server",
    "guake",
    "hyper",
    "kgx",
    "kitty",
    "konsole",
    "lxterminal",
    "mate-terminal",
    "org.gnome.console",
    "org.gnome.ptyxis",
    "org.gnome.terminal",
    "org.wezfurlong.wezterm",
    "ptyxis",
    "qterminal",
    "rxvt",
    "rxvt-unicode",
    "sakura",
    "st",
    "st-256color",
    "tabby",
    "terminator",
    "terminology",
    "tilda",
    "tilix",
    "urxvt",
    "uxterm",
    "warp",
    "wezterm",
    "x-terminal-emulator",
    "xfce4-terminal",
    "xterm",
    "yakuake",
}


class TextInserter:
    def __init__(self, config: AppConfig):
        self.config = config

    def insert(self, text: str) -> None:
        if not text:
            return

        payload = text + " " if self.config.append_trailing_space else text

        if self.config.type_text_instead_of_paste:
            self._type_text(payload)
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
        self._paste_from_clipboard()

        if self.config.restore_clipboard_after_paste and previous_clipboard is not None:
            time.sleep(self.config.clipboard_restore_delay_seconds)
            pyperclip.copy(previous_clipboard)

    def _type_text(self, payload: str) -> None:
        if _is_linux():
            if shutil.which("wtype"):
                try:
                    subprocess.run(["wtype", payload], check=True)
                    return
                except subprocess.SubprocessError:
                    pass
            if shutil.which("xdotool") and os.environ.get("DISPLAY"):
                try:
                    subprocess.run(["xdotool", "type", "--clearmodifiers", payload], check=True)
                    return
                except subprocess.SubprocessError:
                    pass
        keyboard.write(payload)

    def _paste_from_clipboard(self) -> None:
        if _is_linux():
            if shutil.which("wtype") and os.environ.get("WAYLAND_DISPLAY"):
                try:
                    subprocess.run(["wtype", "-M", "ctrl", "v", "-m", "ctrl"], check=True)
                    return
                except subprocess.SubprocessError:
                    pass
            if shutil.which("xdotool") and os.environ.get("DISPLAY"):
                try:
                    subprocess.run(["xdotool", "key", "--clearmodifiers", _paste_keys()], check=True)
                    return
                except subprocess.SubprocessError:
                    pass
            return
        keyboard.press_and_release("ctrl+v")


def _is_linux() -> bool:
    return platform.system().lower() == "linux"


def _paste_keys() -> str:
    if _active_window_wm_classes() & TERMINAL_WM_CLASSES:
        return "ctrl+shift+v"
    return "ctrl+v"


def _active_window_wm_classes() -> set[str]:
    if not (shutil.which("xdotool") and shutil.which("xprop")):
        return set()
    try:
        window_id = subprocess.run(
            ["xdotool", "getactivewindow"],
            capture_output=True, text=True, timeout=1.0, check=True,
        ).stdout.strip()
        wm_class = subprocess.run(
            ["xprop", "-id", window_id, "WM_CLASS"],
            capture_output=True, text=True, timeout=1.0, check=True,
        ).stdout
        return {part.strip().strip('"').lower() for part in wm_class.split("=", 1)[1].split(",")}
    except Exception:
        return set()
