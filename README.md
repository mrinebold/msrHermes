# Helio Command Center

Helio Command Center is intended to become a permission-gated MSR Research supervisor running on this Mac mini.

Current state: scaffold and inspection only. No packages have been installed, no shell profiles have been modified, and no services have been exposed.

## Operating Rules

- Do not delete files.
- Do not modify shell profiles.
- Do not use `sudo` without explicit approval.
- Do not expose services publicly.
- Prefer localhost and Tailscale-only access.
- Log bootstrap and inspection actions to `logs/bootstrap.log`.
- Stop after inspection until the phased install plan is approved.

## Project Layout

- `docs/ARCHITECTURE.md` - proposed system architecture.
- `docs/SECURITY_MODEL.md` - permission and access model.
- `docs/ENVIRONMENT_REPORT.md` - machine inspection report.
- `docs/GOOGLE_WORKSPACE_PLAN.md` - Google Workspace integration plan.
- `docs/HOME_ASSISTANT_PLAN.md` - Home Assistant integration plan.
- `docs/GEMMA_WORKER_PLAN.md` - local Gemma/Ollama worker plan.
- `scripts/check_environment.sh` - read-only environment inspection script.
- `scripts/bootstrap_phase_1.sh` - placeholder for approved phase 1 install.
- `scripts/bootstrap_phase_2.sh` - placeholder for approved phase 2 install.
- `config/example.env` - example configuration values.
- `logs/bootstrap.log` - local action log, ignored by default if Git is later initialized.

## Current Workflow

1. Run `scripts/check_environment.sh`.
2. Review `docs/ENVIRONMENT_REPORT.md`.
3. Review the phased install plan in the docs.
4. Approve the next phase before any installation or privileged action.

## Proposed Phased Install Plan

### Phase 0: Inspection and Policy Baseline

Status: complete for this bootstrap pass.

- Create project structure.
- Inspect the machine with read-only commands.
- Record findings in `docs/ENVIRONMENT_REPORT.md`.
- Keep bootstrap install scripts disabled until approval.

### Phase 1: Local Developer Foundation

Requires approval before execution.

- Initialize Git repository if desired.
- Install or configure missing local foundations: Tailscale, Docker or OrbStack, Ollama, Google Cloud CLI, and current Python tooling.
- Keep all services bound to localhost unless Tailscale-only access is explicitly approved.
- Create a local untracked environment file from `config/example.env`.
- Add a basic local supervisor service skeleton with audit logging.

### Phase 2: Permission-Gated Integrations

Requires approval after Phase 1 review.

- Configure Google Workspace OAuth with narrow scopes.
- Configure Home Assistant read-only access first.
- Configure local Gemma worker through Ollama.
- Add explicit approval gates for write actions, external calls, and shell execution.
- Add integration tests and dry-run modes before enabling real actions.

### Phase 3: Autonomous Supervisor Controls

Requires approval after Phase 2 review.

- Add durable task queue and worker lifecycle management.
- Add policy rules for allowed autonomous actions.
- Add audit review UI or CLI.
- Add health checks, backups, and recovery procedures.
- Consider Tailscale-only remote access after local validation.

## Future Tasks

- Validate Gemma4 connectivity to the DevMonster OpenAI-compatible endpoint over Tailscale.
- Benchmark DevMonster Gemma4 latency, throughput, timeout behavior, and failure modes before enabling autonomous routing.
