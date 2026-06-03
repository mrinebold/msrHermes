# Helio Command Center

Helio Command Center is the controlled dispatch and governance layer for the broader MSR/CivicGrantsAI agent team.

Current architecture decision: Hermes is the autonomous Mac mini operator. Helio is not the top-level runtime; Helio is the interface Hermes uses for governed access to DevMonster Gemma4, Google Workspace, GitHub, Home Assistant, the future Supabase task bus, and the 40-agent team.

Current state: scaffold and planning only. Hermes has not been installed, autonomous execution has not been enabled, Google Workspace has not been connected, Home Assistant has not been installed or connected, and no services have been exposed.

## Operating Rules

- Do not delete files.
- Do not modify shell profiles.
- Do not use `sudo` without explicit approval.
- Do not expose services publicly.
- Prefer localhost and Tailscale-only access.
- Log bootstrap and inspection actions to `logs/bootstrap.log`.
- Stop after planning until the next phase is approved.

## Chain Of Command

1. User sets goals and approves sensitive actions.
2. Hermes owns the Mac mini workflow.
3. Helio governs dispatch, model routing, external integrations, audit, and policy.
4. DevMonster, Google Workspace, GitHub, Home Assistant, Supabase, and the 40-agent team sit behind Helio-controlled boundaries.

## Project Layout

- `docs/ARCHITECTURE.md` - canonical Hermes-owned Mac mini and Helio-governed dispatch architecture.
- `docs/HERMES_OWNERSHIP_MODEL.md` - chain of command, permission boundaries, and Phase 5B install proposal.
- `docs/HERMES_INTEGRATION_PLAN.md` - phased Hermes integration roadmap.
- `docs/HERMES_INSTALL_PLAN.md` - Phase 5B Hermes installation readiness plan.
- `docs/HERMES_SECURITY_MODEL.md` - Hermes runtime, credential, command, file, and integration safety model.
- `docs/HERMES_EVALUATION.md` - Phase 5A Hermes capability evaluation.
- `docs/SECURITY_MODEL.md` - permission and access model.
- `docs/ENVIRONMENT_REPORT.md` - machine inspection report.
- `docs/MODEL_ROUTING_POLICY.md` - local-first model routing policy.
- `docs/GOOGLE_WORKSPACE_PLAN.md` - Google Workspace integration plan.
- `docs/HOME_ASSISTANT_PLAN.md` - Home Assistant integration plan.
- `docs/GEMMA_WORKER_PLAN.md` - local Gemma/Ollama worker plan.
- `scripts/check_environment.sh` - approved read-only environment inspection script.
- `scripts/bootstrap_phase_1.sh` - placeholder for approved phase 1 install.
- `scripts/bootstrap_phase_2.sh` - placeholder for approved phase 2 install.
- `config/example.env` - example configuration values.
- `config/hermes.example.env` - Hermes planning env sample with blank placeholders only.
- `logs/bootstrap.log` - local action log, ignored by default if Git is later initialized.

## Hermes Direct Boundary

Hermes may directly:

- inspect approved local project state
- summarize local files and repository structure
- run approved local scripts such as `scripts/check_environment.sh`
- coordinate daily local workflows
- draft plans, proposals, and task requests
- request local-first reasoning through the existing model router

Hermes must not directly:

- delete files
- install packages
- modify shell profiles
- expose public services
- connect Google Workspace
- install or control Home Assistant
- dispatch to the 40-agent team
- write to the future Supabase task bus
- bypass Helio policy for external systems

## Helio-Governed Boundary

Hermes must call Helio for:

- assigning work to one of the 40 MSR/CivicGrantsAI agents
- using the future Supabase task bus
- using DevMonster Gemma4 for governed reasoning
- using Google Workspace after OAuth is approved
- mutating GitHub state
- using Home Assistant after the safety layer exists
- accessing credentials
- executing external writes
- recording approval IDs and audit events

## Proposed Phased Plan

### Phase 0: Inspection and Policy Baseline

Status: complete for the initial bootstrap pass.

- Create project structure.
- Inspect the machine with read-only commands.
- Record findings in `docs/ENVIRONMENT_REPORT.md`.
- Keep bootstrap install scripts disabled until approval.

### Phase 1: Local Developer Foundation

Requires approval before execution.

- Install or configure missing local foundations only after approval.
- Keep all services bound to localhost unless Tailscale-only access is explicitly approved.
- Create a local untracked environment file from `config/example.env`.
- Add local audit logging.

### Phase 2: Permission-Gated Integrations

Requires approval after Phase 1 review.

- Configure Google Workspace OAuth with narrow scopes.
- Configure Home Assistant read-only access first.
- Configure local Gemma worker through Ollama or DevMonster.
- Add explicit approval gates for write actions, external calls, and shell execution.
- Add integration tests and dry-run modes before enabling real actions.

### Phase 5A: Hermes-Owned Mac Mini Architecture

Status: current planning phase.

- Define Hermes as the Mac mini operator.
- Define Helio as the controlled interface to the broader MSR/CivicGrantsAI agent team.
- Document what Hermes may do directly.
- Document what Hermes must route through Helio.
- Document DevMonster, Google Workspace, Home Assistant, and install boundaries.
- Do not install Hermes.
- Do not enable autonomous execution.
- Do not connect Google Workspace.
- Do not install Home Assistant.

### Phase 5B: Hermes Install Readiness Review

Status: current planning phase.

- Identify the official Hermes client, repository, package, and release target.
- Document macOS Apple Silicon install options.
- Document Python, Node, package manager, env, storage, and launch agent requirements.
- Define how Hermes will connect to the local model router, DevMonster Gemma4, Helio dispatcher, Google Workspace, and Home Assistant.
- Define approval gates for shell commands, file edits, Google, Helio dispatch, and Home Assistant.
- Confirm per-user Hermes install path and account.
- Confirm no root-mode or `sudo` install.
- Confirm whether shell path changes are allowed.
- Confirm model provider path through Helio model router and DevMonster Gemma4.
- Define the initial disabled tool list.
- Keep Google Workspace, Home Assistant, GitHub writes, Supabase, and 40-agent dispatch disabled.
- Define rollback steps.
- Do not install Hermes.
- Do not enable autonomous execution.
- Do not connect Google Workspace.
- Do not connect Home Assistant.

### Phase 5C: Hermes Install

Requires approval after Phase 5B review.

- Run the approved install method.
- Record exact Hermes release or commit.
- Configure only the approved model provider path.
- Keep background gateway service disabled unless separately approved.
- Run one safe local validation prompt after install.

## Future Tasks

- Implement a Helio gateway Hermes can call for policy checks, approval requests, audit events, model routing, and agent dispatch.
- Validate Hermes model use through the existing model router and DevMonster Gemma4.
- Build the future Supabase task bus for governed 40-agent dispatch.
- Keep Google Workspace and Home Assistant behind their existing staged safety plans.
