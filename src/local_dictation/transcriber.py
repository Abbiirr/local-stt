from __future__ import annotations

import gc
import threading
import time
from collections.abc import Callable

import numpy as np
from faster_whisper import WhisperModel

from .config import AppConfig, resolve_model_name
from .text import post_process_transcript


StatusCallback = Callable[[str], None]


class WhisperTranscriber:
    def __init__(self, config: AppConfig, status_callback: StatusCallback | None = None):
        self.config = config
        self.status_callback = status_callback
        self._model: WhisperModel | None = None
        self._lock = threading.Lock()
        self.last_used_at = 0.0

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        with self._lock:
            if self._model is not None:
                return
            model_name = resolve_model_name(self.config.model_name)
            self._status(f"Loading {model_name} on {self.config.device}...")
            self._model = WhisperModel(
                model_name,
                device=self.config.device,
                compute_type=self.config.compute_type,
            )
            self.last_used_at = time.time()

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""

        self.load()

        with self._lock:
            if self._model is None:
                raise RuntimeError("Whisper model failed to load.")

            self._status("Transcribing locally...")
            segments, info = self._model.transcribe(
                audio,
                language=self.config.language,
                task="transcribe",
                beam_size=self.config.beam_size,
                vad_filter=self.config.vad_filter,
                condition_on_previous_text=self.config.condition_on_previous_text,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            self.last_used_at = time.time()

        return post_process_transcript(
            text,
            enable_spoken_punctuation=self.config.enable_spoken_punctuation,
            capitalize=self.config.capitalize_transcript,
        )

    def unload_if_idle(self) -> bool:
        if not self.config.unload_model_when_idle:
            return False
        if self._model is None:
            return False
        if time.time() - self.last_used_at < self.config.unload_after_seconds:
            return False

        with self._lock:
            self._model = None
            gc.collect()
        return True

    def _status(self, text: str) -> None:
        if self.status_callback:
            self.status_callback(text)
