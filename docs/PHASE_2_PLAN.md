# Phase 2 Plan

Phase 2 is not approved for execution yet. This document records safe-check results and proposed next steps only.

## Safe Check Results

- OrbStack is installed: `2.1.3`.
- OrbStack status reports `Stopped`.
- Ollama CLI is installed: `0.24.0`.
- Ollama does not currently report a running local instance.
- Google Cloud SDK is installed: `570.0.0`.
- No Tailscale install was performed.
- No SSH Remote Login change was performed.
- No Google authentication was performed.
- No models were pulled.
- No Home Assistant install was performed.
- No DevMonster connection was attempted.

## Tailscale Install and Check-In Steps

Requires approval before execution.

1. Install Tailscale using an approved method, preferably Homebrew cask.
2. Open or start Tailscale only as required by the installer.
3. Authenticate the Mac mini to the tailnet.
4. Record hostname, Tailscale IP, MagicDNS status, and tailnet account.
5. Confirm subnet routing, exit node, and public sharing are disabled unless explicitly approved.
6. Re-run environment checks and log the result.

## SSH Remote Login Options

Requires explicit approval before enabling.

- Keep disabled: lowest risk and current state.
- Enable standard macOS Remote Login: requires approval and likely `sudo`; should be paired with firewall review.
- Prefer Tailscale SSH: keep public/LAN SSH disabled and authorize SSH through tailnet policy if needed.
- Enable Tailscale-only macOS SSH: possible only after Tailscale is installed and access can be scoped to tailnet addresses.

Recommended default: keep SSH Remote Login disabled until Tailscale is installed and the access model is decided.

## DevMonster Connectivity Test Plan

Requires approval before any connection attempt.

1. Confirm DevMonster tailnet hostname or Tailscale IP.
2. Confirm OpenAI-compatible base URL path, expected model ID, timeout, and auth requirement.
3. Store `GEMMA_BASE_URL`, `GEMMA_API_KEY`, `GEMMA_MODEL`, and `GEMMA_TIMEOUT` in an approved untracked local env file.
4. Test private DNS or Tailscale IP reachability without sending prompts.
5. Test OpenAI-compatible metadata endpoint, such as `/v1/models`, if available.
6. Run one minimal non-sensitive inference request only after approval.
7. Benchmark latency, timeout behavior, and error handling.
8. Keep all endpoints private and do not enable autonomous routing during validation.

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
