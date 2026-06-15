# Hermes Install Completion Summary

Phase: 7F
Status: final install documentation sync complete; governed local manual resident-shaped stack installed; remote repository verified current after push

## Snapshot

Date/time:

```text
2026-06-15 10:40:47 CDT
```

Repository path:

```text
/Users/michaelrinebold/Documents/Helio/helio-command-center
```

Remote URL:

```text
https://github.com/mrinebold/msrHermes.git
```

Pre-sync local commit:

```text
7ce9612666d031916689a96c1d49c3fc1f6071b9
```

Phase 7F documentation commit verified after initial push:

```text
0a10b7dd084331f6b074cc2bbaa8df1e25bb372a
```

Branch:

```text
main
```

## Installed Components

- Hermes CLI at `/Users/michaelrinebold/.local/bin/hermes`
- persistent local Hermes config pointing to `http://127.0.0.1:8088/v1`
- localhost MSR Model Router Adapter runner
- adapter user LaunchAgent, installed but stopped/unloaded
- adapter Application Support runtime
- governed resident-once script
- governed resident-once user LaunchAgent, installed but stopped/unloaded
- governed resident-once Application Support runtime
- audit log primitive and local audit logs
- approval record primitive and local approval logs
- file-zone classifier
- command-policy classifier
- dry-run policy check command
- emergency stop command
- local status command
- resident status command
- local inbox/outbox/archive scaffold
- governed manual resident runbook

## Runtime Paths

Repo:

```text
/Users/michaelrinebold/Documents/Helio/helio-command-center
```

Adapter LaunchAgent:

```text
/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
```

Resident-once LaunchAgent:

```text
/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

Adapter wrapper:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

Resident-once wrapper:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-resident-once
```

Adapter runtime:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current
```

Resident-once runtime:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-resident-once/current
```

Local task zones:

```text
sandbox/hermes_inbox
sandbox/hermes_outbox
sandbox/hermes_archive
```

Audit and approval logs:

```text
logs/hermes_audit
logs/hermes_approvals
```

## LaunchAgent Labels And Service States

Adapter label:

```text
com.msr.hermes.model-router-adapter
```

Adapter state:

```text
installed; manual only; stopped/unloaded; no 8088 listener
```

Resident-once label:

```text
com.msr.hermes.resident-once
```

Resident-once state:

```text
installed; manual one-shot only; stopped/unloaded
```

Launch policy:

```text
RunAtLoad=false
KeepAlive=false
```

## Desktop State

Desktop app path:

```text
/Applications/Hermes.app
```

Desktop status:

```text
present as setup/bootstrap bundle; not trusted; not running; fail-closed
```

Verification result:

```text
strict codesign failed
spctl assessment failed
```

Desktop boundaries:

- no Gatekeeper bypass
- no quarantine removal
- no signature override
- no Desktop launch
- no sign-in
- no permissions granted
- no external integrations
- no credentials

Desktop remains optional and fail-closed until a signed/notarized artifact verifies cleanly.

## Enabled Capabilities

Hermes is installed as a governed local manual resident-shaped agent stack.

Enabled today:

- inspect local status
- observe approved local inbox task files
- classify local task paths
- classify proposed command metadata without execution
- write dry-run/resident-once proposal outputs
- write metadata-only audit events
- create requested-only approval records for visibility
- respect emergency stop and freeze flags
- report adapter, resident-once, Desktop, audit, approval, and freeze state
- manually start and stop the adapter only when explicitly needed

## Disabled Capabilities

Disabled today:

- command execution
- real resident daemon mode
- autonomous shell operation
- `RunAtLoad=true`
- `KeepAlive=true`
- Google integration
- Supabase/Agent Bus reads or writes
- Home Assistant integration
- GitHub token use
- Helio integration
- cloud provider fallback
- real credentials
- Hermes Desktop launch
- Desktop sign-in or permissions
- broad filesystem authority
- message/email sending

No `docs/HERMES_AGENT_OS.md` file is present. A separate Hermes Agent OS layer is not implemented as a distinct artifact as of this summary.

## Safety Controls

Current safety controls:

- status visibility through `scripts/hermes_local_status.sh`
- resident visibility through `scripts/hermes_resident_status.sh`
- emergency stop through `scripts/hermes_emergency_stop.sh "reason"`
- freeze flags for repo and resident-once runtime
- metadata-only audit logging
- requested-only approval helper
- file-zone classifier
- command-policy classifier
- dry-run policy checker
- no real credentials in examples or runtime state
- Desktop fail-closed policy

## Verify Status

Run:

```sh
scripts/hermes_local_status.sh
```

Expected current state:

- branch `main`
- repo clean
- adapter LaunchAgent installed
- adapter LaunchAgent unloaded/stopped
- no `8088` listener
- resident-once LaunchAgent installed
- resident-once unloaded/stopped
- Desktop installed/present
- Desktop verified `no`
- Desktop running `false`
- command execution enabled `no`
- resident mode enabled `no`
- external integrations enabled `no`
- freeze flag absent

## Run Resident-Once Manually

Direct repo run:

```sh
scripts/hermes_resident_once.sh
```

Application Support wrapper run:

```sh
/Users/michaelrinebold/.local/bin/msr-hermes-resident-once
```

Manual launchctl run:

```sh
launchctl bootstrap "gui/$(id -u)" /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
launchctl kickstart "gui/$(id -u)/com.msr.hermes.resident-once"
launchctl bootout "gui/$(id -u)" /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.resident-once.plist
```

## Emergency Stop

Run:

```sh
scripts/hermes_emergency_stop.sh "reason"
```

Emergency stop freezes both the repo control path and the resident-once Application Support runtime control path. It does not delete artifacts, start services, run Hermes live, launch Desktop, connect integrations, or print secrets.

## Remote Repository Verification

Phase 7F remote verification was completed after the documentation commit was pushed.

Verification commands:

```sh
git fetch origin
git rev-parse HEAD
git rev-parse origin/main
git merge-base HEAD origin/main
git status --short
```

Verified success condition:

```text
local HEAD equals origin/main HEAD, merge-base equals both, and git status is clean
```

The final post-push local and remote HEAD values are recorded in the Phase 7F final report. If this file is changed in a later commit, repeat the same verification commands after that later push.

## Next Optional Enhancements

Possible future phases, each requiring separate explicit approval:

- richer local task format
- stricter resident-once task queue conventions
- command-execution approval gate
- audit viewer or daily audit rollup
- Desktop support clarification with Nous Research
- signed/notarized Desktop artifact validation
- Helio/Agent Bus read-only gateway planning after credential decision
