# Hermes CLI Invocation Notes

Diagnosis date: 2026-06-04.

Phase 5J is diagnosis only. No live prompts were sent, no background services were started, no persistent Hermes home was configured, no cloud provider credentials were provided, and no Google, Supabase, Home Assistant, Helio, or Agent Bus integration was connected.

## Commands Inspected

Local help output was inspected for:

- `hermes --help`
- `hermes chat --help`
- `hermes run --help`
- `hermes config --help`

Local Hermes configuration examples and bundled documentation were also inspected under `~/.hermes/hermes-agent/`.

## One-Shot Command

The installed Hermes CLI documents top-level `-z` / `--oneshot` as the intended one-shot mode:

```text
hermes -z "prompt"
```

The help text says one-shot mode sends a single prompt and prints only the final response text to stdout. It also says there is no banner, spinner, tool preview, or `session_id` line. This is the best fit for bounded sandbox summary runs where the caller expects to redirect stdout into a file.

Important caveat: top-level one-shot mode still loads tools, memory, rules, and `AGENTS.md` from the current working directory unless isolated with flags and runtime state. The help text also says approvals are auto-bypassed. For Helio validation, one-shot runs should therefore use an isolated `HERMES_HOME`, no live credentials, no external integrations, `--ignore-rules` when practical, and a local-only provider config.

## Chat Query Command

`hermes chat -q` / `hermes chat --query` is also non-interactive:

```text
hermes chat -q "prompt"
```

`hermes chat --quiet` / `-Q` suppresses banner, spinner, and tool previews, but its help text says it prints the final response and session info. Phase 5I observed `chat -q -Q` exiting successfully without creating the requested summary files, so it is less suitable than top-level `-z` for file-oriented one-shot summaries unless a later diagnostic confirms the exact output stream behavior.

## Run Command

`hermes run --help` exits with an invalid-command error in the installed version. `run` is not an available Hermes command for this local install.

## Config Commands

`hermes config --help` is available and exposes:

- `show`
- `edit`
- `set`
- `path`
- `env-path`
- `check`
- `migrate`

These commands were inspected for help only. No persistent Hermes configuration was changed in Phase 5J.

## Output Destinations

Expected output behavior from local help and Phase 5I observations:

| Invocation | Expected output destination | Phase 5J assessment |
| --- | --- | --- |
| `hermes -z/--oneshot` | Final response text on stdout only. | Preferred one-shot sandbox pattern. |
| `hermes chat -q` | Non-interactive chat output with session behavior. | Useful for chat-like diagnostics, less direct for stdout-only summary capture. |
| `hermes chat -q -Q` | Final response plus session info. | Phase 5I did not produce usable files with this path. |
| `hermes run` | Not available. | Do not use. |
| TUI/session state | Managed through Hermes sessions/TUI commands. | Not used for sandbox summary capture. |

## Provider Configuration Notes

Bundled Hermes docs and examples show that local/self-hosted OpenAI-compatible endpoints should use `provider: custom` plus a `base_url`.

The future isolated sandbox config shape should remain:

```yaml
model:
  default: gemma4:26b
  provider: custom
  base_url: http://127.0.0.1:8088/v1
  api_key: dummy-local-adapter-key
```

Hermes docs state that when `base_url` is set, Hermes calls that endpoint directly and uses a configured `api_key` or `OPENAI_API_KEY` for auth. For Helio sandbox validation, the key must remain a dummy local value only if Hermes requires one syntactically. Real OpenAI, Anthropic, GitHub, Supabase, Google, Home Assistant, and Helio credentials must remain absent.

The top-level `model.provider` value should be `custom`. The `main` provider is documented for auxiliary/fallback slots and should not be used as the top-level provider.

## Adapter Observability Contract

Phase 5J adds optional adapter request logging behind:

```text
MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true
```

When enabled, request logs include:

- timestamp
- method
- path
- response status
- selected model, when available
- elapsed time

The adapter must not log prompt text, message content, API keys, OAuth tokens, Supabase keys, or other secrets by default.

## Recommendation

Use top-level `hermes -z` for the next bounded one-shot sandbox diagnostic, not `hermes run` and not the chat query path as the default. Start the adapter manually in the foreground on `127.0.0.1:8088` with `MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true`, keep `HERMES_HOME` isolated, keep cloud credentials absent, and inspect adapter logs to confirm whether Hermes calls `/v1/chat/completions`.

Recommended next phase:

Phase 5K: run one bounded Hermes one-shot diagnostic through the local adapter with request logging enabled, then inspect only stdout, stderr, output file size, and adapter request metadata. Do not rerun without approval.

## Phase 5K Result

Diagnosis date: 2026-06-04.

One bounded command was run from a temporary working directory with an isolated `HERMES_HOME`:

```text
hermes -z "Reply with exactly: Hermes adapter diagnostic."
```

Temporary Hermes config used only:

```yaml
model:
  default: gemma4:26b
  provider: custom
  base_url: http://127.0.0.1:8088/v1
  api_key: dummy-local-adapter-key
```

Result:

| Check | Result |
| --- | --- |
| Timeout | 180s cap; command completed before timeout |
| Exit code | 0 |
| Elapsed time | 45.539s |
| Stdout byte count | 8 bytes |
| Stderr byte count | 0 bytes |
| Stdout text | `(empty)` |
| Adapter shutdown | stopped immediately after diagnostic; no `8088` listener remained |

Adapter request metadata proved Hermes called the localhost adapter:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /health` | 1 | 200 |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 4 | 200, selected `gemma4:26b` |
| Unsupported discovery probes | 17 | 404 |

Observed unsupported discovery probes included `/api/v1/models`, `/api/tags`, `/v1/props`, `/props`, `/version`, `/api/show`, and `/v1/models/gemma4:26b`. The adapter rejected these because its approved surface is limited to `GET /health`, `GET /v1/models`, and `POST /v1/chat/completions`.

The four chat-completion calls returned status 200 with selected model `gemma4:26b`; adapter elapsed times were 28.035s, 2.366s, 3.607s, and 7.895s.

Assessment:

- `hermes -z` does call the localhost Model Router adapter.
- The adapter reaches DevMonster Gemma through `services/model_router`.
- Hermes still returns unusable stdout: `(empty)`.
- The remaining issue is not adapter reachability; it is likely a Hermes/custom-provider response-contract or output-handling mismatch.
- No file summaries were run, no persistent Hermes config was changed, no real API keys were used, no background service was started, and no Google, Supabase, Home Assistant, Helio, or Agent Bus access was used.

Updated recommendation:

Phase 5L should inspect Hermes custom-provider response parsing and model capability discovery behavior locally before another live prompt. Focus areas: why Hermes probes unsupported Ollama-style and model-detail endpoints, whether it requires streaming/SSE responses, whether it ignores non-streaming `choices[].message.content` for `-z`, and whether extra model metadata is needed for `gemma4:26b`.

## Phase 5L Response Contract Diagnosis

Diagnosis date: 2026-06-04.

Hermes source was inspected locally under `~/.hermes/hermes-agent`. No Hermes source was modified, no live prompt was sent, no persistent Hermes config was changed, and no cloud credentials or external integrations were used.

Findings:

- `hermes -z` calls `AIAgent.chat()` and returns `result["final_response"]`.
- The one-shot path redirects ordinary stdout/stderr during execution and prints only the returned final response.
- Hermes' chat-completions transport normalizes non-streaming responses from `response.choices[0].message.content`.
- Hermes also reads `choices[0].finish_reason`, optional `choices[0].message.tool_calls`, optional reasoning fields, and optional `usage`.
- Hermes does not use `output_text` on the chat-completions path; that is relevant to Responses-style APIs, not this adapter.
- Hermes' conversation loop prefers streaming for chat completions by default, even without display/TTS consumers.
- The streaming helper sends `stream=True` and `stream_options={"include_usage": True}` to OpenAI-compatible endpoints.
- The streaming helper expects OpenAI-compatible stream chunks with `choices[0].delta.content`, optional `choices[0].delta.tool_calls`, and a terminal `finish_reason`.
- If no visible content is accumulated after retries, Hermes eventually returns the user-facing sentinel `(empty)`.

Adapter comparison:

| Field or behavior | Hermes expectation | Current adapter |
| --- | --- | --- |
| Non-streaming content | `choices[0].message.content` | Present |
| Non-streaming finish reason | `choices[0].finish_reason` | Present: `stop` |
| Usage | optional `usage` object | Present with zero counts |
| Tool calls | optional `choices[0].message.tool_calls` | Absent unless future router response supports tools |
| Responses `output_text` | Not used for chat completions | Absent |
| Streaming content | SSE chunks with `choices[0].delta.content` | Not implemented |
| Streaming finish | terminal SSE chunk with `finish_reason` | Not implemented |
| Streaming usage | optional final usage chunk | Not implemented |

Conclusion:

The adapter response shape is compatible with Hermes' non-streaming chat-completions parser. The likely mismatch is that Hermes first asks for streaming by sending `stream=True`, while the adapter returns ordinary non-streaming JSON. Hermes then accumulates no streamed `delta.content` and can fall into its `(empty)` recovery path.

Phase 5L added metadata-only response-shape logging:

```text
MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true
```

This logs only top-level response keys, choices count, assistant content length, finish reason, and whether the request asked for streaming. It never logs prompt text, message content, model output, or secrets.

Recommended adapter fix:

Implement OpenAI-compatible SSE handling for `POST /v1/chat/completions` when the request has `stream=true`. The first safe implementation can still wait for `services/model_router` to return a full response, then emit a small valid SSE stream:

1. role chunk with `delta.role="assistant"`
2. content chunk with `delta.content` containing the completed model text
3. finish chunk with `finish_reason="stop"`
4. optional usage chunk with empty `choices`
5. `[DONE]`

Keep the endpoint surface unchanged. Do not add new endpoints unless a later phase explicitly approves Hermes model-discovery compatibility work.

## Phase 5M Streaming SSE Support

Implementation date: 2026-06-04.

The localhost adapter now supports Hermes' default streaming chat-completions behavior without changing the approved endpoint surface.

Behavior:

- `POST /v1/chat/completions` with `stream=true` returns `Content-Type: text/event-stream`.
- The adapter still calls `services/model_router` and waits for the full response first.
- After the router response returns, the adapter emits one OpenAI-compatible content delta chunk, one finish chunk, and `data: [DONE]`.
- `POST /v1/chat/completions` with `stream=false` or no `stream` field keeps the existing non-streaming JSON response.

Streaming chunks use:

```text
data: {"object": "chat.completion.chunk", "choices": [{"delta": {"content": "..."}, "finish_reason": null}]}

data: {"object": "chat.completion.chunk", "choices": [{"delta": {}, "finish_reason": "stop"}]}

data: [DONE]
```

The implementation does not log prompt text or model output by default. Response-shape diagnostics remain metadata-only.

No Hermes command was run in Phase 5M. No live prompts, persistent Hermes config, cloud providers, real API keys, background services, Google, Supabase, Home Assistant, Helio, or Agent Bus access were used.

Recommended next phase:

Phase 5N should run one bounded `hermes -z` diagnostic against the SSE-enabled adapter using an isolated `HERMES_HOME`, request logging, and response-shape logging. Do not run file summaries or broaden endpoint support in the same phase.
