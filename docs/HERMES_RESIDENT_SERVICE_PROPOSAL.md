# Hermes Resident Service Proposal

Phase: 6D
Status: proposal only; no resident service created; command and file zone policies proposed

## Purpose

This document proposes the future Hermes resident service design without creating, installing, loading, or starting any Hermes resident service.

Phase 6D is documentation only. It does not create `scripts/hermes_resident_loop.sh`, create a LaunchAgent, set `RunAtLoad=true`, set `KeepAlive=true`, start services, run Hermes live, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority in code.

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

## Proposal Conclusion

Hermes resident service design is viable only after audit logging and emergency stop are implemented and tested. The next safe phase is Hermes-to-Helio delegation interface design.
