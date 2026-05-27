# Local Worker Plan

## Objective

Run a local DevMonster-oriented worker for private local tasks. Ollama is installed as a local runtime foundation, but no models have been pulled.

## Phases

1. Confirm DevMonster runtime requirements.
2. Inspect existing Ollama installation and available local runtimes.
3. Confirm hardware memory and disk capacity.
4. Select the worker backend and model/runtime package only after approval.
5. Bind worker API to localhost.
6. Add task queue integration and audit logging.

## Guardrails

- No model downloads before approval.
- No public worker endpoint.
- No shell execution from model output without a permission gate.
- Keep generated artifacts scoped to the project workspace unless approved.

## Phase 2B DevMonster Discovery

Discovery date: 2026-05-27.

Retry discovery found DevMonster on the Tailscale mesh.

Observed Tailscale peers:

- `michaels-mac-mini` at `100.80.79.75`, local Mac mini.
- `devmonster-4` at `100.93.120.124`, macOS, online.
- `civic-main` at `100.92.126.17`, Linux, online.
- `iphone-15-pro-max` at `100.92.128.26`, iOS, online.
- `rinebolddomain` at `100.77.8.69`, Windows, online.
- `ipad-pro-12-9-gen-5` at `100.96.95.115`, iOS, offline/expired.

Discovery checks:

- `devmonster-4` appears in Tailscale status.
- `devmonster-4.taila2da57.ts.net` is the MagicDNS name.
- `devmonster-4` responded to Tailscale ping at `100.93.120.124` in about `28ms`.
- `devmonster-4.taila2da57.ts.net` responded to Tailscale ping in about `25ms`.
- `100.93.120.124` responded to Tailscale ping in about `20ms`.

Current conclusion:

- DevMonster host: `devmonster-4`.
- DevMonster MagicDNS name: `devmonster-4.taila2da57.ts.net`.
- DevMonster Tailscale IPv4: `100.93.120.124`.
- DevMonster Tailscale IPv6: `fd7a:115c:a1e0::5937:787c`.
- DevMonster is reachable over Tailscale ping.
- Helio should not call any Gemma endpoint until the OpenAI-compatible scheme, port, path, auth method, and model name are confirmed.

## Expected Gemma4 Endpoint Test Plan

Requires explicit approval before any endpoint call.

1. Confirm the OpenAI-compatible base URL for `devmonster-4`, including scheme and port.
2. Confirm `GEMMA_MODEL`, timeout, and authentication requirement.
3. Store `GEMMA_BASE_URL`, `GEMMA_API_KEY`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` only in an approved untracked local env file.
4. Check only metadata first, such as `/v1/models`, if available.
5. Run one minimal non-sensitive inference request only after separate approval.
6. Benchmark latency and timeout behavior before any autonomous routing.

## Phase 2C Endpoint Discovery

Discovery date: 2026-05-27.

Target:

- Host: `devmonster-4`.
- Tailscale IPv4: `100.93.120.124`.
- MagicDNS: `devmonster-4.taila2da57.ts.net`.

Approved non-invasive checks:

- `HEAD /`
- `GET /`
- `GET /v1/models`
- `GET /api/tags`

Ports checked:

- `11434`, common Ollama API port.
- `8000`, common local model/API server port.
- `8080`, common application/API server port.
- `3000`, common development server port.

Results:

- Preferred MagicDNS target `devmonster-4.taila2da57.ts.net` did not resolve for `/usr/bin/curl` during this retry.
- Fallback target `100.93.120.124` was used for port checks.
- Port `11434`: connection refused for `HEAD /`, `GET /`, `GET /v1/models`, and `GET /api/tags`.
- Port `8000`: connection refused for `HEAD /`, `GET /`, `GET /v1/models`, and `GET /api/tags`.
- Port `8080`: connection refused for `HEAD /`, `GET /`, `GET /v1/models`, and `GET /api/tags`.
- Port `3000`: connection refused for `HEAD /`, `GET /`, `GET /v1/models`, and `GET /api/tags`.

Current conclusion:

- No Ollama-compatible endpoint was reachable on `11434`.
- No OpenAI-compatible endpoint was reachable on `8000`, `8080`, or `3000`.
- No server type or response headers could be identified because all approved ports refused connections.
- DevMonster remains reachable over Tailscale ping, but the inference service port/path is not yet known.
- No prompts, completions, authentication, port exposure, DevMonster modifications, installs, SSH enablement, or autonomous services were used during discovery.

Recommended integration posture:

- Do not set `GEMMA_BASE_URL` yet.
- Confirm the intended DevMonster bind address, port, API compatibility mode, and auth policy on the DevMonster host.
- Prefer an OpenAI-compatible endpoint if available; otherwise use Ollama-compatible routing only if `/api/tags` and related Ollama metadata endpoints respond over Tailscale.
- Require a future metadata-only validation step before any prompt or completion request.

## Phase 2D DevMonster Worker Activation Plan

Planning date: 2026-05-27.

This is a plan only. No changes have been made on DevMonster.

### Option 1: Ollama on Tailscale Only

Goal: expose Ollama's native API to Helio over the private Tailscale address only.

DevMonster setup outline:

1. Confirm Ollama is installed on DevMonster.
2. Confirm the Gemma4-compatible model is already available or approve a future model pull separately.
3. Configure Ollama to listen only on DevMonster's Tailscale address, `100.93.120.124`, or on localhost behind a Tailscale-only reverse proxy.
4. Keep public interfaces closed; do not bind to `0.0.0.0` unless a local firewall restricts access to Tailscale.
5. Validate from Helio using metadata-only checks before any prompt.

Compatibility:

- Ollama-compatible via `/api/tags` and related Ollama API routes.
- OpenAI-compatible only if Ollama's OpenAI compatibility routes are enabled and verified.

### Option 2: LM Studio Local Server on Tailscale Only

Goal: expose LM Studio's local server on DevMonster over Tailscale.

DevMonster setup outline:

1. Confirm LM Studio is installed and the Gemma4-compatible model is loaded.
2. Start LM Studio's local server.
3. Bind the server to DevMonster's Tailscale address if supported; otherwise keep it on localhost and place a Tailscale-only reverse proxy in front.
4. Confirm the server exposes OpenAI-compatible endpoints such as `/v1/models`.
5. Keep public interfaces closed and require manual validation before Helio routing.

Compatibility:

- Usually OpenAI-compatible.
- Operationally simple for manual desktop use, but less ideal for headless/autonomous service management.

### Option 3: OpenAI-Compatible Proxy in Front of Ollama

Goal: expose a stable OpenAI-compatible API to Helio while keeping Ollama private behind the proxy.

DevMonster setup outline:

1. Run Ollama bound to localhost on DevMonster.
2. Run a lightweight OpenAI-compatible proxy bound only to `100.93.120.124`.
3. Configure the proxy to route Gemma4 requests to Ollama.
4. Add an API key at the proxy layer if needed.
5. Validate `/v1/models` first, then a single manual non-sensitive inference request after separate approval.

Compatibility:

- OpenAI-compatible for Helio.
- Better long-term abstraction if DevMonster may switch between Ollama, LM Studio, or another local runtime.
- More moving parts than direct Ollama.

### Recommendation

Recommended simplest path: Option 1, Ollama on Tailscale only, if DevMonster already uses Ollama and the required model is available.

Recommended Helio integration target after activation:

- Prefer `http://100.93.120.124:11434` for Ollama-compatible metadata checks.
- Prefer an OpenAI-compatible proxy only if Helio needs provider-neutral `/v1/models` and `/v1/chat/completions` behavior.
- Do not set `GEMMA_BASE_URL` until metadata checks pass.

### Future Helio Validation Commands

Run only after DevMonster has been configured and approved for validation.

```sh
/usr/bin/curl -sS -m 5 -i http://100.93.120.124:11434/
/usr/bin/curl -sS -m 5 -i http://100.93.120.124:11434/api/tags
/usr/bin/curl -sS -m 5 -i http://100.93.120.124:11434/v1/models
```

If an OpenAI-compatible proxy is selected:

```sh
/usr/bin/curl -sS -m 5 -i http://100.93.120.124:<approved-port>/
/usr/bin/curl -sS -m 5 -i http://100.93.120.124:<approved-port>/v1/models
```

### Security Rules

- Tailscale-only access.
- No public binding.
- No `0.0.0.0` listener unless firewall rules restrict access to Tailscale.
- Optional API key recommended before production use, especially for OpenAI-compatible proxy mode.
- No autonomous prompt routing until metadata checks and one manual non-sensitive inference test pass.
- Log endpoint selection, model ID, timeout, and routing decisions.
- Do not log secrets or prompt contents by default.
- Keep shell execution, Home Assistant actions, external writes, and file deletion behind explicit policy gates.
