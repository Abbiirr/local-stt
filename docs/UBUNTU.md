# Ubuntu Install And Validation

Status: ready for Ubuntu target-machine validation.

The Ubuntu package installs a CPU-safe default profile:

```text
model_name=small.en
device=cpu
compute_type=int8
beam_size=1
```

## Build

Run on Ubuntu from the repo root:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip dpkg-dev
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_deb.sh
```

Expected artifact:

```text
dist/local-whisper-dictation_0.1.0_amd64.deb
```

## Install

```sh
sudo apt install ./dist/local-whisper-dictation_0.1.0_amd64.deb
```

The package installs:

```text
/opt/local-whisper-dictation
/usr/bin/local-dictation
/usr/share/applications/local-whisper-dictation.desktop
```

## Validate

```sh
./packaging/linux/validate_ubuntu.sh
local-dictation smoke-model --model tiny --compute-type int8
```

Then run the GUI:

```sh
local-dictation run
```

Manual checks:

- Tray icon appears.
- Start/stop works from the tray menu.
- Overlay `Pause`, `Resume`, and `Stop` controls work.
- Microphone recording starts only after explicit user action.
- Transcript appears in the focused app on X11.
- On Wayland, if paste injection is blocked, transcript remains on clipboard.

## Remove

```sh
sudo apt remove local-whisper-dictation
```

## Notes

Global hotkeys are best-effort on Linux. Use tray menu and overlay buttons as
the reliable fallback.

The first real transcription may download the `small.en` faster-whisper model if
it is not already cached or bundled.
