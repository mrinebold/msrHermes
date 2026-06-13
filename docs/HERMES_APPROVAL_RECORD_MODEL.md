# Hermes Approval Record Model

Phase: 6H
Status: proposal only; approval records are not implemented yet

## Purpose

This document defines the approval record Hermes must require before any future execution, write, send, commit, service start, or external action.

Phase 6H is documentation only. It does not implement approval storage, enable command execution, enable resident mode, start services, run Hermes live, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

Approval records exist to ensure:

- no action beyond current authority without explicit approval
- approvals are scoped
- approvals expire
- approvals are auditable
- approvals do not grant broad permanent power

## Approval Record Fields

Required future fields:

- `approval_id`
- `timestamp_requested`
- `timestamp_granted`
- `requested_by`
- `approved_by`
- `authority_tier`
- `action_type`
- `target`
- `scope`
- `exact_command_or_operation`
- `allowed_paths`
- `forbidden_paths`
- `expiration`
- `one_time_use`
- `risk_level`
- `rollback_plan`
- `audit_event_id`
- `status`
- `human_summary`
- no secret values

Allowed status values:

- `requested`
- `granted`
- `denied`
- `expired`
- `used`
- `revoked`

## Approval Types

Required approval types:

- `local_read`
- `local_write`
- `service_start`
- `service_stop`
- `command_execute`
- `git_commit`
- `git_push`
- `external_read`
- `external_draft`
- `external_write`
- `resident_start`
- `resident_stop`
- `emergency_stop`

## Approval Storage Proposal

Proposed local storage:

```text
logs/hermes_approvals/
logs/hermes_approvals/approvals-YYYY-MM-DD.jsonl
```

Storage rules:

- local JSONL
- no cloud sync by default
- no secrets
- append-only where practical
- linked to audit events
- owner-readable permissions where practical
- one approval record per line

## Approval Lifecycle

1. Requested.
2. Reviewed.
3. Granted or denied.
4. Executed or expired.
5. Logged.
6. Revocable.

Lifecycle rules:

- granted approvals must have expiration
- high-risk approvals should be one-time use
- used approvals cannot be silently reused
- revoked approvals fail closed
- expired approvals fail closed
- denied approvals fail closed

## Non-Goals

This model does not approve:

- blanket permanent approval
- approval by model alone
- hidden approvals
- external approval store
- credentials inside approval record
- command execution
- resident mode
- service start
- external writes
- Agent Bus writes

## Integration With Audit Logs

Every approval request and decision must link to audit events.

Audit event requirements:

- approval requested
- approval granted
- approval denied
- approval expired
- approval used
- approval revoked
- command or action attempted with approval ID

## Integration With Command Policy

Future command execution must:

- classify the command
- check denylist
- match allowlist
- look up approval record when required
- verify approval scope
- verify expiration
- verify one-time-use status
- create an audit event
- fail closed when approval is missing or ambiguous

## Integration With Emergency Stop

Future emergency stop must be able to:

- freeze pending approvals
- revoke resident-related approvals
- mark approval state in audit logs
- prevent new approvals from being used while frozen

## Acceptance Criteria Before Execution

- approval model documented
- audit model references approvals
- command policy references approvals
- emergency stop can revoke or freeze approvals in future phase
- status command can summarize approval state in future phase
- approval storage implemented
- approval lookup tested
- expiration handling tested
- no secret values stored

## Phase 6J Implementation Plan

Phase 6J adds `docs/HERMES_AUDIT_APPROVAL_IMPLEMENTATION_PLAN.md`.

The implementation plan proposes future modules `services/hermes_safety/audit_log.py`, `services/hermes_safety/approval_records.py`, and `services/hermes_safety/redaction.py`; local JSONL storage under `logs/hermes_audit/` and `logs/hermes_approvals/`; approval and audit schemas; redaction rules; append-only behavior; tests; and future status-command integration.

Phase 6J does not implement approval storage, create `services/hermes_safety/`, create approval log directories, enable command execution, start services, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, or enable resident mode.

## Proposal Conclusion

Hermes must not execute, write, send, commit, start services, or take external action without scoped, expiring, auditable human approval where required. Phase 6J plans the first approval record implementation, but approval records are not implemented yet.
