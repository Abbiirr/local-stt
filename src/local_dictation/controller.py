from __future__ import annotations

import threading

from PySide6.QtCore import QObject, QTimer, Signal

from .audio import AudioRecorder
from .config import AppConfig
from .inserter import TextInserter
from .log import get_logger
from .transcriber import WhisperTranscriber


class DictationController(QObject):
    overlay_show = Signal(str)
    overlay_hide = Signal()
    overlay_level = Signal(float)
    tray_message = Signal(str)
    state_changed = Signal(str)
    app_quit = Signal()

    def __init__(self, config: AppConfig):
        super().__init__()
        self.logger = get_logger()
        self.config = config
        self.recorder = AudioRecorder(config, level_callback=self.overlay_level.emit)
        self.transcriber = WhisperTranscriber(config, status_callback=self.overlay_show.emit)
        self.inserter = TextInserter(config)
        self.recording = False
        self.transcribing = False
        self._state_lock = threading.Lock()

        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._idle_model_check)
        self.monitor_timer.start(30_000)

        if config.preload_model:
            threading.Thread(target=self._preload_worker, daemon=True).start()

    def toggle_recording(self) -> None:
        with self._state_lock:
            busy = self.transcribing
            recording = self.recording

        if busy:
            self.tray_message.emit("Already transcribing.")
            return

        if recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        with self._state_lock:
            if self.recording or self.transcribing:
                return
            self.recording = True

        try:
            self.recorder.start()
        except Exception as exc:
            with self._state_lock:
                self.recording = False
            self.logger.exception("Microphone start failed.")
            self.tray_message.emit(f"Microphone error: {exc}")
            return

        self.state_changed.emit("recording")
        self.overlay_show.emit("Recording - Ctrl+Alt+D to stop, Esc to cancel")

    def stop_recording(self) -> None:
        with self._state_lock:
            if not self.recording:
                return
            self.recording = False
            self.transcribing = True

        try:
            audio = self.recorder.stop()
        except Exception as exc:
            with self._state_lock:
                self.transcribing = False
            self.overlay_hide.emit()
            self.logger.exception("Microphone stop failed.")
            self.tray_message.emit(f"Microphone stop error: {exc}")
            return

        duration_seconds = len(audio) / self.config.sample_rate if audio.size else 0.0
        if duration_seconds < self.config.minimum_duration_seconds:
            with self._state_lock:
                self.transcribing = False
            self.overlay_hide.emit()
            self.tray_message.emit("Recording too short.")
            return

        self.state_changed.emit("transcribing")
        self.overlay_show.emit("Transcribing locally...")
        threading.Thread(target=self._transcribe_worker, args=(audio,), daemon=True).start()

    def cancel_recording(self) -> None:
        with self._state_lock:
            if not self.recording:
                return
            self.recording = False

        self.recorder.cancel()
        self.overlay_hide.emit()
        self.state_changed.emit("idle")
        self.tray_message.emit("Recording canceled.")

    def close_overlay(self) -> None:
        with self._state_lock:
            recording = self.recording
            transcribing = self.transcribing

        if recording:
            self.cancel_recording()
            return

        self.overlay_hide.emit()
        if transcribing:
            self.tray_message.emit("Overlay hidden. Transcription continues.")
        else:
            self.tray_message.emit("Overlay hidden.")

    def shutdown(self) -> None:
        try:
            if self.recording:
                self.recorder.cancel()
        except Exception:
            self.logger.exception("Recorder cancel failed during shutdown.")
            pass
        self.app_quit.emit()

    def _preload_worker(self) -> None:
        try:
            self.transcriber.load()
            self.overlay_hide.emit()
            self.tray_message.emit("Whisper model loaded.")
        except Exception as exc:
            self.overlay_hide.emit()
            self.logger.exception("Model preload failed.")
            self.tray_message.emit(f"Model preload error: {exc}")

    def _transcribe_worker(self, audio) -> None:
        try:
            text = self.transcriber.transcribe(audio)
            if text:
                self.inserter.insert(text)
                self.tray_message.emit("Dictation inserted.")
            else:
                self.tray_message.emit("No speech detected.")
        except Exception as exc:
            self.logger.exception("Transcription worker failed.")
            self.tray_message.emit(f"Transcription error: {exc}")
        finally:
            with self._state_lock:
                self.transcribing = False
            self.overlay_hide.emit()
            self.state_changed.emit("idle")

    def _idle_model_check(self) -> None:
        with self._state_lock:
            if self.transcribing:
                return

        try:
            if self.transcriber.unload_if_idle():
                self.tray_message.emit("Whisper model unloaded after idle timeout.")
        except Exception as exc:
            self.logger.exception("Model unload check failed.")
            self.tray_message.emit(f"Model unload error: {exc}")
