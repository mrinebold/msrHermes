# PRD: MSR Hermes Operating System

## Status

Phase SECURITY-2 complete. Next recommended work: confirm or explicitly defer exposed credential rotation before any additional live Agent Bus reads or writes.

Local repository status: complete work through Phase ANO-GOV-1 has been published. Phase SECURITY-2 updates credential-rotation status tracking locally.

## Architecture Decision

Hermes is the resident Mac mini operator. Helio/ANO is the governed coordination layer for the broader MSR/CivicGrantsAI agent society. Hermes must not bypass Helio/ANO to request specialist work, connect Google Workspace, control Home Assistant, or write to the Supabase agent bus.

## Machine-Boundary Gating vs ANO Governance

Hermes is gated because it can cross the Mac mini and external-system boundary. Hermes-specific gates protect the human, local files, local services, secrets, Google Workspace, Home Assistant, Supabase writes, GitHub writes, and external communication.

The broader ANO agent society is not governed by Hermes. Helio/ANO coordinates and governs agents through ANO governance rules, roles, permissions, consensus/workflow rules, and each agent's own policy framework.

Hermes may request work from Helio/ANO, but it does not own or command the ANO. Other agents are not subordinate to Hermes. Hermes approval gates protect boundary-crossing actions; they do not restrict the internal freedom of the agent society.

## Phase History

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 5A | Complete | Defined Hermes-owned Mac mini architecture with Helio as the controlled interface to the agent team. |
| Phase 5B | Complete | Documented Hermes installation, security, configuration, and approval gates without installing Hermes. |
| Phase 5C | Complete | Proposed exact install, config, and rollback commands only. Hermes was not installed. |
| Phase 6A | Complete | Discovered the Supabase Agent Bus source family and designed the Hermes-through-Helio bus plan. |
| Phase 6B | Complete | Elevated `packages/ano-messaging` as the primary canonical message bus source candidate and defined the Hermes-facing Agent Bus contract. |
| Phase 6C | Complete | Designed the Helio-facing adapter scaffold proposal with read-only-first mode, fail-closed rules, and mocked test strategy. |
| Phase 6D | Complete | Implemented the read-only `services/agent_bus` scaffold with mocked tests, no Supabase imports, no writes, and no polling worker. |
| Phase 6E | Complete | Planned the live read-only Supabase preflight, preferring anon-key RLS and defining exact read queries without connecting Supabase. |
| Phase 6G | Complete | Implemented a stdlib-only read-only preflight script and mocked tests without connecting Supabase or installing packages. |
| Phase 6H | Complete | Ran live read-only anon-key validation for org `msr`, workspace `default`, and agent `hermes`; all approved reads returned safely with zero scoped rows. |
| Phase SECURITY-1 | Complete | Documented credential exposure and created a rotation checklist without rotating credentials or calling external APIs. |
| Phase ANO-GOV-1 | Complete | Clarified that Hermes is gated at the machine boundary while ANO agents are governed by Helio/ANO and are not subordinate to Hermes. |
| Phase SECURITY-2 | Complete | Added post-exposure rotation status tracking and blocked further live bus reads/writes until rotation is confirmed or explicitly deferred. |

## Completed Work Snapshot

Completed and committed locally:

- Hermes ownership architecture: Hermes is the resident Mac mini operator, while Helio/ANO is the governed coordination layer for the broader agent society.
- Hermes install planning: install options, security model, prerequisites, config layout, rollback planning, and install-command proposal were documented without installing Hermes.
- Model routing and DevMonster planning: Hermes remains local-first through the existing Helio model router and DevMonster Gemma4 path.
- Google Workspace and Home Assistant planning: both remain future gated integrations; neither is connected or enabled.
- Supabase Agent Bus discovery: `packages/ano-messaging` was elevated as the primary canonical message-bus source candidate.
- Agent Bus contract: canonical tables, fields, statuses, permissions/RLS expectations, payload shapes, services, and polling behavior were documented.
- Hermes-to-Helio bus planning: Hermes may observe and request through Helio/ANO, but must not directly dispatch agents or write to the bus.
- Read-only adapter scaffold: `services/agent_bus/` was added with fail-closed mock behavior and unit tests only.
- Live read-only preflight script: `scripts/agent_bus_readonly_preflight.py` was added using Python stdlib only, process environment only, GET-only requests, and redacted output.
- Live read-only validation: anon-key validation ran for org `msr`, workspace `default`, agent `hermes`; all approved reads returned 0 scoped rows.
- Credential rotation tracking: exposed credential types were documented in the rotation checklist; no rotation was performed automatically.
- ANO governance clarification: Hermes gating is machine-boundary protection, not governance over the ANO agent society.
- SECURITY-2 rotation status: Supabase service-role, OpenAI, Anthropic/Claude, GitHub token, and Supabase anon-key review remain pending user confirmation unless the user later confirms rotation or explicit deferral.

Not completed or not approved:

- Hermes is not installed.
- Autonomous execution is not enabled.
- Google Workspace is not connected.
- Home Assistant is not installed or connected.
- Supabase writes are not enabled.
- Agent dispatch is not enabled.
- Service-role access is not approved for Hermes.
- Further live Agent Bus reads are blocked until high-risk exposed credentials are rotated and a new phase is approved.
- Further live Agent Bus writes are blocked until exposed credential rotation is confirmed or explicitly deferred.

## Phase 6A Finding

No single canonical Supabase Agent Bus PRD exists for the full Hermes need. The implemented system spans the `agent_messages` queue, `agent_tasks` accountability layer, outbound bot bus, org-scoped config, approvals, and audit logs across multiple PRDs, migrations, runtime services, and exported architecture docs.

The current Phase 6A references are:

- [Supabase Agent Bus Source Map](../SUPABASE_AGENT_BUS_SOURCE_MAP.md)
- [Hermes + Helio Agent Bus Plan](../HERMES_HELIO_AGENT_BUS_PLAN.md)

## Phase 6B Finding

`packages/ano-messaging` is the primary canonical source candidate for the portable Agent Bus message layer. It defines `agent_messages`, `bot_outbound_messages`, `org_messaging_config`, message service methods, outbound polling, directive scanning, and baseline computation.

It does not define the full task bus. `agent_tasks`, task events, approvals, and immutable audit still need Helio-owned normalization before Hermes may dispatch agent work.

Phase 6B reference:

- [Canonical Agent Bus Contract](../AGENT_BUS_CONTRACT.md)

## Next Recommended Work

Confirm or explicitly defer exposed credential rotation before any additional live Agent Bus reads or writes.

Security reference:

- [Credential Rotation Checklist](../security/CREDENTIAL_ROTATION_CHECKLIST.md)

After rotation confirmation or explicit deferral, run local tests and `verify-config` only. Do not run `list-org-configs`, `read-hermes-messages`, `read-outbound-audit`, or any write-oriented bus operation until the exposed high-risk credentials are revoked, rotated, or explicitly deferred by the user and a new phase is explicitly approved.

Phase 6I remains the next architecture investigation after rotation: determine whether empty Agent Bus metadata results mean the `msr` Agent Bus config has not been seeded, the anon key is constrained to empty scoped visibility, or Helio should expose an explicit read-only gateway/view.

Phase 6H validated the approved read-only path using `SUPABASE_URL` and `SUPABASE_ANON_KEY` only. The service-role key was not used. No messages were sent, no polling workers were created, and no writes were enabled.

Phase 6H read only:

- `org_messaging_config`
- `agent_messages` addressed to `hermes`
- `bot_outbound_messages` for audit inspection only

Live validation result:

| Check | Org | Workspace | Agent | Row count | Statuses | Latest timestamp |
| --- | --- | --- | --- | --- | --- | --- |
| `verify-config` | `msr` | `default` | `hermes` | n/a | `ok` | n/a |
| `org_messaging_config` | `msr` | `default` | n/a | 0 | none | none |
| `agent_messages` addressed to Hermes | `msr` | `default` | `hermes` | 0 | none | none |
| `bot_outbound_messages` audit | `msr` | `default` | n/a | 0 | none | none |

Phase 6I should determine whether zero rows means the `msr` Agent Bus config has not been seeded, the anon key is constrained to empty scoped visibility, or Helio should expose an explicit read-only gateway/view. The follow-up must not use direct Hermes service-role access.

Phase 6G reference:

- [Read-only preflight script](../../scripts/agent_bus_readonly_preflight.py)
- [Read-only preflight mocked tests](../../tests/agent_bus/test_readonly_preflight.py)

Phase 6E reference:

- [Hermes Helio Adapter Design](../HERMES_HELIO_ADAPTER_DESIGN.md)

## Non-Goals

- Do not install Hermes.
- Do not enable autonomous execution.
- Do not connect Supabase.
- Do not store real secrets.
- Do not send messages to agents.
- Do not connect the scaffold to live services until a later approval is explicit.
- Do not use `SUPABASE_SERVICE_ROLE_KEY` in the Hermes adapter.
- Do not run further live reads until exposed high-risk credentials are rotated.
