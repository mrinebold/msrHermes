# Hermes Resident Validation Gate

Phase: 6X
Status: proposal only; resident mode is not enabled

## Purpose

This document defines the first manual validation gate before any Hermes resident LaunchAgent or service install is considered.

Phase 6X does not create a Hermes launchd service, enable resident mode, set `RunAtLoad=true`, set `KeepAlive=true`, start the adapter, run Hermes live, execute commands, connect external integrations, use credentials, modify `~/.hermes`, launch Hermes Desktop, or broaden Hermes authority.

## Preconditions

Before a future resident validation phase can run:

- audit helper works
- approval helper works
- file-zone classifier works
- command-policy classifier works
- emergency stop works
- dry-run resident loop works
- status command reports safety state
- freeze flag is absent or intentionally cleared before validation
- adapter service is stopped
- no `8088` listener is present
- no Hermes task process is running
- no Hermes Desktop process is running
- no resident-like Hermes process is running
- external integrations remain frozen
- Hermes Desktop remains fail-closed

## Proposed Next Validation

Future validation should run the dry-run resident loop once:

```sh
scripts/hermes_local_status.sh
scripts/hermes_resident_dry_run.sh
scripts/hermes_local_status.sh
```

Expected behavior:

- dry-run loop runs once and exits
- proposal outputs are written under `sandbox/hermes_outbox/`
- no Hermes live run occurs
- no adapter service start occurs
- no command execution occurs
- metadata-only audit event is written
- status is checked before and after
- final state has no adapter listener and no Hermes/Desktop/resident process

## Future Resident LaunchAgent Proposal

This is a proposal only. Do not create this plist in Phase 6X.

Proposed future label:

```text
com.msr.hermes.resident
```

First validation behavior:

- user LaunchAgent only
- `RunAtLoad=false`
- `KeepAlive=false`
- manual start only
- calls dry-run loop only at first
- no command execution
- no live Hermes inference unless separately approved
- no external integrations
- emergency stop compatible
- human approval required before creating any plist

## Explicit Non-Goals

- no resident enablement in this phase
- no Hermes launchd service
- no `RunAtLoad=true`
- no `KeepAlive=true`
- no command execution
- no command executor
- no external integrations
- no Agent Bus reads or writes
- no Google, Supabase, GitHub, Home Assistant, Helio, or cloud provider use
- no Desktop launch
- no credential use
- no `~/.hermes` modification

## Acceptance Criteria For Future Phase 6Y

Future Phase 6Y may proceed only after explicit human approval and must:

- create a resident dry-run LaunchAgent proposal or plist only if human approves
- keep `RunAtLoad=false`
- keep `KeepAlive=false`
- verify it runs once and exits
- verify emergency stop blocks it
- verify no command execution
- verify no adapter start unless separately approved
- verify no Hermes live run unless separately approved
- verify no external integrations
- verify no Desktop launch
- verify final no-listener and no-process state
- update PRD and changelog before commit

## Gate Conclusion

The system is ready to propose a future manual resident dry-run validation only. It is not ready for resident operation, command execution, external integrations, or Desktop launch.

## Phase 7A Gate Outcome

Phase 7A completed the first manual governed resident-once validation.

Result:

- direct `scripts/hermes_resident_once.sh` run succeeded
- Application Support runtime wrapper `/Users/michaelrinebold/.local/bin/msr-hermes-resident-once` succeeded
- user LaunchAgent `com.msr.hermes.resident-once` manually kickstarted and exited with code `0`
- LaunchAgent was booted out afterward
- `RunAtLoad=false` remains
- `KeepAlive=false` remains
- no adapter start occurred
- no Hermes live run occurred
- no command execution occurred
- no external integration occurred
- no Desktop launch occurred

The first launchd attempt from the `Documents` repo path failed closed with exit code `126`; the fix was a minimal no-secret runtime under `/Users/michaelrinebold/Library/Application Support/Helio/hermes-resident-once/current`.

The next resident gate should decide whether to promote this one-shot dry-run runtime into a repeatable manual operating procedure. It must still keep command execution and external integrations disabled unless separately approved.
