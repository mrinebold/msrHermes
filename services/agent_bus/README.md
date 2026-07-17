# Hermes Helio Agent Bus Bridge

This package is the Phase 1 Hermes-to-Helio contract bridge.

Current behavior:

- uses an in-process test gateway only
- no network listener or outbound network calls
- no Supabase imports, configuration, or database calls
- no `ano-messaging` runtime imports
- no polling workers
- no direct `agent_messages` writes
- no direct `bot_outbound_messages` writes
- no task execution or dispatch
- no message send

The test gateway exercises Helio-owned endpoint shapes without impersonating Helio:

- `GET /agent-bus/orgs/{org_id}/messaging-config`
- `GET /agent-bus/messages/inbound/hermes`
- `POST /agent-bus/tasks/propose` as a dry-run result only

Phase 1 configuration is intentionally narrow:

```text
HELIO_AGENT_BUS_MODE=read_only
HELIO_GATEWAY_URL=inprocess://helio-test
HERMES_HELIO_TEST_GATEWAY=1
HELIO_DEFAULT_ORG=msr
HELIO_DEFAULT_WORKSPACE=default
HELIO_AGENT_ID=hermes
```

Any other gateway URL is refused. The bridge is not a Supabase client and must not be pointed at DevMonster, Tailscale hosts, or a public URL.

Canonical sources:

- [Agent Bus Contract](../../docs/AGENT_BUS_CONTRACT.md)
- [Hermes Helio Agent Bus Plan](../../docs/HERMES_HELIO_AGENT_BUS_PLAN.md)
- [Phase 1 private Gemma and Helio bridge](../../docs/HERMES_PHASE1_PRIVATE_GEMMA_HELIO_BRIDGE.md)

A later, explicitly approved phase may replace the test gateway with Helio's private governed API. Hermes must remain a Helio client, never a direct message-bus or Supabase writer.
