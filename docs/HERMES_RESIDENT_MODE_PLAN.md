# Hermes Resident Mode Plan

Phase: 5AO-6A
Status: manual adapter service operation validated; Hermes resident mode disabled; resident authority, audit, emergency stop, and service models proposed

## Purpose

Design how Hermes and the local MSR Model Router Adapter could eventually run in resident/background mode on the Mac mini.

Phase 5AO does not create launchd plists, start background services, run Hermes, start the adapter, connect integrations, use real credentials, modify `~/.hermes`, launch Desktop, or broaden Hermes authority.

Phase 5AP adds `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md` as the exact future LaunchAgent service-install proposal. Phase 5AP also does not create, install, load, bootstrap, kickstart, or start any service.

Phase 5AQ approved one controlled user LaunchAgent install validation. The foreground adapter validated successfully, but the LaunchAgent could not execute the adapter script from the `Documents` repo path and exited `126` before binding. The service was unloaded and stopped; no resident Hermes mode was created.

Phase 5AR proposes remediating the launchd path failure with a minimal no-secret wrapper at `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`. Phase 5AR does not create the wrapper, modify the plist, retry launchd, start the adapter, or enable resident Hermes mode.

Phase 5AS created the wrapper and a self-contained adapter runtime outside `Documents` under `~/Library/Application Support/Helio/hermes-adapter-service/`. The LaunchAgent started manually, served health and model metadata on `127.0.0.1:8088`, and was stopped/unloaded after validation. Hermes resident/autonomous mode remains disabled.

Phase 5AT defines manual adapter service operation with helper scripts and a runbook. The validated policy is manual start/stop only; `RunAtLoad=false`, `KeepAlive=false`, and Hermes resident/autonomous mode remain unchanged.

Phase 6A adds `docs/HERMES_RESIDENT_AUTHORITY_MODEL.md` as the proposal-only authority model for future resident Hermes. It defines authority tiers 0 through 7, human approval rules, audit log requirements, emergency stop requirements, file zones, command allowlist/denylist concepts, credential handling, network access, service management, Hermes-to-Helio boundaries, Hermes-to-DevMonster boundaries, Desktop fail-closed rules, and minimum acceptance criteria before resident mode. It does not enable resident mode.

Phase 6B adds `docs/HERMES_AUDIT_LOG_DESIGN.md` as the proposal-only audit model. It defines event categories, required fields, local JSONL storage under `logs/hermes_audit/`, redaction rules, approval logging, fail-closed logging, rollback logging, audit views, and resident-mode acceptance criteria. It does not implement audit writes or create runtime state.

Phase 6C adds `docs/HERMES_EMERGENCY_STOP_DESIGN.md` as the proposal-only emergency stop model. It defines stop goals, triggers, stop levels, future command proposal, required behavior, audit interaction, and acceptance criteria before resident mode. It does not implement the emergency stop script or change runtime state.

Phase 6D adds `docs/HERMES_RESIDENT_SERVICE_PROPOSAL.md` as the proposal-only future resident service design. It defines the proposed label `com.msr.hermes.resident`, execution model, loop responsibilities, non-goals, allowed and forbidden zones, processing flow, acceptance criteria, and rollback concept. It does not create a resident loop script, plist, or service.

## Proposed Resident Architecture

Resident rollout should be staged:

1. Adapter service only first.
2. Hermes remains manually invoked at first.
3. Future Hermes resident/autonomous mode requires a separate approval phase.

Initial resident service candidate:

```text
Hermes CLI/manual invocation
  -> http://127.0.0.1:8088/v1
  -> launchd-managed local adapter service
  -> services/model_router
  -> DevMonster Gemma over Tailscale
```

Required architecture constraints:

- adapter binds only to `127.0.0.1:8088`
- adapter never binds to `0.0.0.0`, LAN, public, or Tailscale interfaces
- Hermes uses the persistent local config already validated in Phase 5AN
- Hermes Desktop is not a dependency
- Hermes Desktop remains fail-closed
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen
- no real credentials are added to the adapter service environment
- no Hermes autonomous resident process is approved by this plan

## Future Launchd Proposal

No plist is created in Phase 5AO or Phase 5AP. A later approved phase may create a user LaunchAgent with the exact proposal in `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md`.

| Field | Proposed value |
| --- | --- |
| Label | `com.msr.hermes.model-router-adapter` |
| Plist path | `~/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist` |
| ProgramArguments | `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter` |
| WorkingDirectory | `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current` |
| RunAtLoad | `false` for first service install so loading the plist does not auto-start the adapter |
| KeepAlive | `false` for first service install; consider `true` only after foreground and one-shot background validation are stable |
| StandardOutPath | `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log` |
| StandardErrorPath | `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log` |

Proposed environment variables:

```text
MODEL_ROUTER_ADAPTER_HOST=127.0.0.1
MODEL_ROUTER_ADAPTER_PORT=8088
DEVMONSTER_OLLAMA_URL=http://100.93.120.124:11434
DEVMONSTER_DEFAULT_MODEL=gemma4:26b
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true
MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true
MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true
```

Do not include:

- OpenAI, Anthropic, or OpenRouter keys
- Supabase credentials
- Google credentials
- GitHub tokens
- Home Assistant tokens
- Helio gateway or dispatcher tokens
- prompt text
- file contents
- model output

## Future Commands

These commands are proposal-only. Do not run them until a later phase explicitly approves service creation.

Install/load candidate:

```sh
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

Start candidate:

```sh
launchctl kickstart "gui/$(id -u)/com.msr.hermes.model-router-adapter"
```

Stop candidate:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

Rollback candidate:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
```

## Health Checks

Future resident validation must include:

```sh
curl -sS http://127.0.0.1:8088/health
curl -sS http://127.0.0.1:8088/v1/models
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Expected checks:

- `/health` returns healthy status
- `/v1/models` includes `gemma4:26b`
- listener is only `127.0.0.1:8088`
- no `0.0.0.0` listener
- no LAN/public/Tailscale bind
- DevMonster is reachable only through the adapter route
- no cloud provider fallback is selected
- no real secrets appear in the adapter process environment
- no Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or Desktop activity appears

## Logs And Audit

Adapter logs must remain metadata-only:

- request timestamp
- method and path
- response status
- selected model
- elapsed time
- response shape metadata
- message-structure metadata

Adapter logs must not include:

- prompt text
- file contents
- model output text
- API keys
- OAuth tokens
- Supabase keys
- GitHub tokens
- Home Assistant tokens
- Helio credentials

Recommended log handling:

- write stdout/stderr under `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/`
- keep log permissions owner-readable only where possible
- add rotation before long-running resident use
- cap file size or use periodic rotation
- include a cleanup command in every validation phase

## Gates Before Future Resident Mode

Before creating any service:

- human approval for the exact phase
- review and back up existing configs
- test `scripts/run_model_router_adapter.sh` in foreground first
- verify `127.0.0.1:8088` binding
- verify no `0.0.0.0`, LAN, public, or Tailscale bind
- verify no external integrations are enabled
- verify no real credentials are present in process env
- verify stop command works
- verify rollback command works
- verify logs remain metadata-only
- verify no prompt text, file contents, or model output are logged
- verify no Desktop launch
- verify no Hermes autonomous resident process

Before Hermes resident/autonomous operation:

- complete adapter service validation first
- create and approve the Hermes resident authority model
- define exact authority classes Hermes may use
- define audit fields, approval IDs, and refusal behavior
- define stop and rollback procedures
- define maximum runtime, log retention, and monitoring
- require separate human approval

## Non-Goals

Phase 5AO does not approve:

- creating launchd plists
- starting adapter live
- starting background services
- Hermes autonomous resident process
- Hermes Desktop launch
- Google Workspace
- Supabase
- GitHub
- Home Assistant
- Helio gateway or dispatcher use
- Agent Bus reads or writes
- credential rotation
- real credentials
- shell/action automation
- cloud provider fallback
- broad filesystem authority

## Phase 5AO Conclusion

The safest resident path is adapter-service-first, with Hermes remaining manually invoked. The next executable phase, if approved, should create and validate only the adapter LaunchAgent with rollback, not Hermes autonomous resident mode.

## Phase 5AP Service Install Proposal Result

Phase 5AP adds `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md` as a proposal-only service install package. It defines the future user LaunchAgent label, plist path, exact plist XML, command path, working directory, metadata-only log paths, localhost-only environment, future bootstrap/status/health/stop/log/rollback commands, preflight requirements, and future acceptance criteria.

The proposal keeps `RunAtLoad=false` and `KeepAlive=false` for the first service install. Hermes remains manually invoked, Hermes autonomous resident mode remains unapproved, Hermes Desktop remains fail-closed, and credentialed integrations remain frozen. No plist or launchd file was created, loaded, or started in Phase 5AP.

## Phase 5AQ Controlled Install Validation Result

Phase 5AQ installed the user LaunchAgent plist at `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist` and validated it with `plutil`. The plist uses `RunAtLoad=false`, `KeepAlive=false`, approved localhost adapter environment variables, and repo-local logs under `/Users/michaelrinebold/Documents/Helio/helio-command-center/logs/`.

Foreground runner validation passed before launchd was touched: `/health` worked, `/v1/models` worked, DevMonster responded with version `0.30.4`, and listener inspection showed only `127.0.0.1:8088`.

Manual `launchctl kickstart` failed closed with exit code `126`. The stderr log reported `Operation not permitted` for `/Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh`, indicating launchd could not execute from the `Documents` repo path under the current macOS privacy boundary. The service was unloaded afterward and no `8088` listener remained.

Resident mode remains blocked. Hermes remains manually invoked only. The next resident-related phase should remediate the service path or explicitly decide on macOS privacy permissions before retrying launchd.

## Phase 5AR Path Remediation Proposal Result

Phase 5AR added `docs/HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md` and recommends a minimal wrapper outside `Documents` instead of broad macOS privacy permissions or moving the entire repo. The wrapper option keeps the service adapter-only, preserves localhost-only behavior through the existing runner, avoids real credentials, and keeps Hermes resident/autonomous mode disabled.

No remediation was applied in Phase 5AR. Resident mode remains blocked until a later explicit phase creates the wrapper, updates the plist, and validates launchd start/stop behavior.

## Phase 5AS Wrapper Validation Result

Phase 5AS created `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`, moved the minimal adapter runtime to `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current`, updated the adapter LaunchAgent to use that non-`Documents` runtime, and attempted one manual launchctl start. The wrapper passed shell syntax validation, and the plist passed `plutil`.

The service started successfully. `/health` returned status `ok`, `/v1/models` returned model metadata including `gemma4:26b`, and listener inspection showed only `127.0.0.1:8088`. The service was then stopped and unloaded; no `8088` listener remains.

Adapter service mechanics are validated for manual start/stop. Hermes remains manually invoked only, and Hermes resident/autonomous mode remains disabled. The next resident-related phase should decide whether manual adapter service start is allowed as an operational procedure, not enable RunAtLoad or KeepAlive by default.

## Phase 5AT Manual Service Operation Result

Phase 5AT added `docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md` and helper scripts for manual service start, stop, and status. `scripts/adapter_service_start.sh` successfully started the existing adapter LaunchAgent, validated `/health`, validated `/v1/models`, and confirmed only `127.0.0.1:8088` was listening. `scripts/adapter_service_stop.sh` stopped/unloaded the service and confirmed no `8088` listener remained. Final `scripts/adapter_service_status.sh` reported `loaded=false` and `listener=false`.

Manual adapter service start/stop is now documented as the safe operating procedure. Automatic start and keepalive remain disabled.

## Phase 6A Resident Authority Model Result

Phase 6A adds `docs/HERMES_RESIDENT_AUTHORITY_MODEL.md` as the proposal-only authority model for future resident Hermes.

The proposal defines tiers from observe-only through resident delegated operator, plus human approval rules, audit logs, emergency stop, allowed and forbidden file zones, command allowlist/denylist concepts, credential handling, network access, service management, Hermes-to-Helio delegation, Hermes-to-DevMonster inference boundaries, Desktop fail-closed behavior, and minimum acceptance criteria before resident mode.

No resident runtime was enabled. `RunAtLoad=false`, `KeepAlive=false`, adapter manual start/stop only, Hermes manually invoked only, Desktop fail-closed, and credentialed integrations frozen remain the active policy.

## Phase 6B Audit Log Design Result

Phase 6B added `docs/HERMES_AUDIT_LOG_DESIGN.md` as the proposal-only audit model required before resident or execution capability.

The design requires metadata-first local JSONL audit logs, no secret values, prompt/file content redaction by default, approval events, fail-closed events, rollback events, emergency stop events, daily and phase rollups, and local storage under `logs/hermes_audit/`.

No audit directory was created, no audit writer was implemented, no service was started, and resident mode remains disabled.

## Phase 6C Emergency Stop Design Result

Phase 6C added `docs/HERMES_EMERGENCY_STOP_DESIGN.md` as the proposal-only emergency stop model required before resident Hermes.

The design defines status-only, adapter-stop, resident-process-stop, LaunchAgent-disable, inbox-freeze, and artifact-quarantine levels. It requires no sudo, no deletion, no credential printing, no external calls, repeated-safe behavior, preserved logs/artifacts/backups, and audit event emission after audit logging exists.

No emergency stop script was created, no service was stopped or started, and resident mode remains disabled.

## Phase 6D Resident Service Proposal Result

Phase 6D added `docs/HERMES_RESIDENT_SERVICE_PROPOSAL.md` as the proposal-only future service design.

The proposal keeps the first validation user-level, manual-start only, with `RunAtLoad=false`, `KeepAlive=false`, no sudo, audit logging required before execution, emergency stop compatibility, no shell execution, no external integrations, no Desktop, no credentials, and no broad filesystem scanning.

No resident loop script was created, no Hermes LaunchAgent was created, no service was loaded or started, and resident mode remains disabled.
