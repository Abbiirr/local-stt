# REVIEW - Local Whisper Dictation

Review status: 2026-06-01. Independently re-verified 2026-06-01 by re-reading the
source and re-running the fast checks (see "Re-verification this pass" below). This
pass also adds a full-source code review (see "Code Review" below).

Scope reviewed: planning/status docs, `TODO.md`, `TESTING.md`, `README.md`,
`TROUBLESHOOTING.md`, package scripts, runtime settings, PyInstaller outputs, and
the full implemented app under `src/local_dictation` (`audio.py`, `config.py`,
`controller.py`, `diagnostics.py`, `inserter.py`, `overlay.py`, `text.py`,
`transcriber.py`, `tray_app.py`, `__main__.py`) plus the test suite.

## Current Verdict

The custom Path C app is implemented, packaged, and validated as far as this
non-interactive shell can honestly validate it.

The major review blockers from the prior pass are resolved:

- Text post-processing no longer corrupts numbers, decimals, email addresses,
  abbreviations, or version numbers.
- Spoken punctuation is opt-in, so ordinary words like `period` and `comma`
  remain literal by default.
- Local `large-v3` resolution is portable: `model_name = "large-v3"` resolves to
  `models\faster-whisper-large-v3` when present.
- Idle model unload is on by default with a 300-second timeout.
- A typing insertion mode exists for targets that block clipboard paste.
- Repeatable CLI smokes exist for WAV transcription and synthetic non-speech.
- PyInstaller builds include the `faster_whisper` VAD asset required for packaged
  transcription.
- Keyboard hook, elevated-window, AV false-positive, spoken-punctuation, and
  idle-VRAM limitations are documented.
- Regression tests were added for the text bugs.

## Resolved Findings

| Finding | Status | Evidence |
| --- | --- | --- |
| F1 number/email corruption | Resolved | Removed the punctuation spacing rule; tests preserve `3,250`, `19.99`, `john.doe@example.com`, `p.m.`, and `7.7`. |
| F2 spoken-punctuation collision | Resolved | `enable_spoken_punctuation = false` by default; literal `period` and `comma` are preserved. |
| F3 docs said custom build was fallback | Resolved | `PLAN.md`, `TODO.md`, `STATUS.md`, and `EVALUATION.md` now state Path C is active. |
| F4 stale large-v3 download notes | Resolved | `TESTING.md` says the model is local and validates `large-v3` resolution. |
| F5 missing evaluation log | Resolved | `EVALUATION.md` exists and records verification. |
| F6 model stayed in VRAM by default | Resolved | `unload_model_when_idle = true`, `unload_after_seconds = 300`. |
| F7 absolute model path in settings | Resolved | Active settings use `model_name = "large-v3"`; resolver maps to the local model directory. |
| F8 paste only | Resolved | `type_text_instead_of_paste` added as an optional insertion mode. |
| F9 keyboard limitations undocumented | Resolved | `TROUBLESHOOTING.md` documents elevated apps, hook behavior, and AV false-positive risk. |
| F10 capitalization/trailing-space behavior | Resolved | `capitalize_transcript` added; `append_trailing_space` was already configurable. |
| F11 missing text regressions | Resolved | Text regression tests added; OS-level inserter/controller tests remain manual. |
| F12 firewall test elevation ambiguity | Resolved | `TESTING.md` now notes elevated PowerShell is required. |
| F13 smoke-cuda redundant download risk | Resolved | `smoke-cuda --model large-v3` resolves to the local model when present. |
| F14 mixed interpreter invocation | Resolved | Testing commands use the explicit venv interpreter where needed. |
| Direct WAV validation | Resolved | `transcribe-wav` matched the generated English WAV exactly. |
| Synthetic non-speech validation | Resolved | `smoke-nonspeech` passed for 5-second silence and white-noise clips. |
| Automated 60-second model latency | Resolved | Repeated generated WAV took 56.31s elapsed for 60.00s audio, 1.07x realtime including model load. |
| Packaged VAD asset | Resolved | `--collect-data faster_whisper` includes `silero_vad_v6.onnx`; packaged `transcribe-wav` now passes. |

## Verification

Latest checks:

```text
python -m compileall -q src tests
python -m unittest discover -s tests -v
python -m local_dictation print-config
python -m local_dictation smoke-cuda --model large-v3
python -m local_dictation transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."
python -m local_dictation smoke-nonspeech --seconds 5
python -m local_dictation transcribe-wav artifacts\en_test.wav --repeat-to-seconds 60
scripts\build_onedir.ps1
dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe print-config
dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe smoke-cuda --model large-v3
dist\LocalWhisperDictationConsole\LocalWhisperDictationConsole.exe transcribe-wav artifacts\en_test.wav --expect-text "The quick brown fox jumps over the lazy dog near the riverbank."
dist\LocalWhisperDictation\LocalWhisperDictation.exe
```

Note: the windowed exe takes no `startup smoke` subcommand. Both exes are built
from `app_launcher.py` -> `main()`, whose only subcommands are `run`,
`diagnostics`, `print-config`, `write-default-config`, `smoke-cuda`, `smoke-mic`,
`transcribe-wav`, and `smoke-nonspeech`. Launched with no arguments it defaults
to `run` and starts the tray app; that is the windowed startup check.

Results:

- Compile: pass.
- Unit tests: 23/23 pass.
- `print-config`: English-only, `model_name = "large-v3"`, spoken punctuation
  off, idle unload on.
- Source CUDA smoke: `large-v3` resolves to
  `K:\projects\ai\stt\models\faster-whisper-large-v3` and loads on CUDA with
  `float16`.
- Packaged console config/CUDA smoke: pass.
- Packaged console WAV transcription: pass, expected text matched.
- Packaged windowed startup: launching the exe with no arguments starts the tray
  app; it stayed running and was stopped cleanly.
- Direct WAV transcription: exact expected text match.
- Synthetic silence/noise smoke: no transcript.
- 60-second repeated generated WAV: 56.31s elapsed, 1.07x realtime including
  model load.

## Re-verification this pass (2026-06-01)

Re-ran on this machine and confirmed independently:

- Unit tests: 23/23 pass (`test_text`, `test_audio`, `test_config`,
  `test_diagnostics`, `test_inserter`, `test_transcriber`).
- F1/F2 fix at runtime: with defaults, `Order 3,250 units at 19.99 dollars, email
  john.doe@example.com by 5 p.m.` and `7.7 times realtime` pass through unchanged,
  and the literal words `period`/`comma` are preserved. Spoken punctuation still
  works when `enable_spoken_punctuation=True`.
- F6: `unload_model_when_idle=True`, `unload_after_seconds=300` (dataclass and live
  `settings.json`).
- F7: live `settings.json` now stores `model_name = "large-v3"`, and
  `resolve_model_name("large-v3")` maps to
  `K:\projects\ai\stt\models\faster-whisper-large-v3`. Both `transcriber.load` and
  `run_cuda_smoke` go through the resolver.
- F8/F10: `inserter.py` honors `type_text_instead_of_paste`; `text.py` honors the
  `capitalize` flag.
- F9/F12/F14: `TROUBLESHOOTING.md` documents the keyboard hook, elevated apps, and
  AV risk; `TESTING.md` notes the firewall proof needs elevated PowerShell, scopes
  `Get-NetTCPConnection` to the project venv process, and uses the explicit venv
  interpreter throughout.
- Build script: `scripts\build_onedir.ps1` passes `--collect-data faster_whisper`
  for both the windowed and console targets; both `dist\...\*.exe` are present.

Carried forward from the recorded run, not re-executed this pass (GPU/build-bound):
the CUDA `large-v3` load, packaged-exe smokes, exact-match WAV transcription, and
the 60-second latency figure (56.31s elapsed, 1.07x realtime). These remain
plausible and consistent with the code, but were not re-timed here.

## Code Review (2026-06-01)

Read every module and the test suite. No correctness/security bugs were found; the
architecture is clean (Qt signals marshal worker-thread updates onto the UI thread,
the model lock serializes load/transcribe/unload, recording buffers are mutex-guarded,
and no audio/transcript is persisted). The robustness and diagnosability findings
from this pass are now resolved or explicitly deferred.

Changes reviewed since the prior pass: `overlay.py`, `tray_app.py`, and
`controller.py` (mtime 10:21) gained a draggable status overlay with a manual close
button — new `WaveOverlay.close_requested`/`reset_user_close`, mouse press/move/release
handlers, and `DictationController.close_overlay`. Reviewed and **correct**: the close
hit-rect matches the painted button, the overlay suppresses re-showing after a manual
close until the next recording (`state_changed=="recording"` → `reset_user_close`, all
on the main thread so the flag clears before `show_status` runs), a dragged position is
remembered, and the status string is now elided to fit. See CR8 for the one minor note.
Tests still pass 23/23. The two P2 items from the prior pass (**CR1, CR2**) have
now been addressed in the code.

| ID | Sev | Area | Finding | Suggested fix |
| --- | --- | --- | --- | --- |
| CR1 | P2 | `tray_app.py` | **Resolved.** Hotkey registration is wrapped in try/except; failures are logged, surfaced through a tray balloon, and the tray/menu app keeps running. | None. |
| CR2 | P2 | app-wide | **Resolved.** A rotating file log is initialized under `%APPDATA%\LocalWhisperDictation\app.log`; tray messages and key exception paths are logged. | None. |
| CR3 | P3 | `controller.py:97-106` | `Esc` only cancels while `recording` is true. Once `stop_recording` flips to `transcribing`, `Esc` is a no-op, so a long transcription cannot be aborted. | Document that cancel applies to recording only, or add a cooperative cancel for in-flight transcription. |
| CR4 | P3 | `audio.py` / `transcriber.py` | **Partially resolved.** `_idle_model_check` now skips while `transcribing`, avoiding a UI-thread wait on the model lock during transcription. The `_recording` bool remains a benign low-risk callback read. | Optional future cleanup only. |
| CR5 | P3 | `config.py` | **Resolved.** `_candidate_roots` now appends the resolved path consistently after deduping. | None. |
| CR6 | P3 | tests | Good coverage on the pure-logic surface (text, config/resolver, inserter modes, idle-unload, WAV decode). Untested: the `controller` recording/transcribing state machine (the most logic-heavy untestable-by-OS piece) — it could be tested with mocked recorder/transcriber/inserter. `AudioRecorder`, `overlay`, and `tray_app` are reasonably left to manual `TESTING.md`. | Optionally add a `controller` unit test with injected mocks. |
| CR7 | info | privacy | Confirmed at the code level: the only outbound network path is faster-whisper's model download when the model is absent; there is no telemetry, no audio/transcript written to disk, and the single ambient capability (the `keyboard` global hook) is documented. This substantiates the T2/privacy claims beyond the firewall test. | None. |
| CR8 | P3 | `overlay.py` | **Resolved for behavior.** Dragged overlay position is clamped to the current screen. Paint/mouse behavior remains manual-QA territory. | Manual check only. |

## Remaining Work

Only user-interactive validation remains:

- Real spoken English dictation through the tray workflow.
- Paste confirmation in browser, notes app, and VS Code.
- One-minute spoken dictation latency through the tray workflow.
- Silence/noise behavior in the user's room through the tray workflow.
- Clean startup after the next Windows reboot.
- Admin firewall-block proof from elevated PowerShell.

Bangla and mixed English/Bangla validation remain deferred to a later milestone.
