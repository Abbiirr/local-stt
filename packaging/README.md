# Packaging

The stable application behavior is locked as `v0.1-stable`. Packaging work must
preserve that baseline unless a verified regression is being fixed.

## Targets

| OS family | Format | Entry point | Notes |
| --- | --- | --- | --- |
| Windows GPU | PyInstaller `--onedir` ZIP | `Run Local Whisper Dictation.bat` | `large-v3`, CUDA, `float16`. |
| Windows CPU | PyInstaller `--onedir` ZIP | `Run Local Whisper Dictation.bat` | `small.en`, CPU, `int8`. |
| Ubuntu/Debian | `.deb` | `/usr/bin/local-dictation` | Installs app files under `/opt/local-whisper-dictation`. |
| Fedora | `.rpm` | `/usr/bin/local-dictation` | Uses the same `/opt` app layout. |

## Dependency Strategy

Python dependencies are installed into an isolated virtual environment under:

```text
/opt/local-whisper-dictation/.venv
```

Linux packages can include a wheelhouse at:

```text
/opt/local-whisper-dictation/wheelhouse
```

When present, installers use it with `--no-index`. If absent, installers fall
back to normal `pip install`, which requires internet access or a configured
local package mirror.

Model weights are not bundled by default. They are resolved from the normal
faster-whisper cache or app-local model folders named:

```text
models/faster-whisper-<model_name>
```

## Build Order

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition gpu -StartWithWindows
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition cpu
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition gpu
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition cpu
```

Uninstall the current-user Windows install:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\uninstall_current_user.ps1
```

Linux wheelhouse:

```sh
./packaging/linux/build_wheelhouse.sh
```

Debian/Ubuntu package:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip dpkg-dev
# Optional but recommended for repeatable dependency installs:
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_deb.sh
sudo apt install ./dist/local-whisper-dictation_0.1.0_amd64.deb
./packaging/linux/validate_ubuntu.sh
```

Remove:

```sh
sudo apt remove local-whisper-dictation
```

Fedora package:

```sh
./packaging/linux/build_rpm.sh
```

## Artifact Names

Windows:

```text
dist/LocalWhisperDictation/
dist/LocalWhisperDictationConsole/
dist/releases/LocalWhisperDictation-gpu.zip
dist/releases/LocalWhisperDictation-cpu.zip
```

Debian/Ubuntu:

```text
dist/local-whisper-dictation_0.1.0_amd64.deb
```

Fedora:

```text
dist/local-whisper-dictation-0.1.0-1*.noarch.rpm
```

## Linux Runtime Notes

The `.deb` package installs a CPU-safe default profile:

```text
model_name=small.en
device=cpu
compute_type=int8
```

Global hotkeys are best-effort on Linux. If global registration fails, use the
tray menu and overlay mouse controls. Focused-app insertion is also desktop
dependent: X11 uses `xdotool`, Wayland tries `wtype` when available, and if
desktop injection is blocked the transcript remains on the clipboard.
