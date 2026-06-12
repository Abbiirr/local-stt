#!/usr/bin/env sh
set -eu

APP_DIR="/opt/local-whisper-dictation"
PYTHON="$APP_DIR/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "Missing runtime: $PYTHON" >&2
  echo "Run the package post-install step or reinstall the package." >&2
  exit 1
fi

cd "$APP_DIR"
if [ -f "$APP_DIR/settings.json" ]; then
  export LOCAL_DICTATION_CONFIG="$APP_DIR/settings.json"
fi
exec "$PYTHON" -m local_dictation "$@"
