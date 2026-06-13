# Hermes File Zone Policy

Phase: 6G
Status: proposal only; file zone enforcement is not implemented yet; approval model proposed in Phase 6H

## Purpose

This document defines where Hermes may read and write before resident operation or approved execution can be enabled.

Phase 6G is documentation only. It does not implement path enforcement, scan files, start services, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or broaden Hermes authority in code.

## Zone Classes

### Green Read/Write Zones

Hermes may eventually read and write these zones after the relevant runner or resident mode is approved:

- `sandbox/hermes_inbox/`
- `sandbox/hermes_outbox/`
- `sandbox/hermes_archive/`
- `logs/hermes_audit/` once implemented
- `sandbox/output/` for approved validation artifacts

### Yellow Read-Only Zones

Hermes may eventually read bounded approved context from:

- `docs/`
- `scripts/` for inspection only
- `tests/` for inspection only
- selected PRD/changelog files
- repo status metadata

### Orange Approval-Required Zones

These zones require explicit human approval before writes:

- `scripts/` writes
- `tests/` writes
- `docs/` writes
- config examples
- LaunchAgent plist updates
- Application Support runtime wrapper updates
- git commits
- git pushes

### Red Forbidden Zones

Forbidden without separate approval:

- `~/.ssh`
- `~/.gnupg`
- `~/.aws`
- `~/.config` containing credentials
- `~/.hermes` except approved config read
- `~/Library/Keychains`
- `.env` files
- token/key/secret files
- browser profiles/cookies
- arbitrary Desktop scanning
- arbitrary Documents scanning
- Downloads unless explicitly approved artifact path
- private photos/media
- system directories
- other user accounts

## Secret Detection Rules

Treat a file or path as secret-like when it includes:

- filenames containing `env`, `secret`, `token`, `key`, `credential`, or `private`
- common key patterns
- dotenv-like content
- private key headers
- OAuth tokens
- Supabase service role markers
- GitHub tokens
- OpenAI or Anthropic keys

Secret-like paths default to red forbidden unless a later phase creates a narrow read-only exception with redaction.

## Future Enforcement

Future enforcement must include:

- path normalizer
- symlink refusal or resolution
- path traversal refusal
- zone classifier
- write gate
- read gate
- audit event on every file read/write
- fail closed on ambiguity
- refusal of secret-like filenames by default
- bounded context extraction

## Read Rules

- Green zones may be read after the relevant task runner or resident loop is approved.
- Yellow zones may be read only as bounded approved context.
- Orange zones require explicit approval before read or write when sensitive.
- Red zones are forbidden.
- Ambiguous paths fail closed.

## Write Rules

- Green zones are the default write target for local task outputs and audit logs.
- Yellow zones are read-only by default.
- Orange zones require explicit human approval and audit events before writes.
- Red zones are never written by Hermes in early resident phases.
- Writes must be scoped, reversible where practical, and logged.

## Acceptance Criteria Before Resident Mode

- file zone policy exists
- command policy references it
- task runner respects inbox/outbox/archive
- status command remains read-only
- audit log schema includes file read/write events
- tests cover path traversal and forbidden zones in a future implementation phase
- symlink behavior is implemented or explicitly refused
- writes outside green zones require approval records

Phase 6H defines the approval record model in `docs/HERMES_APPROVAL_RECORD_MODEL.md`.

Phase 6K defines the classifier-only implementation plan in `docs/HERMES_POLICY_ENFORCEMENT_IMPLEMENTATION_PLAN.md`.

## Non-Goals

Phase 6G does not approve:

- filesystem enforcement implementation
- broad filesystem scanning
- arbitrary Desktop or Documents scanning
- reading secret files
- writing outside approved zones
- modifying `~/.hermes`
- resident Hermes
- command execution
- external integrations
- Desktop launch

## Phase 6K Implementation Plan

Phase 6K adds `docs/HERMES_POLICY_ENFORCEMENT_IMPLEMENTATION_PLAN.md`.

The plan proposes future modules `services/hermes_safety/file_zones.py`, `services/hermes_safety/command_policy.py`, and `services/hermes_safety/policy_result.py`; path normalization; symlink handling; path traversal refusal; green/yellow/orange/red classification; secret-like file refusal; fail-closed ambiguity behavior; and audit/approval integration.

Phase 6K does not implement path enforcement, create classifier modules, scan files, start services, run Hermes live, execute commands, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or enable resident mode.

## Proposal Conclusion

Hermes needs explicit file zone classification before resident operation or command execution. Phase 6H defines the human approval record model required for writes outside default green zones. Phase 6K plans the first classifier-only implementation, but file-zone enforcement remains unimplemented.
