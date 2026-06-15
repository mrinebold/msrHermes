# Hermes Resident Service Proposal

Phase: 6D
Status: proposal only; no resident service created; dry-run loop script implemented in Phase 6T; command execution and resident mode remain disabled

## Purpose

This document proposes the future Hermes resident service design without creating, installing, loading, or starting any Hermes resident service.

Phase 6D is documentation only. It does not create `scripts/hermes_resident_loop.sh`, create a LaunchAgent, set `RunAtLoad=true`, set `KeepAlive=true`, start services, run Hermes live, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority in code.

Phase 6T added `scripts/hermes_resident_dry_run.sh` as a one-shot dry-run script. It is not a resident service, does not run in the background, does not use launchd, does not start the adapter, does not run Hermes live, and does not execute commands.

## Proposed Resident Service Purpose

Future resident Hermes may:

- watch local inbox
- create recommendations
- write outbox results
- observe status
- summarize local project state
- prepare draft plans
- fail closed on policy violations

Future resident Hermes must:

- never execute shell commands without future explicit approval
- never touch external integrations without future explicit approval
- never launch Desktop without future explicit approval
- never use credentials without future explicit approval

## Proposed Service Label

```text
com.msr.hermes.resident
```

## Proposed Execution Model

- user LaunchAgent only
- no sudo
- `RunAtLoad=false` for first validation
- `KeepAlive=false` for first validation
- manual start only at first
- emergency stop compatible
- audit logging required before any execution
- command policy enforcement required before any execution
- file zone policy enforcement required before any file access
- authority tier must be selected before any resident behavior
- adapter service remains separate from Hermes resident service

No plist is created in Phase 6D.

## Proposed Service Script

Future script:

```text
scripts/hermes_resident_loop.sh
```

Do not create this script in Phase 6D. A later phase may propose or implement a dry-run-only stub after audit logging and emergency stop implementation plans are approved.

Dry-run script now available:

```text
scripts/hermes_resident_dry_run.sh
```

This script scans only `sandbox/hermes_inbox/`, writes redacted dry-run proposal files only under `sandbox/hermes_outbox/`, writes metadata-only audit events when the local audit writer is available, respects `sandbox/hermes_control/FROZEN`, and exits after one pass.

## Resident Loop Responsibilities

Future loop responsibilities:

- check freeze flag
- check adapter health
- process only approved inbox tasks
- write only to outbox
- archive processed tasks
- log audit metadata
- stop or fail closed on policy violations
- respect authority tier
- respect task expiration
- avoid prompt/file content logging

## Resident Loop Non-Goals

- no shell execution
- no file edits outside approved zones
- no external integrations
- no Desktop
- no credentials
- no autonomous installs
- no broad filesystem scanning
- no package installation
- no direct Agent Bus writes
- no Helio dispatch

## Allowed File Zones

Future resident loop may use only approved zones:

- `sandbox/hermes_inbox/`
- `sandbox/hermes_outbox/`
- `sandbox/hermes_archive/`
- `logs/hermes_audit/`
- docs read-only context if explicitly embedded by builder

## Forbidden Zones

Forbidden without separate approval:

- `~/.ssh`
- `~/.gnupg`
- `~/.aws`
- `~/.config` with secrets
- `~/.hermes` except already-approved config read
- `~/Library/Keychains`
- private credential files
- `.env` files
- token/key/secret files
- arbitrary Desktop scanning
- arbitrary Documents scanning
- browser profiles
- cloud credential stores
- launchd paths for Hermes except in an explicitly approved service-install phase

## Proposed Resident Processing Flow

1. Read status and policy config.
2. Refuse to run if freeze flag is present.
3. Verify adapter health if inference is needed.
4. Select one approved inbox task.
5. Validate task path and authority tier.
6. Run Hermes through approved local config.
7. Write result to outbox.
8. Archive task only after successful output handling.
9. Write audit metadata.
10. Stop or sleep without background autonomy beyond approved cadence.

## Future Acceptance Criteria

Before any resident service install:

- audit log implemented
- emergency stop implemented
- command policy implemented
- file zone policy implemented
- approval record model implemented
- resident loop dry-run tested
- status command updated
- `RunAtLoad=false`
- `KeepAlive=false`
- no external integrations
- no Hermes Desktop
- no shell execution
- no broad filesystem scanning
- no real credentials
- no Agent Bus writes
- human approval before install

## Rollback Concept

Future rollback must:

- stop resident service
- unload resident LaunchAgent
- preserve inbox/outbox/archive/logs
- preserve backups
- confirm no resident process remains
- confirm no `8088` listener if adapter stop is part of rollback
- write audit event after audit logging is implemented

## Non-Goals

Phase 6D does not approve:

- resident mode
- creating `scripts/hermes_resident_loop.sh`
- creating `com.msr.hermes.resident`
- creating launchd files
- starting services
- `RunAtLoad=true`
- `KeepAlive=true`
- shell execution
- external integrations
- Desktop launch
- credentials
- Agent Bus reads or writes
- `~/.hermes` modification

## Phase 6L Emergency Stop And Dry-Run Plan

Phase 6L adds `docs/HERMES_EMERGENCY_STOP_AND_DRY_RUN_PLAN.md`.

The plan proposes future scripts `scripts/hermes_emergency_stop.sh` and `scripts/hermes_resident_dry_run.sh`, a freeze flag at `sandbox/hermes_control/FROZEN`, dry-run-only inbox scanning, outbox-only proposed action writing, adapter status checks only, and audit metadata after audit writer implementation.

Phase 6L does not create `scripts/hermes_resident_dry_run.sh`, create `scripts/hermes_emergency_stop.sh`, create freeze flags, create a resident LaunchAgent, start services, run Hermes live, execute commands, connect integrations, use credentials, launch Desktop, modify `~/.hermes`, or enable resident mode.

## Proposal Conclusion

Hermes resident service design is viable only after audit logging and emergency stop are implemented and tested. Phase 6L plans the future emergency stop and dry-run loop implementation, but resident mode and resident service scripts remain unimplemented.

## Phase 6X Resident Validation Gate

Phase 6X adds `docs/HERMES_RESIDENT_VALIDATION_GATE.md` as the final proposal before any future resident dry-run LaunchAgent validation.

The gate requires audit helper, approval helper, file-zone classifier, command-policy classifier, emergency stop, dry-run resident loop, and status visibility to work first. The proposed future resident LaunchAgent remains manual-start only with `RunAtLoad=false`, `KeepAlive=false`, dry-run loop only, no command execution, no live Hermes run unless separately approved, no external integrations, and emergency stop compatibility.

Phase 6X does not create a plist, create a Hermes launchd service, start services, run Hermes live, execute commands, or enable resident mode.

## Phase 7B Resident-Once Runtime Note

Phase 7B validates a separate governed one-shot runtime, not the full resident service proposed here.

The validated runtime is documented in `docs/HERMES_RESIDENT_ONCE_RUNTIME.md` and uses `com.msr.hermes.resident-once`, `RunAtLoad=false`, and `KeepAlive=false`. It runs once, writes redacted local proposals and audit metadata, and exits.

It does not execute commands, run Hermes live, start the adapter, launch Desktop, connect integrations, use credentials, or stay alive as a daemon. The full `com.msr.hermes.resident` service remains unimplemented and unapproved.

## Phase 7F Service Boundary

Phase 7F confirms no full resident service exists.

Installed service surfaces:

- `com.msr.hermes.model-router-adapter`: adapter service, manual-only, stopped/unloaded by default
- `com.msr.hermes.resident-once`: governed one-shot resident-shaped service, manual-only, stopped/unloaded by default

Not installed/enabled:

- unconstrained `com.msr.hermes.resident`
- daemon resident loop
- command executor
- external integration service
