# Hermes Safety Implementation Roadmap

Phase: 6I
Status: implementation roadmap only; resident mode not enabled

## Purpose

This roadmap defines the staged implementation order for Hermes safety infrastructure before resident mode, command execution, service automation, or external integrations can be enabled.

Phase 6I is planning only. It does not implement safety modules, create a command executor, start the adapter service, run Hermes live, enable resident mode, create a Hermes launchd service, connect external integrations, use credentials, modify `~/.hermes`, or broaden Hermes authority.

External integrations remain frozen.

## Stage 1: Audit Log Writer

Objective:

- implement local metadata-first audit event writing

Likely files/scripts:

- `services/hermes_safety/audit_log.py`
- `services/hermes_safety/redaction.py`
- tests under `tests/services/hermes_safety/`

Risks:

- accidental secret logging
- accidental prompt/file content logging
- malformed JSONL

Tests:

- writes valid JSONL
- redacts secret-like values
- refuses raw prompt/file content by default
- append-only behavior

Rollback:

- disable audit writer import path
- preserve audit artifacts
- revert code changes

Acceptance criteria:

- local JSONL event writes pass tests
- no secrets in test fixtures or output
- no cloud sync

What remains forbidden:

- resident mode
- command execution
- external integrations

## Stage 2: Approval Record Writer/Reader

Objective:

- implement scoped expiring approval record storage and lookup

Likely files/scripts:

- `services/hermes_safety/approval_records.py`
- tests under `tests/services/hermes_safety/`

Risks:

- approvals too broad
- expired approvals reused
- hidden approvals

Tests:

- grant/deny/expire/revoke lifecycle
- one-time-use behavior
- audit event linkage
- no secret values

Rollback:

- disable approval lookup
- preserve approval JSONL
- fail closed

Acceptance criteria:

- approval lookup fails closed
- expired/revoked approvals blocked
- no blanket permanent approval

What remains forbidden:

- model-only approval
- resident mode
- external writes

## Stage 3: File Zone Classifier

Objective:

- classify paths as green, yellow, orange, or red

Likely files/scripts:

- `services/hermes_safety/file_zones.py`
- tests under `tests/services/hermes_safety/`

Risks:

- path traversal
- symlink escape
- secret-like filename bypass

Tests:

- green/yellow/orange/red classification
- symlink refusal or safe resolution
- path traversal refusal
- secret-like filename refusal

Rollback:

- disable classifier integration
- fail closed on file access

Acceptance criteria:

- ambiguous paths fail closed
- red zones blocked
- file read/write audit metadata ready

What remains forbidden:

- broad filesystem scanning
- arbitrary Desktop/Documents scanning
- secret file reads

## Stage 4: Command Policy Classifier

Objective:

- classify proposed commands without executing them

Likely files/scripts:

- `services/hermes_safety/command_policy.py`
- `services/hermes_safety/policy_result.py`
- tests under `tests/services/hermes_safety/`

Risks:

- shell parsing gaps
- denylist bypass
- unsafe command marked safe

Tests:

- denylist first
- allowlist exact/bounded patterns
- approval-required classification
- fail closed on ambiguity

Rollback:

- disable classifier integration
- keep execution disabled

Acceptance criteria:

- classifier only, no execution
- dangerous commands denied
- safe status commands classified read-only

What remains forbidden:

- command execution
- Hermes shell authority
- external integrations

## Stage 5: Emergency Stop Script

Objective:

- implement repeat-safe emergency stop behavior

Likely files/scripts:

- `scripts/hermes_emergency_stop.sh`
- tests for syntax and dry-run behavior

Risks:

- overbroad process stop
- deletion of artifacts
- accidental service changes

Tests:

- no sudo
- no deletion
- repeat-safe
- creates freeze state only if approved
- records audit event once audit writer exists

Rollback:

- remove script from operator path
- preserve logs/artifacts/backups

Acceptance criteria:

- safe repeated runs
- no secrets printed
- no external calls

What remains forbidden:

- resident mode
- unapproved process killing
- deleting files

## Stage 6: Dry-Run Resident Loop

Objective:

- implement dry-run resident loop that proposes actions only

Likely files/scripts:

- `scripts/hermes_resident_dry_run.sh`
- tests for no execution and zone compliance

Risks:

- accidental live execution
- broad file scanning
- adapter dependency confusion

Tests:

- no command execution
- no external integrations
- scans only approved inbox
- writes only proposed actions to outbox
- respects freeze flag

Rollback:

- disable dry-run script
- preserve outbox artifacts

Acceptance criteria:

- dry-run exits cleanly
- no runtime service created
- no resident mode enabled

What remains forbidden:

- resident LaunchAgent
- RunAtLoad/KeepAlive
- shell execution

## Stage 7: Resident Loop Proposal Validation

Objective:

- validate proposed resident behavior without running as a service

Likely files/scripts:

- docs updates
- dry-run metrics artifacts

Risks:

- assuming dry-run is production ready

Tests:

- dry-run report review
- audit/approval linkage
- emergency stop compatibility

Rollback:

- revert proposal changes
- keep resident mode disabled

Acceptance criteria:

- human-reviewed dry-run evidence
- no service created

What remains forbidden:

- resident enablement

## Stage 8: Manual Resident Dry-Run

Objective:

- manually run dry-run loop once under observation

Likely files/scripts:

- approved dry-run script only
- sandbox artifacts only

Risks:

- long-running process
- unexpected file writes

Tests:

- timeout bounded
- cleanup verified
- no process remains

Rollback:

- stop dry-run process
- preserve artifacts

Acceptance criteria:

- no resident process remains
- no service created

What remains forbidden:

- launchd service
- resident operation

## Stage 9: Future Resident LaunchAgent Proposal

Objective:

- propose exact future LaunchAgent only after dry-run evidence

Likely files/scripts:

- documentation only
- no plist creation

Risks:

- RunAtLoad/KeepAlive too early

Tests:

- proposal keeps `RunAtLoad=false`
- proposal keeps `KeepAlive=false`
- emergency stop path documented

Rollback:

- not applicable until implementation phase

Acceptance criteria:

- human review
- no service created

What remains forbidden:

- LaunchAgent creation

## Stage 10: Future Resident Enablement Gate

Objective:

- define final human gate before any resident mode

Likely files/scripts:

- gate checklist
- approval record template

Risks:

- broad approval
- unclear rollback

Tests:

- approval scope validation
- status command final-state check

Rollback:

- emergency stop
- LaunchAgent unload if later created

Acceptance criteria:

- explicit human approval
- audit, approval, file-zone, command-policy, emergency stop, and dry-run evidence complete

What remains forbidden:

- uncontrolled autonomy
- external integrations without separate phase

## Roadmap Conclusion

Implementation must proceed in order: audit, approval, file-zone, command-policy, emergency stop, dry-run loop, validation, manual dry-run, LaunchAgent proposal, and final enablement gate. Resident mode remains disabled until a later explicit approval phase.

Phase 6J adds `docs/HERMES_AUDIT_APPROVAL_IMPLEMENTATION_PLAN.md`, which expands Stage 1 and Stage 2 into a concrete future implementation plan. Phase 6J remains planning-only and does not implement safety modules, create log directories, start services, run Hermes live, or enable resident mode.

Phase 6K adds `docs/HERMES_POLICY_ENFORCEMENT_IMPLEMENTATION_PLAN.md`, which expands Stage 3 and Stage 4 into a classifier-only implementation plan. Phase 6K remains planning-only and does not implement file-zone enforcement, command-policy enforcement, command execution, service control, or resident mode.

Phase 6L adds `docs/HERMES_EMERGENCY_STOP_AND_DRY_RUN_PLAN.md`, which expands Stage 5 and Stage 6 into a future implementation plan. Phase 6L remains planning-only and does not create emergency stop scripts, dry-run resident scripts, freeze flags, services, live Hermes runs, command execution, or resident mode.

Phase 6M implements Stage 1 as a local audit writer primitive in `services/hermes_safety/audit_log.py`. The implementation remains a library-only primitive and does not integrate with resident mode, command execution, emergency stop, external integrations, adapter service control, live Hermes runs, or autonomous operation.

Phase 6N implements Stage 2 as a local approval record writer/reader primitive in `services/hermes_safety/approval_records.py`. The implementation remains a library-only primitive and does not grant approval automatically, execute approved actions, integrate with resident mode, start services, run Hermes live, or connect external systems.

Phase 6O implements Stage 3 as a local file-zone classifier primitive in `services/hermes_safety/file_zones.py`. The implementation classifies paths only and does not perform file operations, enforce writes, execute commands, start services, run Hermes live, or enable resident mode.

Phase 6P implements Stage 4 as a local command-policy classifier primitive in `services/hermes_safety/command_policy.py` with shared results in `services/hermes_safety/policy_result.py`. The implementation classifies commands only and does not execute commands, start services, run Hermes live, connect integrations, or enable resident mode.

Phase 6Q integrates safety primitive state into the read-only local status command. `scripts/hermes_local_status.sh` reports module importability, audit log state, approval log state, freeze flag state, command execution disabled, and resident mode disabled without creating logs, approvals, freeze flags, services, live Hermes runs, command execution, or resident mode.
