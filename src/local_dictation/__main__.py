from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config, save_config
from .diagnostics import (
    collect_diagnostics,
    run_cuda_smoke,
    run_microphone_smoke,
    run_nonspeech_smoke,
    run_wav_transcription_smoke,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-dictation",
        description="Local Windows tray dictation with faster-whisper.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Start the tray app.")
    subparsers.add_parser("diagnostics", help="Print environment diagnostics.")
    subparsers.add_parser("print-config", help="Print the effective settings.")
    subparsers.add_parser("write-default-config", help="Create the default settings file.")

    cuda = subparsers.add_parser("smoke-cuda", help="Load a faster-whisper model on CUDA.")
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

    if command == "smoke-cuda":
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

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
