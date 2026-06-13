# Hermes Resident Authority Model

Phase: 6A
Status: proposal only; resident mode not enabled yet; audit, emergency stop, resident service, delegation, command policy, and file zone models proposed

## Purpose

This proposal defines how Hermes could eventually become Michael's resident personal agent on the Mac mini.

This phase does not enable resident mode. It does not create a Hermes launchd service, set `RunAtLoad=true`, set `KeepAlive=true`, start the adapter service, run Hermes live, connect external integrations, use credentials, perform Agent Bus reads/writes, launch Desktop, modify `~/.hermes`, or broaden Hermes authority in code.

external integrations remain frozen until approved by a later phase.

## Strategic Objective

Hermes should eventually help operate the Mac mini as a supervised personal agent. It may monitor approved local task inputs, summarize local project state, recommend next actions, prepare draft commands and plans, coordinate with Helio/ANO under defined boundaries, and later use approved Google, Supabase/Agent Bus, GitHub, and Home Assistant capabilities through explicit phased gates.

The core rule is progressive trust: Hermes gains authority by tier, with human approval, audit logs, rollback paths, emergency stop, and scoped allowlists.

## Authority Tiers

### Tier 0: Observe Only

Allowed:

- read explicitly approved local status files
- inspect `sandbox/hermes_inbox/`, `sandbox/hermes_outbox/`, and approved local status artifacts
- inspect repo status through read-only commands
- read metadata-only adapter and status outputs

Not allowed:

- writes except logs/metrics if explicitly approved
- shell actions that change state
- file edits
- network integrations
- credentials
- Desktop launch

### Tier 1: Recommend

Allowed:

- read bounded approved context
- produce recommendations, summaries, and plans
- write advisory output only to `sandbox/hermes_outbox/`

Not allowed:

- shell execution
- file edits outside `sandbox/hermes_outbox/`
- external reads or writes
- sending messages
- credential access

### Tier 2: Draft

Allowed:

- prepare scripts, commands, patches, emails, or implementation plans
- write drafts only to approved draft locations
- label every draft as not executed and not sent

Not allowed:

- execution
- sending
- applying patches
- commits
- external writes
- credential use

### Tier 3: Local Approved Execution

Allowed:

- execute approved local commands only after explicit human approval
- operate only inside a repo/workspace allowlist
- create audited local changes with rollback notes
- use command allowlists and denylist enforcement

Not allowed:

- secrets unless separately approved
- unbounded filesystem access
- destructive commands without explicit approval and rollback
- background services unless separately approved
- external integrations

### Tier 4: External Read-Only

Allowed:

- Google, Supabase, GitHub, and Home Assistant read-only connectors only after separate approval
- scoped reads with least privilege
- metadata and content reads only within approved scopes

Not allowed:

- writes
- sends
- commits
- service calls
- credentials printed to logs or output
- broad OAuth/API scopes

### Tier 5: External Draft/Propose

Allowed:

- create draft emails, proposed GitHub changes, proposed Supabase writes, proposed Home Assistant actions, or Helio/ANO task requests
- store drafts in approved draft locations
- require human review before action

Not allowed:

- send, commit, apply, dispatch, write, or control without approval
- persistent background action
- credential disclosure

### Tier 6: External Approved Action

Allowed:

- send, apply, write, commit, dispatch, or control only after explicit human approval
- operate within a narrow approved scope
- produce audit records with approval IDs and rollback notes

Not allowed:

- uncontrolled autonomy
- broad scopes
- silent retries that change state
- credential printing
- action outside the approved target

### Tier 7: Resident Delegated Operator

Allowed:

- run selected recurring or local tasks without per-task approval only after a dedicated resident-mode approval phase
- operate under allowlists, rate limits, audit logs, health checks, and emergency stop
- monitor approved local inboxes and status files
- escalate boundary-crossing work to the human

Not allowed:

- uncontrolled autonomy
- self-expanding authority
- new integrations without approval
- Desktop launch unless separately approved
- secret access outside approved credential paths
- destructive action without a policy and rollback path

## Human Approval Rules

- Every tier escalation requires explicit human approval.
- Each approval must name the authority tier, target, duration, allowed actions, denied actions, rollback, and audit evidence.
- Approval for one tier or target does not transfer to another tier or target.
- Any write, send, commit, service control, credential use, or external action requires a phase-specific approval until Tier 7 is separately approved.
- Ambiguous authority defaults to denied.

## Audit Log Requirements

Audit logs must exist before any Tier 3 or higher authority is enabled.

Phase 6B defines the proposed audit log model in `docs/HERMES_AUDIT_LOG_DESIGN.md`.

Minimum fields:

- timestamp
- authority tier
- actor: Hermes, Codex, human, or service
- human approval reference
- requested action
- approved target
- command or connector name, with secrets redacted
- files changed or external object touched
- outcome
- rollback path
- errors and refusal reason

Audit logs must not include prompt text, file contents, model output, API keys, OAuth tokens, Supabase keys, GitHub tokens, Home Assistant tokens, Helio credentials, or private message bodies unless a later phase explicitly approves a narrower audit content policy.

## Emergency Stop Requirements

Resident mode cannot be enabled until an emergency stop exists.

Phase 6C defines the proposed emergency stop model in `docs/HERMES_EMERGENCY_STOP_DESIGN.md`.

Minimum emergency stop controls:

- stop Hermes resident process
- stop adapter service
- unload LaunchAgent or LaunchDaemon entries that are in scope
- disable recurring task ingestion
- disable external connectors
- revoke or quarantine active credentials if needed
- confirm no `8088` listener remains
- confirm no Hermes/Desktop/resident process remains
- document final stopped state

Emergency stop must be usable without sudo unless a later phase explicitly approves an administrative service.

## Allowed File Zones

Initial allowed zones:

- `sandbox/hermes_inbox/`
- `sandbox/hermes_outbox/`
- `sandbox/hermes_archive/`
- approved draft directories created by a future phase
- metadata-only logs under approved Hermes/adapter log paths
- repo files only when a Tier 3+ phase explicitly approves local execution or file edits

Phase 6G defines the detailed file zone policy in `docs/HERMES_FILE_ZONE_POLICY.md`.

## Forbidden File Zones

Forbidden without separate approval:

- `~/.hermes/` modifications
- shell profile files
- SSH directories and keys
- cloud credential files
- browser profile data
- macOS Keychain data
- `~/Library/LaunchAgents/` and launchd files for Hermes
- system directories
- Desktop app bundle contents
- Google, Supabase, GitHub, Home Assistant, and Helio credential stores
- arbitrary files outside an approved workspace allowlist

## Command Allowlist Concept

Tier 0 and Tier 1 may use no state-changing commands.

Future allowlists should define:

- exact command path
- exact arguments or argument patterns
- working directory
- environment variables
- expected side effects
- timeout
- output redaction
- rollback or cleanup

Phase 6F defines the proposed command allowlist and denylist in `docs/HERMES_COMMAND_POLICY.md`.

Examples of future candidate read-only commands:

- `git status --short`
- `git rev-parse --abbrev-ref HEAD`
- `scripts/hermes_local_status.sh`
- `scripts/adapter_service_status.sh`

## Command Denylist Concept

The denylist must block commands that are destructive, privilege-escalating, credential-exposing, or externally mutating unless a later phase creates a narrowly approved exception.

Always-denied by default:

- `sudo`
- `rm -rf`
- `launchctl bootstrap`, `launchctl kickstart`, or `launchctl bootout` for Hermes services without approval
- `chmod` or `chown` on credential or system paths
- commands that print environment values wholesale
- credential store reads
- external write CLIs
- Desktop launch commands
- network tunnels or public listeners
- package installs

## Credential Handling Model

- Hermes must never print secret values.
- Credential names may be reported only by name, not value.
- Real credentials remain frozen until a credential-specific phase approves rotation, storage, scope, and use.
- Dummy local adapter keys remain acceptable only for localhost syntax.
- External connector credentials require least-privilege scopes, redaction, audit, and revocation procedure.
- Service-role credentials are not approved for resident Hermes.

## Network Access Model

Current approved network path:

```text
Hermes CLI -> http://127.0.0.1:8088/v1 -> adapter -> DevMonster Gemma worker
```

Rules:

- adapter must bind only to `127.0.0.1:8088`
- no `0.0.0.0`, LAN, public, or Tailscale adapter listener
- DevMonster remains the inference worker, not an operator
- cloud providers remain disabled
- Google, Supabase, GitHub, Home Assistant, Helio, and Agent Bus network access remain frozen until approved

## Process And Service Management Model

Current state:

- adapter LaunchAgent is installed but manual start/stop only
- `RunAtLoad=false`
- `KeepAlive=false`
- Hermes resident process is not approved
- Hermes launchd service is not approved

Future service management must distinguish:

- adapter service: local inference endpoint only
- Hermes resident service: personal agent process with authority tiers
- Desktop app: separate and currently fail-closed

## Hermes-To-Helio Delegation Boundary

Hermes is Michael's Mac mini personal agent. Helio/ANO is the governed agent coordination layer.

Hermes may eventually request work from Helio/ANO through an approved interface, but Hermes does not own, command, or bypass Helio/ANO governance. Other ANO agents are not subordinate to Hermes. Hermes must respect Helio/ANO approval, routing, quality, and audit rules.

Phase 6E defines the proposed Hermes-to-Helio delegation interface in `docs/HERMES_HELIO_DELEGATION_INTERFACE.md`.

## Hermes-To-DevMonster Inference Boundary

DevMonster provides model inference through Gemma and the adapter path. DevMonster is not an operator and must not receive authority to act on the Mac mini, edit files, connect external systems, or dispatch agents.

Hermes may use DevMonster for local reasoning only through the localhost adapter boundary.

## Desktop Status And Fail-Closed Rule

Hermes Desktop remains fail-closed.

Resident Hermes authority must not depend on Desktop, launch Desktop, replace Desktop, remove quarantine, sign in to Nous Portal, grant permissions, or use Desktop as an integration path unless a later Desktop-specific phase approves it.

## Future RunAtLoad And KeepAlive Consideration

`RunAtLoad=true` and `KeepAlive=true` may be considered only after:

- foreground adapter validation remains stable
- manual LaunchAgent start/stop remains stable
- local status command verifies clean final state
- audit logging is designed
- emergency stop is tested
- resident authority tier is approved
- human approval defines whether the adapter, Hermes, or both may auto-start

Default remains:

- `RunAtLoad=false`
- `KeepAlive=false`
- no Hermes resident process

## Minimum Acceptance Criteria Before Resident Mode

Before enabling resident Hermes:

- authority tier policy approved
- emergency stop implemented and tested
- audit log design implemented
- command allowlist and denylist implemented
- allowed and forbidden file zones enforced
- credential handling and rotation decision complete
- network access policy enforced
- Desktop remains fail-closed or is separately resolved
- adapter health and localhost-only checks pass
- no external integration is enabled without its own phase
- rollback procedure tested
- human approval recorded for the exact resident scope

## Proposal Conclusion

Hermes may become a resident personal agent only through staged, audited, tiered authority. Phase 6B proposed the audit log model, and Phase 6C proposed the emergency stop model. The next safe phase is a resident service proposal. Runtime resident mode remains disabled.

Phase 6D proposes the resident service design in `docs/HERMES_RESIDENT_SERVICE_PROPOSAL.md`. The service remains unimplemented and uninstalled.

Phase 6E proposes the Hermes-to-Helio delegation interface. Agent Bus remains frozen until a later credential and scope approval phase.

Phase 6F proposes the command policy. Hermes command execution remains disabled.

Phase 6G proposes the file zone policy. File zone enforcement remains unimplemented.
