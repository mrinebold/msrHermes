# Hermes Helio Agent Bus Scaffold

This package is the Phase 6D read-only scaffold for future Hermes-to-Helio agent bus access.

Current behavior:

- no Supabase imports
- no `ano-messaging` runtime imports
- no network calls
- no database calls
- no polling workers
- no message sends
- no `agent_messages` writes
- no `bot_outbound_messages` writes
- no task execution

The scaffold uses mocked Supabase-shaped records in tests and follows:

- `docs/AGENT_BUS_CONTRACT.md`
- `docs/HERMES_HELIO_ADAPTER_DESIGN.md`

Allowed modes:

- `read_only`: list mocked org messaging config and read mocked inbound messages.
- `dry_run`: build outbound bot message payloads without sending.

Writes are denied by default, including `outbound_with_approval`, until a future approved phase connects Hermes to a governed Helio gateway.

