#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from note_utils import (
    AmbiguousNoteMatchError,
    STATUS_VALUES,
    next_unique_note_path,
    now_iso,
    replace_frontmatter_value,
    resolve_existing_note,
    slugify,
)
from redaction import SensitiveContentError, require_safe_or_confirmed


DEFAULT_BASE_DIR = ".codex/memories"
VALID_MODES = ("repro", "knowledge", "audit")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or resume a conversation memory note with a consistent template.",
    )
    parser.add_argument("--title", required=True, help="Human-readable note title")
    parser.add_argument(
        "--mode",
        action="append",
        choices=VALID_MODES,
        help="Optional explicit mode metadata. Repeat to include multiple modes.",
    )
    parser.add_argument("--slug", help="Optional file slug override")
    parser.add_argument("--path", help="Optional explicit note path")
    parser.add_argument(
        "--workspace",
        default=str(Path.cwd()),
        help="Workspace root used when --path is not provided",
    )
    parser.add_argument(
        "--base-dir",
        default=DEFAULT_BASE_DIR,
        help="Relative directory under the workspace for generated notes",
    )
    parser.add_argument(
        "--status",
        default="in-progress",
        choices=STATUS_VALUES,
        help="Status stored in frontmatter. Defaults to in-progress.",
    )
    parser.add_argument(
        "--allow-redacted-write",
        action="store_true",
        help="Allow saving the redacted form when sensitive content is detected.",
    )
    return parser.parse_args()


def render_note(title: str, modes: list[str] | None, status: str, timestamp: str) -> str:
    frontmatter_lines = [
        "---",
        f"title: {title}",
        f"status: {status}",
        f"created_at: {timestamp}",
        f"updated_at: {timestamp}",
    ]
    if modes:
        frontmatter_lines.append("modes:")
        frontmatter_lines.extend(f"  - {mode}" for mode in modes)
    frontmatter_lines.append("---")

    sections = [
        "## Snapshot\n- Purpose:\n- Current status:\n",
        "## Objective\n- \n",
        "## Constraints\n- \n",
        "## Effective Steps\n- \n",
        "## Decisions\n- \n",
        "## Commands And Artifacts\n- Commands:\n- Files:\n- Outputs:\n",
        "## Validation\n- \n",
        "## Risks And Open Questions\n- \n",
        "## Reuse Notes\n- \n",
    ]

    if modes:
        if "repro" in modes:
            sections.insert(4, "## Reproduction Steps\n- Preconditions:\n- Steps:\n- Observed result:\n")
        if "knowledge" in modes:
            sections.append("## Key Takeaways\n- \n")
        if "audit" in modes:
            sections.append("## Trace\n- Request:\n- Actions:\n- Evidence:\n")

    return "\n".join(frontmatter_lines) + "\n\n" + f"# {title}\n\n" + "\n".join(sections)


def refresh_existing_note(content: str, timestamp: str, status: str) -> str:
    updated = replace_frontmatter_value(content, "updated_at", timestamp)
    updated = replace_frontmatter_value(updated, "status", status)
    return updated


def main() -> int:
    args = parse_args()
    modes = args.mode or None
    try:
        safe_title = require_safe_or_confirmed(
            args.title,
            allow_redacted_write=args.allow_redacted_write,
            field_name="title",
        )
    except SensitiveContentError as exc:
        raise SystemExit(str(exc))

    slug = args.slug or slugify(safe_title)
    timestamp = now_iso()

    if args.path:
        note_path = Path(args.path).expanduser().resolve()
        note_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        workspace = Path(args.workspace).expanduser().resolve()
        base_dir = (workspace / args.base_dir).resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        try:
            existing = resolve_existing_note(base_dir, safe_title)
        except AmbiguousNoteMatchError as exc:
            raise SystemExit(str(exc))
        note_path = existing.path if existing else next_unique_note_path(base_dir, slug, today=timestamp[:10])

    if note_path.exists():
        content = note_path.read_text(encoding="utf-8")
        note_path.write_text(refresh_existing_note(content, timestamp, args.status), encoding="utf-8")
        print(f"RESUMED {note_path}")
        return 0

    note_path.write_text(
        render_note(safe_title, modes, args.status, timestamp),
        encoding="utf-8",
    )
    print(f"CREATED {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
