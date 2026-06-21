from __future__ import annotations

import os
import sys

import keyboard
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .config import load_config
from .controller import DictationController
from .history_window import HistoryWindow
from .log import setup_logging
from .overlay import WaveOverlay
from .single_instance import acquire_lock, bootstrap_lock_is_held, release_lock


class HotkeyBridge(QObject):
    toggle = Signal()
    cancel = Signal()


def create_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(20, 24, 35))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)

    pen = QPen(QColor(92, 218, 255))
    pen.setWidth(5)
    painter.setPen(pen)
    points = [(14, 34), (20, 24), (26, 40), (32, 18), (38, 44), (44, 26), (50, 34)]
    for index in range(len(points) - 1):
        painter.drawLine(points[index][0], points[index][1], points[index + 1][0], points[index + 1][1])

    painter.end()
    return QIcon(pixmap)


def run_app() -> int:
    logger = setup_logging()
    config = load_config()
    logger.info("Starting tray app.")

    instance_lock = None
    if not bootstrap_lock_is_held():
        instance_lock, already_running = acquire_lock(logger)
        if already_running:
            os._exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = WaveOverlay(fps=config.overlay_fps)
    controller = DictationController(config)
    hotkeys = HotkeyBridge()

    controller.overlay_show.connect(overlay.show_status)
    controller.overlay_hide.connect(overlay.hide_overlay)
    controller.overlay_level.connect(overlay.push_level)
    controller.app_quit.connect(app.quit)
    controller.state_changed.connect(overlay.set_state)
    controller.state_changed.connect(lambda state: overlay.reset_user_close() if state == "recording" else None)
    overlay.close_requested.connect(controller.close_overlay)
    overlay.stop_requested.connect(controller.stop_recording)
    overlay.pause_requested.connect(controller.toggle_pause_recording)
    hotkeys.toggle.connect(controller.toggle_recording)
    hotkeys.cancel.connect(controller.cancel_recording)

    tray = QSystemTrayIcon(create_icon(), app)
    tray.setToolTip("Local Whisper Dictation")

    menu = QMenu()
    action_toggle = QAction("Start / Stop Dictation", menu)
    action_toggle.triggered.connect(controller.toggle_recording)

    action_cancel = QAction("Cancel Recording", menu)
    action_cancel.triggered.connect(controller.cancel_recording)

    action_history = QAction("History…", menu)
    history_window: dict[str, HistoryWindow] = {}

    def open_history() -> None:
        window = history_window.get("window")
        if window is None:
            window = HistoryWindow(config, controller)
            history_window["window"] = window
        window.show_window()

    action_history.triggered.connect(open_history)

    action_quit = QAction("Quit", menu)
    action_quit.triggered.connect(controller.shutdown)

    menu.addAction(action_toggle)
    menu.addAction(action_cancel)
    menu.addAction(action_history)
    menu.addSeparator()
    menu.addAction(action_quit)

    tray.setContextMenu(menu)
    tray.show()

    def show_tray_message(message: str) -> None:
        logger.info("Tray message: %s", message)
        tray.showMessage("Local Dictation", message)

    controller.tray_message.connect(show_tray_message)

    _register_hotkey(config.hotkey_toggle, hotkeys.toggle.emit, tray, logger)
    _register_hotkey(config.hotkey_cancel, hotkeys.cancel.emit, tray, logger)

    tray.showMessage(
        "Local Whisper Dictation",
        f"Ready. Press {config.hotkey_toggle} to dictate.",
    )

    try:
        return app.exec()
    finally:
        try:
            keyboard.unhook_all()
        except Exception:
            logger.exception("Failed to unhook global hotkeys.")
        for listener in _pynput_listeners:
            try:
                listener.stop()
            except Exception:
                logger.exception("Failed to stop pynput listener.")
        if instance_lock is not None:
            release_lock(instance_lock, logger)
        logger.info("Tray app exited.")


_pynput_listeners: list = []


def _register_hotkey(hotkey: str, callback, tray: QSystemTrayIcon, logger) -> None:
    try:
        keyboard.add_hotkey(hotkey, callback)
        return
    except Exception:
        logger.info("keyboard could not register hotkey %s; trying pynput.", hotkey)

    try:
        from pynput import keyboard as pynput_keyboard

        listener = pynput_keyboard.GlobalHotKeys({_pynput_combo(hotkey): callback})
        listener.daemon = True
        listener.start()
        _pynput_listeners.append(listener)
        logger.info("Registered hotkey %s via pynput.", hotkey)
    except Exception as exc:
        logger.exception("Failed to register hotkey %s.", hotkey)
        tray.showMessage(
            "Local Dictation",
            f"Hotkey '{hotkey}' could not be registered. Use the tray menu instead. Error: {exc}",
        )


def _pynput_combo(hotkey: str) -> str:
    tokens = [token.strip().lower() for token in hotkey.split("+")]
    return "+".join(f"<{token}>" if len(token) > 1 else token for token in tokens)
