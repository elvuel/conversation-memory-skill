#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


STATUS_VALUES = ("in-progress", "paused", "complete")
DATE_PREFIX_PATTERN = r"\d{4}-\d{2}-\d{2}"


@dataclass(frozen=True)
class NoteMetadata:
    path: Path
    title: str | None
    status: str | None
    updated_at: str | None


class AmbiguousNoteMatchError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "memory-note"


def replace_frontmatter_value(content: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^({re.escape(key)}:\s*).*$", re.MULTILINE)
    return pattern.sub(lambda match: f"{match.group(1)}{value}", content, count=1)


def parse_frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        return {}
    end_index = content.find("\n---\n", 4)
    if end_index == -1:
        return {}
    block = content[4:end_index]
    parsed: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        parsed[match.group(1)] = match.group(2).strip()
    return parsed


def read_note_metadata(path: Path) -> NoteMetadata:
    content = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)
    return NoteMetadata(
        path=path,
        title=frontmatter.get("title") or None,
        status=frontmatter.get("status") or None,
        updated_at=frontmatter.get("updated_at") or None,
    )


def iter_note_files(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted(path for path in base_dir.glob("*.md") if path.is_file())


def find_exact_title_matches(base_dir: Path, title: str) -> list[NoteMetadata]:
    matches: list[NoteMetadata] = []
    for note_path in iter_note_files(base_dir):
        metadata = read_note_metadata(note_path)
        if metadata.title == title:
            matches.append(metadata)
    return sorted(matches, key=lambda item: item.path.name)


def format_note_candidates(candidates: list[NoteMetadata]) -> str:
    lines = []
    for candidate in candidates:
        status = candidate.status or "unknown"
        title = candidate.title or "<missing-title>"
        updated_at = candidate.updated_at or "<missing-updated_at>"
        lines.append(f"- {candidate.path} | status={status} | updated_at={updated_at} | title={title}")
    return "\n".join(lines)


def resolve_existing_note(base_dir: Path, title: str) -> NoteMetadata | None:
    matches = find_exact_title_matches(base_dir, title)
    if not matches:
        return None
    if len(matches) > 1:
        details = format_note_candidates(matches)
        raise AmbiguousNoteMatchError(
            "Multiple candidate notes match this task. Choose one explicitly with --path:\n"
            f"{details}"
        )
    return matches[0]


def next_unique_note_path(base_dir: Path, slug: str, *, today: str | None = None) -> Path:
    date_prefix = today or now_iso()[:10]
    base_path = base_dir / f"{date_prefix}-{slug}.md"
    if not base_path.exists():
        return base_path
    suffix = 2
    while True:
        candidate = base_dir / f"{date_prefix}-{slug}-{suffix}.md"
        if not candidate.exists():
            return candidate
        suffix += 1
