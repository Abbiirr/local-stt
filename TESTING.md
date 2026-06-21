# TESTING - Local Windows Dictation

Repeatable protocol for validating the implemented custom app first, then
optionally comparing public candidates if the custom app fails a hard gate.

Primary implementation under test:

```text
K:\projects\ai\stt
python -m local_dictation run
```

Default runtime target:

```text
Engine: faster-whisper
Model: large-v3
Device: CUDA
Compute: float16
Language: en
Hotkeys: Ctrl+Alt+Space start/stop, Esc cancel
Output: paste into focused app with clipboard restore
```

Record results in `EVALUATION.md`.

## Packaging Preflight

Windows:

```powershell
.\.venv\Scripts\python.exe -m local_dictation --version
.\.venv\Scripts\python.exe -m pip wheel --no-deps . -w build\wheel-smoke
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1
```

Linux Debian/Ubuntu:

```sh
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_deb.sh
sudo apt install ./dist/local-whisper-dictation_0.1.0_amd64.deb
local-dictation --version
local-dictation diagnostics
```

Linux Fedora:

```sh
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_rpm.sh
sudo dnf install ./dist/local-whisper-dictation-0.1.0-*.noarch.rpm
local-dictation --version
local-dictation diagnostics
```

Pass criteria:

- [ ] Windows installer places files under `%LOCALAPPDATA%\Programs\LocalWhisperDictation`.
- [ ] Windows Start Menu shortcut exists.
- [ ] Debian/Ubuntu package installs and removes cleanly.
- [ ] Fedora package installs and removes cleanly.
- [ ] `local-dictation --version` reports `0.1.0` on every package target.
- [ ] `local-dictation diagnostics` reports expected platform, audio, and CUDA state.

## 1. Preconditions

- [ ] Record OS version:
  `Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber`
- [ ] Record GPU, driver, CUDA version, and VRAM:
  `nvidia-smi`
- [ ] Record Python launchers:
  `py -0p`
- [ ] Confirm default microphone device and input level.
- [ ] Confirm no other Whisper/STT process is running.
- [ ] Confirm `Ctrl+Alt+Space` is free.
- [ ] Confirm `Esc` cancellation will not conflict with the target app during testing.
- [ ] Confirm the settings file exists after setup:
  `%APPDATA%\LocalWhisperDictation\settings.json`
- [ ] Reboot before idle/stability tests if resource numbers need to be clean.

## 2. Automated Preflight

Run these from `K:\projects\ai\stt`.

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m local_dictation diagnostics
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model tiny
.\.venv\Scripts\python.exe -m local_dictation smoke-mic --seconds 1.0
.\.venv\Scripts\python.exe -m local_dictation transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."
.\.venv\Scripts\python.exe -m local_dictation smoke-nonspeech --seconds 5
.\.venv\Scripts\python.exe -m local_dictation write-default-config
```

Pass criteria:

- [ ] Compile passes.
- [ ] Unit tests pass.
- [ ] Diagnostics show one CUDA device.
- [ ] `tiny` faster-whisper model loads on CUDA with `float16`.
- [ ] Microphone smoke captures samples.
- [ ] Generated English WAV transcribes correctly.
- [ ] Synthetic silence/noise produces no transcript.
- [ ] Default settings file writes successfully.

## 3. Large-v3 Model Validation

Complete this before claiming the default workflow is validated.

```powershell
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model large-v3
```

If `models\faster-whisper-large-v3` exists, `large-v3` resolves to that local
directory. To force the explicit path:

```powershell
.\.venv\Scripts\python.exe -m local_dictation smoke-cuda --model "K:\projects\ai\stt\models\faster-whisper-large-v3"
```

Pass criteria:

- [ ] `large-v3` resolves to the local model directory or downloads completely if not already cached.
- [ ] `large-v3` loads on CUDA with `float16`.
- [ ] No `cudnn_ops64_9.dll` or CUDA runtime error appears.
- [ ] `nvidia-smi` shows VRAM use rising during load/transcription.

Known current status:

- [x] `large-v3` is downloaded locally.
- [x] `smoke-cuda --model large-v3` resolves to the local model and loads on CUDA with `float16`.
- [x] Generated English WAV transcribes correctly with local `large-v3`.
- [x] 60-second repeated generated WAV transcribes at 1.07x realtime including model load.

## 4. Measurement Methods

### GPU / CUDA usage

Run this in a second terminal during transcription:

```powershell
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1
```

Pass:

- [ ] GPU utilization spikes during transcription.
- [ ] VRAM rises when the model is loaded.
- [ ] CPU does not carry the full transcription while GPU stays flat.

### Idle resource usage

Let the app sit idle in the tray for 5 minutes.

```powershell
Get-Process -Name python | Select-Object Id,Name,CPU,WorkingSet64,PrivateMemorySize64
```

Also check Task Manager CPU over 60 seconds.

Record:

- [ ] Idle CPU percent.
- [ ] Idle RAM.
- [ ] Idle VRAM.
- [ ] Whether the model is resident in VRAM while idle.

### Network / offline proof

Run only after setup and model download are complete. This requires elevated
PowerShell; `New-NetFirewallRule` returns `Access is denied` in a non-admin
shell.

```powershell
$python = (Resolve-Path ".\.venv\Scripts\python.exe").Path
New-NetFirewallRule -DisplayName "STT-test-block" -Direction Outbound -Program $python -Action Block
```

Then dictate into Notepad.

Inspect live connections:

```powershell
Get-NetTCPConnection -OwningProcess (Get-Process python | Where-Object Path -like "*K:\projects\ai\stt*").Id |
  Where-Object State -eq 'Established'
```

Remove the firewall rule:

```powershell
Remove-NetFirewallRule -DisplayName "STT-test-block"
```

Pass:

- [ ] Dictation still works while outbound traffic is blocked.
- [ ] No unexpected established network connections during dictation.

### Latency

Use a stopwatch from recording stop to text appearing.

Automated model-only latency can be checked with:

```powershell
.\.venv\Scripts\python.exe -m local_dictation transcribe-wav artifacts\en_test.wav --repeat-to-seconds 60
```

Known automated result: 60.00s audio, 56.31s elapsed, 1.07x realtime including
model load. This does not replace real tray latency testing.

Record:

- [ ] Short clip: about 6 seconds of audio.
- [ ] Long clip: about 60 seconds of audio.
- [ ] Real-time factor: audio length divided by transcription time.

### Accuracy

Read the standard corpus in section 7. Paste output and compare to the reference.

WER estimate:

```text
(substitutions + insertions + deletions) / reference words
```

Spoken punctuation and casing differences count only when they make the text
unusable.

## 5. Test Suites

### T1 - Install And Launch

- [ ] `install.bat` completes, or manual venv install completes.
- [ ] `run.bat` starts the tray app.
- [ ] Tray icon appears.
- [ ] App can quit cleanly from the tray.
- [ ] Settings file can be created with `write-default-config`.

Pass: installs, launches, and quits cleanly. A settings UI is not required for
this custom app.

### T2 - Local / Offline / Privacy

- [ ] Confirm no cloud or telemetry feature exists in the app code.
- [ ] Confirm audio is not written to disk.
- [ ] Confirm transcripts are not written to disk.
- [ ] Confirm settings are the only intentional persistent app data.
- [ ] After `large-v3` download, run the firewall-block proof in section 4 from elevated PowerShell.

Pass: works offline after setup and does not persist audio/transcript history.

### T3 - GPU / CUDA

- [ ] `smoke-cuda --model tiny` passes.
- [ ] `smoke-cuda --model large-v3` passes.
- [ ] GPU utilization and VRAM rise during transcription.
- [ ] No silent CPU fallback.

Pass: transcription is GPU accelerated on CUDA.

### T4 - Model And Compute Configuration

- [ ] Default config is `large-v3`.
- [ ] Default device is `cuda`.
- [ ] Default compute type is `float16`.
- [ ] Default/current language is `en`.
- [ ] Default spoken punctuation is off.
- [ ] Default idle unload is on with a 300-second timeout.
- [ ] Optional: test `int8_float16` if VRAM pressure appears.
- [ ] Optional later: set `language` to `bn` or `null` when Bangla/mixed support is reopened.

Pass: `large-v3` + CUDA + `float16` + English language selection is working or a documented fallback is chosen.

### T5 - Hotkeys

- [ ] `Ctrl+Alt+Space` starts recording.
- [ ] Overlay appears while recording.
- [ ] `Ctrl+Alt+Space` stops recording and starts transcription.
- [ ] `Esc` cancels and inserts no text.
- [ ] Hotkeys work while Notepad is focused.
- [ ] Hotkeys work while a browser field is focused.

Pass: start, stop, and cancel are reliable and global.

### T6 - Insertion Across Apps

Dictate the same short sentence into each target:

- [ ] Notepad.
- [ ] Browser text field.
- [ ] Notes app: Standard Notes, Obsidian, or similar.
- [ ] VS Code editor.
- [ ] Optional: Word or Outlook.
- [ ] Confirm clipboard content is restored after paste.

Pass: text lands correctly in Notepad, browser, notes, and VS Code.

### T7 - Accuracy Across Corpus

Read each section 7 item:

- [ ] EN-1.
- [ ] EN-2.
- [ ] EN-NUM.
- [ ] EN-TECH.
- [ ] Record approximate WER per item.

Pass: English is usable with minimal edits.

### T8 - Silence And Hallucination

- [ ] Start recording, stay silent for about 5 seconds, stop.
- [ ] Expect empty or near-empty output.
- [ ] Record background noise with no speech.
- [ ] Expect no fabricated text.

Pass: no meaningful phantom text on silence or background noise.

### T9 - Latency And Speed

- [ ] Short clip, about 6 seconds: record stop-to-text latency.
- [ ] Long clip, about 60 seconds: record stop-to-text latency.
- [ ] Record real-time factor.

Pass: short dictation feels near-immediate; long dictation completes in seconds,
not minutes.

### T10 - Idle Resource Use

- [ ] Let the tray app idle for 5 minutes.
- [ ] Record CPU percent.
- [ ] Record RAM.
- [ ] Record VRAM.
- [ ] Confirm microphone is not recording while idle.
- [ ] Confirm waveform overlay is hidden while idle.

Pass: low enough to leave running all day. Flag idle CPU above about 2 percent
or unexpected microphone activity.

### T11 - History / Logging

- [ ] Confirm no audio files are created.
- [ ] Confirm no transcript files are created.
- [ ] Confirm settings file contains configuration only.
- [ ] Confirm diagnostics do not write private audio/transcript data.

Pass: history is off by design.

### T12 - Stability / Reboot / Startup

- [ ] 10 consecutive short dictations with no crash or stuck state.
- [ ] Rapid start/stop sequence does not wedge the app.
- [ ] Quit from tray leaves no `local_dictation` process running.
- [ ] Optional: add startup shortcut and reboot.
- [ ] Optional: verify app returns to tray idle after reboot.

Pass: stable through repeated use and clean shutdown.

### T13 - Edge Cases

- [ ] Switch the default mic mid-session and dictate again.
- [ ] Very long dictation, about 3 minutes, has no truncation or timeout.
- [ ] Clipboard restore still works if previous clipboard has Unicode text.
- [ ] If a target app blocks paste, document whether typing simulation is needed.

Pass: edge cases degrade predictably and any hard limits are documented.

## 6. Target Apps

Required:

- [ ] Notepad.
- [ ] Browser text field.
- [ ] Notes app: Standard Notes, Obsidian, or similar.
- [ ] VS Code.

Optional:

- [ ] Word.
- [ ] Outlook.
- [ ] ChatGPT text box.

## 7. Standard Dictation Corpus

For the current milestone, read the English corpus verbatim every time.

**EN-1:** "The quick brown fox jumps over the lazy dog near the riverbank."

**EN-2:** "Please schedule the review for next Thursday and send everyone the agenda."

**EN-NUM:** "Order 3,250 units at $19.99 each, then email john.doe@example.com by 5 p.m."

**EN-TECH:** "Run faster-whisper with the large-v3 model on CUDA using float16 precision."

Deferred: Bangla and mixed English/Bangla corpus items will be added when that
phase starts.

Use the same mic, distance, room, and speaking pace for every run.

## 8. Scoring And Decision Rubric

Score each suite 0/1/2:

```text
0 = fail
1 = partial
2 = pass
```

| Suite | What it proves | Weight |
| --- | --- | ---: |
| T2 Offline/privacy | Local-first, no leaks | 3 |
| T3 GPU/CUDA | Uses RTX 4060 Ti | 3 |
| T6 Insertion | Works in real apps | 3 |
| T5 Hotkeys | Start/stop/cancel reliable | 2 |
| T7 Accuracy | Usable EN + BN transcripts | 2 |
| T9 Latency | Fast enough for daily use | 2 |
| T8 Silence | No phantom text | 2 |
| T10 Idle | Cheap to leave running | 2 |
| T12 Stability | Survives repeated use | 2 |
| T1 Install | Reasonable setup | 1 |
| T4 Model config | large-v3 + fp16 selectable | 1 |
| T11 History | Off by design | 1 |
| T13 Edge cases | Graceful limits | 1 |

Hard gates:

- [ ] T2 must pass.
- [ ] T3 must pass for the preferred GPU workflow.
- [ ] T6 must pass.

Reject or patch if any hard gate fails.

## 9. Scorecard

Copy into `EVALUATION.md`.

```text
Subject:              custom local_dictation app
Version / commit:     <workspace timestamp or commit>
Install method:       venv + editable install / run.bat
Engine / runtime:     faster-whisper / CTranslate2
Model used:           large-v3
Compute:              float16
Language:             en
Spoken punctuation:   off unless explicitly testing command mode

T1 Install            [ /2]  notes:
T2 Offline/privacy    [ /2]  firewall-block held? net connections seen?
T3 GPU/CUDA           [ /2]  GPU util %:   VRAM used:   CPU fallback? Y/N
T4 Model/compute      [ /2]  large-v3? fp16 VRAM:
T5 Hotkeys            [ /2]  start/stop/cancel/global:
T6 Insertion          [ /2]  Notepad/browser/notes/VSCode/clipboard-restore:
T7 Accuracy           [ /2]  EN WER ~
T8 Silence            [ /2]  phantom text? severity:
T9 Latency            [ /2]  short stop-to-text:   60s stop-to-text:   RTF:
T10 Idle              [ /2]  CPU%:  RAM:  VRAM held:
T11 History/logging   [ /2]  audio/transcript persisted? settings only?
T12 Stability         [ /2]  10-burst OK? clean quit? reboot OK?
T13 Edge cases        [ /2]  mic switch / 3-min / rapid cycle / unicode:

Hard gates:           T2 pass? T3 pass? T6 pass?
Weighted total:       <sum>
Verdict:              ADOPT / PATCH / REJECT - one-line reason
```

## 10. Run Order

1. Run preconditions.
2. Run automated preflight.
3. Complete `large-v3` model validation.
4. Run live hotkey and insertion tests.
5. Run accuracy, silence, latency, idle, history, stability, and edge-case tests.
6. Fill the scorecard in `EVALUATION.md`.
7. If the custom app fails a hard gate, return to `PLAN.md` and evaluate public
   candidates in this order: `whisper-key-local`, `whisper-writer`, `OpenWhispr`,
   `TypeWhisper`, `whisper-local`.

## 11. Packaged Build Check

After `scripts\build_onedir.ps1`, confirm packaged transcription works:

```powershell
.\dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."
```

The build script must collect `faster_whisper` data files. Packaged
transcription with VAD requires `faster_whisper\assets\silero_vad_v6.onnx`.
