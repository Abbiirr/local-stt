#!/usr/bin/env sh
set -eu

APP_DIR="/opt/local-whisper-dictation"

if [ "${1:-}" = "remove" ] || [ "${1:-}" = "purge" ] || [ "${1:-}" = "0" ]; then
  rm -rf "$APP_DIR/.venv"
fi
