from __future__ import annotations

import platform
import subprocess
import time
import wave
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import sounddevice as sd

from .audio import AudioRecorder, rms_to_level
from .config import AppConfig, default_config_path, effective_config_path
from .transcriber import WhisperTranscriber


def collect_diagnostics() -> str:
    lines: list[str] = []
    lines.append("Local Dictation Diagnostics")
    lines.append(f"Python: {platform.python_version()} ({platform.python_implementation()})")
    lines.append(f"Platform: {platform.platform()}")
    lines.append(f"Config path: {effective_config_path()}")
    lines.append(f"User config path: {default_config_path()}")
    lines.append("")
    lines.append("NVIDIA:")
    lines.extend(_indent(_run_command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])))
    lines.append("")
    lines.append("CTranslate2 CUDA:")
    lines.extend(_indent(_ctranslate2_status()))
    lines.append("")
    lines.append("Audio devices:")
    lines.extend(_indent(str(sd.query_devices()).splitlines()))
    return "\n".join(lines)


def run_cuda_smoke(model_name: str, device: str, compute_type: str) -> str:
    from faster_whisper import WhisperModel

    from .config import resolve_model_name

    resolved_model_name = resolve_model_name(model_name)
    model = WhisperModel(resolved_model_name, device=device, compute_type=compute_type)
    del model
    return f"Loaded faster-whisper model '{resolved_model_name}' on {device} with {compute_type}."


def run_microphone_smoke(config: AppConfig, seconds: float = 1.5) -> str:
    levels: list[float] = []
    recorder = AudioRecorder(config, level_callback=levels.append)
    audio = recorder.record_for(seconds)
    duration = len(audio) / config.sample_rate if audio.size else 0.0
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    rms_level = rms_to_level(audio, config.waveform_level_gain) if audio.size else 0.0
    return (
        f"Captured {duration:.2f}s from microphone; "
        f"samples={audio.size}; peak={peak:.4f}; level={rms_level:.4f}; "
        f"callbacks={len(levels)}."
    )


def run_wav_transcription_smoke(
    config: AppConfig,
    wav_path: Path,
    expected_text: str | None = None,
    repeat_to_seconds: float | None = None,
) -> str:
    audio = load_wav_mono_float32(wav_path, target_sample_rate=config.sample_rate)
    if repeat_to_seconds and repeat_to_seconds > 0:
        audio = repeat_audio_to_duration(audio, config.sample_rate, repeat_to_seconds)

    duration = len(audio) / config.sample_rate if audio.size else 0.0
    transcriber = WhisperTranscriber(config)
    started_at = time.perf_counter()
    text = transcriber.transcribe(audio)
    elapsed = time.perf_counter() - started_at
    realtime_factor = duration / elapsed if elapsed > 0 else 0.0

    lines = [
        f"File: {wav_path}",
        f"Duration: {duration:.2f}s",
        f"Elapsed: {elapsed:.2f}s",
        f"Realtime factor: {realtime_factor:.2f}x",
        f"Text: {text}",
    ]

    if expected_text is not None:
        normalized_text = _normalize_for_compare(text)
        normalized_expected = _normalize_for_compare(expected_text)
        if normalized_text != normalized_expected:
            raise AssertionError(f"Expected {expected_text!r}, got {text!r}")
        lines.append("Expected text: matched")

    return "\n".join(lines)


def run_nonspeech_smoke(config: AppConfig, seconds: float = 5.0, noise_amplitude: float = 0.002) -> str:
    sample_count = max(1, int(config.sample_rate * seconds))
    transcriber = WhisperTranscriber(config)

    silence = np.zeros(sample_count, dtype=np.float32)
    noise_rng = np.random.default_rng(0)
    noise = noise_rng.normal(0.0, noise_amplitude, sample_count).astype(np.float32)

    started_at = time.perf_counter()
    silence_text = transcriber.transcribe(silence)
    noise_text = transcriber.transcribe(noise)
    elapsed = time.perf_counter() - started_at

    if silence_text.strip():
        raise AssertionError(f"Silence produced text: {silence_text!r}")
    if noise_text.strip():
        raise AssertionError(f"Noise produced text: {noise_text!r}")

    return (
        f"Silence/noise smoke passed for {seconds:.2f}s clips; "
        f"noise_amplitude={noise_amplitude}; elapsed={elapsed:.2f}s."
    )


def load_wav_mono_float32(path: Path, target_sample_rate: int) -> np.ndarray:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())

    if sample_width == 1:
        data = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sample_width == 2:
        data = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 3:
        raw = np.frombuffer(frames, dtype=np.uint8).reshape(-1, 3)
        values = (
            raw[:, 0].astype(np.int32)
            | (raw[:, 1].astype(np.int32) << 8)
            | (raw[:, 2].astype(np.int32) << 16)
        )
        values = np.where(values & 0x800000, values | ~0xFFFFFF, values)
        data = values.astype(np.float32) / 8388608.0
    elif sample_width == 4:
        data = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported WAV sample width: {sample_width}")

    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)

    if sample_rate != target_sample_rate and data.size:
        data = _resample_linear(data, sample_rate, target_sample_rate)

    return data.astype(np.float32)


def repeat_audio_to_duration(audio: np.ndarray, sample_rate: int, duration_seconds: float) -> np.ndarray:
    target_samples = max(1, int(sample_rate * duration_seconds))
    if audio.size == 0:
        return np.zeros(target_samples, dtype=np.float32)
    repeats = int(np.ceil(target_samples / audio.size))
    return np.tile(audio, repeats)[:target_samples].astype(np.float32)


def _run_command(command: list[str]) -> list[str]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
    except FileNotFoundError:
        return [f"{command[0]} not found."]
    except subprocess.TimeoutExpired:
        return [f"{command[0]} timed out."]

    output = (completed.stdout or completed.stderr).strip()
    if not output:
        return [f"{command[0]} exited with code {completed.returncode} and no output."]
    return output.splitlines()


def _ctranslate2_status() -> list[str]:
    try:
        import ctranslate2
    except Exception as exc:
        return [f"ctranslate2 import failed: {exc}"]

    try:
        count = ctranslate2.get_cuda_device_count()
        compute_types = sorted(ctranslate2.get_supported_compute_types("cuda")) if count else []
        return [f"cuda devices: {count}", f"supported compute: {compute_types}"]
    except Exception as exc:
        return [f"CUDA check failed: {exc}"]


def _indent(lines: Iterable[str]) -> list[str]:
    return [f"  {line}" for line in lines]


def _resample_linear(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    source_positions = np.arange(audio.size, dtype=np.float64)
    target_size = max(1, int(round(audio.size * target_rate / source_rate)))
    target_positions = np.linspace(0, audio.size - 1, target_size, dtype=np.float64)
    return np.interp(target_positions, source_positions, audio).astype(np.float32)


def _normalize_for_compare(text: str) -> str:
    return " ".join(text.strip().lower().split())
