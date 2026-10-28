#!/usr/bin/env python3
from __future__ import annotations

import re


ASSIGNMENT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(?i)\b(password|passwd|pwd)(\s*[:=]\s*)(\S+)"),
        r"\1\2[REDACTED:PASSWORD]",
    ),
    (
        re.compile(r"(?i)\b(pin|otp|cvv|cvc)(\s*[:=]\s*)(\S+)"),
        r"\1\2[REDACTED:CODE]",
    ),
    (
        re.compile(r"(?i)\b(secret|token|api[_-]?key|access[_-]?key)(\s*[:=]\s*)(\S+)"),
        r"\1\2[REDACTED:SECRET]",
    ),
]

CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


class SensitiveContentError(ValueError):
    pass


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern, replacement in ASSIGNMENT_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    redacted = CARD_PATTERN.sub("[REDACTED:CARD]", redacted)
    return redacted


def contains_sensitive_text(text: str) -> bool:
    return redact_sensitive_text(text) != text


def require_safe_or_confirmed(text: str, *, allow_redacted_write: bool, field_name: str) -> str:
    redacted = redact_sensitive_text(text)
    if redacted == text:
        return text
    if allow_redacted_write:
        return redacted
    raise SensitiveContentError(
        f"Sensitive content detected in {field_name}. Refusing raw write. "
        f"Review the redacted value and rerun with --allow-redacted-write if you want to save it: {redacted}"
    )
