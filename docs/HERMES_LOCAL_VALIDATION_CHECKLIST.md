# Hermes Local Validation Checklist

Phase: 5AJ
Status: local-only validation checklist

## Purpose

Validate Hermes operating-system readiness using local configuration and documentation checks only. Phase 5AJ operates under the Phase 5AI credential-rotation deferral boundary.

This checklist does not approve credential use, live Agent Bus reads/writes, integrations, Hermes Desktop launch, background services, or broader Hermes authority.

## Approved Surfaces

Inspect only:

- `config/hermes-pilot.example.env`
- `scripts/run_model_router_adapter.sh`
- `scripts/run_hermes_pilot.sh`
- `services/model_router_adapter/README.md`
- `docs/HERMES_PILOT_MODE.md`
- `docs/HERMES_SECURITY_MODEL.md`
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
- Hermes receives no broad filesystem authority
- every boundary-crossing action still requires a new explicit human-approved phase

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

After Phase 5AJ, the safest next step is either:

- continue local-only hardening of tests/docs/config examples, or
- prepare a separate, human-approved read-only configuration phase that states exactly whether any credential-family-specific deferral is being used.

Do not resume live Agent Bus reads/writes or credentialed integrations from this checklist alone.
