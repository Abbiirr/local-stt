from __future__ import annotations

import threading

from PySide6.QtCore import QObject, QTimer, Signal

from .audio import AudioRecorder
from .config import AppConfig
from .history import (
    HistoryEntry,
    create_history_entry,
    update_history_error,
    update_history_status,
    update_history_transcript,
)
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
    history_retry_done = Signal(str, str, str)

    def __init__(self, config: AppConfig):
        super().__init__()
        self.logger = get_logger()
        self.config = config
        self.recorder = AudioRecorder(config, level_callback=self.overlay_level.emit)
        self.transcriber = WhisperTranscriber(config, status_callback=self.overlay_show.emit)
        self.inserter = TextInserter(config)
        self.recording = False
        self.transcribing = False
        self.paused = False
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
            self.paused = False

        try:
            self.recorder.start()
        except Exception as exc:
            with self._state_lock:
                self.recording = False
                self.paused = False
            self.logger.exception("Microphone start failed.")
            self.tray_message.emit(f"Microphone error: {exc}")
            return

        self.state_changed.emit("recording")
        self.overlay_show.emit(f"Recording - {self.config.hotkey_toggle} to stop, Esc to cancel")

    def stop_recording(self) -> None:
        with self._state_lock:
            if not self.recording:
                return
            self.recording = False
            self.paused = False
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
        try:
            history_entry = create_history_entry(audio, self.config)
        except Exception:
            history_entry = None
            self.logger.exception("Failed to save recording to history; continuing.")
            self.tray_message.emit("Warning: could not save this recording to history.")
        if duration_seconds < self.config.minimum_duration_seconds:
            update_history_status(history_entry, "too_short")
            with self._state_lock:
                self.transcribing = False
            self.overlay_hide.emit()
            self.tray_message.emit("Recording too short.")
            return

        self.state_changed.emit("transcribing")
        self.overlay_show.emit("Transcribing locally...")
        threading.Thread(target=self._transcribe_worker, args=(audio, history_entry), daemon=True).start()

    def cancel_recording(self) -> None:
        with self._state_lock:
            if not self.recording:
                return
            self.recording = False
            self.paused = False

        self.recorder.cancel()
        self.overlay_hide.emit()
        self.state_changed.emit("idle")
        self.tray_message.emit("Recording canceled.")

    def toggle_pause_recording(self) -> None:
        with self._state_lock:
            if not self.recording or self.transcribing:
                return
            self.paused = not self.paused
            paused = self.paused

        if paused:
            self.recorder.pause()
            self.state_changed.emit("paused")
            self.overlay_show.emit("Paused - click Resume or Stop")
            self.tray_message.emit("Recording paused.")
            return

        self.recorder.resume()
        self.state_changed.emit("recording")
        self.overlay_show.emit("Recording - click Stop to transcribe")
        self.tray_message.emit("Recording resumed.")

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

    def retry_history_entry(self, entry: HistoryEntry) -> None:
        with self._state_lock:
            if self.recording or self.transcribing:
                self.tray_message.emit("Busy; try the retry again in a moment.")
                return
            self.transcribing = True

        threading.Thread(target=self._retry_worker, args=(entry,), daemon=True).start()

    def _preload_worker(self) -> None:
        try:
            self.transcriber.load()
            self.overlay_hide.emit()
            self.tray_message.emit("Whisper model loaded.")
        except Exception as exc:
            self.overlay_hide.emit()
            self.logger.exception("Model preload failed.")
            self.tray_message.emit(f"Model preload error: {exc}")

    def _transcribe_worker(self, audio, history_entry: HistoryEntry | None = None) -> None:
        try:
            text = self.transcriber.transcribe(audio)
            update_history_transcript(history_entry, text)
            if text:
                self.inserter.insert(text)
                suffix = f" History: {history_entry.id}" if history_entry else ""
                self.tray_message.emit(f"Dictation inserted.{suffix}")
            else:
                suffix = f" History: {history_entry.id}" if history_entry else ""
                self.tray_message.emit(f"No speech detected.{suffix}")
        except Exception as exc:
            update_history_error(history_entry, str(exc))
            self.logger.exception("Transcription worker failed.")
            suffix = f" History: {history_entry.id}" if history_entry else ""
            self.tray_message.emit(f"Transcription error: {exc}.{suffix}")
        finally:
            with self._state_lock:
                self.transcribing = False
            self.overlay_hide.emit()
            self.state_changed.emit("idle")

    def _retry_worker(self, entry: HistoryEntry) -> None:
        from pathlib import Path

        from .diagnostics import load_wav_mono_float32

        text = ""
        error = ""
        try:
            audio = load_wav_mono_float32(Path(entry.audio_path), target_sample_rate=self.config.sample_rate)
            text = self.transcriber.transcribe(audio)
            update_history_transcript(entry, text)
            if text:
                self.tray_message.emit(f"History {entry.id} re-transcribed.")
            else:
                self.tray_message.emit(f"History {entry.id}: no speech detected.")
        except Exception as exc:
            error = str(exc)
            update_history_error(entry, error)
            self.logger.exception("History retry failed.")
            self.tray_message.emit(f"History retry error: {exc}")
        finally:
            with self._state_lock:
                self.transcribing = False
            self.history_retry_done.emit(entry.id, text, error)

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
