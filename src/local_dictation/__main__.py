from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_config, save_config
from .diagnostics import (
    collect_diagnostics,
    load_wav_mono_float32,
    run_cuda_smoke,
    run_microphone_smoke,
    run_nonspeech_smoke,
    run_wav_transcription_smoke,
)
from .history import (
    list_history_entries,
    load_history_entry,
    update_history_error,
    update_history_transcript,
)
from .inserter import TextInserter
from .transcriber import WhisperTranscriber


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-dictation",
        description="Local tray dictation with faster-whisper.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Start the tray app.")
    subparsers.add_parser("diagnostics", help="Print environment diagnostics.")
    subparsers.add_parser("print-config", help="Print the effective settings.")
    subparsers.add_parser("write-default-config", help="Create the default settings file.")

    model = subparsers.add_parser("smoke-model", help="Load a faster-whisper model with the configured device.")
    model.add_argument("--model", default="tiny", help="Model to load. Defaults to tiny.")
    model.add_argument("--compute-type", default=None, help="Override compute type.")

    cuda = subparsers.add_parser("smoke-cuda", help="Compatibility alias for smoke-model.")
    cuda.add_argument("--model", default="tiny", help="Model to load. Defaults to tiny.")
    cuda.add_argument("--compute-type", default=None, help="Override compute type.")

    mic = subparsers.add_parser("smoke-mic", help="Record a short microphone sample without saving it.")
    mic.add_argument("--seconds", type=float, default=1.5, help="Capture duration.")

    wav = subparsers.add_parser("transcribe-wav", help="Transcribe a WAV file with the configured model.")
    wav.add_argument("path", help="Path to a PCM WAV file.")
    wav.add_argument("--expect-text", default=None, help="Fail if the normalized transcript differs.")
    wav.add_argument("--repeat-to-seconds", type=float, default=None, help="Loop the WAV to this duration before transcription.")

    nonspeech = subparsers.add_parser("smoke-nonspeech", help="Verify synthetic silence/noise does not produce text.")
    nonspeech.add_argument("--seconds", type=float, default=5.0, help="Duration of each synthetic clip.")
    nonspeech.add_argument("--noise-amplitude", type=float, default=0.002, help="White-noise standard deviation.")

    history_list = subparsers.add_parser("history-list", help="List saved dictation history entries.")
    history_list.add_argument("--limit", type=int, default=20, help="Maximum entries to print.")

    history_show = subparsers.add_parser("history-show", help="Show one dictation history entry.")
    history_show.add_argument("id", help="History entry id.")

    history_retry = subparsers.add_parser("history-retry", help="Retry transcription for a saved recording.")
    history_retry.add_argument("id", help="History entry id.")
    history_retry.add_argument("--insert", action="store_true", help="Insert recovered text into the focused app.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "run"

    if command == "run":
        from .tray_app import run_app

        return run_app()

    if command == "diagnostics":
        print(collect_diagnostics())
        return 0

    if command == "print-config":
        print(load_config().to_json())
        return 0

    if command == "write-default-config":
        config = load_config()
        path = save_config(config)
        print(f"Wrote {path}")
        return 0

    if command in {"smoke-cuda", "smoke-model"}:
        config = load_config()
        compute_type = args.compute_type or config.compute_type
        print(run_cuda_smoke(model_name=args.model, device=config.device, compute_type=compute_type))
        return 0

    if command == "smoke-mic":
        config = load_config()
        print(run_microphone_smoke(config=config, seconds=args.seconds))
        return 0

    if command == "transcribe-wav":
        config = load_config()
        print(
            run_wav_transcription_smoke(
                config=config,
                wav_path=Path(args.path),
                expected_text=args.expect_text,
                repeat_to_seconds=args.repeat_to_seconds,
            )
        )
        return 0

    if command == "smoke-nonspeech":
        config = load_config()
        print(run_nonspeech_smoke(config=config, seconds=args.seconds, noise_amplitude=args.noise_amplitude))
        return 0

    if command == "history-list":
        for entry in list_history_entries(limit=args.limit):
            print(
                f"{entry.id}\t{entry.status}\t{entry.duration_seconds:.2f}s\t"
                f"{entry.model_name}\t{entry.audio_path}"
            )
        return 0

    if command == "history-show":
        entry = load_history_entry(args.id)
        print(entry.to_dict())
        if entry.transcript_path:
            transcript = Path(entry.transcript_path)
            if transcript.exists():
                print("")
                print(transcript.read_text(encoding="utf-8"))
        if entry.error_path:
            error = Path(entry.error_path)
            if error.exists():
                print("")
                print(error.read_text(encoding="utf-8"))
        return 0

    if command == "history-retry":
        config = load_config()
        entry = load_history_entry(args.id)
        audio = load_wav_mono_float32(Path(entry.audio_path), target_sample_rate=config.sample_rate)
        try:
            text = WhisperTranscriber(config).transcribe(audio)
            update_history_transcript(entry, text)
            print(text)
            if args.insert and text:
                TextInserter(config).insert(text)
            return 0
        except Exception as exc:
            update_history_error(entry, str(exc))
            raise

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
