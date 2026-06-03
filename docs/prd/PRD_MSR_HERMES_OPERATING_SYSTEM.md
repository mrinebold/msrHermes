# PRD: MSR Hermes Operating System

## Status

Phase 6A complete. Next required work: Phase 6B: Canonical Agent Bus Contract.

## Architecture Decision

Hermes is the resident Mac mini operator. Helio is the governed dispatch layer for reaching the broader MSR/CivicGrantsAI agent team. Hermes must not bypass Helio to call specialist agents, connect Google Workspace, control Home Assistant, or write to the Supabase agent bus.

## Phase History

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 5A | Complete | Defined Hermes-owned Mac mini architecture with Helio as the controlled interface to the agent team. |
| Phase 5B | Complete | Documented Hermes installation, security, configuration, and approval gates without installing Hermes. |
| Phase 5C | Complete | Proposed exact install, config, and rollback commands only. Hermes was not installed. |
| Phase 6A | Complete | Discovered the Supabase Agent Bus source family and designed the Hermes-through-Helio bus plan. |

## Phase 6A Finding

No single canonical Supabase Agent Bus PRD exists for the full Hermes need. The implemented system spans the `agent_messages` queue, `agent_tasks` accountability layer, outbound bot bus, org-scoped config, approvals, and audit logs across multiple PRDs, migrations, runtime services, and exported architecture docs.

The current Phase 6A references are:

- [Supabase Agent Bus Source Map](../SUPABASE_AGENT_BUS_SOURCE_MAP.md)
- [Hermes + Helio Agent Bus Plan](../HERMES_HELIO_AGENT_BUS_PLAN.md)

## Next Required Work

Phase 6B: Canonical Agent Bus Contract.

Phase 6B must elevate `packages/ano-messaging` as the primary canonical Agent Bus source candidate and produce `docs/AGENT_BUS_CONTRACT.md` before any `services/agent_bus/` scaffold is implemented.

## Non-Goals

- Do not install Hermes.
- Do not enable autonomous execution.
- Do not connect Supabase.
- Do not store real secrets.
- Do not send messages to agents.
- Do not scaffold `services/agent_bus/` until the contract is clear enough.

