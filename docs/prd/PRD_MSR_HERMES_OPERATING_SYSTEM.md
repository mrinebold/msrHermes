# PRD: MSR Hermes Operating System

## Status

Phase 6B complete. Next recommended work: Phase 6C: Helio Agent Bus Gateway scaffold proposal and approval.

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

Phase 6C: Helio Agent Bus Gateway scaffold proposal and approval.

Phase 6C should propose a `services/agent_bus/` scaffold that remains Helio-facing only, creates no Supabase client, sends no messages, and defaults to fail-closed behavior.

## Non-Goals

- Do not install Hermes.
- Do not enable autonomous execution.
- Do not connect Supabase.
- Do not store real secrets.
- Do not send messages to agents.
- Do not scaffold `services/agent_bus/` until the contract is clear enough.
