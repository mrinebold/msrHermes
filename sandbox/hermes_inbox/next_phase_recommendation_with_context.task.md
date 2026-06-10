Using only the embedded local context below, recommend the next safest local-only Hermes phase.
Do not request external integrations, credentials, Desktop launch, Agent Bus access, Google, Supabase, Home Assistant, GitHub, or Helio.
Do not ask to read files. Do not use tools. Do not execute shell commands.
Return exactly these fields:
recommended phase name
objective
why it is safe
required human approval
non-goals
acceptance criteria

Embedded local context:
## Source: docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md
Character limit: 1800

# PRD: MSR Hermes Operating System

## Status

Phase 5AX ran one local inbox task through the manual adapter service procedure. The runner accepted `sandbox/hermes_inbox/next_step_review.task.md`, wrote stdout/stderr/metrics only under `sandbox/hermes_outbox/`, exited `0`, and Hermes returned a safe fail-closed answer because the sample task contained no embedded local context. The adapter service was stopped/unloaded afterward.

Repository status is maintained by git; this PRD records Phase 5AX as first local inbox task execution complete. The LaunchAgent plist remains installed on disk at `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist`, but it is unloaded and not running. Persistent config remains in `~/.hermes/config.yaml`; backup remains `/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak`. Hermes rema
[...excerpt truncated...]
o empty scoped visibility, or Helio should expose an explicit read-only gateway/view. The follow-up must not use direct Hermes service-role access.

Phase 6G reference:

- [Read-only preflight script](../../scripts/agent_bus_readonly_preflight.py)
- [Read-only preflight mocked tests](../../tests/agent_bus/test_readonly_preflight.py)

Phase 6E reference:

- [Hermes Helio Adapter Design](../HERMES_HELIO_ADAPTER_DESIGN.md)

## Non-Goals

- Do not run Hermes setup.
- Do not start Hermes as a background or resident service.
- Do not enable Hermes autonomous execution.
- Do not connect Supabase.
- Do not store real secrets.
- Do not send messages to agents.
- Do not connect the scaffold to live services until a later approval is explicit.
- Do not use `SUPABASE_SERVICE_ROLE_KEY` in the Hermes adapter.
- Do not run further live reads until exposed high-risk credentials are rotated.

## Source: docs/prd/CHANGELOG.md
Character limit: 1300

# PRD Changelog

## 2026-06-09

- Completed Phase 5AX local Hermes task inbox execution.
- Started the adapter service through `scripts/adapter_service_start.sh`; `/health` returned status `ok`, `/v1/models` returned model metadata including `gemma4:26b`, and listener inspection showed only `127.0.0.1:8088`.
- Ran `scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_step_review.task.md`.
- Captured `sandbox/hermes_outbox/next_step_review.out.md`, `sandbox/hermes_outbox/next_step_review.stderr`, and `sandbox/hermes_outbox/next_step_review.metrics`.
- Recorded runner exit code `0`, elapsed time `65` seconds, stdout `148` by
[...excerpt truncated...]
-messaging`.
- Added `docs/AGENT_BUS_CONTRACT.md`.
- Updated the source map to elevate `packages/ano-messaging` as the primary portable message bus source candidate.
- Recorded that `ano-messaging` does not implement `agent_tasks`, task events, approvals, or a full conversation model.
- Recommended Phase 6C as a Helio Agent Bus Gateway scaffold proposal only.
- Added master PRD entry for Phase 6A Agent Bus discovery.
- Recorded that no single canonical Supabase Agent Bus PRD was found during Phase 6A.
- Linked the Phase 6A source map and Hermes-to-Helio bus plan.
- Set next required work to Phase 6B: Canonical Agent Bus Contract.

## Source: docs/HERMES_OPERATIONAL_READINESS_REVIEW.md
Character limit: 1200

# Hermes Operational Readiness Review

Phase: 5AK
Status: local-only readiness review

## Purpose

Review Hermes local operating-system readiness before any future credentialed or read-only integration phase.

Phase 5AK is local-only. It does not approve live credentials, live Agent Bus reads/writes, integrations, Hermes Desktop launch, background services, resident operation, or broader Hermes authority.

## Current Proven Capabilities

- Hermes CLI is installed locally and can run in isolated `HERMES_HOME` profiles.
- The managed adapter runner is configured for foreground-only
[...excerpt truncated...]
ows that future recommendation tasks need bounded context embedded in the task file.

The service was stopped immediately afterward. No `8088` listener, adapter, Hermes, Desktop, or resident process remained. No external integration, real credential, Agent Bus read/write, Desktop launch, background service, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred.

Readiness position: the local inbox/outbox path is validated for a single bounded task. The next improvement should be a context-bearing task template, not resident mode or external integrations.

## Source: docs/HERMES_LOCAL_TASK_INBOX.md
Character limit: 1000

# Hermes Local Task Inbox

Phase: 5AW-5AX
Status: local-only task inbox scaffold and first sample task validated

## Purpose

The local task inbox is a file-based handoff mechanism for explicitly approved Hermes tasks. It is local-only and does not connect Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, Desktop, cloud providers, or credentialed integrations.

No external integrations are approved by this scaffold.

Hermes remains a reasoning participant only. Codex and
[...excerpt truncated...]
xt, Hermes did not fabricate a recommendation and returned:

```text
The provided local context does not contain information regarding Hermes phases or their safety levels; therefore, I cannot recommend a next phase.
```

Phase 5AX does not broaden authority. It does not approve additional live tasks, automatic adapter start/stop, resident mode, Desktop launch, credentials, integrations, Agent Bus reads/writes, shell execution by Hermes, or file writes outside the local task outbox.

## Source: docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md
Character limit: 1000

# Hermes Local Validation Checklist

Phase: 5AJ-5AX
Status: local validation checklist, resident design, adapter service validation, manual runbook input, bounded manual-service Hermes validation, bounded local PRD review, local task inbox scaffold, and first inbox task validation

## Purpose

Validate Hermes operating-system readiness using local configuration and documentation checks only. Phase 5AJ operates under the Phase 5AI credential-rotation deferral boundary.

This checkli
[...excerpt truncated...]
t Bus read/write, background service, or authority-broadening action occurred

## Next Gate

After Phase 5AX, the safest next step is either:

- define a context-bearing local inbox task template so future task runs include bounded PRD/changelog context when a recommendation is expected, or
- defer background service work and continue local-only hardening of tests/docs/config examples.

Do not resume live Agent Bus reads/writes or credentialed integrations from this checklist alone.

## Source: docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md
Character limit: 900

# Hermes Adapter Service Runbook

Phase: 5AT-5AU
Status: manual adapter service operating procedure and bounded Hermes validation

## Purpose

Define the approved manual operating procedure for the MSR Model Router Adapter user LaunchAgent.

The adapter service may be started manually when Hermes needs local inference and must be stopped afterward unless a later phase explicitly approves a different policy.

## Current Service Asset
[...excerpt truncated...]
policy changes, and Phase 5AU does not approve:

- `RunAtLoad=true`
- `KeepAlive=true`
- Hermes resident/autonomous mode
- Hermes launchd service
- leaving the adapter service running
- additional Hermes live prompt execution
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud-provider integrations
- real credentials
- Desktop launch
- `~/.hermes` modification
- sudo
- broad filesystem or privacy permission grants
