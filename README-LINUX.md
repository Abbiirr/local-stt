# Linux (Ubuntu) Guide

Running Local Whisper Dictation from source on Ubuntu. Verified on Ubuntu 24.04
(GNOME, X11, CPU-only). For the `.deb` package flow see
[docs/UBUNTU.md](docs/UBUNTU.md).

## Prerequisites

- Python 3.11+
- System libraries:

```sh
sudo apt install -y libportaudio2 libxcb-cursor0 xdotool xclip
```

| Package | Needed by |
|---|---|
| `libportaudio2` | `sounddevice` (microphone capture) |
| `libxcb-cursor0` | Qt 6.5+ xcb platform plugin (the GUI) |
| `xdotool`, `xclip` | paste injection on X11 |
| `wtype` (optional) | paste injection on Wayland |

### Without sudo

If you cannot install system packages, extract them locally and point
`LD_LIBRARY_PATH` at them:

```sh
mkdir -p .libs && cd .libs
apt-get download libportaudio2 libxcb-cursor0
for deb in *.deb; do dpkg -x "$deb" extracted; done
ln -sf libportaudio.so.2 extracted/usr/lib/x86_64-linux-gnu/libportaudio.so
cd ..
export LD_LIBRARY_PATH=$PWD/.libs/extracted/usr/lib/x86_64-linux-gnu
```

The `libportaudio.so` symlink is required because `ctypes.util.find_library`
only resolves unversioned names from `LD_LIBRARY_PATH`.

## Build

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

Or with `uv`:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt -e .
```

## Settings (CPU profile)

The built-in defaults target CUDA (`large-v3`, `float16`). On a machine without
an NVIDIA GPU, write a CPU profile before the first run:

```sh
mkdir -p ~/.config/LocalWhisperDictation
cat > ~/.config/LocalWhisperDictation/settings.json <<'EOF'
{
  "model_name": "small.en",
  "device": "cpu",
  "compute_type": "int8",
  "beam_size": 1,
  "language": "en"
}
EOF
```

Use `tiny.en` for the fastest model (~75 MB download), `small.en` for better
accuracy (~460 MB). Models download from Hugging Face on first use, or are
resolved from `models/faster-whisper-<model_name>` if present.

Set `XDG_CONFIG_HOME` to keep settings somewhere else (the config file is then
`$XDG_CONFIG_HOME/LocalWhisperDictation/settings.json`).

## Verify

```sh
.venv/bin/python -m local_dictation diagnostics
.venv/bin/python -m local_dictation smoke-model --model tiny.en --compute-type int8
.venv/bin/python -m local_dictation transcribe-wav /usr/share/sounds/alsa/Front_Center.wav
```

The last command should print `Text: Front center.`

## Run

```sh
.venv/bin/python -m local_dictation run
```

A waveform tray icon appears in the top bar. On GNOME, tray icons require the
AppIndicator support that Ubuntu ships by default.

## Hotkeys on Linux

The `keyboard` library requires root on Linux, so the app falls back to
`pynput` for global hotkeys. This works on X11 sessions; on Wayland, global
hotkeys are unavailable — use the tray menu and overlay buttons instead.

```text
Ctrl+Alt+D = start / stop dictation
Esc        = cancel current recording
```

### GNOME: Ctrl+Alt+D conflict

Ubuntu GNOME binds Ctrl+Alt+D to "Hide all normal windows" (show desktop). If
that binding is active, pressing the dictation hotkey also hides every window,
focus moves to the desktop, and the transcript is pasted into the wrong place.

Remove the conflicting combo (Show Desktop stays available on Super+D):

```sh
gsettings set org.gnome.desktop.wm.keybindings show-desktop "['<Primary><Super>d', '<Super>d']"
```

Restore the Ubuntu default later with:

```sh
gsettings reset org.gnome.desktop.wm.keybindings show-desktop
```

Alternatively, change the app hotkey in `settings.json` (`"hotkey_toggle"`).

## Usage

1. Focus the app you want to dictate into.
2. Press Ctrl+Alt+D (or tray menu > Start / Stop Dictation). The waveform
   overlay appears bottom-center without taking focus.
3. Speak, then press Ctrl+Alt+D again (or click Stop on the overlay).
4. The transcript is pasted into the focused app. If paste injection is
   unavailable, the text remains on the clipboard.

Pasting is clipboard-based: the transcript is copied, then a paste shortcut is
sent to the focused window with `xdotool`. The shortcut adapts to the target:
terminal emulators (detected by `WM_CLASS`, e.g. gnome-terminal, kitty,
alacritty, warp, ptyxis) receive Ctrl+Shift+V; everything else receives Ctrl+V.
Apps where neither works can use `"type_text_instead_of_paste": true` in
`settings.json` to type the text key-by-key instead.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `OSError: PortAudio library not found` | Install `libportaudio2` (see Prerequisites). |
| `Could not load the Qt platform plugin "xcb"` | Install `libxcb-cursor0`. |
| Hotkeys do nothing | Wayland session, or pynput failed — check `~/.config/LocalWhisperDictation/app.log`; use the tray menu. |
| Pressing Ctrl+Alt+D hides all windows | GNOME show-desktop conflict (see above). |
| Transcript pastes into wrong window | Same conflict, or focus changed between stop and paste. |
| No tray icon | Enable an AppIndicator/StatusNotifier extension for your desktop. |
| `You must be root to use this library` in log | Expected on Linux — the `keyboard` module is skipped and pynput is used. |

Logs are written to `~/.config/LocalWhisperDictation/app.log` (or under
`$XDG_CONFIG_HOME` when set).
