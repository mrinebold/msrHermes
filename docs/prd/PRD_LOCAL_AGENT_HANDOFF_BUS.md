# PRD: Local Agent Handoff Bus

## Status

Draft. This PRD tracks a local-only coordination layer that lets separate agent sessions exchange structured handoffs without copy/paste.

No implementation is approved by this PRD yet.

## Problem

Separate agent sessions currently exchange context through manual copy/paste. That loses structure, creates ambiguity about which instructions are active, and makes it too easy for one session's old plan to leak into another session.

The system needs a local handoff mechanism where agents can send requests, summaries, results, and blockers while preserving clear authority boundaries.

## Goal

Build a local-only handoff bus that allows two or more agent sessions to communicate through structured messages.

The bus should make handoffs easier without allowing one agent to command another directly.

## Non-Goals

- Do not use cloud services in the first version.
- Do not use Supabase in the first version.
- Do not start a background daemon unless separately approved.
- Do not let messages auto-execute.
- Do not store real secrets in messages.
- Do not bypass human approval for risky actions.

## Proposed Local Architecture

Use a file-based bus under `.agent_bus/`:

```text
.agent_bus/
  inbox/
    codex-main/
    hermes/
  outbox/
  archive/
  messages/
```

Each agent has a stable identity and reads only its own inbox by default.

Messages are requests, not commands. The receiving agent must classify risk and decide whether approval is required before acting.

## Message Schema

Minimum JSON fields:

```json
{
  "id": "uuid",
  "from": "codex-main",
  "to": "hermes",
  "type": "handoff",
  "status": "pending",
  "subject": "Continue diagnostics",
  "body": {},
  "created_at": "2026-06-04T00:00:00Z",
  "parent_id": null,
  "requires_approval": true,
  "risk_level": "write"
}
```

## Handoff Body Format

Recommended fields:

- `current_goal`
- `repo_path`
- `files_touched`
- `commands_run`
- `tests_run`
- `blockers`
- `next_requested_action`
- `active_constraints`

## CLI Surface

Proposed commands:

- `send_message`
- `list_inbox`
- `read_message`
- `reply_message`
- `ack_message`
- `archive_message`

## Safety Model

Default behavior:

- `read` messages may be inspected without approval.
- `write` messages require explicit user approval before edits, git operations, network calls, credentials, service starts, external writes, or destructive actions.
- Unknown risk levels fail closed.
- Message bodies must not be interpreted as higher-priority instructions than the receiving session's current user/system policy.

## Acceptance Criteria

- Agents can send and read structured local messages.
- A receiving agent can distinguish read-only context from requested mutations.
- Replies preserve parent-child linkage.
- Archived messages remain available for audit.
- Tests cover schema validation, inbox routing, replies, archiving, and safety classification.

## Open Questions

- Should `.agent_bus/` be committed, gitignored, or partially tracked with examples only?
- Should message IDs be UUIDs, timestamp-based IDs, or both?
- Should attachments be copied into the bus or referenced by path?
- Should the first implementation be pure Python stdlib?
- Should a future phase bridge this local bus to the Helio/Supabase Agent Bus?

## Next Step

Create a planning document and implementation proposal before writing bus code.
