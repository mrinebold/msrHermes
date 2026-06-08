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
- `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE`
- `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE`
- `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS`
- `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS`

For Phase 5G, `MODEL_ROUTER_ADAPTER_HOST` must remain `127.0.0.1`.

Set `MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true` only for bounded diagnostics. Request logs are emitted as JSON lines with timestamp, method, path, response status, selected model when available, and elapsed time. Prompt text, message content, API keys, OAuth tokens, Supabase keys, and other secrets are not logged by default.

Set `MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true` only for bounded diagnostics. Response-shape logs are emitted as JSON lines with top-level response keys, choices count, assistant content length, finish reason, and whether the request asked for streaming. They do not include prompt text, message content, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

Set `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true` only for bounded diagnostics. Message-structure logs include message count, roles present, character counts per message, final-user-message emptiness, file-content heuristic status, and request option presence for tools, tool choice, max tokens, temperature, and streaming. They do not include prompt text, message content, file contents, tool descriptions, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

When local compat mode is enabled, message-structure diagnostics also include prompt-construction metadata only: flattened prompt character count, role sections included, section order, markdown fence count, XML/tool-like tag count, JSON-looking block count, tool/function/schema/call keyword counts, the final user content start index, and user/system character counts. The first and last prompt snippets are intentionally logged as 0 characters.

## Hermes Contract Notes

Hermes' non-streaming OpenAI-compatible parser expects `choices[0].message.content`, `choices[0].finish_reason`, optional `choices[0].message.tool_calls`, and optional `usage`.

Hermes' default chat-completions path prefers streaming, including in quiet one-shot mode. For `stream=true`, Hermes expects OpenAI-compatible SSE chat-completion chunks using `choices[0].delta.content`, followed by a terminal chunk with `finish_reason` and `data: [DONE]`.

The adapter keeps non-streaming JSON for requests without `stream=true` and returns `text/event-stream` for requests with `stream=true`. The first streaming implementation waits for `services/model_router` to return the full response, then emits one content delta chunk, one finish chunk, and `data: [DONE]`.

For the current DevMonster Gemma route, Hermes tool schemas are diagnostic metadata only. The adapter does not execute tools and does not forward tool schemas to `services/model_router`.

Set `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true` to treat local Gemma as non-tool-capable. In this mode, Gemma requests are flattened into a single prompt with role-labeled blocks like `[system]`, `[user]`, and `[assistant]`; only message text is included, tool schemas and `tool_choice` are ignored for routing, non-text structured parts are omitted, and requests without non-empty user content fail closed with an adapter `400`.

`MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE` is a diagnostic prompt-shaping flag for local compat mode. Supported values are:

| Mode | Behavior |
| --- | --- |
| `flattened` | Default; preserve non-empty role-labeled message sections in original order. |
| `user_only` | Keep only user message sections. |
| `final_user` | Keep only the final non-empty user message. |
| `instruction_context` | Move the final non-empty user message first, then append prior context sections. |
| `local_summary` | Build a compact summary prompt from the latest user instruction plus file-like context, while dropping unrelated Hermes scaffold. |
| `no_tool_vocab` | Preserve flattened sections while removing plain `tool`, `function`, `schema`, and `call` vocabulary. |

`local_summary` is the preferred mode for Hermes file-summary validation. It produces a compact prompt shaped as:

```text
You are summarizing a local sandbox document.
Follow the user instruction exactly.

User instruction:
...

Document/context:
...

Return only the requested answer.
```

The mode extracts the latest user instruction, preserves file-like context from the user message or from file-like system/developer context when needed, drops tool schemas and tool-choice semantics, and fails closed with `400` if it cannot identify both a useful instruction and file-like context. Metadata logs include only character counts and extraction status, never instruction text or file contents.

Use `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS` to cap context sent to Gemma. When truncation is needed, the adapter preserves the beginning and end of the context with a neutral truncation marker between them. Metadata records `context_original_chars`, `context_sent_chars`, and `context_truncated`, but not the context text.

Use `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS` to set the local provider HTTP timeout used by `services/model_router`; `GEMMA_TIMEOUT` remains a legacy fallback. The recommended next bounded live retry settings are:

```text
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
```

These settings were validated successfully for `sandbox/input/sample_note.md` in Phase 5AA. The adapter produced one successful chat completion with `gemma4:26b`, response content length 284, and usable five-bullet output.

## Managed Foreground Runner

Phase 5AB-AC added a manual runner:

```sh
scripts/run_model_router_adapter.sh
```

The runner is the recommended way to start the adapter for a limited Hermes pilot. It:

- binds only to `127.0.0.1`
- refuses non-localhost binds
- refuses non-`8088` pilot ports
- points DevMonster to `http://100.93.120.124:11434`
- uses `gemma4:26b`
- sets provider timeout to 120 seconds
- enables local compatibility mode
- defaults `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context`
- sets local summary context budget to 1500 characters
- enables metadata-only request, response-shape, and message-structure logging
- prints startup config with dummy/secrets redacted
- runs in the foreground only
- creates no launchd plist and no background service

Use dry-run mode for guardrail checks:

```sh
scripts/run_model_router_adapter.sh --dry-run
```

For file-summary validation, override the prompt mode explicitly:

```sh
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary scripts/run_model_router_adapter.sh
```

For general planning/recommendation prompts, keep the default `instruction_context`.

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
