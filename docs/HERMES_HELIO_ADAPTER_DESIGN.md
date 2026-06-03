# Hermes Helio Adapter Design

## Status

Phase 6C scaffold proposal only. Do not implement `services/agent_bus/` yet.

This design uses [Agent Bus Contract](AGENT_BUS_CONTRACT.md) as the canonical message-bus contract and keeps Hermes behind Helio. It does not authorize direct Supabase access, direct agent dispatch, autonomous execution, or task execution.

## Goal

Design the minimum safe Hermes-to-Helio adapter so Hermes can observe and prepare bus-compatible messages without owning the Supabase Agent Bus.

Hermes remains the resident Mac mini operator. Helio remains the governed adapter to the MSR/CivicGrantsAI agent team and the only layer that may eventually use `ano-messaging` services with real credentials.

## Narrow Initial Scope

Initial scope is read-only plus dry-run payload construction:

- Read inbound `agent_messages` addressed to `hermes`, through Helio only.
- Resolve `org_messaging_config`, through Helio only.
- Respect polling behavior defined by `ano-messaging`: no realtime subscription assumption.
- Respect directive scanning semantics when rendering dry-run outbound payloads.
- Respect baseline behavior by treating message reads as inputs to monitoring, not execution.
- Dry-run outbound `bot_outbound_messages` payloads using the Helio-compatible contract.
- Do not execute tasks.
- Do not create `agent_tasks`.
- Do not create approvals.
- Do not write `agent_messages`.
- Do not write `bot_outbound_messages` in read-only mode.

The adapter is a local Hermes-side client for Helio, not an `ano-messaging` wrapper and not a Supabase client.

## Explicit Non-Scope

- No Supabase connection.
- No service-role key handling.
- No direct `agent_messages` writes.
- No task dispatch or task status mutation.
- No approvals table integration.
- No background worker or launchd service.
- No autonomous polling loop.
- No modification to `/Users/michaelrinebold/dev/msrresearch/msrresearch/packages/ano-messaging`.

## Proposed Structure

Proposed only; do not create these files in Phase 6C.

```text
services/agent_bus/
  config.py
  client.py
  schemas.py
  audit.py
  permissions.py
  README.md
```

### config.py

Purpose: parse local adapter settings and fail closed before any Helio call.

Responsibilities:

- Read `HELIO_AGENT_BUS_MODE`.
- Read `HELIO_GATEWAY_URL`.
- Read `HELIO_DEFAULT_ORG`.
- Read `HELIO_DEFAULT_WORKSPACE`.
- Validate allowed modes.
- Refuse operation when mode is missing, unknown, or `disabled`.
- Never read or expose `SUPABASE_SERVICE_ROLE_KEY`.

Proposed modes:

| Mode | Allowed behavior |
| --- | --- |
| `disabled` | No bus operations. |
| `read_only` | List org config and read recent inbound messages via Helio. |
| `dry_run` | Read-only plus payload construction without writes. |
| `outbound_with_approval` | Later mode: insert `bot_outbound_messages` through Helio after explicit approval. |

### client.py

Purpose: local Hermes-to-Helio API client.

Responsibilities:

- Call Helio endpoints on localhost or another approved gateway URL.
- Provide read-only calls for org config and inbound messages.
- Provide dry-run outbound payload validation.
- Provide a later approved outbound write call that targets `bot_outbound_messages` only.
- Never import `supabase`.
- Never instantiate `ano_messaging.MessageService` or `OutboundService` directly.

Proposed Helio endpoints:

| Method | Path | Initial mode |
| --- | --- | --- |
| `GET` | `/agent-bus/orgs` | `read_only` |
| `GET` | `/agent-bus/orgs/{org_id}/messaging-config` | `read_only` |
| `GET` | `/agent-bus/messages/inbound/hermes` | `read_only` |
| `POST` | `/agent-bus/outbound/dry-run` | `dry_run` |
| `POST` | `/agent-bus/outbound` | later `outbound_with_approval` |

### schemas.py

Purpose: local typed shapes for Hermes/Helio requests and responses.

Proposed schema names:

- `AgentBusMode`
- `OrgMessagingConfigSummary`
- `InboundAgentMessage`
- `OutboundBotMessageDraft`
- `OutboundBotMessageDryRunResult`
- `AdapterError`

Schema source:

- `InboundAgentMessage` maps to `agent_messages` columns from `docs/AGENT_BUS_CONTRACT.md`.
- `OutboundBotMessageDraft` maps to `bot_outbound_messages` columns from `docs/AGENT_BUS_CONTRACT.md`.
- `OrgMessagingConfigSummary` maps to `org_messaging_config` config types from `docs/AGENT_BUS_CONTRACT.md`.

### audit.py

Purpose: local adapter audit records for Hermes-side visibility.

Responsibilities:

- Record local read/dry-run/write-attempt events to a local log only after approval.
- Redact payloads before writing local audit records.
- Include `hermes_request_id`, `org_id`, `workspace`, action, mode, outcome, and timestamp.
- Do not store secrets.
- Do not store raw message transcripts unless explicitly approved.

Initial Phase 6C recommendation: document audit shape only; do not create log writer code until scaffold implementation is approved.

### permissions.py

Purpose: centralize mode and target checks.

Responsibilities:

- Reject unsupported orgs or workspaces.
- Reject unsupported message targets.
- Reject writes unless mode and explicit approval allow them.
- Reject direct `agent_messages` write attempts.
- Reject task execution attempts.
- Reject approval mutation attempts.

### README.md

Purpose: local module explanation when scaffold is approved.

Required content:

- Link to `docs/AGENT_BUS_CONTRACT.md`.
- Link to this design.
- Explain that the adapter is Helio-facing only.
- Explain read-only-first behavior.
- Explain that Supabase and `ano-messaging` are Helio responsibilities.

## Exact Fail-Closed Behavior

| Condition | Required behavior |
| --- | --- |
| Missing `HELIO_AGENT_BUS_MODE` | Treat as `disabled`; refuse all bus operations. |
| `HELIO_AGENT_BUS_MODE=disabled` | Refuse all bus operations and return a clear disabled-mode error. |
| Unknown mode | Refuse startup for the adapter. |
| Missing `HELIO_GATEWAY_URL` in non-disabled mode | Refuse all bus operations. |
| Missing `HELIO_DEFAULT_ORG` | Refuse org-scoped reads and dry runs. |
| Missing `HELIO_DEFAULT_WORKSPACE` | Refuse workspace-scoped reads and dry runs. |
| Missing Supabase config | No direct effect in Hermes adapter because Hermes must not read Supabase config; if Helio reports missing config, surface read-only error. |
| Unknown org/workspace | Refuse operation; do not fall back to `msr` silently. |
| Unavailable `org_messaging_config` | Refuse target resolution, dry-run writes, and any later outbound write. |
| Unsupported message target | Refuse dry run and later write. |
| Unsupported bot target | Refuse dry run and later write. |
| Write not approved | Return `requires_approval`; do not call Helio write endpoint. |
| Helio unavailable | Return unavailable error; do not retry indefinitely. |
| Directive scanner returns blocked | Dry-run result is blocked; do not allow later write without human review and Helio policy override. |

## Read-Only First Mode

Read-only mode is the first approved implementation target.

Allowed:

- List available org messaging config summaries through Helio.
- Read recent `agent_messages` addressed to `hermes` through Helio.
- Read recent message metadata and status only.
- Build dry-run outbound payloads in `dry_run` mode.
- Show whether a dry-run payload would pass target checks and scanning.

Not allowed:

- Claim messages.
- Complete messages.
- Fail messages.
- Insert messages.
- Insert outbound bot messages.
- Create tasks.
- Create approvals.
- Start background polling.

Inbound message query shape:

```json
{
  "org_id": "msr",
  "workspace": "default",
  "to_agent": "hermes",
  "status": ["pending", "claimed", "executing", "completed", "failed"],
  "limit": 25
}
```

Dry-run outbound payload shape:

```json
{
  "org_id": "msr",
  "workspace": "default",
  "bot_name": "summit",
  "chat_id_ref": "approved-chat-ref",
  "message_text": "Draft status note; no secrets.",
  "parse_mode": null,
  "reply_to_message_id": null,
  "requested_by": "hermes",
  "hermes_request_id": "uuid"
}
```

Use `chat_id_ref`, not a raw Telegram ID, in Hermes-facing drafts. Helio may resolve the reference if a later write is approved.

## Later Write Mode

Later write mode is restricted to `bot_outbound_messages` inserts through Helio.

Allowed after explicit approval:

- Insert a `bot_outbound_messages` row through Helio.
- Use only the fields defined in `docs/AGENT_BUS_CONTRACT.md`.
- Include `requested_by='hermes'` or `requested_by='hermes_via_helio'`.
- Include `org_id` resolved from approved config.

Never allowed in the Hermes adapter:

- Direct `agent_messages` insert.
- Direct `agent_messages` claim/complete/fail.
- Direct task creation or mutation.
- Direct approval creation or mutation.
- Direct Supabase RPC calls.
- Direct use of `ano_messaging.MessageService`.
- Direct use of `ano_messaging.OutboundService`.

Rationale: `agent_messages` is an execution bus. Hermes writing directly to it would bypass Helio dispatch governance. `bot_outbound_messages` is an outbound delivery queue and can be safer for status notifications, but only when Helio resolves bot ACL, org scope, chat reference, and approval.

## Polling, Scanning, and Baseline Behavior

Polling:

- The canonical package uses polling for `agent_messages` and `bot_outbound_messages`.
- The Hermes adapter must not create a background poller in the first scaffold.
- Manual read calls may request recent inbound messages through Helio.

Scanning:

- Dry-run outbound text must be scanned or ask Helio to scan using `DirectiveScanner` semantics.
- A `blocked` scan result prevents write-mode submission.
- A `flagged` scan result requires human review before any later write.

Baselines:

- The adapter does not compute baselines.
- Helio may expose baseline summaries later.
- Hermes must not treat baseline data as permission to execute work.

## Test Strategy

Use mocked Helio and mocked Supabase-shaped responses. Do not connect to Supabase.

Unit tests should cover:

- `config.py` rejects missing or unknown modes.
- `config.py` rejects non-disabled modes without `HELIO_GATEWAY_URL`.
- `permissions.py` rejects unknown org/workspace.
- `permissions.py` rejects unsupported message and bot targets.
- `client.py` read-only methods format expected Helio requests.
- `client.py` refuses write methods in `read_only` and `dry_run` modes.
- `schemas.py` accepts canonical `agent_messages` rows.
- `schemas.py` accepts canonical `bot_outbound_messages` dry-run drafts.
- `audit.py` redacts message text and never records secrets.
- dry-run outbound returns blocked when mocked scanner result is `blocked`.
- later write mode only targets outbound bot messages.

Mock response fixtures:

```json
{
  "org_messaging_config": {
    "org_id": "msr",
    "config_type": "agent_roster",
    "config_data": {
      "agents": ["helio", "hermes"],
      "bot_senders": ["summit"],
      "human_agents": ["michael"],
      "system_senders": ["email-router"]
    }
  },
  "agent_messages": [
    {
      "id": "00000000-0000-0000-0000-000000000001",
      "from_agent": "helio",
      "to_agent": "hermes",
      "message_type": "query",
      "payload": {"directive": "Status check", "context": {"source": "helio"}},
      "risk_level": "read",
      "status": "pending",
      "priority": 5,
      "org_id": "msr",
      "created_at": "2026-06-03T00:00:00Z"
    }
  ]
}
```

Integration tests are not part of the first scaffold. Add them only after Helio exposes a local test gateway that does not require real Supabase credentials.

## Implementation Recommendation

Do not implement `services/agent_bus/` yet.

The safest next implementation phase is a read-only scaffold with mocked tests only, after explicit approval. That scaffold should include `config.py`, `client.py`, `schemas.py`, `audit.py`, `permissions.py`, and `README.md`, but it should still avoid Supabase imports and avoid direct `ano-messaging` service construction.

