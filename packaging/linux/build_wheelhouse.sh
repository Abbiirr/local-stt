#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
OUT_DIR="$ROOT_DIR/dist/wheelhouse"

mkdir -p "$OUT_DIR"
python3 -m pip download -r "$ROOT_DIR/requirements.txt" -d "$OUT_DIR"

echo "Wheelhouse written to $OUT_DIR"
