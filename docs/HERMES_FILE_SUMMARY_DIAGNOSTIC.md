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
