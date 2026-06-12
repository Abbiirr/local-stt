#!/usr/bin/env sh
set -eu

echo "== Local Whisper Dictation Ubuntu validation =="

if ! command -v local-dictation >/dev/null 2>&1; then
  echo "local-dictation is not on PATH. Install the .deb first." >&2
  exit 1
fi

local-dictation --version
local-dictation print-config
local-dictation diagnostics

echo ""
echo "Optional model checks:"
echo "  CPU smoke: local-dictation smoke-model --model tiny --compute-type int8"
echo "  WAV smoke: local-dictation transcribe-wav /path/to/test.wav --expect-text 'expected text'"
echo ""
echo "Manual checks still required:"
echo "  1. Start: local-dictation run"
echo "  2. Confirm tray icon appears."
echo "  3. Use tray menu or hotkey to start recording."
echo "  4. Confirm overlay Stop/Pause controls work."
echo "  5. Confirm transcript pastes on X11, or remains on clipboard on unsupported Wayland injection."
