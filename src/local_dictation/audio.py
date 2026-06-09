from __future__ import annotations

import threading
import time
from collections.abc import Callable

import numpy as np
import sounddevice as sd

from .config import AppConfig


LevelCallback = Callable[[float], None]


def rms_to_level(data: np.ndarray, gain: float) -> float:
    if data.size == 0:
        return 0.0
    rms = float(np.sqrt(np.mean(np.square(data))))
    return max(0.0, min(1.0, rms * gain))


class AudioRecorder:
    def __init__(self, config: AppConfig, level_callback: LevelCallback | None = None):
        self.config = config
        self.level_callback = level_callback
        self._stream: sd.InputStream | None = None
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._recording = False
        self._paused = False

    @property
    def recording(self) -> bool:
        return self._recording

    @property
    def paused(self) -> bool:
        return self._paused

    def start(self) -> None:
        if self._recording:
            return

        with self._lock:
            self._frames = []

        self._recording = True
        self._paused = False
        try:
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype="float32",
                blocksize=self.config.block_size,
                device=self.config.input_device,
                callback=self._callback,
            )
            self._stream.start()
        except Exception:
            self._recording = False
            self._stream = None
            raise

    def stop(self) -> np.ndarray:
        if not self._recording:
            return np.empty((0,), dtype=np.float32)

        self._recording = False
        self._paused = False
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
        finally:
            self._stream = None

        with self._lock:
            if not self._frames:
                return np.empty((0,), dtype=np.float32)
            audio = np.concatenate(self._frames, axis=0).flatten().astype(np.float32)
            self._frames = []
            return audio

    def cancel(self) -> None:
        self._recording = False
        self._paused = False
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
        finally:
            self._stream = None

        with self._lock:
            self._frames = []

    def record_for(self, seconds: float) -> np.ndarray:
        self.start()
        time.sleep(max(0.0, seconds))
        return self.stop()

    def pause(self) -> None:
        if self._recording:
            self._paused = True
            if self.level_callback:
                self.level_callback(0.0)

    def resume(self) -> None:
        if self._recording:
            self._paused = False

    def _callback(self, indata, frames, time_info, status) -> None:
        if not self._recording:
            return

        if self._paused:
            if self.level_callback:
                self.level_callback(0.0)
            return

        data = indata.copy()
        with self._lock:
            self._frames.append(data)

        if self.level_callback:
            self.level_callback(rms_to_level(data, self.config.waveform_level_gain))
