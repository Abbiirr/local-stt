#!/usr/bin/env sh
set -eu

APP_DIR="/opt/local-whisper-dictation"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if [ ! -d "$APP_DIR/.venv" ]; then
  "$PYTHON_BIN" -m venv "$APP_DIR/.venv"
fi

"$APP_DIR/.venv/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true

if [ -d "$APP_DIR/wheelhouse" ] && [ "$(find "$APP_DIR/wheelhouse" -type f | wc -l)" -gt 0 ]; then
  "$APP_DIR/.venv/bin/python" -m pip install --no-index --find-links "$APP_DIR/wheelhouse" -r "$APP_DIR/requirements.txt"
else
  "$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"
fi

"$APP_DIR/.venv/bin/python" -m pip install --no-deps -e "$APP_DIR"
