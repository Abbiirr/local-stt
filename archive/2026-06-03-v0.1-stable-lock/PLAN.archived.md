# Local Dictation Plan

## Current Objective

Build and validate the selected custom local Windows dictation app for
system-wide English speech-to-text with GPU acceleration, low idle overhead, and
clear recording feedback.

Path C, the custom app, is now the active path. The public candidate checklists
below are retained as historical/deferred fallback material; `TODO.md`,
`STATUS.md`, and `EVALUATION.md` are the current source of truth.

## Phase 0: Repo Setup

- [x] Create `VISION.md`.
- [x] Create `PLAN.md`.
- [x] Add an evaluation log once testing begins.
- [x] Add setup notes for the selected candidate.
- [x] Add troubleshooting notes for CUDA, microphone, hotkeys, and paste behavior.

## Phase 1: Define Evaluation Matrix

Create a simple comparison table for each candidate:

```text
Candidate
Install method
License
Release maturity
Local/offline behavior
Model support
CUDA support
Hotkey behavior
Cancel behavior
Focused-app insertion
Overlay/state feedback
History/logging behavior
Idle CPU/RAM/VRAM
Active transcription speed
Network behavior after setup
Configuration location
Security/privacy concerns
Decision
```

Candidates to test, in priority order (verified May 2026):

1. **whisper-key-local** — https://github.com/PinW/whisper-key-local — MIT, faster-whisper + CUDA, tray, `.exe`. Closest fit; test first.
2. **whisper-writer** — https://github.com/savbell/whisper-writer — mature Python dictation app, faster-whisper local default.
3. **OpenWhispr** — https://github.com/OpenWhispr/openwhispr — polished Electron, MIT, local whisper.cpp; verify Windows CUDA.
4. **TypeWhisper for Windows** — https://github.com/TypeWhisper/typewhisper-win — feature-rich; whisper.cpp / SherpaOnnx.
5. **whisper-local** — https://github.com/pg0/whisper-local — tray client + self-hosted Docker/WSL2 Whisper server.

## Phase 1.5: Model and Runtime Decision

Settle the model strategy before deep app testing, because it filters candidates:

- **Default engine:** `faster-whisper` (CTranslate2) on CUDA, `large-v3`, `float16`,
  with `language` forced to `en` for the current milestone.
- **Deferred language scope:** Bangla and mixed English/Bangla are later work after
  English dictation is stable in the target apps.
- **Optional English-only fast mode:** NVIDIA Parakeet TDT v3 can be evaluated later
  as a speed-focused alternative, but it is not required for this milestone.
- **Avoid as default for now:** `large-v3-turbo`, because the already validated
  local `large-v3` path is accurate enough and keeps future multilingual expansion open.

Runtime gotchas to verify on this machine (Windows + RTX 4060 Ti):

- faster-whisper needs CUDA 12 + cuDNN 9. The classic failure is
  `Could not locate cudnn_ops64_9.dll` — the cuDNN 9 DLLs must be on `PATH`.
- Match CTranslate2 to the CUDA/cuDNN pair (CUDA 12 + cuDNN 9 → CTranslate2 ≥ 4.5;
  CUDA 12 + cuDNN 8 → pin CTranslate2 4.4.0). If a tool bundles its own CUDA libs
  (whisper-key-local offers one-press install), prefer that over a manual setup.

## Phase 2: Environment Baseline

Record the local baseline before app testing:

- Windows version.
- NVIDIA driver version.
- GPU model and VRAM.
- CUDA visibility through app/runtime.
- Python versions available.
- Default microphone device.
- Current conflicts for candidate hotkeys.
- Existing local Whisper/model caches.

Minimum commands:

```powershell
nvidia-smi
py -0p
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
```

## Phase 3: Test whisper-key-local (primary candidate)

Purpose: validate the closest-fit, faster-whisper + CUDA daily-driver first.

Tasks:

- [ ] Install via standalone `whisper-key.exe`, or `pipx install whisper-key` in an isolated env.
- [ ] Let it detect the GPU and run the one-press CUDA runtime install.
- [ ] Confirm local/offline mode.
- [ ] Confirm CUDA is actually used (not silent CPU fallback).
- [ ] Configure model to `large-v3` (add via HuggingFace/local model if not preset).
- [ ] Set language behavior to English-only for the current milestone.
- [ ] Test hotkey start/stop/cancel.
- [ ] Test paste into Notepad.
- [ ] Test paste into browser field.
- [ ] Test paste into notes app.
- [ ] Test paste into VS Code.
- [ ] Check idle CPU/RAM/VRAM.
- [ ] Check active GPU use during transcription.
- [ ] Check whether it stores history or logs by default.
- [ ] Check network behavior after model download.

Exit criteria:

- Continue with it if it is reliable, local, configurable, and unobtrusive.
- Reject or defer it if insertion, CUDA setup, privacy posture, or idle overhead is unacceptable.

## Phase 4: Test whisper-writer

Purpose: validate the mature fallback dictation app (faster-whisper local default).

Tasks:

- [ ] Clone or download source.
- [ ] Inspect installer script before running.
- [ ] Inspect code paths for network, history, clipboard, hotkeys, and startup behavior.
- [ ] Install only after the code/installer review is acceptable.
- [ ] Confirm `large-v3`, CUDA, and `float16` behavior.
- [ ] Configure and test the start/stop/cancel hotkeys.
- [ ] Evaluate overlay/status feedback usefulness and distraction level.
- [ ] Test insertion into the same target apps as Phase 3.
- [ ] Check history file behavior and whether it can be disabled.
- [ ] Check idle and active resource usage.

Exit criteria:

- Use it if its UX is clearly better and the code/privacy posture is acceptable.
- Reject or defer it if maturity, installer behavior, history behavior, or reliability is weak.

## Phase 5: Test whisper-local

Purpose: validate the clean local-server architecture.

Tasks:

- [ ] Review server requirements.
- [ ] Start local Whisper server through Docker or WSL2.
- [ ] Run the Windows tray client.
- [ ] Configure endpoint, microphone, language, and model.
- [ ] Test hold-to-talk behavior.
- [ ] Test focused-app insertion.
- [ ] Measure server idle overhead.
- [ ] Confirm all traffic stays on localhost.
- [ ] Decide whether the server/client split is worth the operational overhead.

Exit criteria:

- Use it if privacy architecture and reliability outweigh setup complexity.
- Reject or defer it if Docker/WSL2 overhead is too high for a small tray utility.

## Phase 6: Test OpenWhispr

Purpose: validate whether a polished product-style app can be constrained to local mode.

Note: OpenWhispr is Electron + whisper.cpp (GGML models). Its docs do not mention
CUDA on Windows, so confirm GPU use before relying on it — it may run CPU-only locally.

Tasks:

- [ ] Install current Windows release.
- [ ] Configure local transcription only.
- [ ] Disable or avoid cloud features (it supports cloud BYOK).
- [ ] Confirm whether the local whisper.cpp engine uses the GPU or falls back to CPU.
- [ ] Test dictation into focused apps.
- [ ] Check local model support (GGML) and large-v3 availability.
- [ ] Review settings for telemetry, sync, cloud transcription, and stored notes.
- [ ] Measure idle and active overhead (Electron baseline).

Exit criteria:

- Use it only if local mode is clear, GPU-accelerated, reliable, and not too heavy.
- Reject or defer it if it is CPU-only on Windows or the product surface is larger than the dictation requirement.

### Optional: TypeWhisper for Windows

If more features are wanted (history, dictionary, snippets, file transcription),
evaluate TypeWhisper. Confirm its engine (whisper.cpp / SherpaOnnx), GPU behavior,
license, and whether the extra surface stays out of the way for plain dictation.

## Phase 7: Decision Gate

Choose one of three paths:

### Path A: Adopt Existing App

Use this if one candidate satisfies the vision with acceptable tradeoffs.

Deliverables:

- [ ] Installation notes.
- [ ] Configuration notes.
- [ ] Hotkey notes.
- [ ] Privacy settings notes.
- [ ] Startup-with-Windows instructions.
- [ ] Troubleshooting checklist.

### Path B: Fork or Patch Existing App

Use this if a candidate is close but needs small changes.

Possible patches:

- Disable history by default.
- Add waveform/status overlay.
- Change hotkeys.
- Improve CUDA/model configuration.
- Reduce startup or idle overhead.
- Improve paste behavior.

Deliverables:

- [ ] Fork or local patch branch.
- [ ] Minimal code changes.
- [ ] Local build instructions.
- [ ] Validation checklist.

### Path C: Build Custom App

Selected and implemented in this workspace.

Custom milestones:

- [x] Minimal tray app.
- [x] Global hotkeys.
- [x] Microphone capture.
- [x] Waveform/status overlay.
- [x] Local CUDA faster-whisper transcription.
- [x] Text insertion into focused app.
- [x] Settings file.
- [x] Error reporting.
- [x] Startup shortcut.
- [x] PyInstaller `--onedir` package.

## Phase 8: Validation Checklist

Run this checklist for the selected path:

- [ ] Starts from a clean reboot.
- [x] Shows only tray UI while idle.
- [x] Records only after the hotkey.
- [x] Cancel works and discards audio.
- [x] Stop transcribes and inserts text.
- [x] Works in Notepad.
- [ ] Works in browser text fields.
- [ ] Works in notes app.
- [ ] Works in VS Code.
- [x] Handles short English dictation from generated WAV audio.
- [ ] Handles one-minute dictations.
- [ ] Handles silence without phantom text.
- [x] Handles English in automated model validation.
- [x] Defers Bangla or mixed language to a later milestone.
- [x] Uses CUDA during transcription.
- [x] Does not use network during normal dictation after setup, based on limited non-admin observation.
- [ ] Keeps idle resource usage low.
- [x] Can be quit cleanly from tray/process lifecycle tests.

## Immediate Next Step

See `TODO.md`, `STATUS.md`, and `EVALUATION.md` for the current state.

The custom app is implemented, packaged, configured with local `large-v3`, and
validated through automated checks. The remaining current-milestone work is
user-interactive English live dictation validation in browser, notes app, VS Code,
and confirmation after the next reboot. Bangla/mixed speech is deferred.
