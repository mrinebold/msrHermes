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

## Phase 5T Live Retry With Local Compat Mode

Validation date: 2026-06-05.

One bounded Hermes file-summary test was run against `sandbox/input/sample_note.md` only. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging, response-shape logging, message-structure logging, and local compat mode enabled. It was stopped immediately after inspection, and no listener remained on `8088`.

Run result:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Exit code | 0 |
| Elapsed time | 52.126s |
| Stdout file | `sandbox/output/sample_note_phase5t_summary.md` |
| Stdout byte count | 8 |
| Stderr file | `sandbox/output/sample_note_phase5t_stderr.txt` |
| Stderr byte count | 0 |
| Output usable | No; it contains only the empty-response sentinel |

Adapter metadata:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 4 | 200, selected `gemma4:26b` |
| Unsupported discovery probes | 16 | 404 |

Chat-completion elapsed times were 29.388s, 6.618s, 5.464s, and 6.715s.

Response-shape metadata:

| Chat call count | Streaming requested | Choices | Finish reason | Content length |
| ---: | --- | ---: | --- | ---: |
| 4 | true | 1 each | `stop` | 0 each |

Compat metadata was identical for all four chat-completion calls:

| Field | Value |
| --- | --- |
| `compat_mode_enabled` | true |
| `flattened_message_count` | 2 |
| `flattened_prompt_chars` | 5724 |
| `tool_schemas_present` | true |
| `tool_schemas_forwarded` | false |
| Message roles | `system`, `user` |
| Message character counts | `[5628, 78]` |
| Final user message empty | false |

Conclusion:

Phase 5T proves local compat mode activated and tool schemas were not forwarded, but it did not fix the Hermes file-summary path. The remaining blocker is likely not transport, missing file-like context, or tool-schema forwarding. It is more likely the content/shape of Hermes' large system prompt as flattened for Gemma, DevMonster Gemma behavior with that prompt size/instruction mix, or a need for a purpose-built summarization prompt that bypasses Hermes' agent scaffold for local file summaries.

Recommended next phase:

Phase 5U should avoid another Hermes retry at first. Use mocked or direct adapter-level diagnostics to compare local Gemma prompt variants without Hermes agent scaffolding: final-user-first prompt ordering, system-context truncation or demotion, and a purpose-built summary prompt containing only sandbox file text plus the five-bullet instruction. Do not run `sample_prd.md` until `sample_note.md` can produce usable output.

## Phase 5U Gemma Prompt Construction Diagnosis

Diagnosis date: 2026-06-05.

Phase 5U ran no live Hermes prompts and sent no live model calls. The adapter flattening strategy was inspected and expanded with metadata-only prompt-construction diagnostics.

New diagnostics, emitted only when `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true` and local compat mode is active, include:

- flattened prompt total character count
- role sections included and section order
- first/last prompt snippet lengths, fixed at 0 characters
- markdown fence count
- XML/tool-like tag count by pattern
- JSON-looking block count by pattern
- plain `tool`, `function`, `schema`, and `call` keyword counts and booleans
- final user content start index
- user and system character counts
- whether user content dominates system content

These diagnostics do not log prompt text, file contents, tool schema JSON, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

Prompt-mode options were added for mocked/offline diagnosis behind:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE
```

Supported values are `flattened`, `user_only`, `final_user`, `instruction_context`, and `no_tool_vocab`. The default remains `flattened`.

Phase 5T's recorded shape strongly suggests that `flattened` is not the right next live mode: the prompt contained two sections, with about 5,628 system characters before about 78 final-user characters. The final instruction therefore arrives after a much larger Hermes scaffold.

Recommendation:

For the next approved live retry, use `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context` with `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`. This preserves the file-like context but places the final user instruction first, reducing the chance that local Gemma treats Hermes' system scaffold as the main task. If that still returns zero content, the next offline comparison should try `no_tool_vocab` or a purpose-built local summary prompt that strips Hermes system/developer scaffold more aggressively.

## Phase 5V Instruction-Context Live Retry

Validation date: 2026-06-05.

One bounded Hermes file-summary test was run against `sandbox/input/sample_note.md` only. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging, response-shape logging, message-structure logging, local compat mode, and `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context`. Hermes used a temporary isolated `HERMES_HOME` with only the localhost adapter, `gemma4:26b`, and a dummy local API key. The adapter was stopped immediately after the run.

Run result:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Exit code | 0 |
| Elapsed time | 58.639s |
| Stdout file | `sandbox/output/sample_note_phase5v_summary.md` |
| Stdout byte count | 8 |
| Stderr file | `sandbox/output/sample_note_phase5v_stderr.txt` |
| Stderr byte count | 0 |
| Output usable | No; it contains only the empty-response sentinel |
| Adapter shutdown | Stopped immediately; no listener remained on `8088` |

Adapter metadata:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 4 | 200, selected `gemma4:26b` |
| Unsupported discovery probes | 17 | 404 |

Chat-completion elapsed times were 28.975s, 4.843s, 12.543s, and 8.489s.

Response-shape metadata:

| Chat call count | Streaming requested | Choices | Finish reason | Content length |
| ---: | --- | ---: | --- | ---: |
| 4 | true | 1 each | `stop` | 0 each |

Prompt-construction metadata was identical for all four chat-completion calls:

| Field | Value |
| --- | --- |
| Prompt mode | `instruction_context` |
| Compat mode | true |
| Message count | 2 |
| Message character counts | `[5628, 83]` |
| Prompt characters | 5729 |
| Final user content start index | 7 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Content length | 0 |
| User content dominates system content | false |
| Tool keyword count | 9 |
| Call keyword count | 1 |
| XML/tool-like tag count | 1 |
| Markdown fence count | 0 |
| JSON-looking block count | 0 |

Conclusion:

`instruction_context` worked mechanically: the final user instruction moved to the front of the prompt, with its content starting at index 7. However, DevMonster Gemma still returned zero visible content for all four chat-completion calls. The remaining blocker is therefore not only final-instruction placement. The prompt still contains a large Hermes system scaffold and tool/call vocabulary in message text.

Recommendation:

Do not rerun `sample_prd.md` yet. The next bounded diagnostic should try `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=no_tool_vocab` for `sample_note.md`, or implement a stronger local summary prompt mode that preserves file-like context while stripping Hermes system/tool scaffold more aggressively. Keep cloud providers fail-closed and keep Hermes configuration isolated.

## Phase 5W No-Tool-Vocabulary Live Retry

Validation date: 2026-06-05.

One bounded Hermes file-summary test was run against `sandbox/input/sample_note.md` only. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging, response-shape logging, message-structure logging, local compat mode, and `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=no_tool_vocab`. Hermes used a temporary isolated `HERMES_HOME` with only the localhost adapter, `gemma4:26b`, and a dummy local API key. The adapter was stopped immediately after the run.

Run result:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Exit code | 0 |
| Elapsed time | 39.471s |
| Stdout file | `sandbox/output/sample_note_phase5w_summary.md` |
| Stdout byte count | 8 |
| Stderr file | `sandbox/output/sample_note_phase5w_stderr.txt` |
| Stderr byte count | 0 |
| Output usable | No; it contains only the empty-response sentinel |
| Adapter shutdown | Stopped immediately; no listener remained on `8088` |

Adapter metadata:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 4 | 200, selected `gemma4:26b` |
| Unsupported discovery probes | 17 | 404 |

Chat-completion elapsed times were 16.647s, 4.226s, 7.283s, and 7.804s.

Response-shape metadata:

| Chat call count | Streaming requested | Choices | Finish reason | Content length |
| ---: | --- | ---: | --- | ---: |
| 4 | true | 1 each | `stop` | 0 each |

Prompt-construction metadata was identical for all four chat-completion calls:

| Field | Value |
| --- | --- |
| Prompt mode | `no_tool_vocab` |
| Compat mode | true |
| Message count | 2 |
| Message character counts | `[5628, 83]` |
| Prompt characters | 5689 |
| Final user content start index | 5606 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Content length | 0 |
| User content dominates system content | false |
| Tool/function/schema/call keyword counts | all 0 |
| XML/tool-like tag count | 1 |
| Markdown fence count | 0 |
| JSON-looking block count | 0 |

Conclusion:

`no_tool_vocab` worked mechanically: the plain `tool`, `function`, `schema`, and `call` keyword counts dropped to zero while tool schemas still were not forwarded. However, Gemma still returned zero visible content for all four chat-completion calls. Because `no_tool_vocab` preserves flattened ordering, the final user instruction remained late in the prompt at index 5606, after the large Hermes system scaffold.

Recommendation:

Stop one-off live retries against the current Hermes scaffold. The next implementation phase should add a stronger local summary prompt mode that combines the useful parts of prior diagnostics: remove tool vocabulary, put the final user instruction first, preserve file-like context, and drop or sharply demote Hermes agent/system scaffold that is not needed for summarization. Do not run `sample_prd.md` until `sample_note.md` can produce usable output.

## Phase 5X Local Summary Prompt Mode

Implementation date: 2026-06-05.

Phase 5X added a purpose-built local Gemma prompt mode:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
```

No live Hermes prompts were run and no live model calls were sent in Phase 5X.

`local_summary` builds a compact prompt for Hermes file-summary requests:

```text
You are summarizing a local sandbox document.
Follow the user instruction exactly.

User instruction:
<extracted latest user instruction>

Document/context:
<extracted file-like context>

Return only the requested answer.
```

Behavior:

- identifies the latest user message as the task instruction
- extracts file-like context from the user message when present
- falls back to file-like system/developer context when the user message contains only the task
- handles markdown starts, fenced blocks, and `Source file:` / document/context markers
- drops unrelated Hermes system/developer/tool scaffold from the routed prompt
- does not include tool schemas or tool-choice semantics
- does not include a role-labeled full transcript
- fails closed with `400` when both a usable instruction and file-like context cannot be identified

Metadata-only diagnostics now include:

- `gemma_prompt_mode=local_summary`
- `instruction_chars`
- `context_chars`
- `dropped_system_chars`
- `dropped_tool_schema_count`
- `local_summary_extraction_success`

The adapter still does not log instruction text, prompt text, file contents, tool schema JSON, model output, API keys, OAuth tokens, Supabase keys, or other secrets by default.

Recommendation:

Phase 5Y should run exactly one bounded `sample_note.md` retry with `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true` and `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary`. Keep `sample_prd.md` out of scope until `sample_note.md` produces usable output.

## Phase 5Y Local Summary Live Validation

Validation date: 2026-06-05.

One bounded Hermes file-summary test was run against `sandbox/input/sample_note.md` only. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging, response-shape logging, message-structure logging, local compat mode, and `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary`. Hermes used a temporary isolated `HERMES_HOME` with only the localhost adapter, `gemma4:26b`, and a dummy local API key. The adapter was stopped immediately after the run.

Run result:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Exit code | 0 |
| Elapsed time | 101.268s |
| Stdout file | `sandbox/output/sample_note_phase5y_summary.md` |
| Stdout byte count | 110 |
| Stderr file | `sandbox/output/sample_note_phase5y_stderr.txt` |
| Stderr byte count | 0 |
| Output usable | No; stdout contains a provider timeout diagnostic |
| Adapter shutdown | Stopped immediately; no listener remained on `8088` |

Stdout contained:

```text
API call failed after 3 retries: HTTP 502: Timed out after 30.0s for http://100.93.120.124:11434/api/generate
```

Adapter metadata:

| Request class | Count | Result |
| --- | ---: | --- |
| `GET /v1/models` | 2 | 200 |
| `POST /v1/chat/completions` | 3 | 502, selected `gemma4:26b` |
| Unsupported discovery probes | 17 | 404 |

Chat-completion elapsed times were 30.011s, 30.052s, and 30.015s. No response-shape records were emitted because no chat-completion call returned a successful model response.

Prompt-construction metadata was identical for all three chat-completion attempts:

| Field | Value |
| --- | --- |
| Prompt mode | `local_summary` |
| Compat mode | true |
| Extraction success | true |
| Message count | 2 |
| Message character counts | `[5628, 83]` |
| Prompt characters | 3139 |
| Instruction chars | 83 |
| Context chars | 2899 |
| Dropped system chars | 5628 |
| Dropped tool schema count | 26 |
| Tool schemas present | true |
| Tool schemas forwarded | false |

Conclusion:

`local_summary` worked mechanically and changed the failure mode. It successfully extracted a compact Gemma-facing prompt and dropped a large amount of Hermes scaffold, reducing the routed prompt from the prior 5,689-5,729 character range to 3,139 characters. Unlike previous modes, the adapter did not receive zero-content 200 responses; instead, DevMonster/Gemma timed out at the router/provider layer after 30 seconds on each retry.

Recommendation:

The next phase should not rerun Hermes unchanged. Diagnose the local router/provider timeout for compact summary prompts first. Likely options are increasing the approved Gemma generation timeout for this task, reducing `local_summary` context further, or adding a shorter local-summary context budget. Keep `sample_prd.md` out of scope until `sample_note.md` returns usable output.

## Phase 5Z Timeout And Context Budget Tuning

Implementation date: 2026-06-05.

Phase 5Z added timeout and context-budget controls without running live Hermes prompts or sending live model calls.

New local provider timeout setting:

```text
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS
```

Default remains 30 seconds through current behavior. `GEMMA_TIMEOUT` remains a legacy fallback. The recommended value for the next bounded `local_summary` live retry is 120 seconds.

New local summary context budget:

```text
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS
```

Default is 3000 characters. The recommended value for the next bounded live retry is 1500 characters.

`local_summary` now truncates context when needed while preserving the beginning and end of the document/context body with a neutral truncation marker. The user instruction remains first.

Additional metadata-only fields:

- `context_original_chars`
- `context_sent_chars`
- `context_truncated`
- `timeout_seconds`

The adapter still does not log actual prompt text, instruction text, file contents, tool schemas, model output, or secrets by default.

Recommendation:

Phase 5AA should run exactly one bounded `sample_note.md` retry with:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
```

Keep `sample_prd.md` out of scope until `sample_note.md` produces usable output.

## Phase 5AA Tuned Local Summary Success

Validation date: 2026-06-05.

One bounded Hermes file-summary retry was run against `sandbox/input/sample_note.md` only with:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
```

| Check | Result |
| --- | --- |
| Hermes exit code | 0 |
| Elapsed time | 112.635s |
| Stdout file | `sandbox/output/sample_note_phase5aa_summary.md` |
| Stdout byte count | 285 |
| Stderr byte count | 0 |
| Output usable | Yes |
| Adapter shutdown | Stopped immediately; no listener remained on `8088` |
| Chat completion | 1 call, status 200 |
| Selected model | `gemma4:26b` |
| Response content length | 284 |
| Context truncation | 2899 -> 1499 chars |
| Timeout used | 120s |

Conclusion:

The tuned local-summary path produced the first usable Hermes sandbox summary through the localhost adapter.

Recommendation:

Phase 5AB should repeat the same tuned settings for `sandbox/input/sample_prd.md` only, still using an isolated `HERMES_HOME`, foreground adapter, no cloud credentials, and no background services.
