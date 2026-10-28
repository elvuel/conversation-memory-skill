# Conversation Memory Skill

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-412991?logo=openai&logoColor=white)](https://github.com/elvuel/conversation-memory-skill)
[![Conversation Memory](https://img.shields.io/badge/Purpose-Conversation%20Memory-2ea44f)](https://github.com/elvuel/conversation-memory-skill)
[![Sensitive Data Redaction](https://img.shields.io/badge/Sensitive%20Data-Redacted-1f6feb)](https://github.com/elvuel/conversation-memory-skill)
[![Last Commit](https://img.shields.io/github/last-commit/elvuel/conversation-memory-skill)](https://github.com/elvuel/conversation-memory-skill/commits/main)
[![GitHub Stars](https://img.shields.io/github/stars/elvuel/conversation-memory-skill?style=social)](https://github.com/elvuel/conversation-memory-skill)

> **English**: A Codex skill that captures the behavior-changing parts of a working conversation and saves them as reusable Markdown notes for replay, knowledge capture, audit trails, and later handoff.
>
> **中文**：一个面向 Codex 的技能，用来把对话中真正影响执行结果的关键步骤、决策、验证和证据沉淀为可复用的 Markdown 记录，方便后续重现、知识复用、留痕与交接。

A Codex skill for capturing the behavior-changing parts of a conversation and saving them as reusable Markdown notes.

## Quick Start

Use this skill when you want Codex to keep a durable task note automatically while working.

### 1. Ask Codex normally

```text
Help me build a TODO web app with React and TypeScript.
Please automatically record the key steps, decisions, validation results,
and reusable conclusions for later replay and knowledge reuse.
```

### 2. Let the skill capture the task note

By default, the skill will create or reuse a note under the current workspace:

```text
<workspace>/.codex/memories/
```

### 3. Expect the note to capture only durable changes

The note records:

- objective and success bar;
- constraints and scope changes;
- decisions that changed implementation direction;
- commands, files, outputs, and validations;
- risks, open questions, and reuse guidance.

The note does **not** keep raw secrets, passwords, tokens, card numbers, or other sensitive values.

## What It Does

- creates a neutral memory note early in a task;
- reuses the same note when the same task continues;
- asks the user to choose when more than one existing note looks like a valid match;
- records durable steps, decisions, validations, risks, and reusable takeaways;
- prefers append-first updates over rewriting old history;
- avoids chat noise and redacts sensitive values;
- detects common sensitive values such as passwords, card numbers, tokens, and API keys;
- refuses raw writes when sensitive values are detected, and only saves the redacted form after explicit confirmation;
- defers classification until the note's eventual use is clear.

## Repository Layout

- `SKILL.md` - skill entrypoint and operating rules
- `agents/openai.yaml` - UI metadata
- `references/memory-schema.md` - capture rules, note structure, and update mapping
- `scripts/note_utils.py` - note matching, frontmatter helpers, and file naming logic
- `scripts/redaction.py` - shared redaction helpers for note content
- `scripts/create_memory_note.py` - creates or resumes a memory note
- `scripts/update_memory_note.py` - appends durable updates to the appropriate section

## Usage

Create or resume a neutral note for the same task:

```powershell
python scripts/create_memory_note.py --title "Issue Reproduction" --workspace D:\projects\some-repo
```

If sensitive content is detected and you want to save the redacted version explicitly:

```powershell
python scripts/create_memory_note.py --title "password=abc123" --workspace D:\projects\some-repo --allow-redacted-write
```

Append an update:

```powershell
python scripts/update_memory_note.py --path D:\projects\some-repo\.codex\memories\2026-10-28-issue-reproduction.md --section effective-steps --bullet "Reproduced the failure locally."
```

Append a timestamped update only when timing matters:

```powershell
python scripts/update_memory_note.py --path D:\projects\some-repo\.codex\memories\2026-10-28-issue-reproduction.md --section validation --bullet "Regression test passed after the fix." --timestamp-prefix
```

If sensitive content is detected in an update and you want to save the redacted version explicitly:

```powershell
python scripts/update_memory_note.py --path D:\projects\some-repo\.codex\memories\2026-10-28-issue-reproduction.md --section effective-steps --bullet "token=xyz and card=4111 1111 1111 1111 were observed" --allow-redacted-write
```

## Validation

```powershell
python -m py_compile scripts/note_utils.py scripts/redaction.py scripts/create_memory_note.py scripts/update_memory_note.py
```
