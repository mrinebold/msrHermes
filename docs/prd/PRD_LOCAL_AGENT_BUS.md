# PRD: Local Agent Handoff Bus

## Status

Draft tracking PRD.

This document tracks a local-first way for separate agent sessions to exchange structured handoffs without copy/paste. It does not approve implementation, autonomous execution, credential sharing, or background operation.

## Problem

Agent sessions currently cannot reliably talk to each other. When one session has context another session needs, the human has to copy and paste summaries, prompts, logs, and constraints between windows. That is brittle, noisy, and easy to get wrong during long operational threads.

The desired improvement is a controlled local handoff channel where one agent can leave a structured message for another agent, and the receiving agent can inspect, accept, reject, or ask for clarification.

## Goals

- Provide a local-only message channel for agent session handoffs.
- Preserve enough context for another agent to safely continue or advise.
- Make handoffs inspectable, auditable, and easy for the human to review.
- Treat every message as a request or note, not as an instruction that auto-executes.
- Keep the first version simple enough to test without cloud services or resident daemons.

## Non-Goals

- No automatic task execution from received messages.
- No credential exchange.
- No Supabase, Google, Slack, GitHub, or cloud dependency for the MVP.
- No background service, daemon, launch agent, or resident watcher in the MVP.
- No permission bypass between sessions.
- No direct mutation of another agent's workspace state.

## Users And Actors

- Human operator: decides what sessions should coordinate and approves risky work.
- Sender agent: writes a structured handoff, status update, or question.
- Receiver agent: reads messages and decides what to do with human-visible context.
- Future bridge process: optional local or cloud bridge that may relay messages after the MVP safety model is proven.

## Proposed MVP

Create a local file-backed message bus rooted at `.agent_bus/`.

Suggested structure:

```text
.agent_bus/
  agents/
    codex-main/
      inbox/
      outbox/
      archive/
    codex-side/
      inbox/
      outbox/
      archive/
  messages/
  schema/
```

Each message is a JSON document. Agents can write messages for other named agents, then the receiver can list and inspect its inbox.

## Message Schema

Required fields:

- `id`: stable unique message id.
- `created_at`: ISO 8601 timestamp.
- `from`: sender agent id.
- `to`: receiver agent id or `human`.
- `type`: `handoff`, `question`, `status`, `proposal`, or `review`.
- `status`: `new`, `read`, `acknowledged`, `rejected`, or `archived`.
- `subject`: short human-readable title.
- `body`: structured markdown body.
- `risk_level`: `info`, `low`, `medium`, or `high`.
- `requires_approval`: boolean.

Optional fields:

- `parent_id`: previous message id for threading.
- `workspace`: absolute workspace path if relevant.
- `files`: referenced file paths.
- `commands`: commands already run or proposed.
- `constraints`: active safety constraints.
- `next_actions`: suggested next steps.

Example:

```json
{
  "id": "msg_2026-06-04T15-30-00Z_agent_handoff",
  "created_at": "2026-06-04T15:30:00Z",
  "from": "codex-main",
  "to": "codex-side",
  "type": "handoff",
  "status": "new",
  "subject": "Need review of local adapter plan",
  "risk_level": "info",
  "requires_approval": false,
  "workspace": "/Users/michaelrinebold/Documents/Helio/helio-command-center",
  "body": "Summary, constraints, findings, and requested review go here."
}
```

## Functional Requirements

- Agents can create a message for another named agent.
- Agents can list unread messages addressed to them.
- Agents can read a message without executing any requested action.
- Agents can mark a message as acknowledged, rejected, or archived.
- Messages preserve sender, receiver, timestamps, status, risk level, and approval requirement.
- The bus supports handoff summaries, questions, status notes, and proposals.
- The bus keeps an append-only audit trail for sent and received messages.

## Safety Requirements

- Receiving agents must treat bus messages as untrusted input.
- Messages must never contain secrets, tokens, cookies, private keys, or live credentials.
- Prompt or command text inside messages must not be executed automatically.
- Any requested file write, git operation, network access, credentialed integration, external service call, destructive command, or background operation requires fresh human approval in the receiving session.
- The bus must not expose a network listener in the MVP.
- The bus must fail closed when schema validation fails.

## CLI Contract

Future local tooling may expose:

```text
agent-bus send --to <agent> --type handoff --subject <subject> --body-file <file>
agent-bus inbox --agent <agent>
agent-bus read --agent <agent> --id <message-id>
agent-bus ack --agent <agent> --id <message-id>
agent-bus reject --agent <agent> --id <message-id>
agent-bus archive --agent <agent> --id <message-id>
```

The CLI must validate schema, avoid logging secrets, and avoid network access by default.

## Phases

### LAB-1: PRD And Schema

- Create this tracking PRD.
- Define schema fields, safety model, and MVP boundaries.
- Decide canonical agent ids and local bus path.

### LAB-2: Local File Bus Scaffold

- Create `.agent_bus/` layout.
- Add schema validation.
- Add local send, list, read, acknowledge, reject, and archive commands.
- Add tests using only temporary directories.

### LAB-3: Agent Handoff Dry Run

- Have one session write a non-sensitive handoff.
- Have another session read and summarize it.
- Confirm no automatic execution occurs.

### LAB-4: Codex/Hermes Integration Notes

- Document how Codex sessions and Hermes should identify themselves.
- Document when a human must approve a received request.
- Keep resident operation disabled.

### LAB-5: Optional Bridge Review

- Evaluate whether a future bridge should sync messages to Supabase or another shared system.
- Require a separate security review before any cloud-backed bridge.

## Success Metrics

- Handoffs require less copy/paste.
- A receiving agent can reconstruct current state from a single message.
- Message history is auditable.
- No received message can trigger automatic mutation.
- No credentials are stored in the bus.

## Open Questions

- What should the canonical local path be: `.agent_bus/` in each repo, a user-level directory, or both?
- Should agent ids be human-assigned, session-generated, or derived from tool identity?
- How long should messages be retained before archive cleanup?
- Should messages support attachments, or only references to files?
- What is the minimum UI needed so the human can see and approve handoffs comfortably?
