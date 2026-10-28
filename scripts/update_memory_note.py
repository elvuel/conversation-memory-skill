#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import tempfile
import time
from pathlib import Path

from note_utils import STATUS_VALUES, now_iso, replace_frontmatter_value
from redaction import SensitiveContentError, require_safe_or_confirmed


SECTION_TITLES = {
    "snapshot": "Snapshot",
    "objective": "Objective",
    "constraints": "Constraints",
    "effective-steps": "Effective Steps",
    "reproduction-steps": "Reproduction Steps",
    "decisions": "Decisions",
    "commands-and-artifacts": "Commands And Artifacts",
    "validation": "Validation",
    "risks-and-open-questions": "Risks And Open Questions",
    "reuse-notes": "Reuse Notes",
    "key-takeaways": "Key Takeaways",
    "trace": "Trace",
}


class FileLock:
    def __init__(self, target: Path, timeout_seconds: float = 10.0, poll_seconds: float = 0.1):
        self.lock_path = target.with_suffix(target.suffix + ".lock")
        self.timeout_seconds = timeout_seconds
        self.poll_seconds = poll_seconds
        self.fd: int | None = None

    def __enter__(self) -> "FileLock":
        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                self.fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self.fd, str(os.getpid()).encode("utf-8"))
                return self
            except FileExistsError:
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out waiting for lock: {self.lock_path}")
                time.sleep(self.poll_seconds)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        if self.lock_path.exists():
            self.lock_path.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append durable updates into a conversation memory note.",
    )
    parser.add_argument("--path", required=True, help="Path to the memory note")
    parser.add_argument(
        "--section",
        required=True,
        choices=tuple(SECTION_TITLES.keys()),
        help="Target section slug",
    )
    parser.add_argument(
        "--bullet",
        action="append",
        default=[],
        help="Bullet line to append. Repeat for multiple bullets.",
    )
    parser.add_argument("--text", help="Optional paragraph or block to append")
    parser.add_argument(
        "--status",
        choices=STATUS_VALUES,
        help="Optional status value to write into frontmatter",
    )
    parser.add_argument(
        "--timestamp-prefix",
        action="store_true",
        help="Prefix appended bullets with an ISO timestamp",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Append duplicates instead of skipping existing identical lines",
    )
    parser.add_argument(
        "--allow-redacted-write",
        action="store_true",
        help="Allow saving the redacted form when sensitive content is detected.",
    )
    return parser.parse_args()


def atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=path.parent) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, path)


def update_frontmatter(content: str, timestamp: str, status: str | None) -> str:
    updated = replace_frontmatter_value(content, "updated_at", timestamp)
    if status and re.search(r"^status:\s*.*$", updated, flags=re.MULTILINE):
        updated = replace_frontmatter_value(updated, "status", status)
    return updated


def build_entries(args: argparse.Namespace, timestamp: str) -> list[str]:
    entries: list[str] = []
    prefix = f"[{timestamp}] " if args.timestamp_prefix else ""
    for bullet in args.bullet:
        safe_bullet = require_safe_or_confirmed(
            bullet,
            allow_redacted_write=args.allow_redacted_write,
            field_name="bullet",
        )
        entries.append(f"- {prefix}{safe_bullet}".rstrip())
    if args.text:
        block = require_safe_or_confirmed(
            args.text.rstrip(),
            allow_redacted_write=args.allow_redacted_write,
            field_name="text",
        )
        if prefix:
            block = prefix + block
        entries.append(block)
    return entries


def upsert_section(content: str, title: str, entries: list[str], allow_duplicates: bool) -> str:
    pattern = re.compile(rf"(?ms)^##\s+{re.escape(title)}\s*\n(.*?)(?=^##\s+|\Z)")
    match = pattern.search(content)
    if match:
        body = match.group(1)
        body_lines = body.splitlines()
        meaningful_lines = [
            line for line in body_lines if line.strip() and not re.match(r"^\s*-\s*$", line)
        ]
        existing_lines = {line.rstrip() for line in meaningful_lines}
        additions = []
        for entry in entries:
            if allow_duplicates or entry.rstrip() not in existing_lines:
                additions.append(entry)
        if not additions:
            return content
        new_body = "\n".join(meaningful_lines)
        if new_body:
            new_body += "\n\n" + "\n".join(additions) + "\n"
        else:
            new_body = "\n".join(additions) + "\n"
        return content[: match.start(1)] + new_body + content[match.end(1) :]

    append_block = f"## {title}\n" + "\n".join(entries) + "\n"
    return content.rstrip() + "\n\n" + append_block + "\n"


def main() -> int:
    args = parse_args()
    note_path = Path(args.path).expanduser().resolve()
    timestamp = now_iso()
    try:
        entries = build_entries(args, timestamp)
    except SensitiveContentError as exc:
        raise SystemExit(str(exc))
    if not entries and not args.status:
        raise SystemExit("Nothing to update. Provide --bullet, --text, or --status.")

    with FileLock(note_path):
        content = note_path.read_text(encoding="utf-8")
        updated = content
        if entries:
            updated = upsert_section(
                updated,
                SECTION_TITLES[args.section],
                entries,
                args.allow_duplicates,
            )
        status_changed = bool(
            args.status and not re.search(rf"^status:\s*{re.escape(args.status)}\s*$", content, flags=re.MULTILINE)
        )
        if not status_changed and updated == content:
            print(f"UNCHANGED {note_path}")
            return 0
        updated = update_frontmatter(updated, timestamp, args.status)
        atomic_write(note_path, updated)

    print(f"UPDATED {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
