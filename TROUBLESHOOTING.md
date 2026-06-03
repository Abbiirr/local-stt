# Troubleshooting

## CUDA And cuDNN

Check CUDA visibility:

```powershell
.\.venv\Scripts\python.exe -m local_dictation diagnostics
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model tiny
```

Validate the default model:

```powershell
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model large-v3
```

When `models\faster-whisper-large-v3` exists under the project root,
`large-v3` resolves to that local directory. If the repo is moved, keep
`model_name` as `large-v3` instead of hardcoding the old absolute path.

If the error mentions `cudnn_ops64_9.dll`, install or expose the CUDA 12 +
cuDNN 9 runtime DLLs on `PATH`. On this machine, CTranslate2 currently sees CUDA
and the `tiny` CUDA smoke test passes, but `where cudnn_ops64_9.dll` does not
find that split cuDNN DLL on `PATH`.

## Microphone

List devices:

```powershell
.\.venv\Scripts\python.exe -m local_dictation diagnostics
```

The current default input device is a USB microphone. To force another device,
edit:

```text
%APPDATA%\LocalWhisperDictation\settings.json
```

Set `input_device` to the numeric device id or device name reported by
`sounddevice`.

## Hotkey Conflicts

Default hotkeys:

```text
Ctrl+Alt+D = start/stop
Esc        = cancel recording
```

If another app uses `Ctrl+Alt+D`, edit `hotkey_toggle` in the settings file.

The app uses the Windows keyboard hook provided by the `keyboard` package only
to match the configured hotkeys. If dictation or paste does nothing inside an
administrator/elevated app, run this app elevated too; non-elevated processes
cannot reliably send keys into elevated windows. Some antivirus products may
flag packaged apps that install global keyboard hooks, even when the hook is
used only for local hotkey matching.

## Paste Or Clipboard Problems

The app inserts text by copying the transcript, sending `Ctrl+V`, then restoring
the previous clipboard content.

If a target app blocks paste:

- test in Notepad first,
- increase `paste_delay_seconds`,
- disable `restore_clipboard_after_paste` temporarily,
- set `type_text_instead_of_paste` to `true` to type the transcript instead of
  using the clipboard.

## Text Post-Processing

By default, spoken punctuation commands are disabled. This avoids corrupting
ordinary dictated words such as "period" or "comma" and preserves numbers,
decimals, email addresses, and abbreviations. If you want commands like
"new line" or "comma", set `enable_spoken_punctuation` to `true`.

If chained dictation produces unwanted capitalization, set
`capitalize_transcript` to `false`. If the trailing inserted space is not wanted,
set `append_trailing_space` to `false`.

## Idle VRAM

The model loads on first transcription and unloads after 5 idle minutes by
default:

```json
"unload_model_when_idle": true,
"unload_after_seconds": 300
```

Set `unload_model_when_idle` to `false` if you prefer faster follow-up
dictations and accept the model staying resident in VRAM until quit.

## Startup With Windows

Create the startup shortcut:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create_startup_shortcut.ps1
```

Remove it:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\remove_startup_shortcut.ps1
```
