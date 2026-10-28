# Conversation Memory Skill

A Codex skill for capturing the behavior-changing parts of a conversation and saving them as reusable Markdown notes.

## What It Does

- creates a neutral memory note early in a task;
- keeps the note updated throughout the conversation;
- records durable steps, decisions, validations, risks, and reusable takeaways;
- avoids chat noise and redacts sensitive values;
- detects common sensitive values such as passwords, card numbers, tokens, and API keys;
- refuses raw writes when sensitive values are detected, and only saves the redacted form after explicit confirmation;
- defers classification until the note's eventual use is clear.

## Repository Layout

- `SKILL.md` - skill entrypoint and operating rules
- `agents/openai.yaml` - UI metadata
- `references/memory-schema.md` - capture rules, note structure, and update mapping
- `scripts/redaction.py` - shared redaction helpers for note content
- `scripts/create_memory_note.py` - scaffolds a memory note
- `scripts/update_memory_note.py` - appends durable updates to the appropriate section

## Usage

Create a neutral note:

```powershell
python scripts/create_memory_note.py --title "Issue Reproduction" --workspace D:\projects\some-repo
```

If sensitive content is detected and you want to save the redacted version explicitly:

```powershell
python scripts/create_memory_note.py --title "password=abc123" --workspace D:\projects\some-repo --allow-redacted-write
```

Append an update:

```powershell
python scripts/update_memory_note.py --path D:\projects\some-repo\.codex\memories\2026-10-28-issue-reproduction.md --section effective-steps --bullet "Reproduced the failure locally." --timestamp-prefix
```

If sensitive content is detected in an update and you want to save the redacted version explicitly:

```powershell
python scripts/update_memory_note.py --path D:\projects\some-repo\.codex\memories\2026-10-28-issue-reproduction.md --section effective-steps --bullet "token=xyz and card=4111 1111 1111 1111 were observed" --timestamp-prefix --allow-redacted-write
```

## Validation

```powershell
python -m py_compile scripts/redaction.py scripts/create_memory_note.py scripts/update_memory_note.py
```
