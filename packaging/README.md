# Packaging

The stable application behavior is locked as `v0.1-stable`. Packaging work must
preserve that baseline unless a verified regression is being fixed.

## Targets

| OS family | Format | Entry point | Notes |
| --- | --- | --- | --- |
| Windows | PyInstaller `--onedir` | `LocalWhisperDictation.exe` | Current stable path. |
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

Model weights are not bundled. They are resolved from the normal faster-whisper
cache or an app-local `models/faster-whisper-large-v3` directory.

## Build Order

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -StartWithWindows
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
./packaging/linux/build_deb.sh
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

The current code remains the Windows-proven baseline. Linux packaging is the next
distribution layer; global hotkeys, tray behavior, and focused-app text insertion
still need distro/desktop validation, especially on Wayland.
