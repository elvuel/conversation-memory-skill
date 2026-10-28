---
name: conversation-memory
description: Capture and save the behavior-changing parts of a conversation into a reusable Markdown note. Use when the user wants key steps preserved, a durable audit trail, reusable knowledge capture, a running task journal, or decisions and evidence saved for later reuse. Default to neutral capture first, and add usage-specific classification only when the later use is explicit.
---

# Conversation Memory

A **memory note** captures only the parts of a conversation that changed the work or are likely to matter later.

Treat the note as **live state**, not a retrospective summary.

Treat classification as **optional later enrichment**, not a requirement during capture.

When this skill is used:

1. Start with a neutral note. Do not infer later usage intent, mode, tags, or audience unless the user explicitly provides them.
2. Choose the destination in this order:
   - follow an existing project convention if one exists;
   - otherwise default to `<workspace>/.codex/memories/`;
   - use `docs/` only when the note is meant to be committed and shared.
3. Create the note early, keep its path in working context, and tell the user where it lives.
4. Reuse the existing note for the same task whenever possible. Search only within the current workspace boundary. If multiple candidates match, stop and ask the user which note to continue.
5. Update the note whenever a material event happens:
   - the objective or constraints change;
   - a decision closes an open branch;
   - a command changes repository or environment state;
   - a bug is reproduced, diagnosed, fixed, or ruled out;
   - validation succeeds or fails;
   - the task pauses or is handed off.
6. Capture only durable, behavior-changing information:
   - the user's objective, success bar, and constraints;
   - decisions, approvals, and rejected options that changed the path;
   - commands run, files changed, artifacts produced, and validations performed;
   - errors, root causes, fixes, and remaining risks;
   - exact paths, identifiers, dates, and versions when they will matter later.
7. Omit noise and protect sensitive data:
   - skip small talk, repeated phrasing, and dead-end brainstorming that never affected execution;
   - passwords, card numbers, secrets, tokens, keys, and personal data must never be stored in raw form;
   - when suspected sensitive content appears, refuse the raw write, show only a redacted preview, and require explicit confirmation before saving the redacted form;
   - use placeholders such as `[REDACTED]`, `[REDACTED:PASSWORD]`, and `[REDACTED:CARD]`.
8. Batch updates by meaningful change, not by sentence. Prefer one clean write per material turn over many tiny writes. Default to append-first updates and avoid rewriting older content unless you are correcting a clear error.
9. Add usage-specific sections or metadata only when the user asks for them or the intended use is already clear.
10. Before the final answer, sync the note so it reflects the current stopping point, outcome, and next step.
11. If note creation or updating fails, report the failure clearly but continue the main task unless the user made note capture the primary objective.

Use `references/memory-schema.md` for the capture bar, file placement rules, and note structure. Use `scripts/create_memory_note.py` to create or resume a note and `scripts/update_memory_note.py` to append durable updates to the appropriate section.

**Done when:** a stable note exists, the important effective steps and decisions are recorded during the task, and the note reflects the final outcome or the current stopping point.
