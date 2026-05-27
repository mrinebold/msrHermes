# Phase 2 Plan

Phase 2 is not approved for execution yet. This document records safe-check results and proposed next steps only.

## Safe Check Results

- OrbStack is installed: `2.1.3`.
- OrbStack status reports `Stopped`.
- Ollama CLI is installed: `0.24.0`.
- Ollama does not currently report a running local instance.
- Google Cloud SDK is installed: `570.0.0`.
- Tailscale is installed and checked in as `michaels-mac-mini`.
- Tailscale IPv4 is `100.80.79.75`.
- MagicDNS appears enabled with name `michaels-mac-mini.taila2da57.ts.net`.
- This machine does not appear to advertise itself as an exit node.
- This machine is not advertising subnet routes.
- This machine is not using an exit node.
- No SSH Remote Login change was performed.
- No Google authentication was performed.
- No models were pulled.
- No Home Assistant install was performed.
- DevMonster discovery was limited to Tailscale peer status and Tailscale ping.
- No definitive `devmonster` peer was found.
- `civic-main` at `100.92.126.17` is the only online Linux peer and responded to Tailscale ping; it is a candidate only, not confirmed DevMonster.
- No Gemma endpoint call was attempted.

## Tailscale Install and Check-In Steps

Phase 2A status: completed for install/check-in verification.

Completed:

1. Confirmed Tailscale app is installed.
2. Opened Tailscale for user check-in.
3. Recorded hostname, Tailscale IP, MagicDNS status, and tailnet account.
4. Confirmed no local Tailscale SSH, exit node use, advertised subnet routes, or advertised services were enabled.

Still requires future approval:

1. Admin-console review of ACLs, sharing controls, device expiry, and tailnet policy.
2. Any change to Tailscale SSH, advertised routes, exit-node use, or device sharing.

## SSH Remote Login Options

Requires explicit approval before enabling.

- Keep disabled: lowest risk and current state.
- Enable standard macOS Remote Login: requires approval and likely `sudo`; should be paired with firewall review.
- Prefer Tailscale SSH: keep public/LAN SSH disabled and authorize SSH through tailnet policy if needed.
- Enable Tailscale-only macOS SSH: possible only after Tailscale is installed and access can be scoped to tailnet addresses.

Recommended default: keep SSH Remote Login disabled until Tailscale is installed and the access model is decided.

## DevMonster Connectivity Test Plan

Phase 2B status: discovery only completed. Requires approval before any Gemma endpoint call.

Discovery results:

1. `devmonster` did not resolve over Tailscale DNS.
2. `devmonster.taila2da57.ts.net` did not resolve over Tailscale DNS.
3. `civic-main` responded to Tailscale ping at `100.92.126.17` in about `1ms`.
4. `civic-main` is a possible DevMonster candidate because it is the only online Linux peer, but it is not confirmed.

Next approved test sequence:

1. Confirm the actual DevMonster node name and Tailscale IP.
2. Confirm OpenAI-compatible base URL path, expected model ID, timeout, and auth requirement.
3. Store `GEMMA_BASE_URL`, `GEMMA_API_KEY`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` in an approved untracked local env file.
4. Test OpenAI-compatible metadata endpoint, such as `/v1/models`, only after approval.
5. Run one minimal non-sensitive inference request only after approval.
6. Benchmark latency, timeout behavior, and error handling.
7. Keep all endpoints private and do not enable autonomous routing during validation.

## Ollama Local Health Check Plan

No model pulls.

1. Confirm `ollama --version`.
2. Check whether the Ollama app or service is running.
3. Check localhost API health only if the service is already running.
4. Record status without downloading or loading models.

## OrbStack Health Check Plan

1. Confirm `orb version`.
2. Check `orb status`.
3. If approved later, open OrbStack and verify Docker-compatible context availability.
4. Do not run containers or expose ports during health checks.

## Google Cloud CLI Authentication Plan

No authentication or OAuth app setup yet.

1. Decide whether Helio uses user authentication, service account credentials, or workload identity.
2. Prefer least-privilege project roles and separate development credentials.
3. Avoid storing credentials in tracked files.
4. Do not run `gcloud auth login`, `gcloud init`, or OAuth app setup until approved.

## Home Assistant Architecture Decision

No install or token creation yet.

1. Decide whether Home Assistant will be reached over LAN, Tailscale, or both.
2. Prefer Tailscale or LAN-only access, never public ingress.
3. Start with read-only entity/state inventory.
4. Require policy approval before service calls or automations.
