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

Ports checked:

- `11434`, common Ollama API port.
- `8000`, common local model/API server port.
- `8080`, common application/API server port.
- `3000`, common development server port.

Results:

- Port `11434`: connection refused for `HEAD /`, `GET /`, and `GET /v1/models`.
- Port `8000`: connection refused for `HEAD /`, `GET /`, and `GET /v1/models`.
- Port `8080`: connection refused for `HEAD /`, `GET /`, and `GET /v1/models`.
- Port `3000`: connection refused for `HEAD /`, `GET /`, and `GET /v1/models`.

Current conclusion:

- No Ollama-compatible endpoint was reachable on `11434`.
- No OpenAI-compatible endpoint was reachable on `8000`, `8080`, or `3000`.
- No server type or response headers could be identified because all approved ports refused connections.
- DevMonster remains reachable over Tailscale ping, but the inference service port/path is not yet known.
- No prompts, completions, authentication, port exposure, DevMonster modifications, installs, SSH enablement, or autonomous services were used during discovery.
