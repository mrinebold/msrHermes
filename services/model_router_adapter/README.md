# Model Router Adapter

Phase 5G scaffold for a localhost-only OpenAI-compatible adapter in front of `services/model_router`.

## Scope

The adapter is intended for future Hermes validation as Hermes' sole inference provider. It is not configured in Hermes yet and should not be run as a background service in Phase 5G.

## Defaults

- Host: `127.0.0.1`
- Port: `8088`
- Default task type: `summary`

Environment overrides:

- `MODEL_ROUTER_ADAPTER_HOST`
- `MODEL_ROUTER_ADAPTER_PORT`
- `MODEL_ROUTER_ADAPTER_TASK_TYPE`

For Phase 5G, `MODEL_ROUTER_ADAPTER_HOST` must remain `127.0.0.1`.

## Endpoints

The adapter exposes only:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

All other endpoints return `404`.

## Safety

- No cloud provider credentials.
- No Hermes configuration changes.
- No background service or launchd setup.
- No external bind, LAN bind, Tailscale bind, or `0.0.0.0`.
- Cloud providers remain fail-closed through `services/model_router`.
- Tests use mocked router objects and do not send live prompts.

