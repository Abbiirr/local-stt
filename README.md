# Local Whisper Dictation

Local tray dictation app for speech-to-text. The stable baseline is currently
validated on Windows; Linux packaging for Ubuntu, Debian, and Fedora is in
progress.

Build and package instructions for a fresh clone are in [BUILD.md](BUILD.md).

Default behavior:

```text
Ctrl+Alt+D = start recording
Ctrl+Alt+D = stop, transcribe locally, paste into focused app
Esc        = cancel current recording
```

The waveform overlay can be dragged by holding the overlay body. Use the `X`
button on the overlay to close it; while recording, this cancels the recording.
While transcribing, it hides the overlay and lets transcription continue.
While recording, the overlay also shows mouse controls:

```text
Pause  = temporarily discard incoming audio until resumed
Resume = continue recording after pause
Stop   = stop recording and start local transcription
```

The app records only while active. It uses `faster-whisper` with CUDA by default,
targets `large-v3` with `float16` on an RTX 4060 Ti 16 GB, and forces English
transcription for the current milestone (`language = "en"`). Bangla and mixed
English/Bangla dictation are deferred. Spoken punctuation commands are off by
default so ordinary words like "period" and "comma" are not silently rewritten.

## Install

Use Python 3.11.

```powershell
cd K:\projects\ai\stt
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

If `py -3.11` does not resolve on this machine, use the installed 3.11 runtime:

```powershell
& 'C:\Users\abirh\AppData\Roaming\uv\python\cpython-3.11.13-windows-x86_64-none\python.exe' -m venv .venv
```

## Run

```powershell
.\run.bat
```

or:

```powershell
.\.venv\Scripts\python.exe -m local_dictation run
```

## Diagnostics

```powershell
.\.venv\Scripts\python.exe -m local_dictation diagnostics
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model tiny
.\.venv\Scripts\python.exe -m local_dictation smoke-mic --seconds 1.5
.\.venv\Scripts\python.exe -m local_dictation transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."
.\.venv\Scripts\python.exe -m local_dictation smoke-nonspeech --seconds 5
```

The local model is expected at `models\faster-whisper-large-v3`. If that
directory exists, `--model large-v3` resolves to it before falling back to a
Hugging Face model id.

To pre-download the default model into the project-local model directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_large_v3.ps1
```

To validate the default model from Hugging Face cache or local model path:

```powershell
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model large-v3
```

The model loader is config-driven. To validate whichever device/compute profile
is active:

```powershell
.\.venv\Scripts\python.exe -m local_dictation smoke-model --model tiny
```

This can take a while on the first run because the model is several GB.

To measure model-only latency without using the microphone:

```powershell
.\.venv\Scripts\python.exe -m local_dictation transcribe-wav artifacts\en_test.wav --repeat-to-seconds 60
```

## Packaged Build

Build both the windowed tray app and a console diagnostic executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_onedir.ps1
```

The build script includes `faster_whisper` data files so packaged transcription
can use the bundled Silero VAD model.

Outputs:

```text
dist\LocalWhisperDictation\LocalWhisperDictation.exe
dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe
```

## Installable Packages

Packaging assets live under:

```text
packaging\
```

Windows current-user install:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition gpu -StartWithWindows
```

Windows CPU current-user install:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition cpu
```

Windows uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\uninstall_current_user.ps1
```

Debian/Ubuntu package build on Linux:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip dpkg-dev
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_deb.sh
sudo apt install ./dist/local-whisper-dictation_0.1.0_amd64.deb
./packaging/linux/validate_ubuntu.sh
```

Remove the Ubuntu/Debian package:

```sh
sudo apt remove local-whisper-dictation
```

See [docs/UBUNTU.md](docs/UBUNTU.md) for the target-machine validation protocol.

Fedora package build on Linux:

```sh
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_rpm.sh
```

Linux packages install the app under `/opt/local-whisper-dictation` and expose:

```sh
local-dictation run
local-dictation diagnostics
local-dictation --version
```

The Ubuntu/Debian package installs a CPU-safe profile by default:

```json
{
  "model_name": "small.en",
  "device": "cpu",
  "compute_type": "int8",
  "beam_size": 1
}
```

Desktop hotkeys, focused-app insertion, tray behavior, microphone access, and
CUDA runtime setup still need verification on each target desktop environment.
On Linux, tray menu and overlay mouse controls are the fallback if global hotkeys
are blocked. Text insertion uses `xdotool` on X11 or `wtype` on Wayland when
available; otherwise the transcript remains on the clipboard.

## Windows ZIP Distribution

The app is distributed as a folder, not as one standalone EXE. To create ZIPs:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition gpu
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition cpu
```

Outputs:

```text
dist\releases\LocalWhisperDictation-gpu.zip
dist\releases\LocalWhisperDictation-cpu.zip
```

Recipients should extract the ZIP and run:

```text
Run Local Whisper Dictation.bat
```

The launcher forces the packaged `settings.json`, so the CPU edition uses CPU
settings even if the user previously had GPU settings elsewhere.

GPU edition profile:

```json
{
  "model_name": "large-v3",
  "device": "cuda",
  "compute_type": "float16"
}
```

CPU edition profile:

```json
{
  "model_name": "small.en",
  "device": "cpu",
  "compute_type": "int8",
  "beam_size": 1
}
```

To swap models, edit `settings.json` and change `model_name`, `device`, and
`compute_type`. Local faster-whisper model folders are resolved from:

```text
models\faster-whisper-<model_name>
```

Examples:

```text
models\faster-whisper-small.en
models\faster-whisper-base.en
models\faster-whisper-large-v3
```

To download a model into the project-local `models` folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_model.ps1 -ModelName small.en
```

## Start With Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_startup_shortcut.ps1
```

Remove it:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\remove_startup_shortcut.ps1
```

## Settings

Write the default settings file:

```powershell
.\.venv\Scripts\python.exe -m local_dictation write-default-config
```

Settings are stored under:

```text
%APPDATA%\LocalWhisperDictation\settings.json
```

On Linux, settings are stored under:

```text
$XDG_CONFIG_HOME/LocalWhisperDictation/settings.json
```

or, when `XDG_CONFIG_HOME` is not set:

```text
~/.config/LocalWhisperDictation/settings.json
```

Runtime logs are written under:

```text
%APPDATA%\LocalWhisperDictation\app.log
```

On Linux, logs use the same config directory:

```text
~/.config/LocalWhisperDictation/app.log
```

Current default language:

```json
"language": "en"
```

Recommended current settings:

```json
{
  "model_name": "large-v3",
  "language": "en",
  "compute_type": "float16",
  "unload_model_when_idle": true,
  "unload_after_seconds": 300,
  "enable_spoken_punctuation": false,
  "type_text_instead_of_paste": false
}
```

Set `enable_spoken_punctuation` to `true` only if you explicitly want commands
such as "new line" or "comma" rewritten. Set `type_text_instead_of_paste` to
`true` only for target apps where clipboard paste is blocked.
