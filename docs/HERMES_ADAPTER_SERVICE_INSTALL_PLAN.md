# Hermes Adapter Service Install Plan

Phase: 5AP-5AS
Status: adapter LaunchAgent wrapper service validated and stopped

## Purpose

Draft the exact future user-level LaunchAgent installation plan for the localhost MSR Model Router Adapter.

Phase 5AP did not create a plist, install, load, start, or stop a service. It did not start the adapter, run Hermes, modify `~/Library/LaunchAgents`, modify `~/.hermes`, connect integrations, use credentials, launch Desktop, or broaden Hermes authority.

Phase 5AQ created the user LaunchAgent plist and attempted one controlled launchctl validation. The foreground runner validated successfully, but the LaunchAgent start failed closed with exit code `126` because launchd could not execute the adapter script from the `Documents` repo path. The service was unloaded and stopped; the plist remains installed on disk for inspection.

Phase 5AR added `docs/HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md` as a proposal-only remediation plan. It recommends a minimal no-secret wrapper at `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter` over broad macOS privacy permissions, moving the whole repo, or retrying launchd unchanged.

Phase 5AS created that wrapper, then fixed the remaining launchd path issue by creating a self-contained runtime under `~/Library/Application Support/Helio/hermes-adapter-service/`. The LaunchAgent started manually, served `/health` and `/v1/models` on `127.0.0.1:8088`, and was stopped/unloaded after validation.

## Service Scope

The future service is adapter-only:

- service label: `com.msr.hermes.model-router-adapter`
- adapter binds only to `127.0.0.1:8088`
- Hermes remains manually invoked
- Hermes autonomous resident mode is not approved
- Hermes Desktop is not a dependency and remains fail-closed
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen
- no real credentials or secret-like values belong in the plist

## Proposed LaunchAgent Plist

Future plist path:

```text
~/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
```

Future plist content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.msr.hermes.model-router-adapter</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current</string>

  <key>RunAtLoad</key>
  <false/>

  <key>KeepAlive</key>
  <false/>

  <key>StandardOutPath</key>
  <string>/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>MODEL_ROUTER_ADAPTER_HOST</key>
    <string>127.0.0.1</string>
    <key>MODEL_ROUTER_ADAPTER_PORT</key>
    <string>8088</string>
    <key>DEVMONSTER_OLLAMA_URL</key>
    <string>http://100.93.120.124:11434</string>
    <key>DEVMONSTER_DEFAULT_MODEL</key>
    <string>gemma4:26b</string>
    <key>MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS</key>
    <string>120</string>
    <key>MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE</key>
    <string>true</string>
    <key>MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE</key>
    <string>instruction_context</string>
    <key>MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS</key>
    <string>1500</string>
    <key>MODEL_ROUTER_ADAPTER_LOG_REQUESTS</key>
    <string>true</string>
    <key>MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES</key>
    <string>true</string>
  </dict>
</dict>
</plist>
```

RunAtLoad is `false` for the first install proposal so the service does not auto-start merely because the plist is loaded. KeepAlive is `false` for first service validation so failure loops cannot hide bad state or repeatedly reconnect to DevMonster.

## Future Commands

These commands were proposal-only in Phase 5AP. Phase 5AQ approved the controlled install validation and used the same commands with repo-local log paths.

Prepare paths:

```sh
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs"
```

Write plist path:

```text
$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
```

Bootstrap command:

```sh
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

Print/status command:

```sh
launchctl print "gui/$(id -u)/com.msr.hermes.model-router-adapter"
```

Manual start command, only after bootstrap and explicit approval:

```sh
launchctl kickstart "gui/$(id -u)/com.msr.hermes.model-router-adapter"
```

Bootout/stop command:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

Log tail commands:

```sh
tail -n 100 "/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log"
tail -n 100 "/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log"
```

Health check commands:

```sh
curl -sS http://127.0.0.1:8088/health
curl -sS http://127.0.0.1:8088/v1/models
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Rollback/removal commands:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

## Preflight Requirements

Before any future service install:

- validate `scripts/run_model_router_adapter.sh` in foreground immediately before install
- confirm no existing `8088` listener
- confirm DevMonster is reachable through the foreground adapter path
- review exact plist content with the human operator
- ensure `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current` exists
- ensure `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs` exists
- confirm plist contains no secrets
- confirm no broad filesystem or accessibility permissions are required
- confirm no Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or Desktop access is enabled
- confirm rollback path and bootout command are ready

## Future Acceptance Criteria

A future install phase succeeds only if:

- plist is user-level under `~/Library/LaunchAgents`
- service does not auto-start unless explicitly loaded and kicked
- adapter binds only to `127.0.0.1:8088`
- `/health` works
- `/v1/models` works
- no `0.0.0.0` listener exists
- no LAN/public/Tailscale bind exists
- no cloud provider fallback is selected
- no real credentials are present in the service plist or process environment
- logs contain metadata only
- service stops cleanly with `launchctl bootout`
- rollback removes or backs up the plist and leaves no `8088` listener
- Hermes Desktop remains closed and fail-closed
- Hermes autonomous resident mode is not started

## Non-Goals

Phase 5AP does not approve:

- creating the plist
- installing, bootstrapping, loading, kicking, or starting the service
- starting the adapter live
- running Hermes live
- modifying `~/Library/LaunchAgents`
- modifying `~/.hermes`
- launchd background operation
- Hermes autonomous resident operation
- Hermes Desktop launch
- Google, Supabase, GitHub, Home Assistant, Helio, or Agent Bus access
- credential use or credential rotation
- shell/action automation
- cloud provider fallback
- broad filesystem authority

## Phase 5AP Conclusion

The future install path is ready for human review as a proposal. The next phase must explicitly approve whether to create the plist and whether to bootstrap/kickstart the adapter service. Until then, no service exists and no resident/background operation is enabled.

## Phase 5AQ Controlled Install Validation Result

Phase 5AQ was approved to install and validate the user LaunchAgent. Preflight passed:

- no existing `127.0.0.1:8088` listener
- no adapter process running
- no Hermes Desktop process running
- DevMonster responded at `http://100.93.120.124:11434/api/version` with version `0.30.4`
- foreground `scripts/run_model_router_adapter.sh` started with `127.0.0.1:8088`, DevMonster `gemma4:26b`, provider timeout `120`, local compatibility mode, `instruction_context`, metadata-only logging, and no prompt/file-content logging
- foreground `/health` returned status `ok`
- foreground `/v1/models` returned model metadata including `gemma4:26b`
- foreground listener inspection showed only `TCP 127.0.0.1:8088 (LISTEN)`
- foreground adapter stopped cleanly and left no `8088` listener

The LaunchAgent plist was created at:

```text
/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
```

The plist was validated with `plutil -lint` and parsed with `plutil -p`. It contains no real credentials, uses `RunAtLoad=false`, uses `KeepAlive=false`, points to the approved script path, and writes stdout/stderr under:

```text
/Users/michaelrinebold/Documents/Helio/helio-command-center/logs/
```

Launchctl validation result:

- `launchctl bootstrap gui/501 ...` loaded the user LaunchAgent
- `launchctl print gui/501/com.msr.hermes.model-router-adapter` showed type `LaunchAgent`, state `not running`, `runs = 0`, and the approved environment before manual start
- `launchctl kickstart gui/501/com.msr.hermes.model-router-adapter` attempted one manual start
- the service exited with code `126` and did not bind `8088`
- stderr recorded:

```text
shell-init: error retrieving current directory: getcwd: cannot access parent directories: Operation not permitted
bash: /Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh: Operation not permitted
```

Codex classification: the foreground adapter is healthy, but the LaunchAgent cannot execute from the `Documents` repo path under the current macOS privacy/TCC boundary. No broad filesystem permission was granted and no attempt was made to bypass that boundary.

Final Phase 5AQ state:

- plist path: `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist`
- plist installed on disk: yes
- service loaded: no
- service running: no
- health check result for service: not available because the service failed before binding
- logs path: `/Users/michaelrinebold/Documents/Helio/helio-command-center/logs/model-router-adapter.stdout.log` and `logs/model-router-adapter.stderr.log`
- stdout log: empty
- stderr log: contains the launchd `Operation not permitted` failure
- no `8088` listener remains
- no adapter, Hermes, or Hermes Desktop process remains
- no Hermes resident/autonomous process was created
- no real credentials, cloud providers, Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, Desktop, or `~/.hermes` modification was involved

Rollback command:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" || true
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Recommended next action: approve a narrow Phase 5AR service path remediation plan. The safest options to compare are a non-`Documents` adapter runner location such as `~/.local/bin` or `~/Library/Application Support/Helio/`, or an explicit human-managed macOS privacy permission decision. Do not grant broad permissions, move files, or retry launchd until that remediation plan is approved.

## Phase 5AR Path Remediation Proposal Result

Phase 5AR compared five remediation options: minimal wrapper outside `Documents`, moving the whole repo, broad macOS privacy permission, foreground-only deferral, and another user-owned non-protected service directory.

The recommended next path is a minimal wrapper at:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

The proposed wrapper contains no secrets and delegates to the existing reviewed runner. The future plist change would only replace `ProgramArguments` with the wrapper path while preserving `RunAtLoad=false`, `KeepAlive=false`, localhost-only adapter environment variables, repo-local logs, and no Hermes resident mode.

Phase 5AR did not create the wrapper, edit the plist, load or start launchd, grant privacy permissions, move the repo, start the adapter, run Hermes, connect external services, use credentials, launch Desktop, or modify `~/.hermes`.

## Phase 5AS Wrapper Service Validation Result

Phase 5AS created the approved wrapper at `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter` with permissions `-rwx------`. The first wrapper-only attempt still failed because launchd could not use the `Documents` repo path.

The final fix copied only the required adapter runtime modules to:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current/
```

The LaunchAgent plist at `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist` now uses:

- `ProgramArguments=/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`
- `WorkingDirectory=/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current`
- `StandardOutPath=/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log`
- `StandardErrorPath=/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log`
- `RunAtLoad=false`
- `KeepAlive=false`

`plutil -lint` passed. Manual `launchctl kickstart` started the service successfully. `/health` returned status `ok`; `/v1/models` returned model metadata including `gemma4:26b`; listener inspection showed only `127.0.0.1:8088`.

Final state:

- wrapper installed: yes
- self-contained runtime installed: yes
- plist installed: yes
- service loaded: no
- service running: no
- logs path: `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/`
- health result: passed during manual start
- models result: passed during manual start and included `gemma4:26b`
- no `8088` listener remains
- no adapter, Hermes, Hermes Desktop, or Hermes resident/autonomous process remains
- `~/.hermes` was not modified

Rollback command:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" || true
mv "$HOME/.local/bin/msr-hermes-model-router-adapter" "$HOME/.local/bin/msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)"
mv "$HOME/Library/Application Support/Helio/hermes-adapter-service/current" "$HOME/Library/Application Support/Helio/hermes-adapter-service/current.disabled.$(date +%Y%m%dT%H%M%S)"
```

Recommended next action: define operating policy for manual service start/stop. Do not enable `RunAtLoad`, `KeepAlive`, Hermes resident mode, Desktop, credentials, or integrations without separate approval.
