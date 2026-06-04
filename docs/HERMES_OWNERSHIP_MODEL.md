# Hermes Ownership Model

Planning date: 2026-06-03.

Phase 5A is planning only. Hermes has not been installed. Autonomous execution, Google Workspace access, and Home Assistant access remain disabled.

## Architecture Decision

Hermes is the autonomous Mac mini operator.

Helio is not the top-level runtime. Helio is the controlled dispatch and governance layer Hermes uses when work should leave the Mac mini workflow and move into the broader MSR/CivicGrantsAI agent team or an external integration.

## Chain Of Command

1. User sets goals and approves sensitive actions.
2. Hermes owns the Mac mini workflow and coordinates daily local work.
3. Helio governs access to external systems and the broader MSR/CivicGrantsAI agent team.
4. The model router provides local-first reasoning through DevMonster Gemma4 when Hermes needs governed model work.
5. Google Workspace, GitHub, Home Assistant, Supabase, and the 40-agent team remain behind Helio policy gates.

In short:

```text
User
  -> Hermes, resident Mac mini operator
    -> Helio, governed dispatch interface
      -> DevMonster, Google Workspace, GitHub, Home Assistant, Supabase, 40 agents
```

## Machine-Boundary Gating vs ANO Governance

Hermes is gated because Hermes is the resident Mac mini operator. Its approval gates protect the human, the local machine, local files, local services, secrets, and external systems.

The broader ANO agent society is not governed by Hermes. Helio/ANO coordinates and governs the agent society through ANO governance rules, roles, permissions, consensus/workflow rules, and each agent's policy framework.

Hermes may request work from Helio/ANO, but it does not own, command, or subordinate the ANO agents. When Hermes asks for specialist work, it is crossing from the Mac mini boundary into the agent society; Helio/ANO decides how that work is routed, approved, refused, decomposed, or handled by agents.

Hermes-specific gates apply to boundary-crossing actions:

- shell
- file edits
- secrets
- local services
- Google Workspace
- Home Assistant
- Supabase writes
- external communication

Those gates do not restrict the internal freedom of the ANO agent society. They restrict Hermes' ability to affect the Mac mini, the human's accounts, external systems, and durable shared state.

## Permission Boundaries

Hermes owns local workflow coordination, but ownership does not mean unrestricted execution.

Hermes may work directly inside the local low-risk boundary. It must route through Helio when work touches external authority, the agent fleet, credentials, physical-world systems, or durable shared state.

Helio owns:

- policy checks
- approval records
- audit logging
- agent dispatch
- integration scope limits
- model routing policy
- future Supabase task bus access

Hermes owns:

- local task coordination
- project inspection
- local workflow management
- conversation and planning surface
- daily work orchestration
- handoff requests into Helio

## What Hermes May Do Directly

Hermes may directly:

- inspect local project state in approved project directories
- summarize local files and repository structure
- run approved read-only scripts, including `scripts/check_environment.sh`
- run future approved local workflow scripts listed by Helio policy
- maintain local task notes and planning context
- coordinate daily work on the Mac mini
- draft plans, proposals, messages, issues, PR descriptions, and task requests
- call the model router for approved local-first reasoning

Hermes may not treat local direct access as permission to delete files, install packages, modify shell profiles, expose network services, or execute arbitrary shell actions.

## What Hermes Must Route Through Helio

Hermes must route these through Helio:

- assigning work to any of the 40 MSR/CivicGrantsAI agents
- creating, leasing, updating, or completing future Supabase task bus records
- Google Workspace reads after OAuth is enabled
- Google Workspace drafts, sends, edits, shares, or deletes
- GitHub writes such as pushes, PR creation, PR updates, issue mutations, and merges
- Home Assistant reads or actions after the safety layer exists
- DevMonster Gemma4 reasoning for governed or audit-worthy tasks
- credential access, credential creation, or credential rotation
- package installation or runtime configuration changes
- any external API write

## What Requires Human Approval

Human approval is required before:

- installing Hermes
- enabling autonomous execution
- enabling shell write automation
- installing packages or modifying system configuration
- exposing any service beyond localhost
- connecting Google Workspace
- sending email or messages as the user
- creating, updating, deleting, moving, or sharing Google resources
- connecting Home Assistant
- running Home Assistant service calls
- modifying locks, alarms, garage doors, HVAC, appliances, power, or security-related entities
- giving Hermes direct credentials for GitHub, Google, Home Assistant, Supabase, or the 40-agent team
- dispatching work to an agent with external side effects
- deleting files
- editing production code without review
- enabling cloud model providers

Every approved action should carry an approval ID and audit event.

## DevMonster Gemma4 Use

Hermes should use the existing Helio model router for local-first reasoning through DevMonster Gemma4.

Approved direction:

- DevMonster Gemma4 remains the private deep reasoning worker.
- Hermes uses it for planning, summarization, PRD drafting, internal reasoning, and low-risk agent reasoning.
- The model router records provider, model, task type, elapsed time, and approval requirement.
- Cloud providers remain fail-closed until explicitly approved.
- DevMonster Gemma4 is not approved for autonomous execution decisions, Google actions, Home Assistant control, or production code edits without policy gates.

Hermes may later use a faster local model for command parsing and triage, but that model must be installed and validated in a separate approved phase.

## Future Google Workspace Use

Hermes will use Google Workspace only through the existing permission and audit framework.

Planned progression:

1. Read-only validation for Gmail, Calendar, Drive, Docs, Sheets, and People/Contacts.
2. Draft-only workflows for email, calendar proposals, Docs/Sheets changes, and Drive organization.
3. Human-approved execution after audit logging and approval IDs are working.

Hermes may draft Google actions before execution is enabled. It may not authenticate, read, send, edit, share, or delete Google resources during Phase 5A.

## Future Home Assistant Use

Hermes will use Home Assistant only through a future safety-gated Helio tool layer.

Planned progression:

1. Confirm LAN or Tailscale-only Home Assistant access.
2. Add read-only telemetry.
3. Build domain and entity allowlists.
4. Add approval-gated service calls.
5. Audit every Home Assistant read, proposal, and service call.

No Home Assistant install, token creation, or service call is allowed during Phase 5A.

## Installation Prerequisites

Current Hermes installation requirements from official Hermes documentation:

- Linux, macOS, WSL2, and Termux use the official shell installer.
- Native Windows uses an early-beta PowerShell installer.
- The standard installer provisions `uv`, Python 3.11, Node.js 22, `ripgrep`, `ffmpeg`, Git where needed, the Hermes source checkout, a Python virtual environment, and the global `hermes` command.
- The per-user install layout places code under `~/.hermes/hermes-agent/`, data and config under `~/.hermes/`, and the command symlink under `~/.local/bin/hermes`.
- Hermes requires at least one model provider or custom endpoint before it can operate usefully.

Phase 5A does not run the installer.

References:

- https://hermes-agent.nousresearch.com/docs/getting-started/installation/
- https://hermes-agent.nousresearch.com/docs/integrations/providers/
- https://github.com/NousResearch/hermes-agent

## Phase 5B Install Proposal

Phase 5B should be an install readiness review, not an immediate authority grant.

Proposed Phase 5B steps:

1. Confirm Hermes per-user install under the current Mac mini user account.
2. Confirm no `sudo` install path unless separately approved.
3. Confirm whether the installer may add `hermes` to the user path.
4. Confirm model provider setup through Helio model router or a constrained DevMonster custom endpoint.
5. Define which Hermes tools are enabled at first launch.
6. Keep Google Workspace, GitHub writes, Home Assistant, Supabase, and fleet dispatch credentials disabled.
7. Create a Helio gateway design for policy checks, approval requests, and audit events.
8. Define a rollback/removal plan for `~/.hermes/` and any shell path changes.
9. Run only safe local validation after install.

Phase 5B should still not enable autonomous execution, Google Workspace, or Home Assistant.

## Phase 5A Stop Conditions

Stop after documenting and committing this architecture.

Do not:

- install Hermes
- enable autonomous execution
- connect Google Workspace
- install or connect Home Assistant
- create new credentials
- dispatch tasks to the 40-agent team
- modify runtime services
