# Hermes Emergency Stop Design

Phase: 6C
Status: proposal only; emergency stop not implemented yet; resident mode not enabled yet; resident service proposal added in Phase 6D

## Purpose

This document designs the emergency stop model required before resident Hermes can be enabled.

Phase 6C is documentation only. It does not create an emergency stop script, start or stop services, enable resident mode, create a Hermes launchd service, modify launchd settings, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

## Emergency Stop Goals

- stop resident Hermes if enabled later
- stop adapter service
- prevent new task execution
- leave logs intact
- preserve artifacts
- avoid deleting backups
- require no sudo
- be safe to run repeatedly
- leave repo recoverable
- produce audit evidence once audit logging is implemented

## Emergency Stop Triggers

Emergency stop should be triggered by:

- human command
- policy violation
- non-localhost listener
- credential exposure suspicion
- external integration attempt outside approval
- runaway process
- repeated failures
- Desktop unexpectedly running
- resident-like process unexpectedly running
- audit log write failure after audit logging is required
- command denylist hit

## Stop Levels

### Level 0: Status Only

Inspect state without changing it.

Expected checks:

- repo state
- adapter LaunchAgent loaded state
- `8088` listener state
- Hermes process state
- Desktop process state
- resident-like process state
- freeze flag state when implemented

### Level 1: Stop Adapter Service

Stop the adapter service through approved user-level controls.

Requirements:

- no sudo
- no deletion
- no credential printing
- confirm no `8088` listener remains
- log emergency_stop event after audit logging exists

### Level 2: Stop Hermes Task Runner Or Resident Process

If a Hermes resident/task process is later enabled, stop only the approved process targets.

Requirements:

- no broad process killing
- no Desktop launch
- no file deletion
- repeated-safe behavior
- final process confirmation

### Level 3: Disable Resident LaunchAgent

If a Hermes resident LaunchAgent is later created, disable it without deleting artifacts.

Requirements:

- preserve plist and logs unless a later phase approves removal
- no `RunAtLoad=true` or `KeepAlive=true` changes during emergency stop
- record final disabled state

### Level 4: Freeze Inbox Processing

Prevent new task execution by creating or honoring a future freeze flag.

Proposed future flag:

```text
sandbox/hermes_inbox/.frozen
```

The flag should stop resident processing but must not delete inbox, outbox, archive, logs, or backups.

### Level 5: Quarantine Suspect Artifacts

Quarantine suspect output/log artifacts without deleting them.

Requirements:

- move only within approved quarantine/archive locations
- preserve timestamps where practical
- write an audit event when audit logging exists
- never delete backups

## Future Command Proposal

Future script:

```text
scripts/hermes_emergency_stop.sh
```

Do not create this script in Phase 6C. A later phase may implement it after the exact behavior, audit logging, and tests are approved.

Future script requirements:

- no sudo
- no deletion
- no credentials printed
- no external calls
- safe to run repeatedly
- leave repo recoverable
- stop adapter service if requested by stop level
- stop resident Hermes only if resident Hermes exists and is approved
- never launch Hermes Desktop
- never connect external integrations

## Required Behavior

Emergency stop must:

- avoid sudo
- avoid deletion
- avoid printing credential values
- avoid external calls
- be idempotent
- preserve logs
- preserve artifacts
- preserve backups
- leave repo recoverable
- fail closed on ambiguous process identity

## Audit Interaction

After audit logging is implemented, emergency stop must log:

- trigger
- stop level
- actor
- affected process or service
- pre-check state
- actions attempted
- final state
- failures
- rollback or recovery notes

The event category must be `emergency_stop`.

## Acceptance Criteria Before Resident Mode

Before resident Hermes can be enabled:

- emergency stop script implemented and tested in a future phase
- status command detects stopped/frozen state
- audit log records `emergency_stop`
- resident service can be disabled without deleting artifacts
- adapter service stop works without sudo
- resident process stop works without broad process killing
- inbox freeze behavior is implemented
- repeated runs are safe
- no credentials are printed
- no external calls are made

## Non-Goals

Phase 6C does not approve:

- implementing `scripts/hermes_emergency_stop.sh`
- creating freeze flags
- stopping services
- starting services
- resident Hermes
- Hermes launchd service
- RunAtLoad or KeepAlive changes
- Desktop launch
- external integrations
- Agent Bus reads or writes
- credential use
- deleting files
- modifying `~/.hermes`

## Proposal Conclusion

Emergency stop must be implemented and tested before resident Hermes is enabled. Phase 6D proposes the resident service design that will depend on this emergency stop model. Phase 6F defines command policy gates that emergency stop must be able to interrupt or freeze in future implementation.
