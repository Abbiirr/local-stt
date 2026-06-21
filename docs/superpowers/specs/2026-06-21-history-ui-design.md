# History UI — Design

**Date:** 2026-06-21
**Status:** Approved (implementation in progress)

## Problem

A dictation-history backend was merged (`history.py`, controller hooks, CLI subcommands
`history-list` / `history-show` / `history-retry`). It is **CLI-only** — a tray/GUI user has no
way to see past transcriptions, recover failed ones, or retry. The single most important
requirement: **a recording must never be lost, even when transcription fails.**

## Goal

Add a minimal graphical history window, reachable from the tray menu, that lists recent
recordings (including failed/empty/too-short ones) and lets the user copy, re-insert, retry,
delete, and open the recording folder for any entry.

## Requirements (from user)

- View all recent transcribes, including failed ones, with transcript/error preview.
- **Retry available for every entry** (a successful transcription may still be wrong).
- Per-entry actions: Copy transcript, Re-insert into focused app, Delete, Open recording folder.
- Recovered text from a retry is shown in the window with a Copy button.
- Opened from a tray-menu "History…" item.
- Never lose a recording even if transcription fails.

## Architecture

Master–detail single window.

### New module `src/local_dictation/history_window.py`
`HistoryWindow(QWidget)`:
- Left: `QListWidget` populated from `list_history_entries()`. Each row: `HH:MM · status ·
  1.2s · "snippet…"`, with a status color cue (failed=red, empty/too_short=amber,
  transcribed=default, recorded=muted).
- Right: metadata `QLabel` + read-only `QTextEdit` showing transcript, or error text for
  failed entries.
- Button row: **Copy**, **Insert**, **Retry**, **Delete**, **Open folder**, **Refresh**.
- Constructed lazily and reused (single instance held by the tray app).

### `controller.py`
- New signal `history_retry_done = Signal(str, str, str)` → `(entry_id, text, error)`.
- New method `retry_history_entry(entry)`:
  - If `transcribing` (live dictation in progress) → emit a busy message, do nothing.
  - Else set `transcribing = True`, spawn a daemon worker thread that loads `audio.wav` via
    `load_wav_mono_float32(path, target_sample_rate=config.sample_rate)`, runs
    `self.transcriber.transcribe(audio)` (reusing the already-loaded model), calls
    `update_history_transcript` / `update_history_error`, emits `history_retry_done`,
    and clears `transcribing` in `finally`.
- Harden `stop_recording`: wrap `create_history_entry` so a history I/O failure logs +
  notifies but never crashes the flow.

### `tray_app.py`
- Add a "History…" `QAction` before the separator; on trigger, build (once) and `show()` /
  `raise_()` the `HistoryWindow`, passing it the `controller` and `config`.
- Connect `controller.history_retry_done` to the window's refresh handler.

## Data flow

1. Open → `list_history_entries()` → populate list.
2. Select row → read `metadata.json` + `transcript.txt` / `error.txt` → fill detail pane;
   enable/disable buttons by state (Insert/Copy disabled when no transcript).
3. **Copy** → `QApplication.clipboard().setText(text)`.
4. **Insert** → `hide()` the window, then after a short `QTimer` delay (let focus return to the
   previous app) call `TextInserter(config).insert(text)`.
5. **Open folder** → `QDesktopServices.openUrl(QUrl.fromLocalFile(entry_dir))`.
6. **Delete** → confirm dialog → `shutil.rmtree(entry_dir)` → refresh list.
7. **Retry** → `controller.retry_history_entry(entry)` → on `history_retry_done` refresh the
   row and show recovered text with Copy enabled.

## Never-lose-a-recording

- `create_history_entry` writes `audio.wav` **before** transcription (already true) — keep that
  ordering.
- Wrap the `create_history_entry` call in `stop_recording` in try/except so a save error can
  never crash recording or discard in-memory audio.
- Retry only writes `transcript.txt` / updates status — it never touches `audio.wav`.

## Error handling

- Empty history → "No recordings yet." placeholder.
- Missing `audio.wav` on retry → friendly error in the detail pane; entry left intact.
- All disk/clipboard ops wrapped; failures surface in the UI, never crash the tray app.

## Testing (offscreen Qt, like `tests/test_overlay.py`)

- `tests/test_history_window.py`: window populates from a temp history dir; row selection
  fills the detail pane; button enable/disable logic; Delete removes the dir; Copy sets
  clipboard text; empty-history placeholder.
- `tests/test_controller.py` (or new `tests/test_controller_retry.py`): `retry_history_entry`
  with a mocked transcriber — success updates transcript+status, failure records error, busy
  state is rejected.
- Existing `tests/test_history.py` continues to cover the backend.

## Out of scope

- Audio playback inside the window (Open folder is enough to reach `audio.wav`).
- Pagination / search (list is bounded by `list_history_entries(limit=...)`).
- Editing transcripts in place.
