# Hermes Pilot Mode

Phase: 5AB-AC
Status: infrastructure prepared; live pilot not run

## Purpose

Hermes pilot mode is a limited local reasoning harness for the Mac mini. It lets Hermes summarize approved local repo documents and recommend next actions through the localhost MSR Model Router Adapter while Codex or the human operator retains execution control.

Pilot mode is not resident mode, not autonomous execution, and not Desktop validation.

## Components

| Component | Path | Purpose |
| --- | --- | --- |
| Adapter runner | `scripts/run_model_router_adapter.sh` | Starts the localhost OpenAI-compatible MSR Model Router Adapter manually in the foreground. |
| Hermes pilot harness | `scripts/run_hermes_pilot.sh` | Runs one isolated Hermes prompt against the localhost adapter. |
| Example env | `config/hermes-pilot.example.env` | Documents safe pilot variables with dummy local key only. |
| Next-action prompt | `sandbox/input/hermes_pilot_next_action_prompt.md` | Template prompt for a future PRD/changelog summary run. |

## Adapter Runner

Run manually only:

```sh
scripts/run_model_router_adapter.sh
```

The runner:

- binds only to `127.0.0.1`
- uses port `8088`
- points `DEVMONSTER_OLLAMA_URL` to `http://100.93.120.124:11434`
- uses `DEVMONSTER_DEFAULT_MODEL=gemma4:26b`
- sets `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120`
- enables `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`
- defaults `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context`
- sets `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500`
- enables metadata-only request, response-shape, and message-structure logging
- refuses non-localhost bind
- refuses non-`8088` pilot port
- prints startup config with dummy/secrets redacted
- runs in the foreground only
- exits on Ctrl-C

The adapter logging contract remains metadata-only. It must not log prompt text, file contents, model output text, API keys, OAuth tokens, Supabase keys, Home Assistant tokens, GitHub tokens, or Helio credentials.

Dry-run guardrail check:

```sh
scripts/run_model_router_adapter.sh --dry-run
```

## Hermes Pilot Harness

Run one explicit prompt:

```sh
scripts/run_hermes_pilot.sh --prompt "Summarize the approved local docs." --stdout
```

Run one explicit prompt file:

```sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md
```

By default, generated stdout is written to:

```text
sandbox/output/hermes_pilot_output.md
```

Use `--stdout` when the task should print to terminal only. Use `--output <path>` only for approved local outputs; by default the harness refuses output outside `sandbox/output`.

The harness:

- uses isolated `HERMES_HOME=/private/tmp/hermes-pilot-home` by default
- writes only the isolated pilot `config.yaml`
- configures Hermes with `model.provider=custom`
- points Hermes only at `http://127.0.0.1:8088/v1`
- uses only `gemma4:26b`
- uses dummy local API key `dummy-local-adapter-key`
- disables CLI platform toolsets with `platform_toolsets.cli: []`
- starts no resident mode
- starts no background service
- does not start the adapter
- requires explicit `--prompt` or `--prompt-file`
- runs Hermes in a sanitized child environment

The sanitized Hermes child process removes real provider and integration variables by using an allowlisted environment. These variables are not passed through:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `HASS_URL`
- `HASS_TOKEN`
- `HELIO_GATEWAY_URL`
- `HELIO_DISPATCHER_MCP_URL`

Dry-run guardrail check:

```sh
scripts/run_hermes_pilot.sh --dry-run --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md
```

## Allowed Pilot Behavior

Hermes may:

- perform safe local reasoning
- summarize explicitly supplied local repo docs
- recommend next actions
- write generated output only to `sandbox/output` unless separately overridden
- print to stdout when `--stdout` is explicitly used

## Disallowed Pilot Behavior

Hermes may not:

- execute shell commands independently
- install software
- send messages
- write Supabase
- connect Google
- control Home Assistant
- launch Hermes Desktop
- modify credentials
- modify persistent Hermes CLI config
- modify files outside `sandbox/output` in pilot mode
- create launchd plists
- run as a background or resident service
- connect GitHub, Helio, Agent Bus, cloud providers, or other external services

## First Pilot Task Template

The first future pilot task template is:

```text
sandbox/input/hermes_pilot_next_action_prompt.md
```

It asks Hermes to read only:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`

and then summarize status, identify the next safest phase, and write recommendation text to stdout only.

Do not run this live pilot task until a later phase explicitly approves it.

## Stop Conditions

Stop immediately if Hermes:

- asks for a real API key
- attempts setup/login
- attempts a tool call
- attempts file writes outside `sandbox/output`
- attempts to connect external services
- recommends launching Desktop despite the current fail-closed signing state
- tries to use a provider other than the localhost adapter
