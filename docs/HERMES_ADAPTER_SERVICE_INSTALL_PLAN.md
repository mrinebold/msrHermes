# Hermes Adapter Service Install Plan

Phase: 5AP
Status: proposal only

## Purpose

Draft the exact future user-level LaunchAgent installation plan for the localhost MSR Model Router Adapter.

Phase 5AP does not create a plist, install, load, start, or stop a service. It does not start the adapter, run Hermes, modify `~/Library/LaunchAgents`, modify `~/.hermes`, connect integrations, use credentials, launch Desktop, or broaden Hermes authority.

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
    <string>/Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/michaelrinebold/Documents/Helio/helio-command-center</string>

  <key>RunAtLoad</key>
  <false/>

  <key>KeepAlive</key>
  <false/>

  <key>StandardOutPath</key>
  <string>/Users/michaelrinebold/.hermes/logs/model-router-adapter.stdout.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/michaelrinebold/.hermes/logs/model-router-adapter.stderr.log</string>

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
    <key>MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE</key>
    <string>true</string>
  </dict>
</dict>
</plist>
```

RunAtLoad is `false` for the first install proposal so the service does not auto-start merely because the plist is loaded. KeepAlive is `false` for first service validation so failure loops cannot hide bad state or repeatedly reconnect to DevMonster.

## Future Commands

These commands are proposal-only. Do not run them in Phase 5AP.

Prepare paths:

```sh
mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$HOME/.hermes/logs"
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
tail -n 100 "$HOME/.hermes/logs/model-router-adapter.stdout.log"
tail -n 100 "$HOME/.hermes/logs/model-router-adapter.stderr.log"
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
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/.hermes/backups/com.msr.hermes.model-router-adapter.plist.$(date +%Y%m%dT%H%M%S).bak"
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

## Preflight Requirements

Before any future service install:

- validate `scripts/run_model_router_adapter.sh` in foreground immediately before install
- confirm no existing `8088` listener
- confirm DevMonster is reachable through the foreground adapter path
- review exact plist content with the human operator
- ensure `$HOME/.hermes/logs` exists
- ensure `$HOME/.hermes/backups` exists
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
