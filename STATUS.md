# Implementation Status

Status date: 2026-06-03

## Summary

The custom local dictation app is implemented, packaged, and configured to use a
project-local `large-v3` model on CUDA with `float16`. The current language
scope is English-only: `language = "en"`.

The active runtime settings file is:

```text
%APPDATA%\LocalWhisperDictation\settings.json
```

Its `model_name` is portable:

```text
large-v3
```

At runtime, `large-v3` resolves to `models\faster-whisper-large-v3` when that
local directory exists.

## Verified

- Dependencies installed in `.venv`.
- App package installed editable.
- `large-v3` downloaded locally.
- `large-v3` loads on CUDA with `float16`.
- `large-v3` transcribes generated WAV audio correctly.
- Runtime language is set to English-only for the current milestone.
- Rotating app log is written to `%APPDATA%\LocalWhisperDictation\app.log`.
- Packaged tray app created the rotating app log and wrote startup entries.
- Hotkey registration failures are handled without crashing the tray app.
- Spoken punctuation is opt-in, so words like `period` and `comma` remain literal by default.
- Number/email post-processing regressions are covered and passing.
- Model unloads after 5 idle minutes by default.
- CTranslate2 sees one CUDA device.
- Microphone smoke capture works.
- Tray app starts and stays running.
- Waveform/status overlay is draggable and has an `X` close control.
- Waveform/status overlay has mouse `Pause`/`Resume` and `Stop` controls while recording.
- Windowed packaged EXE starts and stays running.
- Windowed packaged EXE is currently running from `dist\LocalWhisperDictation`.
- Console packaged EXE runs diagnostics.
- Console packaged EXE loads `tiny` on CUDA.
- Console packaged EXE loads local `large-v3` on CUDA.
- Console packaged EXE transcribes generated WAV audio with the bundled VAD asset.
- Direct WAV transcription smoke matches generated English test audio.
- Synthetic silence/noise smoke produces no transcript.
- 60-second repeated generated WAV latency: 56.31s elapsed, 1.07x realtime including model load.
- Notepad paste path works.
- Global hotkey start/cancel cycle works without crash.
- Startup shortcut exists.
- No established TCP connections were observed during local large-v3 transcription.
- Python package wheel smoke builds successfully.
- Windows current-user installer copies the onedir build to `%LOCALAPPDATA%\Programs\LocalWhisperDictation`.
- Windows current-user installer creates a Start Menu shortcut.
- Unit tests: 26 passed.

## Not Fully Automatable Here

- Real user speech through the tray workflow.
- Browser, notes app, and VS Code focused-app confirmation.
- One-minute real spoken latency through the tray workflow.
- Real-room silence/noise behavior through the tray workflow.
- Clean reboot startup confirmation.
- Admin firewall-block proof, because firewall rule creation returned `Access is denied`.
- Linux `.deb` and `.rpm` package builds, because this machine does not have a working Linux shell/package toolchain.

Deferred to a later milestone:

- Bangla or mixed-language spoken dictation by the user.

## Run

```powershell
cd K:\projects\ai\stt
.\run.bat
```

Hotkeys:

```text
Ctrl+Alt+D = start/stop dictation
Esc        = cancel recording
```

Packaged app:

```powershell
K:\projects\ai\stt\dist\LocalWhisperDictation\LocalWhisperDictation.exe
```

Console diagnostics:

```powershell
K:\projects\ai\stt\dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe diagnostics
```
