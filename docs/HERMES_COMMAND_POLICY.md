# Hermes Command Policy

Phase: 6F
Status: proposal only; Hermes command execution is not enabled; file zone and approval models proposed

## Purpose

This document defines the command policy Hermes must follow before it can ever perform local approved execution.

Phase 6F is documentation only. Hermes cannot execute commands yet. This phase does not create a command executor, enable resident mode, start the adapter service, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or broaden Hermes authority in code.

## Policy Principles

- Hermes cannot execute commands yet.
- Hermes may only draft or recommend commands.
- Future execution requires human approval, audit log, emergency stop, and allowlist match.
- Commands must be scoped, reversible where possible, and logged.
- Commands must never reveal secrets.
- Commands must never use sudo in early resident phases.
- Commands must fail closed when policy classification is ambiguous.
- Human approval for one command does not authorize adjacent commands.

## Command Categories

### A. Read-Only Status Commands

Commands that inspect current state without changing files, services, credentials, or external systems.

Examples:

- `pwd`
- `scripts/hermes_local_status.sh`
- `scripts/adapter_service_status.sh`

### B. Repo Inspection Commands

Read-only git and repository metadata inspection.

Examples:

- `git status --short`
- `git branch --show-current`
- `git log --oneline -n <bounded number>`

### C. Test/Check Commands

Bounded local validation commands.

Examples:

- `git diff --check`
- `python3 -m unittest discover`
- `bash -n <approved script>`

### D. Documentation Generation Commands

Commands that create or update approved documentation artifacts only after approval and within approved zones.

### E. Safe File Creation In Approved Zones

Future candidate commands may create files only in approved green zones or approved draft zones.

Examples:

- `mkdir -p` only in approved zones
- `cp` only inside approved zones
- `mv` only inside `sandbox/hermes_inbox/`, `sandbox/hermes_outbox/`, or `sandbox/hermes_archive/`

### F. Service Status Commands

Read-only service status commands.

Examples:

- `scripts/adapter_service_status.sh`
- `scripts/hermes_local_status.sh`

### G. Service Start/Stop Commands For Already-Approved Services

Commands that start or stop already-approved services require explicit human approval and audit logging.

Examples:

- `scripts/adapter_service_start.sh` only with explicit human approval
- `scripts/adapter_service_stop.sh`

Hermes resident service start/stop is not approved.

### H. Git Commands

Git commands are split by risk:

- read-only git inspection may be allowed in early tiers
- `git commit` requires human approval
- `git push` requires human approval
- force push is denied
- destructive reset/clean commands are denied

### I. Forbidden Commands

Forbidden commands are blocked regardless of normal approval in early resident phases.

### J. Requires Separate Human Approval Commands

Commands that write files, start services, stop services, commit, push, or touch external systems require separate explicit human approval.

## Initial Allowlist Candidates

These are candidates only. They are not executable by Hermes until enforcement exists and human approval is granted where required.

- `pwd`
- `git status --short`
- `git branch --show-current`
- `git log --oneline -n <bounded number>`
- `git diff --check`
- `python3 -m unittest discover`
- `bash -n <approved script>`
- `scripts/hermes_local_status.sh`
- `scripts/adapter_service_status.sh`
- `scripts/adapter_service_start.sh` only with explicit human approval
- `scripts/adapter_service_stop.sh`
- `mkdir -p` only in approved zones
- `cp` only inside approved zones
- `mv` only inside `sandbox/hermes_inbox/`, `sandbox/hermes_outbox/`, or `sandbox/hermes_archive/`
- `cat`, `head`, and `tail` only on approved non-secret files
- `grep` only on approved non-secret files

## Initial Denylist

Always denied in early resident phases:

- `sudo`
- `rm -rf`
- `chmod 777`
- `chown`
- `launchctl` for Hermes resident service until approved
- `security`
- `defaults write` for security or privacy-sensitive settings
- `osascript` controlling apps
- `curl` to external network except approved localhost or DevMonster health checks
- `ssh`
- `scp`
- `rsync`
- `brew install`
- `brew uninstall`
- global `pip install`
- global `npm install`
- `git push --force`
- `git reset --hard`
- `git clean -fdx`
- any command reading `~/.ssh`, `~/.gnupg`, Keychains, `.env`, token, key, or secret files
- any command writing outside approved zones
- any command modifying `~/.hermes` unless separately approved
- any command launching Hermes Desktop
- any command starting external integrations

## Approval Classes

- no approval needed for read-only status in allowed zones after enforcement exists
- approval needed for service start
- approval needed for file writes
- approval needed for `git commit`
- approval needed for `git push`
- separate approval needed for external integrations
- prohibited regardless of approval in early phases when denylisted

## Future Command Policy Enforcement

Future enforcement must include:

- command parser
- allowlist matcher
- denylist matcher
- approval record lookup
- audit event creation
- dry-run mode
- fail-closed behavior
- file zone classification
- secret-path refusal
- timeout and output redaction

Phase 6G defines the file zone policy in `docs/HERMES_FILE_ZONE_POLICY.md`.
Phase 6H defines the approval record model in `docs/HERMES_APPROVAL_RECORD_MODEL.md`.
Phase 6K defines the classifier-only implementation plan in `docs/HERMES_POLICY_ENFORCEMENT_IMPLEMENTATION_PLAN.md`.

## Acceptance Criteria Before Command Execution

- command policy exists
- audit log implemented
- emergency stop implemented
- approval record implemented
- file zone policy implemented
- dry-run tests pass
- human approval required
- command executor refuses ambiguous commands
- command executor refuses secret paths
- command executor records audit events

## Non-Goals

Phase 6F does not approve:

- Hermes command execution
- command executor implementation
- resident Hermes
- Hermes launchd service
- adapter service start
- Hermes live prompt
- external integrations
- Desktop launch
- credential use
- `~/.hermes` modification

## Phase 6K Implementation Plan

Phase 6K adds `docs/HERMES_POLICY_ENFORCEMENT_IMPLEMENTATION_PLAN.md`.

The plan proposes future modules `services/hermes_safety/file_zones.py`, `services/hermes_safety/command_policy.py`, and `services/hermes_safety/policy_result.py`; argv-based command parsing; denylist-first classification; exact/bounded allowlist matching; approval-required outcomes; fail-closed ambiguity handling; and audit/approval integration.

Phase 6K does not implement a command executor, execute commands through Hermes, create classifier modules, start services, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or enable resident mode.

Phase 6O implements file-zone classification only in `services/hermes_safety/file_zones.py`. Command-policy classification and command execution remain disabled until later phases.

## Proposal Conclusion

Hermes may draft and recommend commands, but execution remains disabled until command policy enforcement, audit logging, emergency stop, file zone policy enforcement, and approval record lookup are implemented and approved. Phase 6K plans classifier-only policy enforcement, but command execution remains disabled.
