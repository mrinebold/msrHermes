# Hermes File Summary Diagnostic

Diagnosis date: 2026-06-04.

Phase 5P is a local inspection and instrumentation phase only. No live Hermes prompts were run, no persistent Hermes configuration was changed, no cloud credentials were provided, and no Google, Supabase, Home Assistant, Helio, or Agent Bus integration was connected.

## Known Facts

- Phase 5N proved the simple one-shot prompt path works through the localhost adapter after SSE support was added.
- Phase 5O proved sandbox file-summary prompts reached the adapter and received successful `200` responses.
- Phase 5O response-shape logs showed `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0` for all eight chat-completion calls.
- The resulting sandbox summary files contained only `(empty)` and are not usable.

## Adapter And Router Prompt Path

The adapter receives Hermes' OpenAI-style `messages` array and converts it into a single plain prompt before delegating to `services/model_router`.

Current extraction behavior:

- The adapter reads all messages in order.
- It prefixes each message with its role.
- It does not read only the first message.
- It does not read only the last message.
- It handles `system`, `user`, `assistant`, `tool`, and other roles uniformly as text-bearing messages.
- It now normalizes string content, list content with OpenAI-style text parts, non-dict list items, `None`, and other primitive content safely.

Router behavior:

- `services.model_router.router.ModelRouter.generate()` receives the adapter-created prompt string.
- The router selects the provider from `task_type` and model policy.
- For the current summary path, it routes to `devmonster_ollama`.
- `DevMonsterOllamaProvider.generate()` sends the full prompt to Ollama `/api/generate` as `{"prompt": "...", "stream": false}` and reads the returned `response` field as model text.

This makes prompt truncation-by-first-message or prompt truncation-by-last-message unlikely. The unresolved question is what Hermes actually places into the `messages` array during the file-summary workflow.

## Hermes CLI Findings

Local Hermes source inspection under `~/.hermes/hermes-agent` found:

- Top-level `hermes -z` is the intended one-shot path and returns only `final_response` to stdout.
- `hermes -z` still builds an `AIAgent` and routes through the normal chat-completions path.
- One-shot mode sets noninteractive approval environment flags internally, so tool use may be attempted without an interactive approval prompt.
- Hermes' default chat-completions path sends `stream=true` and may include tool schemas and `tool_choice` depending on enabled toolsets and agent state.
- The streaming parser returns content from accumulated `choices[0].delta.content`; if accumulated content is empty, the one-shot stdout path can surface `(empty)`.

The adapter currently forwards message text to the model router. It does not execute Hermes-provided tools, and it does not transform tool schemas into local file reads. If the file-summary workflow relies on model-generated tool calls to read local files, the constrained adapter path may need a different approved invocation pattern or explicit prompt content injection rather than broader adapter behavior.

## Added Diagnostic Logging

Phase 5P added optional metadata-only message-structure logging:

```text
MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true
```

When enabled, the adapter logs:

- message count
- roles present
- character counts per message
- whether the final user message is empty
- whether any message resembles file content
- whether `tools` are present
- whether `tool_choice` is present
- whether `max_tokens`, `temperature`, and `stream` are present
- whether streaming was requested

The log does not include prompt text, message content, file contents, tool descriptions, API keys, OAuth tokens, Supabase keys, or other secrets by default.

## Recommendation

Phase 5Q should run one bounded sandbox file-summary diagnostic with `MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true`, `MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true`, and `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true`.

The next diagnostic should answer:

- Did Hermes send actual file contents in any message?
- Was the final user message empty?
- Did Hermes include `tools` or `tool_choice`?
- Did message counts increase across the repeated chat-completion calls, suggesting a tool loop or retry loop?
- Did content lengths differ between the direct prompt call and later file-summary calls?

If no message contains file content, prefer an explicit content-injection summary pattern for sandbox validation or an approved Hermes toolset invocation that is proven to read only sandbox paths. If file content is present but model output remains zero length, focus next on prompt shape and DevMonster Gemma behavior with multi-message or tool-scaffolded prompts.

## Phase 5Q Metadata Diagnostic

Validation date: 2026-06-04.

One bounded Hermes file-summary diagnostic was run against `sandbox/input/sample_note.md` only. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging, response-shape logging, and message-structure logging enabled, then stopped immediately after inspection. Hermes used a temporary isolated `HERMES_HOME` with only the localhost adapter, `gemma4:26b`, and a dummy local API key.

Run result:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Exit code | 0 |
| Elapsed time | 33.501s |
| Stdout file | `sandbox/output/sample_note_phase5q_summary.md` |
| Stdout byte count | 8 |
| Stderr file | `sandbox/output/sample_note_phase5q_stderr.txt` |
| Stderr byte count | 0 |
| Output usable | No; it contains only the empty-response sentinel |
| Adapter shutdown | Stopped immediately; no listener remained on `8088` |

Adapter request metadata:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 4 | 200, selected `gemma4:26b` |
| Unsupported discovery probes | 16 | 404 |

Chat-completion elapsed times were 17.514s, 2.509s, 6.755s, and 2.888s.

Response-shape metadata:

| Chat call count | Streaming requested | Choices | Finish reason | Content length |
| ---: | --- | ---: | --- | ---: |
| 4 | true | 1 each | `stop` | 0 each |

Message-structure metadata was identical for all four chat-completion calls:

| Field | Value |
| --- | --- |
| Message count | 2 |
| Roles | `system`, `user` |
| Character counts | `[5630, 71]` |
| Final user message empty | false |
| File content appears present by length/shape | true |
| `tools` present | true |
| `tool_choice` present | false |
| `stream` present | true |
| `max_tokens` present | false |
| `temperature` present | false |

Conclusion:

Phase 5Q rules out the simplest missing-file-content theory. Hermes appears to send substantial file-like content to the adapter, and the final user message is not empty. The zero-content result is more likely caused by the prompt/tool scaffold sent by Hermes, the adapter passing tool-oriented instructions as plain prompt text without tool execution, or DevMonster Gemma returning an empty response for this specific multi-message/tool-present shape.

Recommendation:

Phase 5R should avoid another full Hermes file-summary rerun at first. Instead, use mocked or direct adapter-level diagnostics to compare three prompt shapes without logging content: plain user-only summary with injected sandbox text, the same two-message shape without `tools`, and the same two-message shape with `tools` present but no executable tool loop. If a live model check is approved later, run one minimal non-Hermes adapter call using synthetic sandbox text to isolate DevMonster prompt-shape behavior from Hermes agent/tool orchestration.

## Phase 5R Tool-Payload Compatibility Diagnosis

Diagnosis date: 2026-06-04.

Phase 5R ran no live Hermes prompts and sent no live model calls. A sanitized mocked fixture was added to mimic the Phase 5Q metadata shape: system and user messages, final user message non-empty, `tools` present, `stream=true`, and no real prompt/file content.

Findings:

- Hermes includes `tools` because `hermes -z` still builds a normal `AIAgent`, uses configured CLI toolsets when no explicit toolsets are passed, and passes `agent.tools` into chat-completion kwargs.
- The adapter currently ignores `tools` and `tool_choice` for routing.
- The adapter flattens all message text in order and sends only the resulting plain prompt to `services/model_router`.
- Mocked case A, `tools` present, and case B, `tools` stripped, produce the same router prompt.
- Mocked case C, messages pre-flattened into one user prompt, and case D, tools stripped plus pre-flattened, produce a simpler Gemma-facing prompt shape.

Conclusion:

Tool stripping alone is not sufficient because the adapter already omits tool schemas from the router prompt. The safer compatibility fix for local Gemma is to combine tool stripping with an explicit prompt-flattening mode that treats DevMonster Gemma as non-tool-capable and prioritizes the final non-empty user instruction.

Recommendation:

Phase 5S should implement local Gemma prompt compatibility in the adapter: ignore `tools` and `tool_choice`, flatten system/developer/user context into a single Gemma-friendly prompt, preserve file-like context without logging it, and keep SSE behavior unchanged. Preserve room for future tool-capable providers, but do not pass Hermes tool semantics to DevMonster until a real tool execution contract exists.

## Phase 5S Local Gemma Compatibility

Implementation date: 2026-06-05.

Phase 5S implemented `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`. With this opt-in mode enabled for local Gemma requests, Hermes multi-message payloads are converted into one role-labeled plain prompt using blocks like `[system]`, `[user]`, and `[assistant]`. Tool schemas and `tool_choice` are ignored for routing, structured content is reduced to safe text parts only, and requests with no non-empty user content fail closed.

The compatibility mode preserves streaming SSE behavior and adds metadata-only diagnostics for whether compat mode was enabled, how many messages were flattened, flattened prompt character count, whether tool schemas were present, and the invariant `tool_schemas_forwarded=false`.

No live Hermes prompt or live model call was run in Phase 5S.

Recommended next phase:

Phase 5T should run one bounded `sample_note.md` Hermes file-summary retry through the adapter with local compat mode enabled, using the same isolated-home and metadata-only logging constraints from Phase 5Q.
