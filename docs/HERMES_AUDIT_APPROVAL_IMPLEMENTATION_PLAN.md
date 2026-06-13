# Hermes Audit And Approval Implementation Plan

Phase: 6J
Status: audit writer primitive implemented in Phase 6M; approval record primitive implemented in Phase 6N

## Purpose

This plan defines how Hermes should later implement local audit logs and human approval records before any command execution, file writes, resident operation, external integration, or service automation is enabled.

Phase 6J is planning only. It does not create `services/hermes_safety/`, create log directories, write audit events, write approval records, run Hermes live, start the adapter service, enable resident mode, create a Hermes launchd service, connect integrations, use credentials, modify `~/.hermes`, or broaden Hermes authority.

## Proposed Modules

Future modules:

- `services/hermes_safety/audit_log.py`
- `services/hermes_safety/approval_records.py`
- `services/hermes_safety/redaction.py`

Module responsibilities:

- `audit_log.py`: build, validate, redact, and append metadata-first audit events.
- `approval_records.py`: build, validate, append, read, and resolve scoped approval records.
- `redaction.py`: centralize value redaction, secret-like marker detection, path redaction, and summary sanitization.

No module is implemented in Phase 6J.

## Proposed Storage

Future local storage:

```text
logs/hermes_audit/*.jsonl
logs/hermes_approvals/*.jsonl
```

Storage rules:

- local filesystem only
- no cloud sync
- no external writes
- no secrets
- append-only where practical
- one record per line
- owner-readable permissions where practical
- daily files by default
- rotation and retention follow `docs/HERMES_AUDIT_LOG_DESIGN.md`

## Audit Event Schema

Future audit events should include:

- `schema_version`
- `timestamp`
- `event_id`
- `phase`
- `actor`
- `authority_tier`
- `action_type`
- `target_type`
- `target_identifier`
- `approval_id`
- `status`
- `risk_level`
- `redaction_applied`
- `rollback_available`
- `human_summary`
- `machine_summary`
- `artifact_hash`

Audit events must not include secret values, raw prompt text, raw file contents, model output by default, credential payloads, or private message bodies.

## Approval Record Schema

Future approval records should include:

- `schema_version`
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

Approval records must not include secret values. Approval records must be scoped, expiring, and auditable. Blanket permanent approval and approval by model alone remain forbidden.

## Redaction Rules

The future redaction module should:

- redact API keys, OAuth tokens, provider keys, GitHub tokens, Supabase keys, Home Assistant tokens, Helio credentials, private key material, and dotenv values
- redact raw prompt text and file contents by default
- redact model output by default unless a later phase approves narrower content logging
- keep safe metadata such as event category, status, authority tier, non-sensitive target identifier, and artifact hash
- fail closed when a field cannot be confidently sanitized

## Append-Only Behavior

Future writers should:

- append one JSON object per line
- fsync where practical for high-risk actions
- never rewrite prior events as part of normal operation
- represent corrections with new events instead of modifying old ones
- preserve logs during emergency stop and rollback
- fail closed if append fails for an action requiring audit evidence

## Migration Decision

No migration is required for Phase 6J because audit and approval storage do not exist yet.

Future implementation should start with a schema version of `1` and a no-migration path. If schema changes are needed later, a migration plan must be proposed before rewriting or transforming audit/approval artifacts.

## Test Strategy

Future tests should cover:

- valid audit JSONL append
- valid approval JSONL append
- malformed event refusal
- missing required field refusal
- redaction of secret-like values
- no prompt/file content in default audit events
- approval expiration
- one-time-use approval behavior
- approval denied/revoked/expired fail-closed behavior
- audit event linkage from approval records
- local-only storage path enforcement
- no cloud sync or external writes

## Future Status Command Integration

A later phase should update `scripts/hermes_local_status.sh` to report:

- whether audit log storage exists
- latest audit event timestamp and type, without secret values
- whether approval storage exists
- latest approval state counts, without secret values
- whether a freeze/emergency state exists once emergency stop is implemented

The status command must remain read-only and must not start services.

## Acceptance Criteria Before Implementation

- this implementation plan is reviewed
- audit schema and approval schema are stable enough for first implementation
- redaction behavior is defined
- tests are written before runtime authority depends on the modules
- no cloud sync is introduced
- no secrets are stored
- resident mode remains disabled
- command execution remains disabled

## Plan Conclusion

Phase 6M implemented the first local audit writer primitive in `services/hermes_safety/audit_log.py` with temp-dir tests and no runtime authority. Phase 6N implemented the local approval record writer/reader in `services/hermes_safety/approval_records.py`, including expiration checks, one-time-use handling, no model-only granted approvals, no blanket permanent approvals, and secret redaction. Audit integration, resident mode, command execution, and external integrations remain disabled.
