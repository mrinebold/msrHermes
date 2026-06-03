# Hermes Integration Plan

Planning date: 2026-06-03.

Phase 5A is planning only. Do not install Hermes, enable autonomous execution, connect Google Workspace, or install Home Assistant in this phase.

## Target Architecture

Hermes is the autonomous Mac mini operator. Helio is the controlled dispatch layer that gives Hermes governed access to the broader MSR/CivicGrantsAI agent team, model router, and external integrations.

```text
User
  |
  v
Hermes Agent
  - Mac mini workflow owner
  - local project inspection
  - approved local scripts
  - daily coordination
  - planning and drafting
  |
  v
Helio Governance Gateway
  - policy checks
  - approval IDs
  - audit logging
  - model router access
  - integration permissions
  - 40-agent dispatch
  - future Supabase task bus
  |
  +--> DevMonster Gemma4
  +--> Google Workspace
  +--> GitHub
  +--> Home Assistant safety layer
  +--> Supabase task bus
  +--> MSR/CivicGrantsAI agent team
```

## Design Principles

- Hermes owns the Mac mini workflow.
- Helio is not the top-level runtime.
- Helio owns dispatch and governance outside the local low-risk boundary.
- Hermes may inspect local project state, run approved scripts, manage local workflows, and coordinate daily work.
- Hermes calls Helio when work should be assigned to one of the 40 agents.
- Hermes uses the existing model router for local-first reasoning through DevMonster Gemma4.
- Hermes uses Google Workspace tools only through the existing permission and audit framework.
- Hermes uses Home Assistant only through a future safety-gated tool layer.
- Human approval remains required for sensitive actions.

## Permission Boundaries

| Area | Hermes direct | Helio mediated | Human approval |
| --- | --- | --- | --- |
| Local project inspection | Yes, in approved directories | Optional | No, unless secrets or private data are involved |
| Approved scripts | Yes, for allowlisted scripts | Policy defines allowlist | Required to add new write-capable scripts |
| Local workflow coordination | Yes | Optional | No for planning and status work |
| Shell writes | No by default | Yes | Yes |
| Package installation | No | Yes | Yes |
| Public service exposure | No | Yes | Yes |
| DevMonster Gemma4 | Through model router | Yes | Required for new autonomous categories |
| Google Workspace | No direct access | Yes | Yes for auth and all writes |
| GitHub reads | Limited after approval | Yes | Depends on token scope |
| GitHub writes | No direct access | Yes | Yes |
| Home Assistant | No direct access | Yes, future safety layer | Yes for token and service calls |
| Supabase task bus | No raw DB writes | Yes | Yes for schema/credential changes |
| 40-agent dispatch | No direct fanout | Yes | Required for high-risk or external-side-effect work |

## What Hermes May Do Directly

Hermes may directly:

- inspect approved local project directories
- summarize local repo state
- read local planning and architecture docs
- run `scripts/check_environment.sh`
- run future approved local workflow scripts
- manage local daily work queues and planning notes
- draft task requests for Helio
- draft Google, GitHub, and Home Assistant proposals without executing them
- call Helio's model router for approved local-first reasoning

## What Hermes Must Route Through Helio

Hermes must route through Helio for:

- selecting and dispatching one of the 40 MSR/CivicGrantsAI agents
- creating future Supabase task bus records
- updating task leases or results
- using DevMonster Gemma4 for governed model tasks
- reading or writing Google Workspace after OAuth is enabled
- mutating GitHub state
- reading Home Assistant telemetry or calling services
- accessing credentials or tokens
- executing external API writes
- changing runtime configuration

## What Requires Human Approval

Human approval is required for:

- Hermes installation
- autonomous execution enablement
- adding new approved scripts
- shell writes outside narrow approved scripts
- package installs
- `sudo`
- shell profile changes
- public network exposure
- Google OAuth connection
- Google sends, edits, shares, deletes, or calendar changes
- GitHub pushes, PR creation, issue mutation, merge, or destructive operations
- Home Assistant token creation or service calls
- Supabase credentials or schema changes
- assigning high-risk work to any agent
- deleting files
- enabling cloud model providers

## DevMonster Gemma4 Integration

Hermes should use DevMonster Gemma4 through the existing Helio model router.

Current policy:

- DevMonster Gemma4 is the private deep reasoning worker.
- Approved uses include private brainstorming, summarization, PRD drafting, internal planning, and low-risk agent reasoning.
- Not approved uses include autonomous execution decisions, email sending, Google Workspace actions, Home Assistant control, and production code edits without review.
- The model router should record task type, provider, model, timestamp, elapsed time, and approval requirement.

Implementation direction:

- Hermes sends governed reasoning requests to Helio.
- Helio routes to DevMonster Gemma4 when policy allows.
- Helio fails closed for cloud-reserved work until cloud providers are approved.
- A faster local model may later be installed for classification and command parsing.

## Future Google Workspace Integration

Hermes will use Google Workspace only through Helio's existing permission and audit framework.

Planned progression:

1. Read-only Gmail, Calendar, Drive, Docs, Sheets, and Contacts/People validation.
2. Draft-only Gmail, Calendar, Docs, Sheets, Drive, and contact proposals.
3. Human-approved execution with approval IDs and audit events.

Hermes may draft proposed Google actions in Phase 5 planning, but it may not authenticate, read, send, edit, share, or delete Google resources yet.

## Future Home Assistant Integration

Hermes will use Home Assistant only through a future Helio safety-gated tool layer.

Planned progression:

1. Confirm Home Assistant URL and LAN or Tailscale-only access.
2. Add read-only telemetry.
3. Define safe entity/domain allowlists.
4. Add proposal rendering for service calls.
5. Require human approval for service calls.
6. Audit every service call and automation trigger.

Locks, alarms, garage doors, HVAC, appliances, power controls, and security devices remain high risk.

## Installation Prerequisites

Current Hermes installation requirements from official Hermes documentation:

- Linux, macOS, WSL2, and Termux can use the official shell installer.
- Native Windows can use the early-beta PowerShell installer.
- Developer setup can clone the repository and run `setup-hermes.sh`, or install with Python 3.11 and `uv`.
- The standard installer provisions `uv`, Python 3.11, Node.js 22, `ripgrep`, `ffmpeg`, Git where needed, a Hermes source checkout, a virtual environment, and a global `hermes` command.
- Per-user layout uses `~/.hermes/hermes-agent/` for code, `~/.hermes/` for data and config, and `~/.local/bin/hermes` for the command symlink.
- Hermes needs a model provider or custom endpoint before meaningful operation.

References:

- https://hermes-agent.nousresearch.com/docs/getting-started/installation/
- https://hermes-agent.nousresearch.com/docs/integrations/providers/
- https://github.com/NousResearch/hermes-agent

## Phase 5B Install Proposal

Phase 5B should approve installation readiness before any install command runs.

Proposed Phase 5B checklist:

1. Confirm per-user install path and user account.
2. Confirm no root-mode or `sudo` install.
3. Confirm whether the installer may modify shell startup files or create the `~/.local/bin/hermes` symlink.
4. Confirm model setup path: Helio model router first, DevMonster custom endpoint only if constrained, cloud disabled.
5. Define the initial disabled tool list.
6. Keep Google Workspace credentials disabled.
7. Keep Home Assistant token disabled.
8. Keep GitHub write tokens disabled.
9. Keep Supabase credentials disabled.
10. Keep 40-agent dispatch disabled until the Helio gateway exists.
11. Define Helio policy/audit tools Hermes can call after install.
12. Define rollback steps for `~/.hermes/`, path changes, and any generated config.
13. Run one safe local validation prompt after install.

Phase 5B should still not enable autonomous execution.

## Future Helio Gateway Tools

Candidate tools for Hermes to call:

- `helio_policy_check`
- `helio_request_approval`
- `helio_audit_event`
- `helio_model_route`
- `helio_agent_list`
- `helio_task_draft`
- `helio_task_submit`
- `helio_google_propose`
- `helio_github_propose`
- `helio_homeassistant_propose`

The first implementation should expose read-only status and dry-run proposal tools before execution tools.

## Stop Conditions

Stop Phase 5A after documentation and commit.

Do not:

- install Hermes
- enable autonomous execution
- connect Google Workspace
- install or connect Home Assistant
- create credentials
- expose services publicly
- dispatch work to the 40-agent team
- modify runtime services
