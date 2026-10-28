# Memory Schema

## Capture Bar

Record an item only when it is likely to matter in one of these later situations:

- rerunning or reproducing the work;
- reusing the result as a knowledge-base entry;
- showing what happened and why;
- resuming the task without rereading the full conversation.

Strong candidates for capture:

- the real user goal and explicit success criteria;
- constraints that changed the implementation or validation path;
- environment facts that affected behavior;
- commands that changed state or produced evidence;
- files created, updated, deleted, or chosen as the source of truth;
- errors, confirmed hypotheses, and the actual fix;
- approvals, decisions, tradeoffs, and unresolved risks.

Do not keep:

- greetings and filler;
- repeated summaries that add no new information;
- speculative branches that never changed the executed path;
- secret values or private identifiers that should not persist.

## Sensitive Data Handling

Never store raw sensitive values in the note.

- detect passwords, card numbers, OTP codes, secrets, tokens, API keys, and similar credentials before writing;
- refuse raw writes when such values are detected;
- show only a redacted preview and require explicit confirmation before saving the redacted form;
- prefer placeholders such as `[REDACTED]`, `[REDACTED:PASSWORD]`, and `[REDACTED:CARD]`;
- if traceability matters, keep only the smallest safe fragment, such as a provider name or the last 4 digits of a card, and only when that detail is truly needed;
- if a user message already contains sensitive data, preserve the event, not the raw value.

## Capture First

During an agent conversation, the eventual use of a note is often unclear.

Default rule:

- capture first;
- classify later;
- do not guess mode, tags, audience, or downstream purpose;
- prefer neutral facts over interpretation.

If the eventual use becomes clear later, enrich the note then. Until that point, keep it general and reusable.

## Task Boundary

Default to one note per task.

Treat work as the same task while the objective, deliverable, and success bar remain materially the same. Start a new note only when the task itself clearly changes.

## Live Update Rule

The note is a running memory, not a retrospective essay.

- create it early;
- keep the path visible in working context;
- append updates after material changes, not every turn;
- prefer sectioned, durable bullets over chat-like transcripts;
- always update `updated_at` when the note changes.

A good live update usually adds one or more bullets to an existing section instead of rewriting the whole file.

## Resume And Match Rules

When continuing the same task:

- prefer reusing the existing note over creating a new one;
- search only within the current workspace boundary;
- if the existing note is `paused` or `complete`, move it back to `in-progress` when work resumes;
- if multiple notes look like valid matches, stop and ask the user which one to continue;
- if no matching note exists, create a new one;
- if the new file name collides, add a readable numeric suffix such as `-2`.

## Location Rules

Choose the destination in this order:

1. Follow an existing project convention, if the repository already has one for notes, runbooks, ADRs, or task journals.
2. Use `<workspace>/.codex/memories/` for personal, iterative, or session-scoped notes.
3. Use `docs/` only when the note is intended to be versioned and shared.

Default file name:

`YYYY-MM-DD-short-slug.md`

## Recommended Frontmatter

Use minimal frontmatter by default:

```yaml
---
title: Example title
status: in-progress
created_at: 2026-10-28T09:00:00+08:00
updated_at: 2026-10-28T09:15:00+08:00
---
```

Add optional metadata such as `modes:` or future tags only when the intended use is explicit.

## Status Lifecycle

Keep the lifecycle small and predictable:

- `in-progress` — the task is actively moving;
- `paused` — the task is temporarily stopped but expected to continue;
- `complete` — the current success bar has been met.

## Core Sections

These sections are the default structure:

1. `Snapshot` — a one-screen summary of the situation and current status.
2. `Objective` — what the user needed and what counted as done.
3. `Constraints` — limits, assumptions, approvals, and non-goals.
4. `Effective Steps` — only the steps that materially advanced or redirected the work.
5. `Decisions` — the decision, the reason, and the impact.
6. `Commands And Artifacts` — commands, files, outputs, links, or generated assets that matter later.
7. `Validation` — how the result was checked and what remains unverified.
8. `Risks And Open Questions` — unresolved items.
9. `Reuse Notes` — what to carry forward next time.

## Incremental Update Mapping

When updating a live note, prefer this mapping:

- changed user goal or success bar -> `Objective`
- changed assumptions, approvals, or non-goals -> `Constraints`
- meaningful action taken -> `Effective Steps`
- committed choice with rationale -> `Decisions`
- commands, file paths, outputs, or generated assets -> `Commands And Artifacts`
- test results or manual checks -> `Validation`
- blockers, doubts, or follow-up questions -> `Risks And Open Questions`
- reusable pattern or takeaway -> `Reuse Notes`

## Optional Usage-Specific Sections

Add these only when the intended use is already explicit:

- `Reproduction Steps` for exact rerun instructions
- `Key Takeaways` for distilled lessons or knowledge-base curation
- `Trace` for audit-oriented request/action/evidence tracking

## Update Rhythm

Update the note when one of these happens:

- the objective or constraints change;
- a decision closes an open branch;
- a command changes repository or environment state;
- a bug is reproduced, diagnosed, fixed, or ruled out;
- validation succeeds or fails;
- the task stops and a handoff is needed.

## Failure Handling

Unless note capture is itself the user's primary goal, creation or update failures should be reported without blocking the main task.

## Quality Bar

The note is good when a future reader can quickly answer all of these:

- What was the task really about?
- Which steps actually mattered?
- What changed in the repository or environment?
- How was the result validated?
- What should happen next?
