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

## Phase 5E Sandbox Security Finding

Phase 5E ran Hermes against synthetic local sandbox files with an isolated `HERMES_HOME`, empty isolated `.env`, no MCP servers, provider credential environment variables removed, no setup wizard, no launchd/background service, and no external integrations.

Observed result:

- Hermes CLI startup succeeded.
- Hermes summarization failed closed because no inference provider was configured.
- The non-zero exit is expected and acceptable for the credential-free validation phase.
- No cloud credentials were provided.
- No Google Workspace, Supabase, Home Assistant, Helio, or Agent Bus access was used.
- No autonomous execution or resident/background operation was enabled.

Security review item before resident operation:

- Hermes plugin discovery registered provider plugins and logged lazy dependency behavior for a Bedrock provider. Before Hermes becomes resident, define a constrained profile that disables unneeded provider/plugin surfaces and prevents unexpected lazy dependency installation during local-only operation.

Phase 5F should configure only the existing local model router and/or approved DevMonster Gemma endpoint. Do not configure cloud model providers for Phase 5F.

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

## Hermes Desktop Policy

Phase DESKTOP-1 is planning only. Hermes Desktop must not be downloaded, installed, opened, signed into, or granted permissions until a later phase explicitly approves Desktop installation.

Future Desktop validation must follow these minimum rules:

- download only from the official Nous Research Desktop page
- verify macOS package/app identity if possible
- do not sign into Nous Portal until explicitly approved
- do not add cloud provider credentials
- do not grant broad filesystem permissions on first launch
- do not connect Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus
- do not enable background/resident operation
- keep Desktop pointed at the localhost model adapter if configurable
- confirm whether Desktop shares `~/.hermes` with CLI before adding any durable credentials
- confirm whether Desktop starts background services, launch items, login items, or helper processes
- preserve ANO governance: Desktop is a UI surface only, not a bypass around Helio/ANO rules, roles, permissions, approvals, or audit requirements
- on DevMonster, do not change Ollama/Gemma serving, Tailscale binding, host binding, firewall/network exposure, launch behavior, or model-worker configuration

Desktop rollback must remove the app and Desktop-specific launch/login items while leaving CLI state intact unless a separate phase approves CLI rollback.

DevMonster rollback must also leave Ollama/Gemma, Tailscale, and approved model-worker configuration intact.

Reference:

- [Hermes Desktop Install Plan](HERMES_DESKTOP_INSTALL_PLAN.md)
- [Hermes Desktop DevMonster Plan](HERMES_DESKTOP_DEVMONSTER_PLAN.md)

## Hermes Pilot Mode Policy

Phase 5AB-AC added pilot infrastructure only. Phase 5AD approved and completed one controlled live pilot run through that infrastructure.

Reference:

- [Hermes Pilot Mode](HERMES_PILOT_MODE.md)

Pilot mode permits Hermes to perform safe local reasoning over explicitly supplied local prompts or files through the localhost model router adapter. It may summarize local repo docs and recommend next actions.

Pilot mode must use:

- isolated `HERMES_HOME=/private/tmp/hermes-pilot-home` by default
- `model.provider=custom`
- `model.default=gemma4:26b`
- `model.base_url=http://127.0.0.1:8088/v1`
- dummy local API key only
- `platform_toolsets.cli: []`
- sanitized child environment with real provider and integration variables removed
- foreground-only execution

Pilot mode must not:

- execute shell commands independently
- install software
- send messages
- write Supabase
- connect Google
- control Home Assistant
- launch Hermes Desktop
- modify credentials
- modify persistent Hermes CLI config
- modify files outside `sandbox/output`
- create launchd plists
- run as a background or resident service
- connect GitHub, Helio, Agent Bus, cloud providers, or other external services

The adapter runner may log request/status metadata, response shape metadata, and message-structure metadata only. It must not log prompt text, file contents, model output text, credentials, tokens, or keys.

Phase 5AD security result:

- adapter bound only to `127.0.0.1:8088`
- Hermes used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`
- Hermes used only `http://127.0.0.1:8088/v1`
- Hermes used only dummy local API key material
- real provider and integration environment variables were not passed into the child process
- adapter received model calls and selected `gemma4:26b`
- model responses contained repeated zero-length content, so pilot output was not usable
- Hermes did not execute shell commands independently
- Hermes did not install software
- Hermes did not send messages
- Hermes did not write Supabase
- Hermes did not connect Google, Home Assistant, GitHub, Helio, Agent Bus, cloud providers, or external services
- Hermes did not launch Desktop
- Hermes did not modify credentials or persistent Hermes CLI config
- Hermes did not create launchd plists, resident mode, or background services
- no `8088` listener or Hermes pilot process remained after cleanup

The next pilot attempt must remain under the same security policy. It should adjust prompt construction or harness context delivery before rerun, not expand permissions.

Phase 5AE security result:

- built a bounded explicit-context prompt from local PRD/changelog excerpts under Codex control
- did not ask Hermes to read paths, use tools, connect integrations, or modify files
- adapter ran foreground-only on `127.0.0.1:8088`
- adapter used `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary`
- adapter used `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120`
- adapter used `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500`
- adapter metadata showed local summary extraction success with 1426 context chars and no truncation
- adapter metadata showed `tools_present=false` and `tool_schemas_forwarded=false`
- Hermes used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`
- Hermes used only `http://127.0.0.1:8088/v1`
- Hermes used only dummy local API key material
- real provider and integration environment variables were not passed into the child process
- Hermes produced usable stdout and exited 0
- no Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, Desktop launch, message send, software install, credential modification, persistent CLI config change, background service, resident mode, or launchd plist was used
- no `8088` listener or Hermes pilot/adapter/Desktop process remained after cleanup

The Phase 5AE/5AF explicit-context and `local_summary` shape is the current security-approved pattern for future bounded local reasoning pilots. Further phases must preserve the same no-tools, no-integrations, foreground-only guardrails unless separately approved.

Phase 5AF security result:

- reused the bounded explicit-context prompt pattern under Codex control
- included bounded context from the PRD, changelog, pilot-mode doc, and security model
- did not ask Hermes to read paths, use tools, connect integrations, or modify files
- adapter ran foreground-only on `127.0.0.1:8088`
- adapter used `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary`
- adapter used `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120`
- adapter used `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500`
- adapter metadata showed local summary extraction success with 1480 context chars and no truncation
- adapter metadata showed `tools_present=false` and `tool_schemas_forwarded=false`
- Hermes used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`
- Hermes used only `http://127.0.0.1:8088/v1`
- Hermes used only dummy local API key material
- real provider and integration environment variables were not passed into the child process
- Hermes produced usable stdout and exited 0
- no Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, Desktop launch, message send, software install, credential modification, persistent CLI config change, background service, resident mode, or launchd plist was used
- no `8088` listener or Hermes pilot/adapter/Desktop process remained after cleanup

Hermes' Phase 5AF recommendation correctly required human approval before executing the next PRD-review phase and kept authority broadening as a non-goal. The next phase may perform bounded local reasoning over explicit context only; it must not introduce shell execution, file edits, gateway behavior, external integrations, Agent Bus access, Desktop launch, or resident operation without separate approval.

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
