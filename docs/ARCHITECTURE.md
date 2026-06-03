# Architecture

## Goal

Helio Command Center coordinates controlled access to the broader MSR/CivicGrantsAI agent team and external integrations while Hermes owns the Mac mini workflow.

Hermes is the primary resident operator on the Mac mini. Helio is not the top-level runtime; Helio is the governed dispatch interface Hermes calls when work needs model routing, external systems, audit controls, or one of the 40 agents.

## Chain Of Command

```text
User
  -> Hermes Agent
    -> Helio Governance Gateway
      -> DevMonster Gemma4
      -> Google Workspace
      -> GitHub
      -> Home Assistant
      -> Supabase task bus
      -> MSR/CivicGrantsAI agent team
```

Responsibilities:

- User: sets goals and approves sensitive actions.
- Hermes: autonomous Mac mini operator for local workflow, project inspection, approved scripts, local planning, and daily coordination.
- Helio: policy, audit, model routing, permissions, dispatch, and future task bus access.
- Agent team: specialized workers reached through Helio, not directly through ad hoc Hermes delegation.

## Proposed Components

- Hermes resident operator: primary local command surface for Mac mini workflow, local project inspection, approved script execution, planning, scheduling, and daily coordination.
- Helio governance gateway: controlled interface for policy checks, approval IDs, audit events, model routing, integration access, and 40-agent dispatch.
- Model router: private/local-first reasoning path, with DevMonster Gemma4 as the approved deep reasoning worker.
- Agent dispatch layer: future controlled registry and task gateway for the broader MSR/CivicGrantsAI agent team.
- Future Supabase task bus: durable task queue for agent assignments, leases, results, retries, and audit references.
- Google Workspace connector: permission-scoped integration for mail, calendar, drive, docs, sheets, and contacts through the existing approval/audit framework.
- GitHub connector: governed read, draft, branch, PR, issue, and CI workflows through narrow scopes and approval gates.
- Home Assistant connector: future LAN or Tailscale-only safety-gated layer for telemetry and approved automations.
- Audit log: append-only local event stream for commands, approvals, rejections, dispatches, integration calls, and worker outputs.
- Secrets store: local untracked files during development, moving to OS keychain or a managed secret store before production use.

## Hermes Direct Boundary

Hermes may directly:

- inspect local project state in approved directories
- summarize repository structure and file contents
- run approved local scripts such as `scripts/check_environment.sh`
- coordinate local daily workflows
- prepare drafts and plans
- call the model router for approved local-first reasoning

Hermes must not directly:

- delete files
- install packages
- modify shell profiles
- expose services publicly
- run unapproved shell writes
- connect Google Workspace
- control Home Assistant
- dispatch to the 40-agent team
- write to the future Supabase task bus
- bypass Helio policy for external systems

## Helio-Governed Boundary

Hermes must route through Helio for:

- assigning work to MSR/CivicGrantsAI agents
- accessing Google Workspace
- mutating GitHub state
- using Home Assistant
- creating or updating future Supabase task bus records
- accessing credentials
- installing or changing runtime services
- sending messages or emails as the user
- running external API writes
- making audit-worthy model routing decisions

Helio should return:

- policy decision
- approval requirement
- approval ID when granted
- scoped execution path
- audit event ID
- result status

## Model Routing Strategy

Hermes uses the existing Helio model router for local-first reasoning through DevMonster Gemma4.

Routing order:

1. DevMonster Gemma4 endpoint on the private Tailscale mesh for approved private deep reasoning.
2. Localhost-only fast model runtime on the Mac mini, if later installed and validated, for command parsing and quick triage.
3. Cloud AI APIs only when explicitly approved and only through a Helio policy gate.

The DevMonster endpoint should remain private and auditable. Hermes should not use DevMonster Gemma4 for autonomous execution decisions, Google Workspace actions, Home Assistant control, or production code edits until separate policy gates approve those uses.

Initial configuration placeholders:

- `GEMMA_BASE_URL`
- `GEMMA_API_KEY`
- `GEMMA_MODEL`
- `GEMMA_TIMEOUT`
- `FAST_LOCAL_MODEL`

## Google Workspace Strategy

Hermes will use Google Workspace only through Helio's permission and audit framework.

Rollout:

1. Read-only Gmail, Calendar, Drive, Docs, Sheets, and People/Contacts validation.
2. Draft-only Gmail, Calendar, Docs, Sheets, Drive, and contact proposal workflows.
3. Human-approved execution with approval IDs and audit events.

No Google authentication, API calls, sends, edits, shares, or deletes are enabled in Phase 5A.

## Home Assistant Strategy

Hermes will use Home Assistant only through a future safety-gated Helio tool layer.

Rollout:

1. Confirm LAN or Tailscale-only access.
2. Add read-only telemetry.
3. Define domain and entity allowlists.
4. Require human approval for service calls.
5. Treat locks, alarms, garage doors, HVAC, appliances, power, and security systems as high risk.

No Home Assistant install, token creation, or connection is enabled in Phase 5A.

## Default Network Posture

- Bind local services to `127.0.0.1` by default.
- Permit remote access only through Tailscale when explicitly approved.
- Do not expose inbound services to the public internet.
- Do not give Hermes public-facing service authority during initial install.

## Bootstrap Boundary

Phase 5A is architecture planning only.

Do not:

- install Hermes
- enable autonomous execution
- connect Google Workspace
- install or connect Home Assistant
- create new credentials
- dispatch work to the 40-agent team
- modify runtime services

Installation and service configuration are deferred until Phase 5B approval.
