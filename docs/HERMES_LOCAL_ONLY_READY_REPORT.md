# Hermes Local-Only Ready Report

Phase: 5BB-6A
Status: certified for manual local-only use; read-only status command added; resident authority, audit, and emergency stop models proposed; not certified for resident or integrated operation

## Certification

Hermes is ready for manual local-only use on the Mac mini through the documented adapter service and local task inbox workflow.

This certification is narrow. It does not approve resident Hermes, automatic adapter service startup, Desktop launch, external integrations, live Agent Bus activity, real credentials, shell execution by Hermes, or broad filesystem authority.

## Proven Capabilities

- Hermes persistent config works with the localhost adapter.
- The adapter service can start and stop manually through the approved helper scripts.
- The adapter binds localhost only on `127.0.0.1:8088`.
- DevMonster Gemma4 works through the adapter as `gemma4:26b`.
- Hermes can produce useful output for bounded local prompts.
- The local inbox/outbox workflow exists under `sandbox/hermes_inbox/` and `sandbox/hermes_outbox/`.
- The context-bearing task builder exists at `scripts/build_hermes_local_task.py`.
- Compact task remediation is validated: Phase 5AZ-R succeeded with `sandbox/hermes_inbox/next_phase_recommendation_compact.task.md` after the larger generated task timed out in Phase 5AZ.
- A read-only local status command exists at `scripts/hermes_local_status.sh`.
- Phase 6M adds a local audit writer primitive that writes redacted JSONL events in tests without starting services or enabling runtime authority.
- Phase 6Q extends the local status command to report safety module importability, audit log state, approval log state, freeze flag state, command execution disabled, and resident mode disabled without creating files or starting services.
- Phase 6R adds a no-sudo emergency stop script that can create a local freeze flag, write reason metadata, stop the approved adapter service only if already running, and emit a metadata-only audit event.
- Phase 6U refines the local status command to show audit file counts, latest audit risk level, approval file counts, latest approval action/expiration, valid approval count, freeze reason visibility, and emergency/policy/dry-run script presence while remaining read-only.
- Phase 6V adds local audit and approval visibility helpers that can create harmless audit events and requested-only approval records for status testing. They do not grant approval or execute actions.
- Phase 6X defines the resident validation gate for a future manual dry-run LaunchAgent validation. It does not enable resident mode or command execution.
- Tests pass for the local-only scripts, docs, task builder, local task runner, and guardrails.

## Current Approved Operating Mode

- manual adapter service start/stop only
- Hermes CLI local-only
- context-bearing or compact inbox tasks only
- no Desktop
- no external integrations
- no resident Hermes mode

## Not Approved Yet

- resident Hermes
- `RunAtLoad=true`
- `KeepAlive=true`
- Desktop launch
- Google
- Supabase live reads/writes
- Helio
- Home Assistant
- GitHub token use
- cloud providers
- real credentials
- broad filesystem authority
- shell execution by Hermes
- audit integration with resident behavior, command policy, emergency stop, or approval lookup
- dry-run resident loop

## Current Operational Procedure

0. Check local status:

```sh
scripts/hermes_local_status.sh
```

1. Start adapter service manually:

```sh
scripts/adapter_service_start.sh
```

2. Check status:

```sh
scripts/adapter_service_status.sh
```

3. Build a local compact task:

```sh
python3 scripts/build_hermes_local_task.py --compact --task-type next_phase_recommendation --output sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

4. Run the local task:

```sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

5. Inspect outbox:

```text
sandbox/hermes_outbox/
```

6. Stop adapter service manually:

```sh
scripts/adapter_service_stop.sh
```

7. Verify cleanup:

```sh
scripts/adapter_service_status.sh
```

## Current Final Expected State

- LaunchAgent installed but stopped/unloaded.
- No `8088` listener.
- No Hermes process.
- No adapter process.
- No Desktop process.
- Repo clean.
- Command execution reports disabled.
- Resident mode reports disabled.

Confirm with:

```sh
scripts/hermes_local_status.sh
```

## Remaining Blockers Before Hermes Resident Operation

- Approve and implement the resident authority model proposed in `docs/HERMES_RESIDENT_AUTHORITY_MODEL.md`.
- Decide resident authority model implementation and approval path.
- Implement the audit log design proposed in `docs/HERMES_AUDIT_LOG_DESIGN.md`.
- Implement the emergency stop design proposed in `docs/HERMES_EMERGENCY_STOP_DESIGN.md`.
- Define audit log storage implementation and retention policy.
- Decide `RunAtLoad` and `KeepAlive` policy.
- Decide credential rotation.
- Define Google, Supabase, and Home Assistant phased integration plans.
- Decide Desktop fate after Nous Research clarification.
- Define Hermes-to-Helio delegation boundary.
- Define approved shell/file-operation gate.
- Complete an explicitly approved resident dry-run validation gate before any resident LaunchAgent or service install.

## Recommended Next 5 Phases

- Phase 6D: resident service proposal.
- Phase 6E: Helio delegation interface proposal.
- Phase 6F: command allowlist and denylist proposal.
- Phase 6G: audit log implementation proposal.
- Phase 6H: emergency stop implementation proposal.

## Final Boundary

Local-only readiness is certified for manual use only. Any move beyond this report requires a new explicit phase and human approval.

## Phase 7A Governed Runtime Update

Phase 7A moved the first resident layer from proposal to a governed one-shot implementation while preserving the local-only boundary.

Proven additions:

- `scripts/hermes_resident_once.sh` runs once and exits in observe/recommend/dry-run mode.
- `scripts/hermes_resident_status.sh` reports resident-once, Desktop, adapter, audit, approval, and freeze state without writes.
- Resident-once direct repo execution succeeded and wrote redacted proposals for approved local inbox tasks.
- A minimal launchd runtime under `/Users/michaelrinebold/Library/Application Support/Helio/hermes-resident-once/current` avoids the macOS `Documents` privacy denial.
- The user LaunchAgent `com.msr.hermes.resident-once` validated with manual kickstart, exited with code `0`, and was unloaded afterward.
- The LaunchAgent remains `RunAtLoad=false` and `KeepAlive=false`.
- Command execution remains disabled.
- Live Hermes inference remains disabled for resident-once.
- External integrations remain disabled.
- Desktop remains fail-closed.

Current expected final state after Phase 7A:

- adapter LaunchAgent installed but stopped/unloaded
- resident-once LaunchAgent installed but stopped/unloaded
- no `8088` listener
- no adapter process
- no Hermes resident process
- no Desktop process
- command execution enabled: no
- external integrations enabled: no

Desktop certification remains blocked: the official DMG verifies as a disk image, but both the mounted app and `/Applications/Hermes.app` are `com.nousresearch.hermes.setup` version `0.0.1` setup/bootstrap bundles that fail strict codesign and Gatekeeper assessment.

Phase 7B adds a validated Application Support runtime for governed resident-once operation. The runtime is documented in `docs/HERMES_RESIDENT_ONCE_RUNTIME.md`, can be regenerated from approved repo source files, and has been validated by direct wrapper execution. It remains dry-run/manual only: command execution, external integrations, adapter auto-start, live Hermes inference, Desktop launch, `RunAtLoad=true`, and `KeepAlive=true` are still not approved.

Phase 7D adds `docs/HERMES_GOVERNED_MANUAL_RESIDENT_RUNBOOK.md` as the final current operating procedure. Hermes is ready for manual governed resident-shaped local operation only: observe approved inbox tasks, write dry-run proposals, write audit metadata, respect emergency stop, and report status. Command execution, external integrations, Desktop launch, and daemon operation remain disabled.
