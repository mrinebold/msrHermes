# Hermes Local Validation Checklist

Phase: 5AJ-5AR
Status: local validation checklist, resident design, adapter service validation, and path remediation input

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

## Approved Surfaces

Inspect only:

- `config/hermes-pilot.example.env`
- `scripts/run_model_router_adapter.sh`
- `scripts/run_hermes_pilot.sh`
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

## Evidence To Record

Record:

- inspected surfaces
- whether runner defaults remain localhost-only
- whether pilot env stripping covers all credentialed services
- whether docs/config examples avoid real-looking secrets
- whether local-only mode remains compatible with the Phase 5AI credential deferral freeze
- test results
- confirmation that no live adapter, Hermes pilot, Desktop, integration, credential, Agent Bus read/write, background service, or authority-broadening action occurred

## Next Gate

After Phase 5AR, the safest next step is either:

- explicitly approve a narrow wrapper implementation and launchd retry phase using `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`, or
- defer background service work and continue local-only hardening of tests/docs/config examples.

Do not resume live Agent Bus reads/writes or credentialed integrations from this checklist alone.
