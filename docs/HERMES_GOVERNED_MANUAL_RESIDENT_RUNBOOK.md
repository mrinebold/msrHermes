# Hermes Governed Manual Resident Runbook

Phase: 7D
Status: governed manual resident-shaped operation is available; command execution and integrations remain disabled

## What Is Implemented

- adapter LaunchAgent manual service:
  - `scripts/adapter_service_start.sh`
  - `scripts/adapter_service_stop.sh`
  - `scripts/adapter_service_status.sh`
- local status:
  - `scripts/hermes_local_status.sh`
- emergency stop:
  - `scripts/hermes_emergency_stop.sh`
- audit helper:
  - `scripts/hermes_audit_event.py`
- approval helper:
  - `scripts/hermes_approval_request.py`
- dry-run policy check:
  - `scripts/hermes_policy_check.py`
- resident-once script:
  - `scripts/hermes_resident_once.sh`
- resident-once LaunchAgent:
  - `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist`
- resident-once runtime:
  - `/Users/michaelrinebold/Library/Application Support/Helio/hermes-resident-once/current`
- resident status:
  - `scripts/hermes_resident_status.sh`
- Desktop governed validation:
  - `docs/HERMES_DESKTOP_GOVERNED_INSTALL.md`
  - Desktop remains fail-closed because strict codesign and Gatekeeper assessment fail.

## What Hermes Can Do Today

Hermes can safely operate in a governed resident-shaped local mode by manual invocation only.

Allowed today:

- observe approved local inbox task files
- classify local task file paths
- classify proposed command metadata without execution
- create dry-run/resident-once proposal outputs
- write metadata-only audit events
- respect repo and runtime freeze flags
- report local safety, Desktop, adapter, and resident-once status

## What Hermes Cannot Do Yet

Hermes may not:

- execute commands
- edit arbitrary files
- connect Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud providers
- run or launch Hermes Desktop
- use real credentials
- stay alive as a daemon
- set `RunAtLoad=true`
- set `KeepAlive=true`
- send messages or emails
- write to Agent Bus
- bypass Gatekeeper
- remove quarantine
- grant Full Disk Access
- modify `~/.hermes`

## Exact Commands

Check local status:

```sh
scripts/hermes_local_status.sh
```

Check resident-once status:

```sh
scripts/hermes_resident_status.sh
```

Run resident-once directly from the repo:

```sh
scripts/hermes_resident_once.sh
```

Run resident-once through the Application Support wrapper:

```sh
/Users/michaelrinebold/.local/bin/msr-hermes-resident-once
```

Manually load the resident-once LaunchAgent:

```sh
launchctl bootstrap "gui/$(id -u)" /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

Manually kickstart resident-once once:

```sh
launchctl kickstart "gui/$(id -u)/com.msr.hermes.resident-once"
```

Manually unload resident-once:

```sh
launchctl bootout "gui/$(id -u)" /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

Emergency stop:

```sh
scripts/hermes_emergency_stop.sh "reason"
```

Classify proposed command without executing it:

```sh
python3 scripts/hermes_policy_check.py --command "git status --short"
python3 scripts/hermes_policy_check.py --command "scripts/adapter_service_start.sh"
python3 scripts/hermes_policy_check.py --command "sudo whoami"
```

Classify proposed path operation without reading or writing the target:

```sh
python3 scripts/hermes_policy_check.py --path sandbox/hermes_outbox/example.md --operation write
python3 scripts/hermes_policy_check.py --path docs/HERMES_LOCAL_OPERATIONS_RUNBOOK.md --operation read
```

Create a harmless audit visibility event:

```sh
python3 scripts/hermes_audit_event.py --action-type dry_run --status ok --summary "Manual resident visibility check" --phase 7D
```

Create a requested-only approval visibility record:

```sh
python3 scripts/hermes_approval_request.py --action-type service_start --target resident-once --scope manual-test --summary "Resident-once manual start request" --risk-level low --expires-minutes 15
```

## Daily Manual Workflow

1. Check status:

```sh
scripts/hermes_local_status.sh
scripts/hermes_resident_status.sh
```

2. Add an approved local task file under:

```text
sandbox/hermes_inbox/
```

3. Run resident-once:

```sh
scripts/hermes_resident_once.sh
```

4. Inspect output:

```text
sandbox/hermes_outbox/
```

5. Review latest audit status:

```sh
scripts/hermes_local_status.sh
```

6. If launchd was used, unload resident-once:

```sh
launchctl bootout "gui/$(id -u)" /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

7. If anything unexpected happens, run emergency stop:

```sh
scripts/hermes_emergency_stop.sh "unexpected resident-once behavior"
```

## Recovery

Use emergency stop first:

```sh
scripts/hermes_emergency_stop.sh "recovery"
```

Then verify:

```sh
scripts/hermes_local_status.sh
scripts/hermes_resident_status.sh
```

Expected recovery state:

- adapter stopped
- resident-once unloaded/stopped
- no `8088` listener
- no Hermes process
- no Desktop process
- no resident process
- command execution enabled: no
- external integrations enabled: no

Clear freeze only when safe and explicitly approved. For the current repo/runtime freeze files, clear only the freeze files that were created by the validation or recovery action:

```sh
rm sandbox/hermes_control/FROZEN sandbox/hermes_control/FROZEN.reason \
  "$HOME/Library/Application Support/Helio/hermes-resident-once/current/sandbox/hermes_control/FROZEN" \
  "$HOME/Library/Application Support/Helio/hermes-resident-once/current/sandbox/hermes_control/FROZEN.reason"
```

Do not delete logs, audit files, approval records, outbox artifacts, backups, Desktop artifacts, or `~/.hermes`.

Desktop remains fail-closed until a signed/notarized artifact verifies cleanly.

## Definition Of Wrapped-Up For Now

The local governed resident-shaped operation is available manually.

Wrapped-up state:

- local status command exists
- resident status command exists
- emergency stop exists and freezes repo plus runtime
- resident-once script exists
- resident-once LaunchAgent exists
- resident-once Application Support runtime exists
- resident-once can run directly and through manual launchd kickstart
- resident-once respects freeze
- resident-once writes redacted outbox proposals and audit metadata
- adapter remains manual start/stop only
- command execution remains disabled
- external integrations remain frozen
- Desktop remains fail-closed due verification failure

The next phase is a separate approval decision, not more basic setup. Future work should decide whether to add a strictly bounded manual resident operating cadence, a richer task format, or a command-execution approval gate. Do not enable those from this runbook alone.

## Phase 7F Install Summary Reference

Use `docs/HERMES_INSTALL_COMPLETION_SUMMARY.md` as the canonical install completion snapshot.

Phase 7F confirms this runbook remains the current manual procedure. The installed stack is governed and manual: adapter and resident-once LaunchAgents are installed but stopped/unloaded by default, command execution is disabled, external integrations are frozen, and Desktop remains fail-closed.

## Remote And iPad Use

Remote use is approved only through private network paths.

Use:

```sh
scripts/remote_ipad_access_instructions.sh
```

Current model:

- Tailscale is the primary remote access layer
- iPad access uses a trusted SSH app over Tailscale
- remote laptop access uses standard SSH over Tailscale
- endpoint access uses SSH local port forwarding
- adapter remains bound to `127.0.0.1`
- public exposure is not approved
- Tailscale Funnel/public access is not approved
- direct `8088` exposure is not approved


## Phase 7I Browser Gateway Run

The browser gateway is a manual front door for the existing governed resident-once workflow. It does not start the adapter or LaunchAgents.

```sh
scripts/run_hermes_gateway.sh
```

Authenticate at /login, add tasks through /inbox, run resident once, inspect /outbox, and stop the gateway with Ctrl-C. Emergency stop remains available through the browser action and invokes only scripts/hermes_emergency_stop.sh with the supplied bounded reason.

No RunAtLoad, KeepAlive, Desktop launch, public exposure, Tailscale Funnel, command execution, or external integration is enabled by this gateway.
