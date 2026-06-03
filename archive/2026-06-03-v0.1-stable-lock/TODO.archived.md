# TODO - Local Windows Dictation

Current chosen path: **Path C - custom local app**.

Public app evaluation is no longer the active path. The custom app has been
implemented and validated as far as this non-interactive shell can validate it.

## Completed

- [x] Record GPU, driver, CUDA version, and VRAM from `nvidia-smi`.
- [x] Record Python launchers from `py -0p`.
- [x] Record OS version.
- [x] Record default microphone device.
- [x] Record model/cache locations.
- [x] Check CUDA visibility through CTranslate2.
- [x] Create `EVALUATION.md`.
- [x] Create `STATUS.md`.
- [x] Create `TESTING.md`.
- [x] Create `TROUBLESHOOTING.md`.
- [x] Select Path C: custom app.
- [x] Document why public candidates are deferred.
- [x] Implement PySide6 tray app.
- [x] Implement waveform/status overlay.
- [x] Make waveform/status overlay draggable and closable.
- [x] Implement global `Ctrl+Alt+D` start/stop hotkey.
- [x] Guard global hotkey registration so tray/menu use still works if hook setup fails.
- [x] Implement `Esc` cancel hotkey.
- [x] Implement microphone capture only while active.
- [x] Implement faster-whisper CUDA transcription path.
- [x] Download local `large-v3` model into `models\faster-whisper-large-v3`.
- [x] Configure runtime settings to use the local `large-v3` model path.
- [x] Validate local `large-v3` model load on CUDA with `float16`.
- [x] Validate actual local `large-v3` transcription with generated WAV audio.
- [x] Implement clipboard paste into focused app.
- [x] Implement clipboard restore after paste.
- [x] Validate paste path in Notepad.
- [x] Validate global hotkey start/cancel cycle without app crash.
- [x] Implement JSON settings under `%APPDATA%\LocalWhisperDictation\settings.json`.
- [x] Add rotating app log under `%APPDATA%\LocalWhisperDictation\app.log`.
- [x] Set current language scope to English-only (`language = "en"`).
- [x] Handle UTF-8 BOM settings files.
- [x] Fix text post-processing so decimals, comma-separated numbers, email addresses, and abbreviations are preserved.
- [x] Make spoken punctuation commands opt-in instead of always-on.
- [x] Add regression tests for numeric/email punctuation and literal words like `period` and `comma`.
- [x] Add optional typing insertion mode for apps that block clipboard paste.
- [x] Make `large-v3` resolve to the local model directory when present, avoiding machine-specific absolute paths in settings.
- [x] Set default idle model unload to 5 minutes to reduce idle VRAM after transcription.
- [x] Confirm history is off by design: no audio/transcript persistence.
- [x] Add diagnostics command.
- [x] Add default config writer.
- [x] Add microphone smoke command.
- [x] Add CUDA smoke command.
- [x] Add WAV transcription smoke command.
- [x] Add synthetic silence/noise smoke command.
- [x] Add resumable `large-v3` download script.
- [x] Add startup shortcut creation/removal scripts.
- [x] Create startup-with-Windows shortcut.
- [x] Add PyInstaller `--onedir` package script.
- [x] Include `faster_whisper` data files in PyInstaller builds so packaged VAD transcription works.
- [x] Build windowed package: `dist\LocalWhisperDictation\LocalWhisperDictation.exe`.
- [x] Build console diagnostics package: `dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe`.
- [x] Validate packaged console diagnostics.
- [x] Validate packaged console CUDA load with `tiny`.
- [x] Validate packaged console CUDA load with local `large-v3`.
- [x] Validate packaged console WAV transcription with local `large-v3` and bundled VAD asset.
- [x] Validate packaged windowed app startup.
- [x] Run final compile check.
- [x] Run final unit tests.
- [x] Run final microphone smoke test.
- [x] Check for established TCP connections during local transcription.
- [x] Validate direct WAV transcription against generated English test audio.
- [x] Validate synthetic silence/noise produces no transcript.
- [x] Validate 60-second repeated generated WAV latency: 56.31s elapsed, 1.07x realtime including model load.
- [x] Document keyboard hook, elevated-app paste, AV false-positive, spoken-punctuation, and idle-VRAM behavior.
- [x] Refresh `TESTING.md` for local `large-v3` resolution and elevated firewall requirements.
- [x] Resolve final review robustness items: guarded hotkeys, persistent logging, idle-check skip during transcription, path-root cleanup, overlay drag clamping.

## Deferred / Not Applicable

- [x] `whisper-key-local` evaluation deferred because Path C is implemented.
- [x] `whisper-writer` evaluation deferred because Path C is implemented.
- [x] `OpenWhispr` evaluation deferred because Path C is implemented.
- [x] `TypeWhisper` evaluation deferred because Path C is implemented.
- [x] `whisper-local` evaluation deferred because Path C is implemented.
- [x] Firewall-block offline proof attempted but not available from this shell because `New-NetFirewallRule` returned `Access is denied`.
- [x] Bangla and mixed English/Bangla validation deferred to a later milestone.

## Still Needs User-Interactive Validation

These cannot be honestly completed from this shell without the user speaking into
the microphone and confirming the focused target apps.

- [ ] Real spoken dictation through the tray app: `Ctrl+Alt+D`, speak, `Ctrl+Alt+D`.
- [ ] Confirm pasted transcript in a browser text field.
- [ ] Confirm pasted transcript in notes app.
- [ ] Confirm pasted transcript in VS Code.
- [ ] Confirm one-minute real spoken dictation latency through the tray workflow.
- [ ] Confirm silence/noise behavior in the user's room through the tray workflow.
- [ ] Confirm clean reboot startup behavior after the next Windows reboot.

## Run

```powershell
cd K:\projects\ai\stt
.\run.bat
```

Packaged app:

```powershell
K:\projects\ai\stt\dist\LocalWhisperDictation\LocalWhisperDictation.exe
```
