from __future__ import annotations

import re


COMMAND_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\s*\bnew paragraph\b\s*", "\n\n"),
    (r"\s*\bnew line\b\s*", "\n"),
    (r"\s*\bfull stop\b", "."),
    (r"\s*\bperiod\b", "."),
    (r"\s*\bcomma\b", ","),
    (r"\s*\bquestion mark\b", "?"),
    (r"\s*\bexclamation mark\b", "!"),
    (r"\s*\bcolon\b", ":"),
    (r"\s*\bsemicolon\b", ";"),
)


def post_process_transcript(
    text: str,
    *,
    enable_spoken_punctuation: bool = False,
    capitalize: bool = True,
) -> str:
    text = text.strip()
    if not text:
        return ""

    if enable_spoken_punctuation:
        for pattern, replacement in COMMAND_REPLACEMENTS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"[ \t]+([.,?!:;])", r"\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if capitalize:
        return capitalize_first_letter(text)
    return text


def capitalize_first_letter(text: str) -> str:
    for index, char in enumerate(text):
        if char.isalpha():
            return f"{text[:index]}{char.upper()}{text[index + 1:]}"
    return text
