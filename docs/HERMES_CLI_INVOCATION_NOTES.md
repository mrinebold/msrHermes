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
