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
