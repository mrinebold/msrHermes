# Hermes Model Provider Plan

Planning date: 2026-06-04.

Phase 5F is planning only. Do not connect Hermes to a model, configure credentials, enable autonomous execution, install providers, start background services, connect cloud providers, or run live inference in this phase.

## Goal

Give Hermes a local inference path that preserves Helio's model-routing policy instead of allowing Hermes to talk directly to cloud providers or directly to DevMonster.

## Current Inputs

- Hermes client: installed locally at `~/.hermes/hermes-agent`, not configured for inference.
- Phase 5E result: Hermes CLI starts, but summarization fails closed with `No inference provider configured`.
- Model router: `services/model_router/` is a Python library with routing rules and a DevMonster Ollama provider.
- DevMonster endpoint: `http://100.93.120.124:11434`, Ollama-compatible, previously validated through the Helio router.
- Default model: `gemma4:26b`.
- Cloud providers: OpenAI and Anthropic placeholders only; cloud routing remains disabled and fail-closed.

## Options Evaluated

| Option | Path | Strengths | Risks | Recommendation |
| --- | --- | --- | --- | --- |
| A | Hermes -> DevMonster Ollama directly | Fewest moving parts; Hermes can likely use `model.provider=custom` with an OpenAI-compatible Ollama URL if `/v1` routes work. | Bypasses Helio task policy, audit records, cloud fail-closed placeholders, future approval checks, and provider abstraction. Makes Hermes responsible for knowing DevMonster details. | Reject as the default path. Permit only for emergency diagnostic use with explicit approval. |
| B | Hermes -> MSR Model Router -> DevMonster | Preserves current local-first policy and audit fields; hides DevMonster details from Hermes; keeps cloud providers disabled; supports fail-closed routing. | Requires a small localhost OpenAI-compatible adapter because `services/model_router/` is currently a Python library, not an HTTP server. | Recommended immediate Phase 5F/5G path. |
| C | Hermes -> MSR Model Router -> DevMonster / future providers | Same as B, plus future ability to add approved local or cloud providers behind one governed endpoint. Hermes can keep one provider configuration while Helio controls routing. | Future providers increase governance risk if the router ever permits cloud fallback without explicit policy gates. Requires strict default-deny and audit review. | Recommended target architecture, with current implementation limited to DevMonster only. |

## Recommendation

Use Option C as the recommended architecture:

```text
Hermes -> localhost OpenAI-compatible MSR Model Router adapter -> services/model_router -> DevMonster Gemma
```

Implement Option C initially with only the DevMonster route enabled. This gives Hermes the same stable provider surface now while preserving a governed expansion path for future approved providers.

Hermes should treat the MSR Model Router as its sole inference provider. The router should initially route only to DevMonster Gemma4 through the existing `devmonster_ollama` provider. Future providers may be added behind the router only after explicit approval, with cloud providers remaining fail-closed until approved.

Direct Hermes -> DevMonster must not be the default path. It may be used only as an emergency diagnostic path after explicit approval, and only for low-risk local inference troubleshooting.

This keeps Hermes simple:

```text
Hermes
  |
  | OpenAI-compatible localhost request
  v
MSR Model Router Adapter
  - local-only bind
  - OpenAI-compatible /v1 surface
  - task classification/default task type
  - policy and audit record
  - fail-closed cloud placeholders
  |
  v
services/model_router
  |
  v
DevMonster Ollama over Tailscale
```

## Required Adapter

Hermes expects a model provider endpoint. The safest path is a local OpenAI-compatible adapter in front of `services/model_router`.

The adapter should expose only:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

Adapter requirements:

- bind to `127.0.0.1` only
- no public interface
- no Tailscale bind
- no LAN bind
- no `0.0.0.0`
- no external network exposure
- no launchd/background service until separately approved
- no cloud credentials
- no Supabase, Google Workspace, Home Assistant, GitHub, or Agent Bus access
- accept a Hermes model name such as `msr-router:gemma4`
- map default Hermes chat requests to `task_type=summary` or `task_type=internal_reasoning`
- preserve route records from `ModelRouter.generate`
- redact prompt text from logs by default
- fail closed if the router selects a cloud placeholder or if DevMonster is unavailable

## Hermes Provider Configuration

Hermes can be configured to treat the MSR Model Router as its sole inference provider if the adapter exposes an OpenAI-compatible endpoint.

Proposed future Hermes `config.yaml` shape:

```yaml
model:
  provider: custom
  default: msr-router:gemma4
  base_url: http://127.0.0.1:8787/v1
  api_key: ""
```

Do not apply this configuration in Phase 5F.

`api_key` should remain blank for an initial loopback-only adapter. If authentication is later added for defense in depth, use a non-cloud local token stored outside the repository and never reuse OpenAI, Anthropic, GitHub, Supabase, Google, or Home Assistant credentials.

## Environment Variables

Router-side variables:

| Variable | Purpose | Phase 5F status |
| --- | --- | --- |
| `DEVMONSTER_OLLAMA_URL` | DevMonster Ollama base URL, currently `http://100.93.120.124:11434`. | Document only; do not change. |
| `DEVMONSTER_DEFAULT_MODEL` | Deep local reasoning model, currently `gemma4:26b`. | Document only; do not change. |
| `FAST_LOCAL_MODEL` | Optional future quick model, currently placeholder `gemma3:4b`. | Do not use until installed and validated. |
| `GEMMA_TIMEOUT` | Router timeout. Existing default is 30 seconds, but Gemma4 validation took about 68.697 seconds. | Plan a longer timeout for Hermes summarization before live retry. |

Hermes-side variables:

| Variable | Purpose | Phase 5F status |
| --- | --- | --- |
| `HERMES_HOME` | Isolated Hermes runtime home. | Use only for future validation profile isolation. |
| `OPENAI_API_KEY` | Hermes fallback for custom endpoint auth. | Keep unset/blank. |
| `ANTHROPIC_API_KEY` | Cloud provider credential. | Keep unset/blank. |
| `OPENROUTER_API_KEY` | Cloud provider credential. | Keep unset/blank. |
| `GOOGLE_CLIENT_SECRET_FILE`, `GOOGLE_TOKEN_FILE` | Google Workspace. | Keep unset/blank. |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` | Agent Bus/Supabase. | Keep unset/blank for Hermes. |
| `HASS_URL`, `HASS_TOKEN` | Home Assistant. | Keep unset/blank. |

## Security Implications

Option A would give Hermes direct knowledge of DevMonster and would bypass Helio's policy and audit layer. That is not acceptable for resident operation.

Option B/C keeps the security boundary in the right place:

- Hermes has one local inference endpoint.
- The router owns provider selection.
- Cloud providers remain disabled.
- DevMonster details stay out of Hermes config.
- Future provider expansion happens behind Helio policy, not inside Hermes.
- Credential-free operation remains possible for a localhost adapter.

Required controls:

- bind adapter to `127.0.0.1`
- do not expose on Tailscale or public interfaces
- do not configure cloud credentials
- do not enable Hermes fallback providers
- disable or constrain unnecessary Hermes provider/plugin surfaces before resident operation
- log route metadata, not prompt contents, by default
- require human approval before any task category involving shell writes, external writes, Google, Home Assistant, GitHub mutations, Supabase, Agent Bus writes, or agent dispatch

## Audit Implications

The router should record:

- request ID
- timestamp
- actor: `hermes`
- task type
- selected provider
- selected model
- elapsed time
- route decision
- approval requirement
- outcome
- error class, if any

Do not log:

- API keys
- OAuth tokens
- Supabase keys
- raw prompts by default
- raw model outputs by default
- local file contents unless explicitly approved

The current `RouteResponse` already returns provider, model, task type, timestamp, elapsed seconds, and approval requirement. The adapter should persist or emit those fields as structured audit events.

## Fail-Closed Behavior

Hermes should fail closed when:

- the local adapter is not running
- the adapter is bound anywhere other than loopback
- the adapter cannot reach DevMonster
- DevMonster times out
- the router selects a cloud placeholder
- a request is classified as requiring human approval and no approval is present
- a prompt tries to trigger shell execution, Google, Home Assistant, Supabase, GitHub mutation, Agent Bus access, or agent dispatch
- provider/plugin discovery attempts to install dependencies or register unexpected provider surfaces in the constrained profile

Phase 5E's non-zero `No inference provider configured` result is an acceptable fail-closed baseline. Phase 5F should preserve that posture until the local router adapter is explicitly approved.

## Sole Provider Determination

Hermes can be configured to treat the MSR Model Router as its sole inference provider if all of these are true:

1. The router adapter exposes an OpenAI-compatible `/v1` API.
2. Hermes `model.provider` is set to `custom`.
3. Hermes `model.base_url` points only to `http://127.0.0.1:<approved-port>/v1`.
4. Hermes cloud credential environment variables remain unset.
5. Hermes fallback providers are not configured.
6. Hermes auxiliary/delegation models are not configured to use cloud providers.
7. Provider/plugin surfaces are reviewed so local-only runs do not attempt unexpected lazy dependency installs or cloud provider registration.

Until the adapter exists, Hermes cannot use `services/model_router/` directly as a provider.

## Phase 5G Proposal

Next implementation phase:

Phase 5G: Build localhost OpenAI-compatible Model Router adapter.

1. Add a small local adapter for `services/model_router`.
2. Expose only `GET /health`, `GET /v1/models`, and `POST /v1/chat/completions`.
3. Bind only to `127.0.0.1`.
4. Add mocked tests for health, model listing, chat-completion mapping, cloud fail-closed behavior, timeout handling, loopback binding, and redacted audit output.
5. Do not expose the adapter externally.
6. Do not start the adapter as a background service.
7. Do not configure Hermes yet.
8. Do not run live prompts.
9. Do not configure cloud providers.
10. After tests pass, request a separate validation phase to run Hermes against the adapter using sandbox files.

## Phase 5H Retry Result

Status: complete on 2026-06-04 after DevMonster repair.

The adapter was started manually in the foreground with:

```sh
MODEL_ROUTER_ADAPTER_HOST=127.0.0.1
MODEL_ROUTER_ADAPTER_PORT=8088
DEVMONSTER_OLLAMA_URL=http://100.93.120.124:11434
DEVMONSTER_DEFAULT_MODEL=gemma4:26b
```

Validation results:

| Check | Result |
| --- | --- |
| `GET /health` | 200 in 0.005s |
| `GET /v1/models` | 200 in 0.095s; included `gemma4:26b` |
| `POST /v1/chat/completions` | 200 in 15.179s |
| Response text | `Adapter operational.` |
| Selected model | `gemma4:26b` |
| Selected provider | `devmonster_ollama` |
| Route task type | `summary` |
| Unknown endpoint | `GET /v1/embeddings` returned 404 in 0.001s |
| Bind exposure | `127.0.0.1:8088` only |
| Shutdown | Adapter stopped after validation; no listener remained on port `8088` |

No Hermes configuration, background service, external exposure, cloud provider, Google Workspace, Supabase, Home Assistant, or Helio connection was made.

The next phase should validate Hermes against this localhost adapter using sandbox data only, without changing permanent Hermes configuration.

## Phase 5I Hermes Sandbox Result

Status: complete on 2026-06-04.

Hermes was run with a temporary isolated `HERMES_HOME` configured to use only the localhost adapter:

```yaml
model:
  provider: custom
  default: gemma4:26b
  base_url: http://127.0.0.1:8088/v1
  api_key: dummy-local-adapter-key
```

The adapter was started manually in the foreground on `127.0.0.1:8088` and stopped immediately after inspection. No persistent Hermes config was changed.

Validation results:

| Check | Result |
| --- | --- |
| Hermes startup | 0.394s, exit 0 |
| `sample_note.md` chat attempt | exit 0 in 60.676s; no summary file created |
| `sample_prd.md` chat attempt | exit 0 in 36.896s; no summary file created |
| `sample_note.md` one-shot summary | exit 0 in 105.852s; `sample_note_summary.md` created |
| `sample_prd.md` one-shot summary | exit 0 in 94.954s; `sample_prd_summary.md` created |
| Output file sizes | 8 bytes each |
| Output quality | Not usable; both output files contain only `(empty)` |
| Stderr | empty for one-shot runs |
| Adapter logs | no per-request lines emitted in the foreground stream |
| Adapter bind | manually checked as `127.0.0.1:8088` only before shutdown |
| Shutdown | adapter stopped; no listener remained on port `8088` |

Hermes was configured only with the localhost adapter and a dummy local key. No real OpenAI, Anthropic, OpenRouter, Google, Supabase, Home Assistant, GitHub, or Helio credentials were provided.

Phase 5I proves Hermes can be pointed at the local adapter in an isolated home, but it does not yet prove usable summarization through Hermes. The next investigation should determine why Hermes returns `(empty)` despite the adapter working for direct OpenAI-compatible chat-completion calls.

## Phase 5J Observability and CLI Diagnosis

Status: complete on 2026-06-04.

The localhost Model Router adapter now supports optional request metadata logging through:

```text
MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true
```

When enabled, logs include timestamp, method, path, response status, selected model when available, and elapsed time. Logs intentionally omit prompt text, message content, API keys, OAuth tokens, Supabase keys, and other secrets by default.

Hermes CLI help and bundled local docs were inspected without sending prompts. Findings:

- Top-level `hermes -z` / `hermes --oneshot` is the intended scriptable one-shot invocation and should print only final response text to stdout.
- `hermes chat -q` is non-interactive chat, and `-Q` quiet mode may still include session information.
- The installed Hermes version has no `hermes run` command.
- Local OpenAI-compatible endpoints should use top-level `model.provider: custom` plus `model.base_url`.
- `model.base_url` should point only to `http://127.0.0.1:8088/v1` for the sandbox adapter path.

Phase 5J did not run Hermes against a live prompt, did not change persistent Hermes config, did not start background services, and did not connect cloud providers or external integrations.

Next recommended phase:

Phase 5K should run exactly one bounded `hermes -z` sandbox diagnostic with the adapter started manually on `127.0.0.1:8088` and request logging enabled, then inspect only stdout, stderr, output file size, and adapter request metadata.

## Phase 5K Oneshot Adapter Diagnostic

Status: complete on 2026-06-04.

Hermes was run exactly once with:

```text
hermes -z "Reply with exactly: Hermes adapter diagnostic."
```

The run used a temporary isolated `HERMES_HOME` with only `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging enabled and stopped immediately after the run.

Validation results:

| Check | Result |
| --- | --- |
| Timeout | 180s cap; no timeout |
| Hermes exit code | 0 |
| Hermes elapsed time | 45.539s |
| Stdout | 8 bytes: `(empty)` |
| Stderr | 0 bytes |
| Adapter request logging | confirmed |
| Adapter chat calls | 4 `POST /v1/chat/completions` requests |
| Chat status/model | all 200 with selected model `gemma4:26b` |
| Adapter chat elapsed times | 28.035s, 2.366s, 3.607s, 7.895s |
| Adapter shutdown | stopped after diagnostic; no `8088` listener remained |

Hermes also issued discovery probes that the approved adapter surface does not implement: `/api/v1/models`, `/api/tags`, `/v1/props`, `/props`, `/version`, `/api/show`, and `/v1/models/gemma4:26b`. These returned 404 as expected for the current constrained adapter.

Conclusion:

Hermes `-z` does call the localhost Model Router adapter, and the adapter successfully routes chat-completion calls to DevMonster Gemma through `services/model_router`. However, Hermes still prints `(empty)` to stdout, so the remaining issue is a Hermes/custom-provider response-contract or output-handling mismatch rather than adapter reachability.

Next recommended phase:

Phase 5L should inspect Hermes custom-provider response parsing and model capability discovery locally before another live prompt. Do not broaden the adapter surface, add streaming support, or rerun live prompts until the expected Hermes wire contract is understood.

## Phase 5L Response Contract Diagnosis

Status: complete on 2026-06-04.

Hermes source was inspected locally under `~/.hermes/hermes-agent` without modifying Hermes and without sending live prompts.

Contract findings:

- Hermes non-streaming chat completions parse `response.choices[0].message.content`.
- Hermes also reads `choices[0].finish_reason`, optional `choices[0].message.tool_calls`, optional reasoning fields, and optional `usage`.
- Hermes does not use `output_text` for the chat-completions transport.
- Hermes' default chat-completions path prefers streaming, including quiet one-shot mode.
- Hermes sends `stream=True` plus `stream_options={"include_usage": True}` for OpenAI-compatible streaming.
- Hermes streaming aggregation expects SSE chunks with `choices[0].delta.content` and a terminal `finish_reason`.

Adapter comparison:

- The adapter's non-streaming JSON includes `choices[0].message.content`, `finish_reason`, and `usage`, so the non-streaming shape is compatible.
- The adapter does not yet implement SSE streaming for `stream=true`.
- Returning ordinary non-streaming JSON to a streaming request is the likely cause of Hermes receiving 200 responses but eventually returning `(empty)`.

Phase 5L also added metadata-only response-shape logging behind:

```text
MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true
```

The log records top-level keys, choices count, assistant content length, finish reason, and whether streaming was requested. It does not log prompt text, model output, or secrets.

Recommended adapter fix:

Implement OpenAI-compatible SSE responses inside the existing `POST /v1/chat/completions` endpoint when `stream=true`. The initial implementation may stream the completed router response as one content chunk after model generation completes. Keep the current non-streaming JSON path for requests without `stream=true`.

Do not add new Hermes discovery endpoints in the same fix. The unsupported discovery probes from Phase 5K should remain a separate compatibility decision because Phase 5G intentionally limited the adapter surface.

## Phase 5M Streaming SSE Support

Status: complete on 2026-06-04.

The adapter now supports the OpenAI-compatible streaming behavior Hermes expects on the existing chat-completions endpoint.

Implemented behavior:

| Request | Response |
| --- | --- |
| `POST /v1/chat/completions` with `stream=true` | `text/event-stream` with one content delta chunk, one finish chunk, then `data: [DONE]` |
| `POST /v1/chat/completions` with `stream=false` | Existing non-streaming JSON response |
| `POST /v1/chat/completions` without `stream` | Existing non-streaming JSON response |

The first streaming implementation remains simple and governed: it waits for `services/model_router` to complete, then emits a valid SSE transcript. This fixes the wire contract Hermes expects without exposing new endpoints, changing Hermes configuration, adding credentials, or starting background services.

Mocked tests cover:

- `stream=true` returns `text/event-stream`
- `stream=true` includes `choices[0].delta.content`
- `stream=true` ends with `data: [DONE]`
- `stream=false` keeps JSON behavior
- response-shape logging remains metadata-only
- unknown endpoints still return 404

Next recommended phase:

Phase 5N should run one bounded live `hermes -z` adapter diagnostic against the SSE-enabled adapter. Keep it separate from file-summary validation and from any decision to support Hermes' optional discovery probes.

## Phase 5N Oneshot After SSE Fix

Status: complete on 2026-06-04.

Hermes was run exactly once with:

```text
hermes -z "Reply with exactly: Hermes adapter diagnostic."
```

The run used a temporary isolated `HERMES_HOME` with only `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. The adapter was started manually in the foreground on `127.0.0.1:8088` with request logging and response-shape logging enabled, then stopped immediately after the run.

Validation results:

| Check | Result |
| --- | --- |
| Timeout | 180s cap; no timeout |
| Hermes exit code | 0 |
| Hermes elapsed time | 18.712s |
| Stdout | 27 bytes: `Hermes adapter diagnostic.` |
| Stderr | 0 bytes |
| Adapter chat calls | 1 `POST /v1/chat/completions` request |
| Chat status/model | 200 with selected model `gemma4:26b` |
| Adapter chat elapsed time | 14.976s |
| Response-shape metadata | `streaming_requested=true`, `choices_count=1`, `content_length=26`, `finish_reason=stop` |
| Adapter shutdown | stopped after diagnostic; no `8088` listener remained |

Conclusion:

The Phase 5M SSE implementation fixed the `hermes -z` stdout path for the bounded diagnostic. Hermes now returns usable stdout through the localhost adapter and DevMonster Gemma path.

Hermes still issues unsupported discovery probes such as `/api/v1/models`, `/api/tags`, `/v1/props`, `/props`, `/version`, `/api/show`, and `/v1/models/gemma4:26b`. Those 404s did not block the one-shot diagnostic. Discovery compatibility should remain a separate decision from sandbox file-summary validation.

Next recommended phase:

Phase 5O should validate sandbox file summaries through the SSE-enabled adapter using synthetic sandbox inputs only. Keep the adapter manual/foreground, keep `HERMES_HOME` isolated, and do not configure Hermes persistently.

## Phase 5O Sandbox Summaries After SSE Fix

Status: complete on 2026-06-04.

Hermes ran two bounded one-shot summary commands using a temporary isolated `HERMES_HOME`, dummy local API key, and the SSE-enabled adapter on `127.0.0.1:8088`. The adapter was stopped immediately after both runs.

Validation results:

| File | Exit code | Elapsed | Stdout | Stderr | Output quality |
| --- | ---: | ---: | ---: | ---: | --- |
| `sandbox/input/sample_note.md` | 0 | 36.241s | 8 bytes: `(empty)` | 0 bytes | Not usable |
| `sandbox/input/sample_prd.md` | 0 | 17.647s | 8 bytes: `(empty)` | 0 bytes | Not usable |

Adapter evidence:

- 8 total `POST /v1/chat/completions` calls returned status 200 with selected model `gemma4:26b`.
- 8 response-shape records showed `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`.
- The SSE path was used, but the router/model returned no visible content for these file-summary runs.
- Unsupported Hermes discovery probes remained 404 and did not block execution.

Conclusion:

The Phase 5M SSE fix remains valid because Phase 5N proved simple one-shot stdout works. Phase 5O shows the next blocker is specific to Hermes' file-summary workflow: either local file access/tool invocation in isolated `-z` mode, prompt structure, or model/router behavior for these more complex prompts. The outputs should not be treated as usable summaries.

Next recommended phase:

Phase 5P should diagnose local file-summary behavior before another live summary attempt. Inspect Hermes one-shot toolset configuration, local file read tool availability, and whether the file-summary prompt needs explicit content injection or approved `--toolsets` selection.

## Phase 5P File Summary Prompt Diagnosis

Status: complete on 2026-06-04.

No live prompts were run in Phase 5P. The local adapter/router prompt path and Hermes one-shot chat-completions path were inspected.

Findings:

- The adapter reads all OpenAI-style messages in order, preserving role labels in the generated router prompt.
- The adapter does not choose only the first message, last message, or only user messages.
- The router does not inspect OpenAI message structures; it receives a plain prompt string from the adapter and passes it to the selected provider.
- The DevMonster provider sends that prompt to Ollama `/api/generate` with `stream=false` and maps Ollama's `response` field into the adapter's chat-completion content.
- Hermes `-z` still runs the full `AIAgent` chat path. Depending on toolsets and prompt behavior, file-summary attempts may include multi-message context, tool schemas, tool-choice hints, and repeated tool/retry turns.
- The constrained localhost adapter does not execute Hermes tools. If Hermes expects a tool loop to read files, the model may never receive the actual sandbox file contents.

Phase 5P added optional message-structure logging behind:

```text
MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true
```

The log records only metadata: message count, roles present, character counts per message, final-user-message emptiness, file-content heuristic status, whether `tools` and `tool_choice` are present, and whether `max_tokens`, `temperature`, and `stream` are present. It does not log prompt text, file contents, tool descriptions, model output, API keys, OAuth tokens, Supabase keys, or other secrets.

Recommendation:

Phase 5Q should run a single bounded file-summary diagnostic with request, response-shape, and message-structure logging enabled. If no message contains file content, use explicit sandbox file content injection or an approved local-only Hermes file-read invocation pattern before attempting summaries again. If messages do contain file content and output remains zero length, focus on prompt simplification and DevMonster Gemma response behavior rather than adapter transport.

## Phase 5Q File Summary Metadata Diagnostic

Status: complete on 2026-06-04.

Hermes was run exactly once against `sandbox/input/sample_note.md` using an isolated temporary `HERMES_HOME`, localhost adapter configuration, `gemma4:26b`, and a dummy local API key. The adapter ran manually in the foreground on `127.0.0.1:8088` with request, response-shape, and message-structure logging enabled.

Run result:

| Check | Result |
| --- | --- |
| Exit code | 0 |
| Elapsed time | 33.501s |
| Timeout | 240s cap; no timeout |
| Stdout bytes | 8 |
| Stderr bytes | 0 |
| Output usable | No |

Adapter evidence:

- Hermes made four `POST /v1/chat/completions` calls.
- All four calls returned 200 with selected model `gemma4:26b`.
- All four response-shape records had `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`.
- All four message-structure records had two messages with roles `system` and `user`.
- Character counts were `[5630, 71]` for each call.
- The final user message was not empty.
- File-like content appeared present by length/shape.
- `tools` were present, `tool_choice` was absent, `stream` was present, and `max_tokens`/`temperature` were absent.

Conclusion:

The adapter is receiving non-empty, file-like context from Hermes. The failure is no longer likely to be missing file access alone. The likely issue is how Hermes' tool-present multi-message prompt shape interacts with the constrained adapter, which forwards text to the model router but does not execute Hermes tools or continue a model/tool loop. DevMonster Gemma is returning empty text for this shape.

Recommendation:

Phase 5R should isolate prompt-shape behavior before another Hermes file-summary run. Preferred next checks are adapter-level and metadata-only: compare a plain user-only injected-content summary, the same content without `tools`, and the Hermes-like tool-present shape. Keep cloud providers fail-closed and avoid persistent Hermes configuration.

## Phase 5R Tool Payload Compatibility

Status: complete on 2026-06-04.

No live Hermes prompts or live model calls were run. Local Hermes source was inspected only enough to confirm why `tools` are included: `hermes -z` constructs a normal `AIAgent`, uses configured CLI toolsets when no explicit toolsets are passed, and forwards `agent.tools` into chat-completion kwargs.

Adapter/router diagnosis:

- `tools` and `tool_choice` are currently ignored for routing.
- The adapter converts all message text into one plain prompt and sends that prompt to `services/model_router`.
- The router and DevMonster provider never receive tool schemas as executable tools.
- Current behavior with `tools` present is therefore equivalent to stripping tools before routing.
- The remaining compatibility issue is the Hermes multi-message system/user prompt shape that local Gemma receives.

Mocked tests covered:

| Case | Result |
| --- | --- |
| A. tools passed through unchanged | Router prompt includes message text only; tool metadata is absent. |
| B. tools stripped | Router prompt is identical to A. |
| C. messages flattened into a single Gemma-friendly prompt | Router receives a simpler single-user prompt shape. |
| D. tools stripped plus messages flattened | Router receives the same simplified prompt without tool metadata. |

Recommendation:

For the DevMonster Gemma route, implement a local compatibility mode that strips tool semantics and flattens messages into a single Gemma-friendly prompt. Preserve future provider extensibility, but treat local Gemma as non-tool-capable until the router has a real tool execution contract.

Next recommended phase:

Phase 5S should implement the compatibility mode with mocked tests only. Do not run Hermes live prompts until the adapter behavior is implemented and reviewed.

## Phase 5S Local Gemma Compatibility Implementation

Status: complete on 2026-06-05.

The localhost adapter now has an opt-in local compatibility mode:

```text
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
```

For local Gemma requests, compatibility mode:

- ignores `tools` and `tool_choice` for routing
- flattens Hermes multi-message payloads into one role-labeled prompt
- preserves plain role labels as `[system]`, `[developer]`, `[user]`, `[assistant]`, or `[tool]`
- extracts safe text from structured content parts and omits non-text parts
- fails closed when no non-empty user content is available
- preserves streaming SSE behavior
- emits metadata-only prompt-flattening diagnostics when message-structure logging is enabled

Existing behavior remains unchanged when compatibility mode is disabled.

No live Hermes prompts, live model calls, provider installs, persistent Hermes config changes, cloud credentials, or external integrations were used.

Next recommended phase:

Phase 5T should validate one bounded Hermes `sample_note.md` file-summary retry with local compat mode enabled. Keep `sample_prd.md` out of scope until the sample-note result is usable or a new local blocker is documented.

## Phase 5T Live File Summary Retry

Status: complete on 2026-06-05.

Hermes was run exactly once against `sandbox/input/sample_note.md` using an isolated temporary `HERMES_HOME`, localhost adapter configuration, `gemma4:26b`, a dummy local API key, and `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`.

Run result:

| Check | Result |
| --- | --- |
| Exit code | 0 |
| Elapsed time | 52.126s |
| Timeout | 240s cap; no timeout |
| Stdout bytes | 8 |
| Stderr bytes | 0 |
| Output usable | No |

Adapter evidence:

- Hermes made four `POST /v1/chat/completions` calls.
- All four calls returned 200 with selected model `gemma4:26b`.
- All four response-shape records had `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`.
- All four compat metadata records had `compat_mode_enabled=true`, `flattened_message_count=2`, `flattened_prompt_chars=5724`, `tool_schemas_present=true`, and `tool_schemas_forwarded=false`.

Conclusion:

The local Gemma compatibility mode activated correctly and prevented tool schemas from reaching the router prompt, but the file-summary output remained unusable. The next issue is likely the Gemma-facing prompt content or ordering rather than adapter transport or tool-schema forwarding.

Next recommended phase:

Phase 5U should isolate prompt variants before another Hermes retry. Prefer adapter-level or direct-router diagnostics using synthetic sandbox content: final-user-first ordering, system scaffold demotion/truncation, and a dedicated file-summary prompt shape.

## Phase DESKTOP-1 Desktop Provider Timing

Status: planning only on 2026-06-05.

Phase 5AA confirmed the CLI path can produce useful `sample_note.md` sandbox output through the localhost MSR Model Router adapter. Hermes Desktop is now planned for Mac mini and DevMonster, but must not be installed, opened, or configured until a later phase explicitly approves that work. Desktop should inherit the same local-first model policy:

- local adapter first
- `http://127.0.0.1:8088/v1` if Desktop supports a custom OpenAI-compatible endpoint
- `gemma4:26b` through `services/model_router`
- cloud providers fail-closed
- no real provider API keys
- no Nous Portal login until explicitly approved

Desktop must not become an alternate route around the MSR model router. If Desktop cannot use the localhost adapter without cloud login or durable credentials, Desktop validation should stop and record the blocker.

DevMonster-specific rule: Desktop on DevMonster is a human-facing workstation UI only. It must not change DevMonster Ollama/Gemma serving, Tailscale binding, host binding, launch behavior, firewall/network exposure, or the approved model-worker configuration. Direct Desktop-to-Ollama routing is not the default path; keep the localhost OpenAI-compatible adapter as the configured model surface if Desktop supports it.

Reference:

- [Hermes Desktop Install Plan](HERMES_DESKTOP_INSTALL_PLAN.md)
- [Hermes Desktop DevMonster Plan](HERMES_DESKTOP_DEVMONSTER_PLAN.md)

## Phase 5U Gemma Prompt Construction Diagnosis

Status: complete on 2026-06-05.

Phase 5U ran no live Hermes prompts and sent no live model calls. It inspected the adapter's local Gemma prompt construction path and added metadata-only diagnostics for the prompt shape that reaches `services/model_router`.

Added adapter diagnostics:

- flattened prompt total characters
- role sections included
- section order
- first/last prompt snippet logging fixed at 0 characters
- markdown fence count
- XML/tool-like tag count
- JSON-looking block count
- plain `tool`, `function`, `schema`, and `call` keyword counts
- final user content start index
- user/system character counts and dominance flag

Added local compat prompt-mode selector:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=flattened|user_only|final_user|instruction_context|no_tool_vocab
```

The default remains `flattened`, so existing behavior is unchanged unless a bounded diagnostic explicitly selects another mode.

Prompt modes:

| Mode | Use |
| --- | --- |
| `flattened` | Preserve current role-labeled order. |
| `user_only` | Drop system/assistant context and keep user messages only. |
| `final_user` | Keep only the final user instruction. |
| `instruction_context` | Move final user instruction first, then append prior context. |
| `no_tool_vocab` | Preserve flattened sections but remove plain tool/function/schema/call vocabulary. |

Recommendation:

For the next live Hermes file-summary retry, use `instruction_context` with `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`. This is the safest first variant because it preserves file-like context while moving the concise final instruction ahead of Hermes' large system scaffold. Keep cloud providers fail-closed, keep the adapter localhost-only, and do not configure Hermes persistently.

## Phase 5V Instruction-Context Live Retry

Status: complete on 2026-06-05.

One bounded Hermes `sample_note.md` file-summary retry was run with:

```text
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context
```

Hermes used an isolated temporary `HERMES_HOME` with only `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. The adapter was started manually in the foreground on `127.0.0.1:8088` and stopped immediately after validation.

Validation results:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Hermes exit code | 0 |
| Hermes elapsed time | 58.639s |
| Stdout | 8 bytes: `(empty)` |
| Stderr | 0 bytes |
| Output usable | No |
| `GET /v1/models` | 2 calls, both 200 |
| `POST /v1/chat/completions` | 4 calls, all 200 with selected model `gemma4:26b` |
| Unsupported discovery probes | 17 calls, all 404 |
| Adapter shutdown | stopped; no `8088` listener remained |

Prompt and response metadata:

| Field | Value |
| --- | --- |
| Prompt mode | `instruction_context` |
| Compat mode | true |
| Prompt chars | 5729 |
| Message count | 2 |
| Message char counts | `[5628, 83]` |
| Final user content start index | 7 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Response content length | 0 for all four chat calls |

Conclusion:

`instruction_context` is mechanically correct but does not resolve the file-summary zero-content behavior. The next likely prompt issue is remaining Hermes tool/call vocabulary or agent scaffold text inside message content.

Recommendation:

The next live attempt, if approved, should be another single `sample_note.md` retry using `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=no_tool_vocab`, or an implementation phase should add a stronger local summary prompt mode that extracts only the final instruction and file-like context while dropping Hermes tool scaffold. Do not run `sample_prd.md`, configure Hermes persistently, or broaden provider access until `sample_note.md` produces usable output.

## Phase 5W No-Tool-Vocabulary Live Retry

Status: complete on 2026-06-05.

One bounded Hermes `sample_note.md` file-summary retry was run with:

```text
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=no_tool_vocab
```

Hermes used an isolated temporary `HERMES_HOME` with only `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. The adapter was started manually in the foreground on `127.0.0.1:8088` and stopped immediately after validation.

Validation results:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Hermes exit code | 0 |
| Hermes elapsed time | 39.471s |
| Stdout | 8 bytes: `(empty)` |
| Stderr | 0 bytes |
| Output usable | No |
| `GET /v1/models` | 2 calls, both 200 |
| `POST /v1/chat/completions` | 4 calls, all 200 with selected model `gemma4:26b` |
| Unsupported discovery probes | 17 calls, all 404 |
| Adapter shutdown | stopped; no `8088` listener remained |

Prompt and response metadata:

| Field | Value |
| --- | --- |
| Prompt mode | `no_tool_vocab` |
| Compat mode | true |
| Prompt chars | 5689 |
| Message count | 2 |
| Message char counts | `[5628, 83]` |
| Final user content start index | 5606 |
| Tool schemas present | true |
| Tool schemas forwarded | false |
| Tool/function/schema/call keyword counts | all 0 |
| Response content length | 0 for all four chat calls |

Conclusion:

`no_tool_vocab` is mechanically correct but does not resolve the file-summary zero-content behavior. The result rules out plain tool/function/schema/call vocabulary as the sole cause. The final user instruction also remained after the large Hermes system scaffold because this mode preserves flattened ordering.

Recommendation:

Do not continue with more live one-toggle retries. The next phase should implement a purpose-built local summary prompt mode that extracts the final instruction and file-like context, puts the instruction first, removes tool vocabulary, and drops unrelated Hermes agent scaffold before routing to local Gemma. Keep the adapter localhost-only and keep cloud providers fail-closed.

## Phase 5X Local Summary Prompt Mode

Status: complete on 2026-06-05.

Phase 5X added an opt-in compact prompt mode for local Gemma file-summary validation:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
```

No live Hermes prompt, live model call, cloud provider, real API key, persistent Hermes config, background service, Google, Supabase, Home Assistant, Helio, Agent Bus access, or autonomous execution was used.

The mode builds a Gemma-facing prompt from:

1. The latest user message as the explicit instruction.
2. File-like context extracted from the user message if present.
3. File-like system/developer context only when needed to preserve the document body.

It omits:

- tool schema JSON
- tool-choice semantics
- role-labeled full transcript
- unrelated Hermes agent/system scaffold
- hidden/system-like tool instructions

It fails closed with `400` when no useful instruction and file-like context pair can be identified.

Metadata-only logs include `instruction_chars`, `context_chars`, `dropped_system_chars`, `dropped_tool_schema_count`, and `local_summary_extraction_success`. They do not log actual instructions, file contents, prompt text, tool schemas, model output, or secrets.

Recommendation:

Phase 5Y should run one bounded live `sample_note.md` retry with local compat mode and `local_summary`. Do not run `sample_prd.md` until `sample_note.md` produces usable output.

## Phase 5Y Local Summary Live Validation

Status: complete on 2026-06-05.

One bounded Hermes `sample_note.md` retry was run with:

```text
MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
```

Hermes used an isolated temporary `HERMES_HOME` with only `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. The adapter was started manually in the foreground on `127.0.0.1:8088` and stopped immediately after validation.

Validation results:

| Check | Result |
| --- | --- |
| Timeout | 240s cap; no timeout |
| Hermes exit code | 0 |
| Hermes elapsed time | 101.268s |
| Stdout | 110 bytes; provider timeout diagnostic |
| Stderr | 0 bytes |
| Output usable | No |
| `GET /v1/models` | 2 calls, both 200 |
| `POST /v1/chat/completions` | 3 calls, all 502 with selected model `gemma4:26b` |
| Unsupported discovery probes | 17 calls, all 404 |
| Adapter shutdown | stopped; no `8088` listener remained |

Prompt metadata:

| Field | Value |
| --- | --- |
| Prompt mode | `local_summary` |
| Extraction success | true |
| Prompt chars | 3139 |
| Instruction chars | 83 |
| Context chars | 2899 |
| Dropped system chars | 5628 |
| Dropped tool schema count | 26 |
| Tool schemas forwarded | false |

Conclusion:

`local_summary` succeeded at prompt extraction and scaffold reduction, but DevMonster/Gemma timed out before returning content. The failure mode moved from zero-content successful responses to provider timeouts.

Recommendation:

Diagnose the router/provider timeout before another Hermes run. Candidate fixes are an approved longer Gemma timeout for local summary tasks, a smaller local-summary context budget, or both. Keep the adapter localhost-only, keep cloud providers fail-closed, and do not run `sample_prd.md` yet.

## Phase 5Z Timeout And Context Budget Tuning

Status: complete on 2026-06-05.

Phase 5Z added offline tuning controls for the Phase 5Y timeout failure. No live Hermes prompts or live model calls were run.

Provider timeout:

```text
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
```

This is now the primary model-router timeout env var. `GEMMA_TIMEOUT` remains as a legacy fallback. The default remains 30 seconds.

Local summary context budget:

```text
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
```

The adapter default is 3000 characters. When the extracted context exceeds the configured budget, `local_summary` preserves the beginning and end of context and inserts a neutral truncation marker. It does not log context text.

New metadata-only fields:

- `context_original_chars`
- `context_sent_chars`
- `context_truncated`
- `timeout_seconds`

Recommendation:

For the next bounded live retry, keep the adapter localhost-only and run one `sample_note.md` validation with local compat mode, `local_summary`, provider timeout 120 seconds, and context budget 1500 characters. Do not run `sample_prd.md` until `sample_note.md` is usable.

## Phase 5AA Tuned Local Summary Success

Status: complete on 2026-06-05.

The tuned local summary validation succeeded with:

```text
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500
```

| Check | Result |
| --- | --- |
| Hermes exit code | 0 |
| Elapsed time | 112.635s |
| Stdout | 285 bytes |
| Stderr | 0 bytes |
| Output file | `sandbox/output/sample_note_phase5aa_summary.md` |
| Output usable | Yes |
| Adapter shutdown | stopped; no `8088` listener remained |
| Chat completion | 1 call, status 200 |
| Selected model | `gemma4:26b` |
| Response content length | 284 |
| Context truncation | 2899 -> 1499 chars |
| Timeout used | 120s |

Conclusion:

The local adapter can now produce usable Hermes sandbox summary output through the governed localhost model router path.

Recommendation:

Keep these settings as the current validated baseline for Hermes file-summary work. The next live validation should use the same settings for `sample_prd.md` in a separate approved phase.

## Phase 5AB-AC Managed Adapter Runner And Pilot Harness

Status: infrastructure complete on 2026-06-08. Live pilot not run.

Phase 5AB-AC added the local infrastructure needed for a limited Hermes pilot:

- `scripts/run_model_router_adapter.sh`
- `scripts/run_hermes_pilot.sh`
- `config/hermes-pilot.example.env`
- `docs/HERMES_PILOT_MODE.md`
- `sandbox/input/hermes_pilot_next_action_prompt.md`

The managed adapter runner is foreground-only and binds only to `127.0.0.1:8088`. It sets the validated DevMonster route, provider timeout, local compatibility mode, and metadata-only logging. It refuses non-localhost binds and non-`8088` pilot ports. It does not create a launchd plist or background service.

The Hermes pilot harness creates an isolated pilot home at `/private/tmp/hermes-pilot-home` by default and writes only that isolated `config.yaml`. The pilot config points Hermes only to:

```yaml
model:
  provider: custom
  default: gemma4:26b
  base_url: http://127.0.0.1:8088/v1
  api_key: dummy-local-adapter-key
platform_toolsets:
  cli: []
```

The harness runs Hermes with an allowlisted child environment so real cloud, Supabase, Google, GitHub, Home Assistant, and Helio variables are not passed through. It requires an explicit `--prompt` or `--prompt-file`, writes generated output to `sandbox/output` by default, and supports `--stdout` for stdout-only pilot tasks.

The first future pilot prompt template is `sandbox/input/hermes_pilot_next_action_prompt.md`. It asks Hermes to read only the master Hermes PRD and changelog, summarize current status, identify the next safest phase, and write recommendation text to stdout only.

Phase 5AB-AC did not start the adapter, did not run a live Hermes pilot, did not configure persistent Hermes home, did not connect external services, and did not add credentials.

## Phase 5AD Controlled Hermes Pilot Execution

Status: complete on 2026-06-08. Pilot output not usable.

Phase 5AD ran the first bounded Hermes pilot task with the managed foreground adapter runner and locked-down pilot harness:

```sh
scripts/run_model_router_adapter.sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md --stdout
```

Capture files:

- `sandbox/output/hermes_pilot_next_action.md`
- `sandbox/output/hermes_pilot_next_action.stderr`
- `sandbox/output/hermes_pilot_next_action.metrics`

Validation results:

| Check | Result |
| --- | --- |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter model | `gemma4:26b` |
| Provider timeout | 120 seconds |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| Selected model | `gemma4:26b` |
| Response content length | repeated `0` byte completions |
| Pilot stdout bytes | 471 |
| Pilot stderr bytes | 0 |
| Pilot output usable | no; stdout contained only redacted harness config |
| Pilot exit | interrupted after the harness remained stuck following repeated empty responses |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |

The first controlled pilot stayed within the security envelope but did not produce recommendation text. The adapter received Hermes chat-completion calls, routed to DevMonster Gemma, and logged metadata-only message and response shapes. No prompt text, file contents, credentials, or model output text were logged by the adapter.

No background service, launchd plist, persistent Hermes home configuration, cloud credential, Desktop launch, external integration, message send, software install, Supabase write, credential modification, or file write outside `sandbox/output` was performed by Hermes. The only Desktop-related process observed after cleanup was the pre-existing `Hermes-Setup` process from earlier Desktop phases.

Conclusion:

Phase 5AD validates the managed runner/harness guardrails but not pilot usefulness. The current next-action prompt uses the default `instruction_context` adapter mode and does not reproduce the Phase 5AA useful-output baseline, which used `local_summary` with bounded file-like context.

Recommendation:

Do not broaden Hermes pilot authority or run another open-ended pilot unchanged. This recommendation was executed in Phase 5AE by feeding the PRD and changelog as explicit bounded local context through the validated `local_summary` path under the same foreground/no-tools/no-integrations guardrails.

## Phase 5AE Explicit Local Context Pilot

Status: complete on 2026-06-08. Pilot output usable.

Phase 5AE implemented the Phase 5AD recommendation by adding a deterministic prompt builder and a harness mode that keeps runner config off stdout:

- `scripts/build_hermes_pilot_context_prompt.py`
- `scripts/run_hermes_pilot.sh --config-to-stderr`

The builder created:

- `sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md`

The prompt contains a short instruction, bounded excerpts from the master Hermes PRD and changelog, explicit output format, and a `Document/context:` marker so the adapter's validated `local_summary` extraction path can treat the PRD/changelog excerpts as local context. Hermes was not asked to read paths or use tools.

Run configuration:

| Setting | Value |
| --- | --- |
| Adapter runner | foreground only |
| Bind | `127.0.0.1:8088` |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter prompt mode | `local_summary` |
| Provider timeout | 120 seconds |
| Context budget | 1500 chars |
| Hermes home | `/private/tmp/hermes-pilot-home` |
| Hermes base URL | `http://127.0.0.1:8088/v1` |
| Hermes model | `gemma4:26b` |
| Platform tools | disabled |

Validation results:

| Check | Result |
| --- | --- |
| Pilot exit code | 0 |
| Pilot elapsed time | 174 seconds |
| Pilot stdout bytes | 638 |
| Pilot stderr bytes | 471 |
| Adapter model calls | yes |
| Selected model | `gemma4:26b` |
| Local summary extraction | success |
| Context chars | 1426 |
| Context truncated | false |
| Tools present | false |
| Tool schemas forwarded | false |
| First model call | timed out after 120.011 seconds, status `502` |
| Successful retry | status `200`, response content length `637`, elapsed `49.883s` |
| Output usable | yes |
| Adapter shutdown | stopped immediately after run |
| Post-run listener | no `8088` listener remained |

The successful stdout response was a concise four-line recommendation in the requested format. Stderr contained only the redacted harness runner config because `--config-to-stderr` was used.

No background service, launchd plist, persistent Hermes home configuration, cloud credential, Desktop launch, external integration, message send, software install, Supabase write, credential modification, or Hermes-generated write outside `sandbox/output` occurred. No matching Hermes pilot, adapter, or Desktop process remained after cleanup.

Conclusion:

The explicit local-context shape plus `local_summary` mode is now the validated baseline for bounded Hermes next-action pilot work. The first provider call may still time out at 120 seconds, but Hermes can recover on retry and produce usable output without tools or integrations.

Recommendation:

Keep Phase 5AE's explicit-context builder and `--config-to-stderr` harness behavior for future stdout-only pilots. The next phase should either refine the prompt to ask for a forward-looking Phase 5AF recommendation or run one bounded PRD-review task with the same local-only, no-tools, no-background, no-integration guardrails.
