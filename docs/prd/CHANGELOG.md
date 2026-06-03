# PRD Changelog

## 2026-06-03

- Completed Phase 6D read-only Hermes-Helio agent bus scaffold.
- Added `services/agent_bus/` with fail-closed config, mock client, schemas, audit redaction, and permissions.
- Added mocked unit tests for missing config, read-only reads, write denial, and outbound dry-run payloads.
- Updated env examples with `HELIO_AGENT_ID=hermes` and read-only scaffold placeholders.
- Completed Phase 6C Helio-facing adapter scaffold proposal.
- Added `docs/HERMES_HELIO_ADAPTER_DESIGN.md`.
- Defined read-only-first behavior, later outbound-only write mode, exact fail-closed rules, and mocked test strategy.
- Recorded that `services/agent_bus/` remains unimplemented pending Phase 6D approval.
- Completed Phase 6B Agent Bus contract from `packages/ano-messaging`.
- Added `docs/AGENT_BUS_CONTRACT.md`.
- Updated the source map to elevate `packages/ano-messaging` as the primary portable message bus source candidate.
- Recorded that `ano-messaging` does not implement `agent_tasks`, task events, approvals, or a full conversation model.
- Recommended Phase 6C as a Helio Agent Bus Gateway scaffold proposal only.
- Added master PRD entry for Phase 6A Agent Bus discovery.
- Recorded that no single canonical Supabase Agent Bus PRD was found during Phase 6A.
- Linked the Phase 6A source map and Hermes-to-Helio bus plan.
- Set next required work to Phase 6B: Canonical Agent Bus Contract.
