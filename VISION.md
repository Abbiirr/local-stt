# Local Dictation Vision

## Product Goal

Build or select a Windows dictation tool that turns speech into text anywhere on the system while keeping audio local, private, fast, and easy to control.

Phase 1 delivered the local Windows implementation. Phase 2 extends the project
from a local utility into an installable package that ordinary users can run on
Windows, Ubuntu, Debian, and Fedora while preserving the same local-first privacy
and low-idle-resource principles. A later multilingual phase will add Bangla
dictation that can preserve English words naturally when they appear inside
Bangla speech.

The ideal user experience is:

```text
Tray app in background
-> global hotkey
-> small recording/transcription overlay
-> local Whisper-class model on RTX 4060 Ti
-> paste transcript into the focused app
-> hide again
```

The tool should feel like a keyboard replacement, not a file transcription workstation.

## Target User

The target user dictates into normal Windows applications:

- Notes apps
- Browsers
- ChatGPT
- Email
- Code editors
- Office documents
- Any standard focused text field

The user values privacy, low idle resource usage, predictable hotkeys, and strong local accuracy more than cloud integrations or meeting-note features.

## Core Principles

1. **Local first**
   Audio and transcripts must stay on the machine by default. Network access is allowed only for initial model/app downloads or explicitly enabled integrations.

2. **User-triggered recording only**
   The app must not always listen. Recording starts only from a deliberate hotkey or tray action and stops from a deliberate hotkey, release gesture, silence rule, or cancel action.

3. **Works anywhere**
   Output should go into the currently focused app using paste, typing simulation, or another reliable Windows insertion path.

4. **Low idle cost**
   Idle state should be tray-only or near tray-only. Microphone capture, waveform painting, and transcription should run only when needed.

5. **Fast enough for daily use**
   Short dictations should feel near-immediate after recording stops. The RTX 4060 Ti 16 GB should be used for Whisper large-v3 or a comparable local model.

6. **Auditable behavior**
   Prefer simple, inspectable architecture. Avoid telemetry, background context collection, screen capture, or clipboard inspection unless deliberately enabled. Local dictation history may be enabled for recovery when the user wants failed recordings to be retryable.

7. **Polished feedback**
   The user should always know the current state: idle, recording, transcribing, inserted, canceled, or failed. A waveform or small overlay is preferred, but reliability comes first.

## Required Behavior

- Windows support.
- Future packaged support for Ubuntu, Debian, and Fedora.
- Global start/stop hotkey.
- Cancel hotkey.
- Local/offline transcription mode.
- GPU acceleration on NVIDIA CUDA.
- Configurable model, language, device, and compute type.
- Dictation inserted into the focused app.
- Clear state feedback through tray, overlay, sound, or notification.
- No always-on microphone capture.

## Preferred Defaults

```text
Primary model: faster-whisper large-v3 (CUDA, float16), forced to English for the current milestone
Later language expansion: Bangla with English words mixed into Bangla speech
Speed model candidate: NVIDIA Parakeet TDT v3 for a future English-only fast mode
Device: CUDA
Compute: float16 first, int8_float16 only if VRAM pressure matters
Language: en
Hotkey: Ctrl+Alt+D or another non-conflicting global shortcut
Idle UI: tray only
Active UI: small overlay
History: local recovery history enabled when the user wants retryable failed dictations
```

### Model Note (2026)

The current milestone is English-only. The app therefore forces
`language = "en"` instead of Whisper auto-detection, which should reduce language
misclassification and avoid optimizing current acceptance tests around Bangla
before the English dictation workflow is stable.

Decision: default to **faster-whisper large-v3** on CUDA with `float16` for the
validated local implementation. Revisit **Parakeet** later as an optional
English-only speed mode, and revisit Bangla with mixed English words as a
separate multilingual phase.

## Current Candidate Paths

### Existing App First

Before investing in custom build work, test existing apps against the real requirements:

- **whisper-key-local** (PinW) — MIT, Python + faster-whisper, auto CUDA/ROCm install, tray, standalone `.exe`. Closest match to this vision.
- **whisper-writer** (savbell) — mature Python dictation app, faster-whisper local by default.
- **OpenWhispr** — polished Electron app, MIT, local whisper.cpp + cloud BYOK; Windows GPU/CUDA support unverified.
- **TypeWhisper for Windows** — feature-rich (history, dictionary, snippets), whisper.cpp / SherpaOnnx engines.
- **whisper-local** (pg0) — tray client that talks to a self-hosted Whisper server in Docker/WSL2.

Existing apps win if they provide reliable system-wide dictation, local GPU transcription, low idle overhead, acceptable privacy posture, and enough configuration.

### Custom App Fallback

Build or continue a custom app if existing apps fail on key requirements:

- privacy is unclear or too broad,
- idle resource use is too high,
- dictation insertion is unreliable,
- hotkeys are not suitable,
- local large-v3 configuration is poor,
- UI feedback is missing or distracting,
- code quality/security is not acceptable.

The custom fallback architecture is:

```text
PySide6 tray app
sounddevice microphone stream
faster-whisper local CUDA transcription
small PySide6 overlay for waveform/status
clipboard or SendInput insertion
local settings file
optional packaging with PyInstaller onedir
```

## Non-Goals

- Cloud dictation as the default path.
- Always-listening wake word mode.
- Meeting recorder or notes assistant as the primary product.
- Audio/video file transcription as the primary workflow.
- Multi-user server product.
- Browser extension first approach.
- Heavy Electron UI unless it clearly wins on reliability and maintenance.

## Success Criteria

The chosen or built tool is successful when:

- It starts reliably on Windows.
- It records only when explicitly triggered.
- It transcribes locally on the RTX 4060 Ti.
- It inserts text into at least Notepad, browser text fields, Standard Notes or another notes app, and VS Code.
- Idle CPU and memory remain low enough for an always-running tray utility.
- User-visible state is clear during recording and transcription.
- Network activity is absent during normal dictation after initial setup.
- The user can understand and change the important settings without digging through fragile internals.

## Current Outcome

Path C was selected and implemented as a custom app in this workspace. The
current Windows version is stable-locked as `v0.1-stable`.

Verified:

- Starts reliably from the venv and packaged windowed EXE.
- Records only when triggered by hotkey in the implemented control flow.
- Uses local `large-v3` on CUDA with `float16`.
- Transcribes generated WAV audio correctly with the local model.
- Inserts text into Notepad through the same clipboard paste path used by dictation.
- Provides tray UI and a waveform/status overlay.
- Stores settings in `%APPDATA%\LocalWhisperDictation\settings.json`.
- Does not intentionally persist audio or transcript history.
- Builds with PyInstaller `--onedir`.
- Starts with Windows through a Startup folder shortcut.
- Uses a rotating local app log for diagnosability.
- Has guarded hotkey registration so the tray app can still run if global hooks fail.

Still requires user confirmation:

- Real spoken dictation into browser, notes app, and VS Code.
- Clean reboot startup behavior.

Deferred:

- Bangla or mixed Bangla/English speech from the user's microphone.

## Next Phase: Packaging And Distribution

The next phase is packaging and distribution. The goal is to let users install
and run the app on:

- Windows
- Ubuntu
- Debian
- Fedora

Packaging work must preserve the `v0.1-stable` behavior. It should focus on:

- installer/package formats,
- dependency isolation,
- model download/cache strategy,
- CUDA/runtime expectations,
- autostart integration,
- settings and log locations,
- uninstall/update documentation,
- validation on each supported OS.

This phase should not add new dictation features unless needed to make the
stable app installable and supportable across those platforms.

## Later Phase: Bangla With Embedded English

After packaging and distribution are stable, add a multilingual dictation phase
focused on Bangla speech that naturally contains English words, names, product
terms, code terms, and short English phrases.

The target behavior is:

```text
User speaks mostly Bangla
-> English words inside the Bangla sentence are preserved as English
-> Bangla output remains readable and correctly segmented
-> insertion behavior stays the same as the English workflow
```

Examples of the kind of speech this phase should support:

```text
Bangla sentence with app names like ChatGPT, VS Code, GitHub
Bangla sentence with technical words like API, server, package, commit
Bangla sentence with product names, people names, and short English phrases
```

This phase should evaluate:

- Whisper `language = None` auto-detection versus explicit Bangla mode.
- Faster-whisper large-v3 accuracy for Bangla with embedded English.
- Whether post-processing should be language-aware.
- Punctuation behavior for Bangla and mixed English text.
- Keyboard/font/rendering behavior in common target apps.
- Regression risk to the English-only workflow.

Acceptance criteria:

- English-only dictation remains at least as reliable as `v0.1-stable`.
- Bangla dictation produces readable Bangla text from real user speech.
- Embedded English words are not unnecessarily transliterated or corrupted.
- Mixed Bangla/English insertion works in the same target apps as English.
- The language mode is configurable so users can choose English-only, Bangla,
  or mixed/auto mode.

## Decision Standard

Do not build a custom app merely because it is possible. Use an existing app if it is mature, local, reliable, configurable, and privacy-respecting.

Build custom only when the existing options do not satisfy the real daily workflow.
