from __future__ import annotations

import json
import wave
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .config import AppConfig, config_dir


@dataclass(slots=True)
class HistoryEntry:
    id: str
    created_at: str
    status: str
    sample_rate: int
    duration_seconds: float
    model_name: str
    device: str
    compute_type: str
    language: str | None
    audio_path: str
    transcript_path: str | None = None
    error_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HistoryEntry":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def history_dir() -> Path:
    return config_dir() / "history"


def create_history_entry(audio: np.ndarray, config: AppConfig, status: str = "recorded") -> HistoryEntry | None:
    if not config.history_enabled:
        return None

    now = datetime.now(timezone.utc)
    entry_id = now.strftime("%Y%m%dT%H%M%S.%fZ")
    entry_dir = history_dir() / entry_id
    entry_dir.mkdir(parents=True, exist_ok=False)

    audio_path = entry_dir / "audio.wav"
    _write_wav(audio_path, audio, config.sample_rate)

    entry = HistoryEntry(
        id=entry_id,
        created_at=now.isoformat(),
        status=status,
        sample_rate=config.sample_rate,
        duration_seconds=len(audio) / config.sample_rate if audio.size else 0.0,
        model_name=config.model_name,
        device=config.device,
        compute_type=config.compute_type,
        language=config.language,
        audio_path=str(audio_path),
    )
    save_history_entry(entry)
    return entry


def save_history_entry(entry: HistoryEntry) -> None:
    path = history_dir() / entry.id / "metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_history_transcript(entry: HistoryEntry | None, text: str) -> None:
    if entry is None:
        return
    entry_dir = history_dir() / entry.id
    transcript_path = entry_dir / "transcript.txt"
    transcript_path.write_text(text, encoding="utf-8")
    entry.transcript_path = str(transcript_path)
    entry.status = "transcribed" if text.strip() else "empty"
    save_history_entry(entry)


def update_history_error(entry: HistoryEntry | None, error: str) -> None:
    if entry is None:
        return
    entry_dir = history_dir() / entry.id
    error_path = entry_dir / "error.txt"
    error_path.write_text(error, encoding="utf-8")
    entry.error_path = str(error_path)
    entry.status = "failed"
    save_history_entry(entry)


def update_history_status(entry: HistoryEntry | None, status: str) -> None:
    if entry is None:
        return
    entry.status = status
    save_history_entry(entry)


def list_history_entries(limit: int | None = None) -> list[HistoryEntry]:
    root = history_dir()
    if not root.exists():
        return []

    entries: list[HistoryEntry] = []
    for metadata_path in sorted(root.glob("*/metadata.json"), reverse=True):
        try:
            entries.append(HistoryEntry.from_dict(json.loads(metadata_path.read_text(encoding="utf-8"))))
        except Exception:
            continue
        if limit is not None and len(entries) >= limit:
            break
    return entries


def load_history_entry(entry_id: str) -> HistoryEntry:
    metadata_path = history_dir() / entry_id / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"History entry not found: {entry_id}")
    return HistoryEntry.from_dict(json.loads(metadata_path.read_text(encoding="utf-8")))


def _write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    clipped = np.clip(audio.astype(np.float32), -1.0, 1.0)
    samples = (clipped * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(samples.tobytes())
