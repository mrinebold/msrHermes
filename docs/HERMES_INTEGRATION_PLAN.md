# Hermes Integration Plan

Planning date: 2026-06-03.

Phase 5A is planning only. Do not install Hermes in this phase.

## Target Architecture

Hermes should be the resident operator for the Mac mini. Helio should be the governed access plane that Hermes uses to reach external systems, model workers, and the 40-agent fleet.

```text
User
  |
  v
Hermes Agent
  - local machine owner
  - conversation surface
  - memory and skills
  - scheduler and local execution
  |
  v
Helio Governance Gateway
  - policy checks
  - approval IDs
  - audit logging
  - capability grants
  - model routing policy
  - task bus API
  |
  +--> DevMonster Gemma4
  +--> Google Workspace
  +--> GitHub
  +--> Home Assistant
  +--> Supabase task bus
  +--> 40-agent fleet
```

## Design Principles

- Hermes owns this Mac mini's day-to-day operation.
- Helio owns governance for anything outside the local low-risk machine boundary.
- Hermes may plan, draft, summarize, and propose freely.
- Hermes must request Helio approval for writes, sends, service calls, code changes, physical-world actions, credential changes, package installs, and agent-fleet dispatch.
- Helio records the durable audit trail even when Hermes performs the final action.
- Direct Hermes credentials should be minimized; prefer Helio-issued scoped credentials or Helio MCP/API gateways.
- No public service exposure. Prefer localhost first and Tailscale-only access after approval.

## Proposed Components

### Hermes Local Operator

Responsibilities:

- Provide the primary command surface.
- Maintain local memory and skills.
- Run approved local tasks.
- Schedule reminders and recurring jobs.
- Draft Google/GitHub/Home Assistant actions for approval.
- Submit external or fleet tasks through Helio.

Boundaries:

- No unrestricted shell autonomy.
- No direct broad Home Assistant control.
- No direct broad Google Workspace write access.
- No direct all-agent fleet control.
- No public listener unless separately approved.

### Helio Governance Gateway

Responsibilities:

- Enforce policy for external access.
- Attach approval IDs to sensitive actions.
- Write audit events.
- Maintain integration-specific allowlists.
- Broker credentials.
- Translate Hermes requests into governed tool calls.
- Expose the 40-agent fleet as governed capabilities.

Initial interface options:

- Local HTTP API on `127.0.0.1`.
- Stdio MCP server exposed to Hermes.
- Future HTTP MCP server over Tailscale for remote agents.

Recommended first interface: stdio MCP server or localhost HTTP API with an MCP adapter. This lets Hermes discover Helio capabilities while Helio controls the exposed tool list.

### Agent Fleet Gateway

Responsibilities:

- Maintain the 40-agent registry.
- Describe each agent's capabilities, owner, risk tier, and current availability.
- Accept tasks from Hermes only through Helio policy.
- Assign task leases through the future Supabase task bus.
- Return status, artifacts, and audit references.

Required concepts:

- `agent_id`
- `capability`
- `risk_tier`
- `allowed_actions`
- `approval_required`
- `task_id`
- `lease_owner`
- `deadline`
- `result_status`
- `audit_event_id`

## Integration Phases

### Phase 5A: Evaluation and Planning

Status: current phase.

- Research current Hermes requirements.
- Document capability overlap and gaps.
- Define machine-owner architecture.
- Do not install Hermes.
- Do not create Hermes config.
- Do not authenticate providers.
- Do not connect tools.

### Phase 5B: Install Readiness Review

Requires approval.

- Choose install account and path.
- Confirm `~/.hermes/` data location.
- Confirm whether the global `hermes` command should be added to the shell path.
- Decide whether Hermes may use DevMonster directly or only through Helio.
- Decide first model provider and fallback model.
- Decide which built-in Hermes tools are disabled by default.
- Decide which Helio gateway interface to expose first.
- Confirm backup plan for Hermes config, sessions, and memory.

No install should occur until this review is complete.

### Phase 5C: Local Hermes Install, No External Authority

Requires approval after Phase 5B.

- Install Hermes per-user only.
- Keep services local.
- Configure a local model path suitable for low-risk chat and planning.
- Disable or withhold credentials for Google Workspace, GitHub, Home Assistant, and agent fleet writes.
- Verify Hermes starts and can perform local low-risk conversation.
- Record install actions in Helio logs.

Allowed:

- Local chat.
- Local planning.
- Low-risk file reads in approved directories.

Not allowed:

- Google authentication.
- Home Assistant token setup.
- GitHub token setup.
- Shell write automation.
- Fleet dispatch.

### Phase 5D: Helio Gateway Prototype

Requires approval.

- Create a minimal Helio MCP or localhost API gateway.
- Expose read-only policy and status tools first.
- Add a `request_approval` proposal path.
- Add audit event writing.
- Add dry-run integration calls.

Candidate initial tools:

- `helio_policy_check`
- `helio_request_approval`
- `helio_audit_event`
- `helio_model_route`
- `helio_agent_list`
- `helio_task_draft`

The first version should not execute external writes.

### Phase 5E: Model Routing Integration

Requires approval.

- Point Hermes governed model calls at Helio's model router.
- Preserve private-first routing.
- Use DevMonster Gemma4 for deliberate planning and long reasoning.
- Add or validate a faster local model for command parsing and routing if needed.
- Keep cloud providers fail-closed unless explicitly approved.

Recommended routing:

- Hermes local lightweight model: quick local conversation, classification, command parsing.
- Helio model router: governed task reasoning and audit-worthy decisions.
- DevMonster Gemma4: deeper private reasoning through Helio policy.
- Cloud providers: reserved and disabled until explicitly approved.

### Phase 5F: Google Workspace Through Helio

Requires approval.

- Start with read-only Google scopes.
- Let Hermes draft actions, not execute them.
- Route OAuth state, token storage, and audit logging through Helio's Google security model.
- Add Gmail/Calendar/Drive/Docs/Sheets writes only after approval gates exist.

Hermes may use its bundled Google Workspace skill as an execution backend only if Helio can constrain scopes, log actions, and require approval for writes.

### Phase 5G: GitHub Through Helio

Requires approval.

- Expose GitHub read tools first.
- Add branch/commit/PR draft workflows second.
- Require explicit approval before pushes, PR creation, PR updates, issue mutations, merges, or CI-affecting actions.
- Prefer a filtered GitHub MCP server or Helio GitHub gateway over broad token exposure.

### Phase 5H: Home Assistant Through Helio

Requires approval.

- Start with read-only telemetry.
- Build domain/entity allowlists before service calls.
- Require approval for all physical-world actions.
- Treat locks, alarms, garage doors, HVAC, appliances, power controls, and security devices as high risk.
- Keep Home Assistant reachable only over LAN or Tailscale.

Do not give Hermes a broad long-lived Home Assistant token until Helio can enforce allowlists and audit every service call.

### Phase 5I: Supabase Task Bus and 40-Agent Fleet

Requires approval.

- Build the Supabase task bus as Helio infrastructure.
- Represent the 40 agents as governed workers.
- Let Hermes submit tasks into Helio with requested capabilities.
- Let Helio choose agents, issue leases, and enforce policy.
- Return agent results to Hermes with audit references.

Minimum task bus fields:

- `task_id`
- `requested_by`
- `requested_capability`
- `risk_tier`
- `approval_id`
- `status`
- `assigned_agent_id`
- `lease_expires_at`
- `input_ref`
- `output_ref`
- `audit_event_id`

## Capability Exposure Plan

| Capability | Hermes direct access | Helio-mediated access | Notes |
| --- | --- | --- | --- |
| Local low-risk chat | Yes | Optional | Hermes should feel resident and responsive. |
| Local file reads | Limited | Yes | Scope to approved project roots. |
| Local shell writes | No by default | Yes, with approval | Preserve current Helio operating rules. |
| DevMonster Gemma4 | Limited | Preferred | Keep routing auditable. |
| Google read | No until Phase 5F | Yes | Start read-only. |
| Google write/send | No | Yes, with approval | Draft first, execute later. |
| GitHub read | Limited | Yes | Prefer filtered MCP or gateway. |
| GitHub write | No | Yes, with approval | Token scope must stay narrow. |
| Home Assistant read | No until Phase 5H | Yes | Read-only telemetry first. |
| Home Assistant action | No | Yes, with approval | Physical-world gate required. |
| Supabase task bus | No raw DB writes | Yes | Helio owns queue semantics. |
| 40-agent dispatch | No direct fanout | Yes | Helio owns registry and capability grants. |

## Governance Rules Hermes Must Respect

Hermes may not bypass Helio for:

- External writes.
- Sending email or messages as the user.
- Calendar creation, update, or deletion.
- Drive, Docs, or Sheets modification.
- GitHub pushes, PRs, issue changes, merges, or destructive operations.
- Home Assistant service calls.
- Package installation.
- Credential creation, rotation, or storage.
- Public network exposure.
- File deletion.
- Agent fleet dispatch.
- Supabase task bus writes.

Each governed action should include:

- proposed action
- target system
- risk tier
- expected side effects
- required credential or scope
- human approval ID if required
- audit event ID
- result status

## Open Questions

- Which account should run Hermes on this Mac mini?
- Should Hermes use DevMonster directly for local chat or only through Helio?
- Which fast local model should handle quick command parsing?
- Should Helio expose itself to Hermes as MCP, localhost HTTP, or both?
- What are the names and capability tiers of the 40 agents?
- Which agents are allowed to receive autonomous tasks?
- Which Google account should be authorized first?
- Which Home Assistant entities are safe for read-only telemetry?
- Where should Hermes memory/session backups live?

## Acceptance Criteria For Future Install Approval

Before installing Hermes, the Phase 5B review should approve:

- Install path and user account.
- No-`sudo` per-user install unless explicitly changed.
- Model provider plan.
- Tool enablement plan.
- Helio gateway interface.
- Credential storage plan.
- Audit event plan.
- Rollback/removal plan.
- Initial disabled tool list.
- First safe validation prompt.

## Recommendation

Proceed toward Hermes as the machine owner, not merely as a subordinate tool.

Keep Helio as the governance layer that gives Hermes safe access to the rest of the system:

- Hermes owns the Mac mini.
- Helio owns external authority.
- The 40 agents live behind Helio's registry, policy, and future Supabase task bus.
- High-risk integrations stay fail-closed until explicit approval gates are implemented.

This preserves Hermes' strengths while keeping Helio's purpose sharp: governance, auditability, and safe delegation across a much larger agent network.
