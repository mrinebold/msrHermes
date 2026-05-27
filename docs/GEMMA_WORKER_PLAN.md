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

Tailscale peer discovery did not find a device named `devmonster`.

Observed Tailscale peers:

- `michaels-mac-mini` at `100.80.79.75`, local Mac mini.
- `civic-main` at `100.92.126.17`, Linux, online.
- `iphone-15-pro-max` at `100.92.128.26`, iOS, online.
- `rinebolddomain` at `100.77.8.69`, Windows, online.
- `ipad-pro-12-9-gen-5` at `100.96.95.115`, iOS, offline/expired.

Discovery checks:

- `devmonster` did not resolve through Tailscale DNS.
- `devmonster.taila2da57.ts.net` did not resolve through Tailscale DNS.
- `civic-main` responded to Tailscale ping at `100.92.126.17` in about `1ms`.

Current conclusion:

- No definitive DevMonster hostname or Tailscale IP is available from the current tailnet peer list.
- `civic-main` is the only online Linux peer and is therefore a possible DevMonster candidate, but this is not confirmed.
- Helio should not set `GEMMA_BASE_URL` until the DevMonster hostname/IP and service port are confirmed.

## Expected Gemma4 Endpoint Test Plan

Requires explicit approval before any endpoint call.

1. Confirm whether DevMonster is `civic-main` or another Tailscale node.
2. Confirm the private Tailscale hostname or IP.
3. Confirm the OpenAI-compatible base URL, including scheme and port.
4. Confirm `GEMMA_MODEL`, timeout, and authentication requirement.
5. Store `GEMMA_BASE_URL`, `GEMMA_API_KEY`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` only in an approved untracked local env file.
6. Check only metadata first, such as `/v1/models`, if available.
7. Run one minimal non-sensitive inference request only after separate approval.
8. Benchmark latency and timeout behavior before any autonomous routing.
