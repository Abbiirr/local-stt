# PLAN - Phase 2 Packaging And Distribution

Status: active next phase.

The Phase 1 local Windows dictation app is stable-locked as `v0.1-stable` and
archived under:

```text
archive\2026-06-03-v0.1-stable-lock
```

Do not change core dictation behavior in this phase unless a regression is found.
The locked baseline is:

```text
PySide6 tray app
draggable/closable waveform overlay
Ctrl+Alt+D start/stop
Esc cancel while recording
English-only faster-whisper large-v3
CUDA float16 on Windows
local model resolution
clipboard paste with optional typing fallback
rotating app log
PyInstaller onedir Windows build
```

## Objective

Prepare the app so ordinary users can install and run it on:

- Windows
- Ubuntu
- Debian
- Fedora

The immediate goal is distribution readiness, not new dictation features.

## Phase 2.1: Stable Baseline Protection

- [x] Keep the current Windows behavior frozen.
- [x] Define a release/version marker for `v0.1-stable`.
- [x] Keep automated smoke tests passing before packaging changes.
- [x] Document which tests must pass before any release artifact is published.
- [ ] Keep automated smoke tests passing after packaging changes.

## Phase 2.2: Packaging Strategy

- [ ] Decide supported install formats per OS.
- [ ] Windows: keep PyInstaller `--onedir` first; evaluate installer wrapper later.
- [ ] Ubuntu/Debian: evaluate `.deb`, `pipx`, and app directory approaches.
- [ ] Fedora: evaluate `.rpm`, `pipx`, and app directory approaches.
- [ ] Decide whether Linux packages bundle faster-whisper dependencies or install
  them into an isolated environment.
- [ ] Decide model download/cache strategy for each OS.

## Phase 2.3: Cross-Platform Compatibility Audit

- [ ] Audit global hotkey support on Linux.
- [ ] Audit focused-app text insertion on X11 and Wayland.
- [ ] Audit system tray support across GNOME/KDE and common extensions.
- [ ] Audit microphone permissions and device selection on Linux.
- [ ] Audit CUDA runtime expectations on Linux.
- [ ] Identify where Windows-specific packages or APIs need abstraction.

## Phase 2.4: Installer/User Experience

- [ ] Define first-run flow.
- [ ] Provide diagnostics command for every supported OS.
- [ ] Provide model download/check command for every supported OS.
- [ ] Provide startup/autostart setup for Windows and Linux.
- [ ] Provide uninstall instructions.
- [ ] Document log and settings locations per OS.

## Phase 2.5: Release Validation

- [ ] Build fresh Windows onedir artifact.
- [ ] Verify packaged Windows startup.
- [ ] Verify packaged Windows WAV transcription.
- [ ] Verify settings/log creation.
- [ ] Add Linux CI or documented VM test matrix.
- [ ] Run Ubuntu validation.
- [ ] Run Debian validation.
- [ ] Run Fedora validation.
- [ ] Record results in `EVALUATION.md`.

## Non-Goals For This Phase

- Bangla or mixed-language dictation.
- New transcription engines.
- Cloud features.
- Always-listening mode.
- Major UI redesign.

## Current Starting Point

Use the archived Phase 1 docs as the baseline reference:

```text
archive\2026-06-03-v0.1-stable-lock\PLAN.archived.md
archive\2026-06-03-v0.1-stable-lock\TODO.archived.md
archive\2026-06-03-v0.1-stable-lock\REVIEW.archived.md
```
