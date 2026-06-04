# Hermes Security Model

Planning date: 2026-06-03.

Phase 5B is planning only. Hermes remains uninstalled and unauthenticated.

## Security Objective

Install Hermes later as the resident Mac mini operator without giving it uncontrolled authority over the machine, external accounts, physical devices, or the MSR/CivicGrantsAI agent team.

Hermes may become the day-to-day local operator. Helio remains the governance layer for policy, audit, model routing, credentials, agent dispatch, and external integrations.

## Machine-Boundary Gating vs ANO Governance

Hermes is gated at the Mac mini and external-system boundary because it may eventually inspect local state, run approved scripts, edit files, touch secrets, call local services, and interact with Google Workspace, Home Assistant, Supabase, GitHub, or external communications.

The ANO agent society is not governed by Hermes. ANO agents operate under Helio/ANO governance, roles, permissions, consensus/workflow rules, and their own policy framework. Hermes may request work from Helio/ANO, but Helio/ANO decides whether and how agent work proceeds.

Hermes' approval gates protect:

- the human
- the Mac mini
- local files and services
- secrets and credentials
- external accounts
- physical-world systems
- durable shared systems such as Supabase

Hermes' approval gates do not make Hermes the supervisor of ANO agents and do not constrain internal ANO governance except where a Hermes-originated request crosses a protected machine or external-system boundary.

## Trust Boundaries

### Local Low-Risk Boundary

Hermes may eventually work directly inside this boundary:

- approved project directories
- local planning notes
- read-only inspection
- approved local scripts
- model-router requests approved for local-first reasoning

Even inside this boundary, Hermes may not delete files, install packages, expose services, or perform unrestricted shell writes without approval.

### Helio-Governed Boundary

Hermes must route through Helio for:

- DevMonster Gemma4 governed reasoning
- Google Workspace access
- GitHub mutations
- Home Assistant reads or actions
- future Supabase task bus access
- dispatch to the 40-agent team
- credential access
- audit-worthy external writes

### Human Approval Boundary

Human approval is required before actions with lasting side effects, external authority, physical-world impact, credential exposure, or broad delegation.

## Default Deny Rules

Default-deny until separately approved:

- autonomous execution
- shell command execution beyond approved scripts
- file edits
- file deletion
- package installation
- shell profile modification
- `sudo`
- public network exposure
- Google OAuth
- Google sends, edits, shares, deletes, and calendar mutations
- GitHub writes
- Home Assistant token creation and service calls
- Supabase credentials and writes
- agent dispatch
- cloud model providers
- background gateway service installation

## Shell Command Policy

Phase 5B:

- no Hermes shell execution

Future minimum policy:

- read-only commands may be allowlisted
- write-capable commands require approval
- destructive commands require explicit approval and a rollback plan
- command logs must include command, cwd, timestamp, approval ID, and result
- no `sudo` without explicit approval
- no shell profile edits without explicit approval

Initial allowlist candidate:

- `scripts/check_environment.sh`

Adding more scripts requires updating policy and documenting the expected side effects.

## File Edit Policy

Phase 5B:

- no Hermes file edits

Future minimum policy:

- approved project roots only
- no writes outside approved roots
- no deletion without explicit approval
- no production code edits without review
- show diffs before commits
- log file paths changed and approval IDs

## Model And Reasoning Policy

Hermes should use local-first reasoning through Helio's model router.

Approved model path:

1. Hermes requests model work from Helio.
2. Helio applies task policy.
3. Helio routes approved private reasoning to DevMonster Gemma4.
4. Helio logs provider, model, task type, elapsed time, and approval requirement.

Direct Hermes custom endpoint access to DevMonster may be approved only as a temporary fallback for low-risk local operator chat. It must not be used for autonomous execution decisions or external actions.

Cloud model providers remain disabled until separately approved.

## Credential Policy

No real credentials belong in this repository.

Never commit:

- API keys
- OAuth client secrets
- OAuth refresh tokens
- Home Assistant long-lived tokens
- GitHub tokens
- Supabase keys
- private keys
- personal account passwords

Allowed committed file:

- `config/hermes.example.env`, with blank placeholders only

Runtime secret locations after future approval:

- `~/.hermes/.env` for Hermes secrets
- untracked Helio env files for Helio secrets
- OS keychain or managed secret store before production use

## Google Workspace Policy

Phase 5B:

- no Google OAuth
- no Google API calls
- no Hermes Google Workspace skill setup

Future progression:

1. read-only validation
2. draft-only proposal tools
3. human-approved execution

Every Google action must include:

- account
- API surface
- scope
- permission tier
- target resource
- approval ID when required
- audit event ID

## Home Assistant Policy

Phase 5B:

- no Home Assistant install
- no `HASS_TOKEN`
- no live `HASS_URL`
- no Home Assistant service calls

Future progression:

1. read-only telemetry
2. entity/domain allowlists
3. proposal rendering
4. approval-gated service calls
5. audit logging

High-risk categories:

- locks
- alarms
- garage doors
- HVAC
- power controls
- appliances
- security devices

## Helio Agent Dispatch Policy

Phase 5B:

- no agent dispatch

Future minimum policy:

- agent registry exists
- agent capability tiers are documented
- task risk is classified
- high-risk dispatch requires approval
- task lifecycle is audited
- future Supabase task bus enforces leases and result states

Hermes must not directly fan out work to the 40-agent team.

## Background Service Policy

Phase 5B:

- no `hermes gateway install`
- no launchd plist
- no persistent gateway

Future launchd approval must specify:

- profile or `HERMES_HOME`
- plist path
- captured `PATH`
- `VIRTUAL_ENV`
- log path
- restart behavior
- rollback command

Default macOS plist path for the default profile:

```text
~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Audit Requirements

Every governed action should log:

- timestamp
- actor
- requested action
- target system
- risk tier
- policy decision
- approval ID, if any
- execution status
- error, if any
- result reference

Sensitive content should be summarized or redacted by default.

## Phase 5B Security Decision

Approve planning only.

Do not grant runtime authority until a later phase explicitly approves:

- install command
- model provider setup
- tool enablement
- shell command scope
- file edit scope
- gateway service behavior
- Google scopes
- Home Assistant token
- agent dispatch interface
