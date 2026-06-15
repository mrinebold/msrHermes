# Hermes Local Operations Runbook

Phase: 5BA-6A
Status: manual local-only operations documented; local-only readiness certified; read-only local status command added; resident safety policies proposed

## Current Approved Mode

Hermes is approved for manual local-only use through the validated adapter service and local task inbox.

Approved operating shape:

- manual adapter service start and stop only
- Hermes CLI local-only inference through `http://127.0.0.1:8088/v1`
- context-bearing inbox tasks only
- outputs written under `sandbox/hermes_outbox/`
- Codex or the human operator reviews Hermes output before any action

Not approved:

- Hermes Desktop; it remains fail-closed
- external integrations
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud providers
- real credentials
- Hermes resident/autonomous mode
- `RunAtLoad=true`
- `KeepAlive=true`
- Hermes shell execution
- Hermes file edits outside `sandbox/hermes_outbox/`

## Daily Manual Workflow

Use this sequence when a local-only Hermes recommendation is explicitly approved.

0. Check current local state:

```sh
scripts/hermes_local_status.sh
```

1. Start the adapter service:

```sh
scripts/adapter_service_start.sh
```

2. Check adapter status:

```sh
scripts/adapter_service_status.sh
```

Expected status:

- LaunchAgent loaded only because it was manually started
- listener present only on `127.0.0.1:8088`
- no `0.0.0.0` listener
- no LAN or Tailscale adapter exposure

3. Build a compact context-bearing task:

```sh
python3 scripts/build_hermes_local_task.py --compact --task-type next_phase_recommendation --output sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

4. Run the task:

```sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

5. Read the outbox result:

```text
sandbox/hermes_outbox/next_phase_recommendation_compact.out.md
sandbox/hermes_outbox/next_phase_recommendation_compact.stderr
sandbox/hermes_outbox/next_phase_recommendation_compact.metrics
```

6. Stop the adapter service:

```sh
scripts/adapter_service_stop.sh
```

7. Verify cleanup:

```sh
scripts/adapter_service_status.sh
```

Expected cleanup:

- LaunchAgent loaded state is false
- no `8088` listener remains
- no adapter process remains
- no Hermes Desktop process remains
- no Hermes resident/autonomous process remains

## Safe Boundaries

Hermes may:

- summarize embedded local context
- recommend next local-only actions
- produce advisory text in `sandbox/hermes_outbox/`

Hermes may not:

- execute shell commands independently
- install software
- send messages
- access Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud providers
- use real credentials
- launch Hermes Desktop
- run as a resident/background agent
- modify `~/.hermes`
- modify files outside `sandbox/hermes_outbox/`

## Troubleshooting

### Quick Status Check

Run:

```sh
scripts/hermes_local_status.sh
```

The status command is read-only. It does not start or stop services, does not modify files, does not launch Desktop, does not connect integrations, and does not print secret values.

It reports:

- repo path and git clean/dirty state
- adapter LaunchAgent loaded state
- `127.0.0.1:8088` listener state
- local `/health` and `/v1/models` checks only when a listener is present
- Hermes CLI path and version
- Hermes, Desktop, and resident-like process presence
- whether `~/.hermes/config.yaml` points to the localhost adapter, without printing secrets
- forbidden environment variable names that are currently set, without values
- whether Hermes safety modules are importable
- audit log directory state, file count, latest audit timestamp/action/status/risk level if initialized
- approval log directory state, file count, latest approval timestamp/status/action/expiration, and valid approval count if initialized
- freeze flag path and existence at `sandbox/hermes_control/FROZEN`
- freeze reason existence and first safe redacted line when present
- emergency stop, policy check, and dry-run resident loop script presence
- `command_execution_enabled=no`
- `resident_mode_enabled=no`

If audit or approval logs are absent, the status command reports `not_initialized` rather than creating directories or files.

### Port 8088 Already In Use

Run:

```sh
scripts/adapter_service_status.sh
```

If the listener is not the approved adapter bound only to `127.0.0.1:8088`, stop and investigate. Do not run Hermes against an unknown listener.

### DevMonster Unreachable

The adapter depends on DevMonster at:

```text
http://100.93.120.124:11434
```

If model calls fail because DevMonster is unavailable, stop the adapter service and leave Hermes tasks unrun.

### Gemma Timeout

Use compact tasks first. Phase 5AZ showed the full context task can time out. Phase 5AZ-R validated the compact task with a `1100` character embedded context budget.

### Empty Or Unusable Output

Treat empty output as fail-closed. Do not rerun repeatedly. Reduce context, narrow the task, or open a new phase with explicit approval.

### Service Fails To Start

Check:

```sh
scripts/adapter_service_status.sh
```

Then inspect logs without exposing prompt text or secrets:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log
```

Do not grant broad macOS privacy permissions as a first response.

### Credential Freeze Reminder

Credentialed integrations remain frozen. Do not use Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud provider credentials during local-only Hermes operation.

## Rollback

Emergency stop can freeze future dry-run/resident processing and stop the approved adapter service if it is already running:

```sh
scripts/hermes_emergency_stop.sh
```

The emergency stop script is safe to run repeatedly. It creates `sandbox/hermes_control/FROZEN`, writes reason metadata, and records a metadata-only audit event when available. It does not delete artifacts, use sudo, start services, run Hermes live, launch Desktop, or connect integrations.

Phase 6W validated that emergency stop freezes the dry-run loop: after running `scripts/hermes_emergency_stop.sh "Phase 6W validation"`, status reported the freeze flag and reason, and `scripts/hermes_resident_dry_run.sh` refused work without processing inbox tasks.

There is no unfreeze script yet. If a later phase explicitly approves clearing a repo-local freeze, remove only the documented control files:

```sh
rm sandbox/hermes_control/FROZEN sandbox/hermes_control/FROZEN.reason
```

Do not remove unrelated artifacts, logs, approvals, backups, inbox tasks, outbox results, or Hermes configuration.

Stop the adapter service first:

```sh
scripts/adapter_service_stop.sh
```

If needed, unload the LaunchAgent manually:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

If removal is explicitly approved later, preserve backups and disable rather than delete first:

```sh
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
mv "$HOME/.local/bin/msr-hermes-model-router-adapter" "$HOME/.local/bin/msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)"
```

Persistent Hermes config backup remains:

```text
/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak
```

Do not restore or modify `~/.hermes` without a separate approved phase.

## What Is Ready

- persistent Hermes config points to the localhost adapter
- adapter LaunchAgent can be manually started and stopped
- adapter binds only to `127.0.0.1:8088`
- compact context-bearing inbox task completed successfully
- local outbox artifacts capture stdout, stderr, and metrics
- service cleanup after local tasks is validated
- final local-only readiness is certified in `docs/HERMES_LOCAL_ONLY_READY_REPORT.md`
- read-only local status command exists at `scripts/hermes_local_status.sh`
- status command reports safety module, audit log, approval log, freeze flag/reason, policy script, dry-run loop, command execution, and resident mode state without writes
- dry-run policy checks can classify proposed commands and file operations with `scripts/hermes_policy_check.py`
- dry-run resident loop can inspect inbox task names and write redacted proposal files with `scripts/hermes_resident_dry_run.sh`

## What Is Not Ready

- Hermes resident/autonomous mode
- automatic adapter start at login
- persistent keepalive service operation
- Hermes Desktop
- external integrations
- Agent Bus reads or writes
- credentialed workflows
- Hermes shell execution
- broad filesystem authority

## Dry-Run Policy Checks

Classify proposed commands without running them:

```sh
python3 scripts/hermes_policy_check.py --command "git status --short"
python3 scripts/hermes_policy_check.py --command "scripts/adapter_service_start.sh"
python3 scripts/hermes_policy_check.py --command "sudo whoami"
```

Classify proposed file operations without reading or writing target files:

```sh
python3 scripts/hermes_policy_check.py --path sandbox/hermes_outbox/example.md --operation write
python3 scripts/hermes_policy_check.py --path docs/HERMES_LOCAL_OPERATIONS_RUNBOOK.md --operation read
```

Exit code `0` means allowed read-only or green/yellow path classification, `2` means approval required, and `3` means denied or unknown. This command does not authorize execution; it is dry-run classification only.

## Audit And Approval Visibility Helpers

Create a harmless audit visibility event:

```sh
python3 scripts/hermes_audit_event.py --action-type dry_run --status ok --summary "Test audit visibility" --phase 6V
```

Create a requested-only approval visibility record:

```sh
python3 scripts/hermes_approval_request.py --action-type service_start --target adapter --scope manual-test --summary "Test approval visibility" --risk-level low --expires-minutes 15
```

These helpers are for local visibility testing only. The audit helper refuses executed-command, external-write, and resident-start events. The approval helper creates `requested` records only and cannot grant approval or execute any action.

## Dry-Run Resident Loop

The dry-run loop is a one-shot local check, not resident mode:

```sh
scripts/hermes_resident_dry_run.sh
```

It scans only `sandbox/hermes_inbox/*.task.md`, writes redacted `<task-name>.dry_run.md` proposal files to `sandbox/hermes_outbox/`, records metadata-only audit events when available, and exits. It does not start the adapter, run Hermes live, execute commands, archive tasks, delete files, launch Desktop, or connect integrations. If `sandbox/hermes_control/FROZEN` exists, it refuses work and exits safely.

## Next Recommended Phase

Proceed with a later audit/status refinement phase only if explicitly approved. Daily operation remains manual adapter start/stop plus local task runner use only.

## Phase 7A Governed Resident-Once Operation

Phase 7A added a governed resident-once shell for observe/recommend/dry-run work:

```sh
scripts/hermes_resident_once.sh
scripts/hermes_resident_status.sh
```

The script runs once and exits. It checks the emergency freeze flag, scans only `sandbox/hermes_inbox/*.task.md`, classifies task paths and proposed `command:` metadata, writes redacted proposals only to `sandbox/hermes_outbox/`, and records metadata-only audit events under `logs/hermes_audit/`.

It does not execute commands, start the adapter, run Hermes live, launch Desktop, archive or delete tasks, connect external integrations, use credentials, or modify `~/.hermes`.

For launchd validation, Phase 7A installed a user LaunchAgent at:

```text
/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

The first attempt through a wrapper that still executed from the `Documents` repo failed closed with exit code `126` due macOS privacy restrictions. The remediation was to sync a minimal no-secret runtime to:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-resident-once/current
```

The wrapper at `/Users/michaelrinebold/.local/bin/msr-hermes-resident-once` now runs from that Application Support runtime. Manual launchctl validation succeeded with exit code `0`, wrote a redacted proposal and audit event in the runtime sandbox, and was booted out afterward. The LaunchAgent remains installed but unloaded/stopped. `RunAtLoad=false` and `KeepAlive=false` remain.

Check status with:

```sh
scripts/hermes_resident_status.sh
scripts/hermes_local_status.sh
```

Desktop remains governed separately and fail-closed. Phase 7A verified the official DMG and installed setup bundle but did not install, replace, or launch Desktop because strict codesign and Gatekeeper assessment still fail.

Phase 7B validates that the Application Support runtime is self-contained enough for manual launchd execution. Use `docs/HERMES_RESIDENT_ONCE_RUNTIME.md` as the source for wrapper, plist, working directory, log paths, regeneration, and runtime validation details.

Phase 7C validates that `scripts/hermes_emergency_stop.sh "Phase 7C resident-once emergency stop validation"` freezes both repo and resident-once runtime control paths. Direct resident-once execution and manual LaunchAgent kickstart both refuse work while frozen. Only the Phase 7C-created freeze files were cleared afterward; logs and audit artifacts were preserved.

Phase 7D creates the final governed manual resident runbook at `docs/HERMES_GOVERNED_MANUAL_RESIDENT_RUNBOOK.md`. Use that document for day-to-day governed resident-shaped operation. This older local operations runbook remains useful for adapter and local-only background context.

After Phase 6T, `scripts/hermes_emergency_stop.sh` exists for no-sudo local freeze/stop behavior, `scripts/hermes_policy_check.py` exists for dry-run command/path classification, and `scripts/hermes_resident_dry_run.sh` exists for one-shot dry-run inbox proposal generation. The resident service and command execution remain unimplemented. Daily manual local-only use remains unchanged.
