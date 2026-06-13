# Hermes Audit Log Design

Phase: 6B
Status: proposal only; audit logging not implemented yet; emergency stop design proposed in Phase 6C

## Purpose

This document designs the audit log model Hermes must use before any resident, local execution, external connector, or delegated operator capability is enabled.

Phase 6B is documentation only. It does not create audit directories, start services, run Hermes, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

## Audit Principles

- every Hermes action must be traceable
- no secrets in logs
- prompt/file contents redacted by default
- metadata-first logging
- human approval recorded when required
- fail-closed events logged
- rollback actions logged
- local-first storage
- no cloud sync by default
- no external writes

Audit logs are evidence, not authority. A logged event does not mean the action was approved unless the event references a valid approval.

## Event Categories

Required categories:

- `observe`
- `recommend`
- `draft`
- `approval_requested`
- `approval_granted`
- `approval_denied`
- `local_command_planned`
- `local_command_executed`
- `local_file_read`
- `local_file_write`
- `external_read`
- `external_draft`
- `external_write`
- `service_start`
- `service_stop`
- `emergency_stop`
- `policy_violation`
- `fail_closed`

## Required Event Fields

Each audit event should be one JSON object with these fields:

```json
{
  "timestamp": "2026-06-12T00:00:00Z",
  "event_id": "audit_YYYYMMDDTHHMMSSZ_shortid",
  "phase": "6B",
  "actor": "hermes|codex|human|adapter|system",
  "authority_tier": "tier_0_observe",
  "action_type": "observe",
  "target_type": "file|command|service|connector|approval|policy",
  "target_identifier": "redacted-or-stable-id",
  "approval_id": null,
  "status": "planned|approved|denied|succeeded|failed|blocked",
  "risk_level": "low|medium|high|critical",
  "redaction_applied": true,
  "rollback_available": false,
  "human_summary": "short human-readable summary",
  "machine_summary": "structured short summary",
  "artifact_hash": "sha256-or-null"
}
```

Rules:

- no secret values
- no raw prompt text by default
- no raw file contents by default
- no model output text by default
- no private message bodies by default
- hashes may be recorded for relevant artifacts when useful
- approval IDs are required for Tier 3 and above when an approval gate applies

## Storage Model

Proposed local storage:

```text
logs/hermes_audit/
logs/hermes_audit/events-YYYY-MM-DD.jsonl
logs/hermes_audit/rollups/
```

Storage requirements:

- append-only JSONL proposal
- local filesystem only
- no cloud sync by default
- no external writes
- owner-readable permissions where practical
- one event per line
- stable schema version field may be added before implementation

Rotation policy proposal:

- daily event file
- rotate at 10 MB if a day becomes large
- retain at least 90 days locally before archival review
- archive only after human approval
- never delete audit logs automatically during emergency stop

## Redaction Rules

Redact by default:

- API keys
- OAuth tokens
- Supabase keys
- GitHub tokens
- Home Assistant tokens
- Helio credentials
- private key material
- `.env` values
- prompt text
- file contents
- model output

Allowed by default:

- event category
- timestamp
- authority tier
- command name without secret arguments
- approved target path when not sensitive
- stable artifact hash
- status
- risk level
- short summaries without sensitive content

## Audit Views

Required future views:

- human-readable summary
- raw JSONL
- daily rollup
- phase rollup

Human-readable summaries should be generated from redacted metadata, not raw prompt/file content.

## Approval Logging

Approval flows must log:

- `approval_requested`
- `approval_granted` or `approval_denied`
- authority tier requested
- target
- expiration if any
- human summary
- linked action event ID

Approvals must not include secret values.

## Fail-Closed And Rollback Logging

Hermes must log:

- `fail_closed` when a policy blocks an action
- `policy_violation` when requested behavior crosses authority boundaries
- rollback availability
- rollback action result when rollback is executed
- emergency stop status if emergency stop is triggered

## Acceptance Criteria Before Resident Mode

Before resident Hermes can be enabled:

- audit directory exists
- schema documented
- redaction rules documented
- emergency_stop events are logged
- approval events are logged
- fail_closed events are logged
- rollback events are logged where applicable
- local status command can report latest audit event in a later phase
- no secret values appear in audit logs
- logs remain local by default

## Non-Goals

Phase 6B does not approve:

- implementing audit writes
- creating `logs/hermes_audit/`
- resident Hermes
- Hermes launchd service
- adapter service start
- Hermes live prompts
- external integrations
- Agent Bus reads or writes
- Desktop launch
- credential use
- `~/.hermes` modification

## Phase 6J Implementation Plan

Phase 6J adds `docs/HERMES_AUDIT_APPROVAL_IMPLEMENTATION_PLAN.md`.

The implementation plan proposes future modules `services/hermes_safety/audit_log.py`, `services/hermes_safety/approval_records.py`, and `services/hermes_safety/redaction.py`; local JSONL storage under `logs/hermes_audit/` and `logs/hermes_approvals/`; schemas; redaction rules; append-only behavior; tests; and future status-command integration.

Phase 6J does not implement audit writes, create `services/hermes_safety/`, create log directories, run Hermes live, start the adapter service, enable resident mode, create a Hermes launchd service, connect integrations, use credentials, modify `~/.hermes`, or broaden authority.

## Proposal Conclusion

Hermes needs local, metadata-first, append-only audit logs before resident or execution authority is enabled. Phase 6C defines the emergency stop model that must emit `emergency_stop` events after audit logging is implemented. Phase 6D proposes a future resident service that requires audit logging before execution. Phase 6F defines the command policy that must create audit events before any future approved command execution. Phase 6G defines file zone policy; future file reads and writes must emit audit events. Phase 6H defines approval records that must link to audit events. Phase 6J plans the first audit and approval implementation, but audit writes remain unimplemented.
