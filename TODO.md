# TODO - Phase 2 Packaging And Distribution

Current baseline: `v0.1-stable`.

The previous implementation checklist is archived at:

```text
archive\2026-06-03-v0.1-stable-lock\TODO.archived.md
```

## Stable Lock

- [x] Archive Phase 1 `PLAN.md`, `TODO.md`, `REVIEW.md`, `STATUS.md`, and `EVALUATION.md`.
- [x] Re-run compile check.
- [x] Re-run unit tests.
- [x] Rebuild Windows onedir packages.
- [x] Verify packaged console config.
- [x] Verify packaged console WAV transcription.
- [x] Verify packaged windowed startup.
- [x] Resolve final review robustness findings.
- [x] Keep current dictation behavior frozen for the next phase.

## Packaging Plan

- [x] Define package targets for Windows, Ubuntu, Debian, and Fedora.
- [x] Decide Linux install format: `.deb`, `.rpm`, `pipx`, app directory, or a combination.
- [x] Decide whether to keep PyInstaller for Linux or use native Python packaging.
- [x] Define model download/cache behavior per OS.
- [ ] Define CUDA dependency expectations per OS.
- [x] Define settings/log paths per OS.
- [ ] Define startup/autostart setup per OS.
- [ ] Define uninstall path per OS.

## Compatibility Work

- [ ] Audit Linux global hotkey implementation.
- [ ] Audit Linux text insertion on X11.
- [ ] Audit Linux text insertion on Wayland.
- [ ] Audit Linux tray support across common desktop environments.
- [ ] Audit Linux microphone capture and permissions.
- [ ] Identify Windows-specific code that needs platform abstraction.

## Release Engineering

- [x] Add a version marker for `v0.1-stable`.
- [x] Add release artifact naming convention.
- [x] Add packaging scripts for selected formats.
- [ ] Add release checklist.
- [ ] Add smoke-test script for release artifacts.
- [ ] Add documentation for install, update, and uninstall.

## Validation Matrix

- [x] Windows package validation.
- [ ] Ubuntu package validation.
- [ ] Debian package validation.
- [ ] Fedora package validation.
- [ ] Record validation results in `EVALUATION.md`.

## Deferred

- [ ] Bangla support.
- [ ] Mixed English/Bangla support.
- [ ] Alternative English-only speed model evaluation.
- [ ] Cloud integrations.
- [ ] Major UI redesign.
