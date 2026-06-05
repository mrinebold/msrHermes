# Hermes Tool Payload Compatibility

Diagnosis date: 2026-06-04.

Phase 5R is an offline adapter/router-boundary diagnosis. No live Hermes prompts were run, no live model calls were sent, no persistent Hermes configuration was changed, and no cloud providers or external integrations were connected.

## Problem

Phase 5Q showed that Hermes file-summary runs send non-empty file-like context to the localhost adapter, but DevMonster Gemma returns zero visible content for every chat-completion call.

Phase 5Q message metadata:

| Field | Value |
| --- | --- |
| Message count | 2 |
| Roles | `system`, `user` |
| Character counts | `[5630, 71]` |
| Final user message empty | false |
| File-like content present | true |
| `tools` present | true |
| `tool_choice` present | false |
| `stream` present | true |
| `max_tokens` present | false |
| `temperature` present | false |

## Hermes Source Finding

Local Hermes source inspection found that `hermes -z` still constructs a normal `AIAgent`. When no explicit `--toolsets` are provided, it uses configured CLI toolsets. Hermes then builds chat-completion kwargs with `tools=agent.tools`, so OpenAI-compatible requests can include tool schemas even for one-shot runs.

The localhost adapter does not execute Hermes tools. It accepts the OpenAI-compatible payload, converts `messages` to a plain prompt string, and delegates to `services/model_router`.

## Adapter Behavior

Current adapter behavior:

- `tools` are not included in the router prompt.
- `tool_choice` is not interpreted.
- All message roles are flattened in order as `role: content`.
- `system`, `developer`, `user`, `assistant`, and `tool` messages are treated as text-bearing messages.
- The router receives only a plain prompt string.
- DevMonster receives that prompt through Ollama `/api/generate`.

This means the current adapter already behaves as if tools are stripped for routing. However, it still preserves Hermes' large system-message shape. For local Gemma, that shape appears less reliable than the simple one-shot prompt shape proven in Phase 5N.

## Mocked Fixture Results

Phase 5R added a sanitized fixture that mimics the Phase 5Q metadata shape without using real prompt text or file contents.

Mocked cases:

| Case | Payload Shape | Router Observation |
| --- | --- | --- |
| A | system + user messages, `tools` present, `stream=true` | Router prompt contains system/user text only; tool name and tool description are absent. |
| B | same messages, `tools` stripped | Router prompt is identical to case A. |
| C | messages pre-flattened into one user message, `tools` present | Router prompt is a single user-oriented prompt; tool metadata is absent. |
| D | pre-flattened one user message, `tools` stripped | Router prompt is the same simplified single-user shape without tool metadata. |

Because cases A and B produce the same router prompt today, tool stripping alone is not enough. Because cases C and D produce a simpler Gemma-facing prompt, the recommended compatibility fix should include prompt flattening, not only payload field removal.

## Recommendation

For the local DevMonster Gemma path, add an explicit adapter compatibility mode that:

1. Treats local Gemma as non-tool-capable.
2. Ignores `tools` and `tool_choice` for routing.
3. Converts Hermes multi-message payloads into a Gemma-friendly single prompt with clear sections:
   - system/developer context
   - prior assistant/tool context if present
   - final user instruction
4. Prioritizes the final non-empty user message as the explicit task.
5. Preserves file-like context in the prompt body without logging it.
6. Keeps streaming SSE response behavior unchanged.
7. Logs only metadata, never prompt text, file contents, tool schemas, or model output.

Preserve the current OpenAI-compatible request surface for future providers, but do not pass tool schemas into DevMonster Gemma until the router has a real tool execution contract.

Recommended next phase:

Phase 5S: implement local Gemma prompt compatibility in `services/model_router_adapter`, guarded by an explicit adapter flag for the current DevMonster route. Add tests for tool-present Hermes payloads, system/developer/user flattening, final-user handling, and metadata-only logging. Do not run Hermes live prompts in the implementation phase unless separately approved.

## Phase 5S Implementation

Implementation date: 2026-06-05.

Phase 5S implemented opt-in local Gemma compatibility behind:

```text
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
```

When compatibility mode is enabled for local Gemma requests, the adapter:

- treats DevMonster Gemma as non-tool-capable
- ignores `tools` and `tool_choice` for routing
- flattens message content into one prompt with role-labeled blocks such as `[system]`, `[user]`, and `[assistant]`
- includes only extracted message text, not tool schema JSON
- extracts text from structured content parts and omits non-text parts
- fails closed with an adapter `400` when no non-empty user content is available
- preserves existing streaming SSE response behavior
- logs only metadata when diagnostics are enabled

Metadata-only compatibility logging includes:

- `compat_mode_enabled`
- `flattened_message_count`
- `flattened_prompt_chars`
- `tool_schemas_present`
- `tool_schemas_forwarded=false`

The adapter never logs the flattened prompt text by default.

Mocked tests cover tool-present flattening, tool-schema exclusion, role labels, structured text extraction, empty-user fail-closed behavior, legacy behavior when compat mode is disabled, SSE preservation, and log redaction.

No live Hermes prompts, live model calls, cloud providers, real API keys, persistent Hermes config, background services, Google, Supabase, Home Assistant, Helio, Agent Bus access, or autonomous execution were used.

Recommended next phase:

Phase 5T should run one bounded Hermes `sample_note.md` file-summary retry with `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`, request logging, response-shape logging, and message-structure logging enabled. Keep the adapter foreground-only, keep `HERMES_HOME` isolated, and do not run `sample_prd.md` until `sample_note.md` produces usable output or a new blocker is diagnosed.

## Phase 5T Validation Result

Validation date: 2026-06-05.

One bounded Hermes `sample_note.md` file-summary retry was run with `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`.

Result:

| Check | Result |
| --- | --- |
| Exit code | 0 |
| Elapsed time | 52.126s |
| Timeout | 240s cap; no timeout |
| Stdout bytes | 8 |
| Stderr bytes | 0 |
| Output usable | No |

Compatibility metadata confirmed the intended adapter behavior:

- `compat_mode_enabled=true`
- `flattened_message_count=2`
- `flattened_prompt_chars=5724`
- `tool_schemas_present=true`
- `tool_schemas_forwarded=false`

All four chat-completion calls returned 200 with selected model `gemma4:26b`, but every response-shape record still had `content_length=0`.

Conclusion:

Local compat mode works mechanically, but it is insufficient for Hermes file summaries. Tool-schema forwarding is no longer a plausible root cause. The next fix should focus on the Gemma-facing prompt itself: prompt ordering, reducing or demoting Hermes' system scaffold, or a dedicated local summarization prompt shape that gives Gemma only the sandbox file text and the summary instruction.

## Phase 5U Prompt Construction Diagnosis

Diagnosis date: 2026-06-05.

Phase 5U added offline prompt-construction diagnostics and mocked prompt modes without running Hermes live prompts or sending live model calls.

The new prompt metadata confirms the next investigation should focus on how local Gemma receives the flattened Hermes transcript, not on tool schemas. The Phase 5T live metadata showed a large system section followed by a small final user instruction. Since tool schemas are not forwarded, remaining likely causes are:

- Hermes system/developer scaffold dominates the prompt.
- The final user instruction appears after the large context.
- Tool/function/schema/call vocabulary appears inside message text even after schema JSON is stripped.
- Markdown, XML-like, or JSON-looking structures inside the prompt may affect local Gemma's response behavior.

The adapter now supports a diagnostic prompt-mode flag for local compat mode:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=flattened|user_only|final_user|instruction_context|no_tool_vocab
```

Recommendation:

Use `instruction_context` for the next bounded live sample-note retry. It keeps local Gemma non-tool-capable, keeps tool schemas out of the prompt, preserves the available file-like context, and moves the concise final user instruction before the large Hermes scaffold.

## Phase 5V Instruction-Context Result

Validation date: 2026-06-05.

The bounded live `sample_note.md` retry with `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context` confirmed that prompt reordering alone is insufficient.

Observed metadata:

| Field | Value |
| --- | --- |
| Chat-completion calls | 4 |
| Status | 200 for all calls |
| Selected model | `gemma4:26b` |
| Prompt mode | `instruction_context` |
| Compat mode | true |
| Prompt chars | 5729 |
| Message count | 2 |
| Message char counts | `[5628, 83]` |
| Final user content start index | 7 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Response content length | 0 for all calls |

Conclusion:

The adapter successfully moved the final instruction ahead of Hermes' large system context and continued to suppress tool schema forwarding, but Gemma still returned zero content. The remaining compatibility issue is likely tool/call vocabulary or broader Hermes system scaffold content inside the message text, not tool schema JSON or instruction order alone.

Recommendation:

Try `no_tool_vocab` next for one bounded `sample_note.md` retry, or implement a purpose-built local summary mode that extracts file-like context and the final instruction while dropping Hermes agent/tool scaffold text.

## Phase 5W No-Tool-Vocabulary Result

Validation date: 2026-06-05.

The bounded live `sample_note.md` retry with `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=no_tool_vocab` confirmed that removing plain tool/function vocabulary alone is insufficient.

Observed metadata:

| Field | Value |
| --- | --- |
| Chat-completion calls | 4 |
| Status | 200 for all calls |
| Selected model | `gemma4:26b` |
| Prompt mode | `no_tool_vocab` |
| Compat mode | true |
| Prompt chars | 5689 |
| Message count | 2 |
| Message char counts | `[5628, 83]` |
| Final user content start index | 5606 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Tool/function/schema/call keyword counts | all 0 |
| Response content length | 0 for all calls |

Conclusion:

The adapter removed the requested vocabulary and still suppressed tool schemas, but Gemma returned zero content. Since `no_tool_vocab` keeps flattened ordering, the final user task stayed after the large Hermes system scaffold. The remaining fix should not be another single toggle; it should be a purpose-built local summary prompt that combines instruction-first ordering with scaffold reduction.

Recommendation:

Implement a local summary prompt mode that extracts the final user instruction and file-like context into a compact Gemma prompt, omits tool vocabulary, and drops unrelated Hermes agent/system scaffold. Keep this opt-in, local-only, and covered by mocked tests before any additional live retry.
