from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO


APP_NAME = "LocalWhisperDictation"
ENV_LOCK_HELD = "LOCAL_DICTATION_INSTANCE_LOCK_HELD"
LOCK_FILE_NAME = "app.lock"

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def should_lock_for_argv(argv: list[str]) -> bool:
    command = argv[1] if len(argv) > 1 else "run"
    return command == "run"


def bootstrap_lock_is_held() -> bool:
    return os.environ.get(ENV_LOCK_HELD) == "1"


def mark_bootstrap_lock_held() -> None:
    os.environ[ENV_LOCK_HELD] = "1"


def acquire_lock(logger=None) -> tuple[BinaryIO | None, bool]:
    lock_path = _lock_dir() / LOCK_FILE_NAME
    handle: BinaryIO | None = None
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = lock_path.open("a+b")
        handle.seek(0)

        if os.name == "nt":
            handle.write(b"0")
            handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        return handle, False
    except OSError:
        if handle is not None:
            try:
                handle.close()
            except Exception:
                pass
        if logger is not None:
            logger.info("Another Local Whisper Dictation instance is already running.")
        return None, True
    except Exception:
        if logger is not None:
            logger.exception("Single-instance guard is unavailable.")
        return None, False


def release_lock(handle: BinaryIO, logger=None) -> None:
    try:
        handle.seek(0)
        if os.name == "nt":
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
    except Exception:
        if logger is not None:
            logger.exception("Failed to release single-instance lock.")


def _lock_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / APP_NAME

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / APP_NAME

    return Path.home() / ".config" / APP_NAME
