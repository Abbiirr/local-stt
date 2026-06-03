from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any


APP_NAME = "LocalWhisperDictation"


@dataclass(slots=True)
class AppConfig:
    hotkey_toggle: str = "ctrl+alt+d"
    hotkey_cancel: str = "esc"
    model_name: str = "large-v3"
    device: str = "cuda"
    compute_type: str = "float16"
    language: str | None = "en"
    beam_size: int = 5
    vad_filter: bool = True
    condition_on_previous_text: bool = False
    sample_rate: int = 16000
    channels: int = 1
    block_size: int = 1024
    input_device: int | str | None = None
    minimum_duration_seconds: float = 0.4
    auto_paste: bool = True
    restore_clipboard_after_paste: bool = True
    paste_delay_seconds: float = 0.05
    clipboard_restore_delay_seconds: float = 0.25
    preload_model: bool = False
    unload_model_when_idle: bool = True
    unload_after_seconds: int = 5 * 60
    overlay_fps: int = 30
    waveform_level_gain: float = 14.0
    append_trailing_space: bool = True
    capitalize_transcript: bool = True
    enable_spoken_punctuation: bool = False
    type_text_instead_of_paste: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        valid_names = {field.name for field in fields(cls)}
        filtered = {key: value for key, value in data.items() if key in valid_names}
        return cls(**filtered)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def config_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def default_config_path() -> Path:
    return config_dir() / "settings.json"


def load_config(path: Path | None = None) -> AppConfig:
    target = path or default_config_path()
    if not target.exists():
        return AppConfig()

    with target.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {target}")

    return AppConfig.from_dict(data)


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    target = path or default_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(config.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return target


def resolve_model_name(model_name: str) -> str:
    path = Path(model_name).expanduser()
    roots = _candidate_roots()

    if path.is_absolute():
        return str(path)

    for root in roots:
        candidate = root / path
        if candidate.exists():
            return str(candidate)

    local_dir_name = f"faster-whisper-{model_name}"
    for root in roots:
        candidate = root / "models" / local_dir_name
        if candidate.exists():
            return str(candidate)

    return model_name


def _candidate_roots() -> tuple[Path, ...]:
    roots: list[Path] = [Path.cwd()]

    env_model_root = os.environ.get("LOCAL_WHISPER_MODEL_ROOT")
    if env_model_root:
        roots.append(Path(env_model_root).expanduser())

    module_path = Path(__file__).resolve()
    roots.extend(module_path.parents[:4])

    if getattr(sys, "frozen", False):
        executable_path = Path(sys.executable).resolve()
        roots.extend(executable_path.parents[:4])

    unique_roots: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            resolved = root
        if resolved not in seen:
            seen.add(resolved)
            unique_roots.append(resolved)

    return tuple(unique_roots)
