#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from redaction import SensitiveContentError, require_safe_or_confirmed


DEFAULT_BASE_DIR = ".codex/memories"
VALID_MODES = ("repro", "knowledge", "audit")


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "memory-note"


def replace_frontmatter_value(content: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^({re.escape(key)}:\s*).*$", re.MULTILINE)
    return pattern.sub(lambda match: f"{match.group(1)}{value}", content, count=1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or reuse a conversation memory note with a consistent template.",
    )
    parser.add_argument("--title", required=True, help="Human-readable note title")
    parser.add_argument(
        "--mode",
        action="append",
        choices=VALID_MODES,
        help="Optional explicit mode metadata. Repeat to include multiple modes.",
    )
    parser.add_argument("--slug", help="Optional file slug override")
    parser.add_argument("--path", help="Optional explicit output path")
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
        help="Initial status stored in frontmatter",
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


def update_timestamp(content: str, timestamp: str) -> str:
    if re.search(r"^updated_at:\s*.*$", content, flags=re.MULTILINE):
        return replace_frontmatter_value(content, "updated_at", timestamp)
    return content


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
    now = datetime.now().astimezone().replace(microsecond=0).isoformat()

    if args.path:
        note_path = Path(args.path).expanduser().resolve()
    else:
        workspace = Path(args.workspace).expanduser().resolve()
        note_path = workspace / args.base_dir / f"{now[:10]}-{slug}.md"

    note_path.parent.mkdir(parents=True, exist_ok=True)

    if note_path.exists():
        content = note_path.read_text(encoding="utf-8")
        note_path.write_text(update_timestamp(content, now), encoding="utf-8")
        print(f"EXISTS {note_path}")
        return 0

    note_path.write_text(
        render_note(safe_title, modes, args.status, now),
        encoding="utf-8",
    )
    print(f"CREATED {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
