# Stable Version Lock

Stable label: `v0.1-stable`

Lock date: 2026-06-03

## Scope

This lock covers the current Windows local dictation app:

- PySide6 tray app.
- Draggable and closable waveform/status overlay.
- `Ctrl+Alt+Space` start/stop.
- `Esc` cancel while recording.
- English-only faster-whisper `large-v3`.
- CUDA `float16`.
- Local model resolution through `models\faster-whisper-large-v3`.
- Clipboard paste with optional typing fallback.
- Rotating app log at `%APPDATA%\LocalWhisperDictation\app.log`.
- PyInstaller `--onedir` windowed and console builds.

## Verification

Latest stable-lock verification:

- `python -m compileall -q src tests`: pass.
- `python -m unittest discover -s tests -v`: 23/23 pass.
- `dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe print-config`: pass.
- `dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."`: pass in 26.52s, expected text matched.
- `dist\LocalWhisperDictation\LocalWhisperDictation.exe` startup smoke: pass; process stayed alive and wrote startup entries to `%APPDATA%\LocalWhisperDictation\app.log`.

## Change Rule

Do not change core dictation behavior during the packaging/distribution phase
unless fixing a verified regression. Packaging work should preserve this baseline.

Archived baseline docs:

```text
archive\2026-06-03-v0.1-stable-lock
```
