# Hermes Phase 1: Private Gemma Route and Helio Test Bridge

## Outcome

Phase 1 makes the first-pilot route visible and testable without broadening Hermes authority:

```text
Browser gateway (private/Tailscale)
  -> governed Hermes local surface
  -> localhost model adapter (manual only)
  -> DevMonster private Gemma4 worker

Hermes Phase 1 bridge
  -> in-process Helio contract gateway
  -> no network, no Supabase, no dispatch
```

The gateway status and `GET /api/pilot-readiness` expose configuration state only. They do not send prompts, start the model adapter, contact DevMonster, or create agent work.

## Fixed first-pilot decisions

- Helio is the sole router and dispatcher for agent work.
- Gemma4 is the only allowed inference route for this pilot.
- The approved model worker is private DevMonster Ollama using `gemma4:26b`.
- Hermes reaches models through its local adapter at `127.0.0.1:8088`; that adapter is never browser-exposed.
- Browser chat is not enabled in Phase 1.
- The Helio bridge accepts only `inprocess://helio-test`.
- Direct Supabase access, direct `agent_messages` writes, task dispatch, polling, cloud fallback, and external integrations remain disabled.

## In-process Helio contract gateway

The bridge tests only the contract Hermes will use when Helio provides a governed private endpoint:

| Contract | Phase 1 result |
| --- | --- |
| `GET /agent-bus/orgs/{org_id}/messaging-config` | Scoped in-memory read |
| `GET /agent-bus/messages/inbound/hermes` | Scoped in-memory read |
| `POST /agent-bus/tasks/propose` | Dry-run result; never stored or dispatched |

Enable it only for an explicit local test:

```bash
export HELIO_AGENT_BUS_MODE=read_only
export HELIO_GATEWAY_URL=inprocess://helio-test
export HERMES_HELIO_TEST_GATEWAY=1
export HELIO_DEFAULT_ORG=msr
export HELIO_DEFAULT_WORKSPACE=default
export HELIO_AGENT_ID=hermes
python3 -m unittest tests.agent_bus.test_scaffold
```

Any other `HELIO_GATEWAY_URL` is refused in Phase 1. Do not place a Supabase URL, anon key, service-role key, model token, or OAuth credential in this configuration.

## Private Gemma configuration check

The gateway reports a configuration as eligible only when all conditions are true:

- model worker URL is a literal Tailscale address in `100.64.0.0/10`;
- worker model is `gemma4:26b`;
- local model adapter host is `127.0.0.1`.

The readiness endpoint deliberately returns `live_probe: not_run`. Run a separate bounded, manual validation only after reviewing the adapter plan. No listener is created by this phase.

## Validation

Run from the Hermes repository:

```bash
python3 -m unittest tests.agent_bus.test_scaffold tests.test_hermes_gateway
python3 -m unittest discover
git diff --check
```

For a temporary local gateway check, use the existing token-authenticated gateway script. It remains localhost by default and may bind to the Mac mini's explicitly approved Tailscale IP only with a local token. Tailscale Funnel and public exposure are not approved.

## Next phase

Phase 2 can add the browser workbench conversation shell and an explicit, manual private-Gemma smoke test. Phase 3 may integrate a real Helio-owned private gateway only after its endpoint, identity, approval, audit, and idempotency contracts are accepted. Hermes must never substitute a direct Supabase or raw agent-bus connection.
