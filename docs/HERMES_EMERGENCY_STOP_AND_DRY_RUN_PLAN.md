# Hermes Emergency Stop And Dry-Run Resident Loop Plan

Phase: 6L
Status: emergency stop script implemented in Phase 6R; dry-run resident loop implemented in Phase 6T; resident mode remains disabled

## Purpose

This plan defines how Hermes should later implement a safe emergency stop command and a dry-run resident loop after audit logs, approval records, file-zone classification, and command-policy classification are implemented.

Phase 6L is planning only. It does not create `scripts/hermes_emergency_stop.sh`, create `scripts/hermes_resident_dry_run.sh`, create freeze flags, start services, run Hermes live, enable resident mode, create a Hermes launchd service, execute commands, connect integrations, use credentials, modify `~/.hermes`, or broaden Hermes authority.

Phase 6T implemented `scripts/hermes_resident_dry_run.sh` as a one-shot dry-run script. It does not enable resident mode, create launchd service files, execute commands, run Hermes live, start the adapter, connect integrations, or archive/delete task files.

## Proposed Emergency Stop Script

Future script:

```text
scripts/hermes_emergency_stop.sh
```

The script should be implemented only in a later phase after audit and policy primitives exist.

## Proposed Dry-Run Resident Loop

Future script:

```text
scripts/hermes_resident_dry_run.sh
```

The dry-run loop is a foreground/manual script first. It must not create a launchd service, set `RunAtLoad=true`, set `KeepAlive=true`, run unattended, execute shell commands, connect external integrations, or launch Desktop.

## Emergency Stop Behavior

Future emergency stop behavior:

- no sudo
- no deletion
- no credentials printed
- no external calls
- stop adapter service if running
- detect Hermes CLI, Hermes Desktop, adapter, and resident-like processes
- stop only approved in-scope processes
- write an audit event once audit writer exists
- create or update a freeze flag
- preserve logs, outbox, archive, backups, and suspect artifacts
- be safe to run repeatedly
- fail closed on ambiguous process identity

Emergency stop must not delete task files, audit logs, approval records, backups, Desktop artifacts, or Hermes config.

## Freeze Flag Proposal

Future freeze flag:

```text
sandbox/hermes_control/FROZEN
```

Future freeze metadata may live beside it:

```text
sandbox/hermes_control/FROZEN.reason.json
```

Freeze behavior:

- dry-run and future resident loops refuse new work when frozen
- status command reports frozen state in a later phase
- emergency stop can create or refresh the flag
- freeze records reason, timestamp, actor, and stop level without secret values
- unfreeze requires a later explicit approval phase

## Dry-Run Loop Behavior

Future dry-run resident loop behavior:

- foreground/manual only
- no command execution
- no external integrations
- no Desktop launch
- no credentials
- no Agent Bus reads/writes
- no service creation
- check freeze flag before doing work
- check adapter status only
- scan only `sandbox/hermes_inbox/`
- process only approved task file shapes
- write only proposed actions to `sandbox/hermes_outbox/`
- archive only approved task files after successful dry-run output handling
- write audit metadata only after audit writer exists
- exit cleanly after one bounded pass unless a later phase approves a loop

Dry-run output should be a proposed action summary, not an executed action.

Phase 6T implementation behavior:

- runs once and exits
- refuses work when `sandbox/hermes_control/FROZEN` exists
- scans only `sandbox/hermes_inbox/*.task.md`
- writes `<task-name>.dry_run.md` files only under `sandbox/hermes_outbox/`
- redacts task contents from dry-run proposal files
- records metadata-only audit events under ignored local audit logs when the audit writer is importable
- archives nothing and deletes nothing

## Integration Prerequisites

Before implementation:

- audit writer implemented
- approval record writer/reader implemented
- file-zone classifier implemented
- command-policy classifier implemented
- redaction helper implemented
- status command plan updated for freeze/audit state
- tests cover emergency stop repeatability

## Test Strategy

Future tests should cover:

- `bash -n scripts/hermes_emergency_stop.sh`
- `bash -n scripts/hermes_resident_dry_run.sh`
- no sudo
- no deletion commands
- repeated emergency stop runs
- freeze flag creation
- frozen-state refusal by dry-run loop
- no external calls
- no Desktop launch
- no command execution
- inbox-only scanning
- outbox-only writing
- audit event shape once writer exists
- final no-process/no-listener state

## Rollback

If a later implementation is unsafe:

- stop adapter service if running
- preserve freeze flag and metadata
- preserve logs and artifacts
- disable the scripts from operator docs
- revert code changes through git
- keep resident mode disabled

## Acceptance Criteria Before Implementation

- this plan is reviewed
- audit writer implemented
- approval model implemented
- file-zone classifier implemented
- command classifier implemented
- status command can show freeze and latest audit state
- emergency stop repeatability tests are defined
- resident mode remains disabled
- no external integrations are enabled

## Plan Conclusion

Phase 6R implements the no-sudo emergency stop script at `scripts/hermes_emergency_stop.sh`. It creates the freeze flag, records reason metadata, stops only the already-approved adapter service if it is running, and writes an audit event when safe. The dry-run resident loop remains pending and must still propose actions only and exit cleanly.

Phase 6W validates the freeze behavior end to end. Emergency stop created the repo-local freeze flag and reason file, status reported both, and `scripts/hermes_resident_dry_run.sh` refused work while frozen without starting the adapter, running Hermes, executing commands, or processing inbox tasks.

Unfreeze remains manual and approval-bound. There is no unfreeze script. For Phase 6W only, the phase-created files were cleared after validation so the next resident validation gate can begin with `freeze_flag_exists=no`:

```sh
rm sandbox/hermes_control/FROZEN sandbox/hermes_control/FROZEN.reason
```
