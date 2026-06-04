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
- `MODEL_ROUTER_ADAPTER_LOG_REQUESTS`
- `MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES`
- `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE`

For Phase 5G, `MODEL_ROUTER_ADAPTER_HOST` must remain `127.0.0.1`.

Set `MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true` only for bounded diagnostics. Request logs are emitted as JSON lines with timestamp, method, path, response status, selected model when available, and elapsed time. Prompt text, message content, API keys, OAuth tokens, Supabase keys, and other secrets are not logged by default.

Set `MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true` only for bounded diagnostics. Response-shape logs are emitted as JSON lines with top-level response keys, choices count, assistant content length, finish reason, and whether the request asked for streaming. They do not include prompt text, message content, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

Set `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true` only for bounded diagnostics. Message-structure logs include message count, roles present, character counts per message, final-user-message emptiness, file-content heuristic status, and request option presence for tools, tool choice, max tokens, temperature, and streaming. They do not include prompt text, message content, file contents, tool descriptions, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

## Hermes Contract Notes

Hermes' non-streaming OpenAI-compatible parser expects `choices[0].message.content`, `choices[0].finish_reason`, optional `choices[0].message.tool_calls`, and optional `usage`.

Hermes' default chat-completions path prefers streaming, including in quiet one-shot mode. For `stream=true`, Hermes expects OpenAI-compatible SSE chat-completion chunks using `choices[0].delta.content`, followed by a terminal chunk with `finish_reason` and `data: [DONE]`.

The adapter keeps non-streaming JSON for requests without `stream=true` and returns `text/event-stream` for requests with `stream=true`. The first streaming implementation waits for `services/model_router` to return the full response, then emits one content delta chunk, one finish chunk, and `data: [DONE]`.

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
