# PRD: MSR Hermes Operating System

## Status

Phase SECURITY-1 complete. Next recommended work: rotate exposed credentials before any additional live Agent Bus reads.

## Architecture Decision

Hermes is the resident Mac mini operator. Helio is the governed dispatch layer for reaching the broader MSR/CivicGrantsAI agent team. Hermes must not bypass Helio to call specialist agents, connect Google Workspace, control Home Assistant, or write to the Supabase agent bus.

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

Rotate exposed credentials before any additional live Agent Bus reads.

Security reference:

- [Credential Rotation Checklist](../security/CREDENTIAL_ROTATION_CHECKLIST.md)

After rotation, run local tests and `verify-config` only. Do not run `list-org-configs`, `read-hermes-messages`, or `read-outbound-audit` again until the exposed high-risk credentials are revoked or rotated and a new phase is explicitly approved.

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
