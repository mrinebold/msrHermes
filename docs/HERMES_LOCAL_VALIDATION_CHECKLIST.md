# Hermes Local Validation Checklist

Phase: 5AJ-5BC
Status: local validation checklist, resident design, adapter service validation, manual runbook input, bounded manual-service Hermes validation, bounded local PRD review, local task inbox scaffold, first inbox task validation, compact task validation, local operations runbook documentation, local-only readiness certification, and read-only status command

## Purpose

Validate Hermes operating-system readiness using local configuration and documentation checks only. Phase 5AJ operates under the Phase 5AI credential-rotation deferral boundary.

This checklist does not approve credential use, live Agent Bus reads/writes, integrations, Hermes Desktop launch, background services, or broader Hermes authority.

Phase 5AK uses this checklist as an input to the operational readiness review in `docs/HERMES_OPERATIONAL_READINESS_REVIEW.md`.

Phase 5AL uses this checklist as an input to the proposal-only persistent local config plan in `docs/HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md`.

Phase 5AM applied the approved persistent local config to `~/.hermes/config.yaml` with backup and validation. This checklist still does not approve live Hermes runs, adapter start, background services, integrations, Agent Bus reads/writes, Desktop launch, or broader Hermes authority.

Phase 5AN approved and completed one live local validation prompt through the foreground localhost adapter. This does not approve additional prompts, background services, integrations, Agent Bus reads/writes, Desktop launch, resident mode, or broader Hermes authority.

Phase 5AO added a resident-mode design proposal only in `docs/HERMES_RESIDENT_MODE_PLAN.md`. It does not approve creating launchd plists, starting background services, running Hermes resident mode, or broadening authority.

Phase 5AP added an adapter LaunchAgent service-install proposal only in `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md`. It does not approve creating the plist, modifying `~/Library/LaunchAgents`, loading or starting launchd services, starting the adapter, running Hermes live, or broadening authority.

Phase 5AQ approved one controlled adapter LaunchAgent install validation. Foreground adapter validation passed, but the LaunchAgent failed closed with exit code `126` because launchd could not execute the adapter script from the `Documents` repo path. The service is unloaded and stopped; the plist remains installed on disk.

Phase 5AR added `docs/HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md` as a proposal-only comparison. It recommends a minimal no-secret wrapper under `/Users/michaelrinebold/.local/bin/` and does not approve creating it, editing the plist, retrying launchd, granting privacy permissions, moving the repo, starting the adapter, or running Hermes live.

Phase 5AS created the wrapper, moved only the minimal adapter runtime to `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current`, validated manual LaunchAgent start/health/models/localhost-only binding, and stopped/unloaded the service. It does not approve Hermes resident mode, RunAtLoad, KeepAlive, credentials, integrations, Desktop launch, Agent Bus activity, or `~/.hermes` modification.

Phase 5AT added a manual adapter service runbook and helper scripts. It validates manual start/status/stop only and does not approve automatic service start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AU used the manual adapter service procedure for one harmless Hermes prompt through the persistent localhost-only config. The prompt exited `0`, returned usable output, and the adapter service was stopped/unloaded afterward. It does not approve additional live prompts, automatic service start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AV ran one bounded local PRD review through the manual adapter service and locked-down pilot harness. The output was usable but included one stale statement that task inbox usage was ready before the inbox existed; that statement is not authority or readiness evidence. Phase 5AV does not approve additional live prompts, automatic service start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AW added a scaffold-only local task inbox/outbox/archive and a runner that refuses paths outside `sandbox/hermes_inbox/`, requires adapter health, writes only under `sandbox/hermes_outbox/`, and uses a sanitized child environment. It does not approve running a live inbox task until Phase 5AX, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AX ran one sample inbox task through the manual adapter service procedure. The runner exited `0`, wrote only to `sandbox/hermes_outbox/`, and Hermes produced a fail-closed result because the sample task contained no embedded local context. The adapter service was stopped/unloaded afterward. Phase 5AX does not approve additional live tasks, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AZ attempted one generated context-bearing inbox task, but it did not produce usable output. The local model path timed out once and the second call was terminated fail-closed after more than 180 seconds. The adapter service was stopped/unloaded afterward. Phase 5AZ does not approve additional live tasks, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5AZ-R added compact task generation and ran one compact context-bearing inbox task. The runner exited `0`, wrote only to `sandbox/hermes_outbox/`, and produced usable structured output with a conservative validation-style recommendation. The adapter service was stopped/unloaded afterward. Phase 5AZ-R does not approve additional live tasks, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5BA added `docs/HERMES_LOCAL_OPERATIONS_RUNBOOK.md` for safe daily manual local-only use. The runbook documents manual adapter start/status/stop, compact context-bearing task generation, local task execution, outbox review, cleanup verification, troubleshooting, safe boundaries, rollback, and ready/not-ready status. Phase 5BA does not approve additional live tasks, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5BB added `docs/HERMES_LOCAL_ONLY_READY_REPORT.md` and certifies Hermes for manual local-only use only. It records proven capabilities, approved operating mode, unapproved capabilities, final expected state, resident-mode blockers, and recommended next phases. Phase 5BB does not approve additional live tasks, automatic adapter start, keepalive, Hermes resident mode, Desktop, credentials, integrations, Agent Bus activity, or `~/.hermes` modification.

Phase 5BC added `scripts/hermes_local_status.sh`, a read-only operator status command. It reports local state without starting services, stopping services, modifying files, launching Desktop, connecting integrations, printing secret values, or broadening authority.

## Approved Surfaces

Inspect only:

- `config/hermes-pilot.example.env`
- `scripts/run_model_router_adapter.sh`
- `scripts/run_hermes_pilot.sh`
- `scripts/hermes_local_status.sh`
- `services/model_router_adapter/README.md`
- `docs/HERMES_PILOT_MODE.md`
- `docs/HERMES_SECURITY_MODEL.md`
- `docs/HERMES_MODEL_PROVIDER_PLAN.md`
- `docs/HERMES_OWNERSHIP_MODEL.md`
- `docs/HERMES_OPERATIONAL_READINESS_REVIEW.md`
- `docs/HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md`
- `docs/HERMES_RESIDENT_MODE_PLAN.md`
- `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md`
- `docs/HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md`
- `docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md`
- `docs/HERMES_LOCAL_TASK_INBOX.md`
- `docs/HERMES_LOCAL_OPERATIONS_RUNBOOK.md`
- `docs/HERMES_LOCAL_ONLY_READY_REPORT.md`
- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`

## Local-Only Invariants

The local pilot and adapter configuration must preserve these invariants:

- adapter binds only to `127.0.0.1`
- adapter uses only port `8088`
- Hermes pilot base URL is only `http://127.0.0.1:8088/v1`
- pilot model is only `gemma4:26b`
- pilot API key is only `dummy-local-adapter-key`
- no real OpenAI, Anthropic, OpenRouter, Supabase, Google, GitHub, Home Assistant, Helio, or cloud-provider credentials are passed into the Hermes child process
- cloud providers remain disabled and fail-closed
- Google remains disconnected
- Supabase live access remains frozen
- Home Assistant remains disconnected
- GitHub token use remains disabled
- Helio/Agent Bus writes remain disabled
- Hermes Desktop remains fail-closed and is not launched
- no launchd plist, background service, or resident mode is created
- persistent config points only to the localhost adapter and does not add real credentials
- Hermes receives no broad filesystem authority
- every boundary-crossing action still requires a new explicit human-approved phase
- Phase 5AN proved one harmless prompt can use the persistent config through the localhost adapter
- Phase 5AO keeps resident mode proposal-only and adapter-service-first
- Phase 5AP keeps service installation proposal-only with `RunAtLoad=false`, `KeepAlive=false`, rollback defined, and no plist created
- Phase 5AQ proves the foreground adapter remains healthy but launchd service execution from the `Documents` repo path is blocked by macOS permissions
- Phase 5AR recommends minimal wrapper remediation over broad macOS privacy permission and whole-repo movement
- Phase 5AS validates manual adapter LaunchAgent start/stop from a non-`Documents` self-contained runtime and leaves the service stopped
- Phase 5AT validates helper-driven manual start/stop and keeps `RunAtLoad=false`, `KeepAlive=false`, and Hermes resident mode disabled
- Phase 5AU validates one harmless Hermes prompt through the manual adapter service and leaves the service stopped
- Phase 5AV validates one bounded PRD review through the manual adapter service and leaves the service stopped
- Phase 5AW creates a local-only task inbox scaffold but does not run a live inbox task
- Phase 5AX validates one sample inbox task through the manual adapter service and leaves the service stopped
- Phase 5AZ failed closed for the generated context-bearing inbox task and leaves the service stopped
- Phase 5AZ-R validates one compact context-bearing inbox task through the manual adapter service and leaves the service stopped
- Phase 5BA documents the safe daily manual local-only operations loop without starting the adapter or Hermes
- Phase 5BB certifies manual local-only readiness without starting the adapter or Hermes
- Phase 5BC adds a read-only local status command without starting services or changing runtime state
- Phase 6S adds a dry-run policy check command that classifies proposed commands and paths without executing commands or reading/writing target files
- Phase 6T adds a one-shot dry-run resident loop that scans only `sandbox/hermes_inbox`, writes redacted proposals only to `sandbox/hermes_outbox`, and does not run Hermes live or start the adapter

## Credential Deferral Boundary

Phase 5AI deferred credential rotation only for bounded local-only validation/configuration work.

The deferral does not mean any credential is rotated, revoked, reviewed, or safe. It does not authorize:

- provider console or provider API calls
- live Agent Bus reads/writes
- Supabase service-role use
- Google Workspace operations
- GitHub mutations
- Home Assistant service calls
- Helio gateway or dispatcher use
- credential storage, replacement, deletion, or modification
- Desktop launch or replacement
- shell/file-edit authority expansion for Hermes
- background services or resident mode

## Validation Commands

Run these local checks only:

```sh
bash -n scripts/run_model_router_adapter.sh
bash -n scripts/run_hermes_pilot.sh
python3 -m unittest discover
git diff --check
```

Do not run the adapter or Hermes live in Phase 5AJ.

For Phase 6T dry-run validation, the only approved resident-loop check is:

```sh
scripts/hermes_resident_dry_run.sh
```

It must leave no adapter listener, no Hermes process, no Desktop process, and no resident service. It must not archive or delete task files.

## Evidence To Record

Record:

- inspected surfaces
- whether runner defaults remain localhost-only
- whether pilot env stripping covers all credentialed services
- whether docs/config examples avoid real-looking secrets
- whether local-only mode remains compatible with the Phase 5AI credential deferral freeze
- test results
- confirmation that no live adapter, Hermes pilot, Desktop, integration, credential, Agent Bus read/write, background service, or authority-broadening action occurred
- dry-run policy classifications and dry-run resident proposals when those scripts are explicitly approved

## Next Gate

After Phase 5BC, the safest next step is:

- draft a resident Hermes authority model proposal, without starting services, modifying runtime configs, enabling resident mode, launching Desktop, using credentials, connecting integrations, or touching Agent Bus.

Do not resume live Agent Bus reads/writes or credentialed integrations from this checklist alone.
