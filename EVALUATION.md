# Evaluation And Verification Log

## Decision

Selected path: **Path C - Build custom app**.

Public candidates are deferred because the custom implementation now satisfies
the requested architecture and passes the available local validation gates.

```text
tray app -> global hotkey -> waveform overlay -> local CUDA Whisper -> paste
```

## Local Baseline

- OS: Windows 10 Home, version 2009, build 19045.
- Python used: CPython 3.11.13.
- Python launchers: Python 3.12 default, uv CPython 3.11.13 available.
- GPU: NVIDIA GeForce RTX 4060 Ti.
- NVIDIA driver: 576.40.
- CUDA shown by driver: 12.9.
- VRAM: 16380 MiB.
- CTranslate2 CUDA devices: 1.
- CTranslate2 CUDA compute support includes `float16` and `int8_float16`.
- Default microphone detected: `Microphone (4- USB Audio Device), MME`.
- Settings path: `%APPDATA%\LocalWhisperDictation\settings.json`.
- Current language scope: English-only (`language = "en"`).

## Implemented App

Code location:

```text
K:\projects\ai\stt\src\local_dictation
```

Main entrypoints:

```text
K:\projects\ai\stt\run.bat
K:\projects\ai\stt\install.bat
python -m local_dictation run
```

Packaged entrypoints:

```text
K:\projects\ai\stt\dist\LocalWhisperDictation\LocalWhisperDictation.exe
K:\projects\ai\stt\dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe
```

Implemented features:

- PySide6 tray app.
- Small waveform/status overlay.
- Global hotkey bridge through Qt signals.
- `Ctrl+Alt+D` start/stop.
- `Esc` cancel.
- Microphone capture only while recording.
- faster-whisper transcription through CTranslate2.
- CUDA + `float16`.
- Local `large-v3` model.
- Clipboard paste into focused app.
- Clipboard restore after paste.
- JSON settings under `%APPDATA%`.
- Local history under `%APPDATA%\LocalWhisperDictation\history` for recovery.
- Diagnostics commands.
- Startup shortcut scripts.
- PyInstaller `--onedir` packaging.

## Model

Downloaded model directory:

```text
K:\projects\ai\stt\models\faster-whisper-large-v3
```

Model files:

- `model.bin`: 2944.26 MB.
- `tokenizer.json`: 2.37 MB.
- `vocabulary.json`: 1.02 MB.
- `config.json`.
- `preprocessor_config.json`.

The active settings file uses portable `model_name = "large-v3"`. At runtime,
that resolves to `models\faster-whisper-large-v3` when the local model directory
exists. It also sets `language` to `en`; Bangla and mixed English/Bangla
validation are deferred to a later milestone.

## Automated Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Dependency install | Pass | `pip install -r requirements.txt` completed. |
| Editable package install | Pass | `pip install -e .` completed. |
| Syntax compile | Pass | `python -m compileall -q src tests`. |
| Unit tests | Pass | `37 tests` passed. |
| Diagnostics | Pass | CUDA device and microphone reported. |
| CUDA tiny smoke test | Pass | `tiny` loaded on CUDA with `float16`. |
| CUDA large-v3 smoke test | Pass | Local `large-v3` loaded on CUDA with `float16`. |
| Large-v3 transcription | Pass | Generated WAV transcribed exactly: `The quick brown fox jumps over the lazy dog near the riverbank.` |
| Microphone smoke test | Pass | Captured microphone samples without saving audio. |
| Tray startup smoke test | Pass | App stayed running for the test window. |
| Packaged diagnostics | Pass | Console EXE reported CUDA and microphone. |
| Packaged tiny CUDA | Pass | Console EXE loaded `tiny` on CUDA. |
| Packaged large-v3 CUDA | Pass | Console EXE loaded local `large-v3` on CUDA. |
| Packaged WAV transcription | Pass | Console EXE transcribed generated WAV exactly after bundling `faster_whisper` data. |
| Packaged windowed startup | Pass | Windowed EXE stayed running for the test window. |
| Notepad paste | Pass | Inserted `Local dictation paste test` into Notepad and verified copied content. |
| Hotkey start/cancel | Pass | `Ctrl+Alt+D` then `Esc` left app running without crash. |
| Startup shortcut | Pass | Created in user Startup folder. |
| Network observation | Pass, limited | No established TCP connections observed during local transcription. |
| Firewall-block proof | Not run | `New-NetFirewallRule` failed with `Access is denied`. |
| Text post-processing regression | Pass | Preserves `3,250`, `19.99`, `john.doe@example.com`, `p.m.`, and literal `period`/`comma`. |
| Portable model resolution | Pass | `large-v3` resolves to the local project model directory when present. |
| Direct WAV transcription | Pass | Generated English WAV matched expected text exactly. |
| Synthetic non-speech | Pass | 5-second silence and white-noise clips produced no transcript. |
| 60-second generated latency | Pass | 60.00s repeated WAV transcribed in 56.31s, 1.07x realtime including model load. |
| CLI version | Pass | `python -m local_dictation --version` prints `local-dictation 0.1.0`. |
| Python wheel package | Pass | `pip wheel --no-deps . -w build\wheel-smoke` built `local_whisper_dictation-0.1.0-py3-none-any.whl`. |
| Windows install script syntax | Pass | PowerShell AST parser accepted `packaging\windows\*.ps1`. |
| Windows current-user install | Pass | Copied onedir build to `%LOCALAPPDATA%\Programs\LocalWhisperDictation` and created Start Menu shortcut. |
| Overlay mouse controls | Pass, automated boundary | Unit test verifies paused audio is discarded until resume; packaged app starts after adding Pause/Resume/Stop controls. |
| Model-agnostic profiles | Pass | GPU and CPU profile JSON files load through `AppConfig`; packaged app can read edition-local `settings.json`. |
| Windows CPU/GPU ZIPs | Pass | Created `dist\releases\LocalWhisperDictation-cpu.zip` and `dist\releases\LocalWhisperDictation-gpu.zip`, each with edition-local settings and launcher. |
| CPU transcription runtime | Not run | `small.en` CPU model is not downloaded/validated on this machine yet. |
| Linux package script syntax | Not run here | Local `bash.exe` is a broken WSL shim; validate on Ubuntu/Debian/Fedora. |
| Ubuntu `.deb` hardening | Pass, static | `.deb` now ships CPU-safe settings, launcher-enforced config, desktop entry, Qt/XCB/audio/clipboard/input dependencies, and validation script. |
| Linux insertion fallback | Pass, unit | X11 `xdotool` path, missing-tool clipboard fallback, and failed-injection fallback are covered by unit tests. |
| History recovery layer | Pass, unit | Saved WAV metadata, transcript/error updates, listing, and disabled-history behavior are covered by tests. |

## Current Verdict

The implementation works for the local model, CUDA, microphone capture,
transcription engine, tray startup, Windows packaging/install, startup shortcut, hotkey
start/cancel, paste insertion path, local model resolution, and safer text
post-processing defaults.

Remaining validation is Linux-target and user-interactive: `.deb` build/install
on Ubuntu/Debian, `.rpm` build/install on Fedora, Linux tray/hotkey behavior,
real spoken dictation into the target apps, one-minute live tray latency,
real-room silence/noise behavior, and confirmation after the next reboot.
