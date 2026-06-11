# Hermes Adapter Service Runbook

Phase: 5AT-5AU
Status: manual adapter service operating procedure and bounded Hermes validation

## Purpose

Define the approved manual operating procedure for the MSR Model Router Adapter user LaunchAgent.

The adapter service may be started manually when Hermes needs local inference and must be stopped afterward unless a later phase explicitly approves a different policy.

## Current Service Assets

LaunchAgent plist:

```text
/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
```

Wrapper:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

Runtime:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current
```

Logs:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log
```

LaunchAgent policy:

- `RunAtLoad=false`
- `KeepAlive=false`
- user LaunchAgent only
- no sudo
- adapter binds only to `127.0.0.1:8088`
- no real credentials in plist, wrapper, logs, or process environment
- Hermes remains manually invoked
- Hermes resident/autonomous mode remains disabled
- Hermes Desktop remains fail-closed
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen

## Helper Scripts

Preferred commands:

```sh
scripts/adapter_service_status.sh
scripts/adapter_service_start.sh
scripts/adapter_service_stop.sh
```

The helper scripts:

- use only label `com.msr.hermes.model-router-adapter`
- use only the existing user LaunchAgent plist
- do not use sudo
- do not modify the plist
- do not create services
- do not broaden authority
- verify localhost-only binding after start
- verify no `8088` listener remains after stop
- fail closed on unexpected listener or plist policy drift

## Manual Commands

Set common variables:

```sh
LABEL="com.msr.hermes.model-router-adapter"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"
TARGET="$DOMAIN/$LABEL"
```

Load/bootstrap service:

```sh
launchctl bootstrap "$DOMAIN" "$PLIST"
```

Start/kickstart service:

```sh
launchctl kickstart "$TARGET"
```

Check status:

```sh
launchctl print "$TARGET"
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Health check:

```sh
curl -fsS http://127.0.0.1:8088/health
```

Models check:

```sh
curl -fsS http://127.0.0.1:8088/v1/models
```

Tail logs:

```sh
tail -n 100 "$HOME/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log"
tail -n 100 "$HOME/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log"
```

Stop and unload service:

```sh
launchctl bootout "$DOMAIN" "$PLIST"
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Expected stopped state:

- `launchctl print "$TARGET"` reports service not found
- no `8088` listener
- no adapter process
- no Hermes Desktop process
- no Hermes resident/autonomous process

## Rollback Or Removal

Stop first:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" || true
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Disable LaunchAgent plist:

```sh
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
```

Disable wrapper:

```sh
mv "$HOME/.local/bin/msr-hermes-model-router-adapter" "$HOME/.local/bin/msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)"
```

Disable runtime:

```sh
mv "$HOME/Library/Application Support/Helio/hermes-adapter-service/current" "$HOME/Library/Application Support/Helio/hermes-adapter-service/current.disabled.$(date +%Y%m%dT%H%M%S)"
```

Rollback acceptance:

- service unloaded
- no `8088` listener
- wrapper disabled or removed
- plist disabled or removed
- runtime disabled or removed
- no adapter, Hermes, Hermes Desktop, or resident process
- no `~/.hermes` modification

## Phase 5AT Validation Result

Phase 5AT added helper scripts for manual start, stop, and status:

```text
scripts/adapter_service_start.sh
scripts/adapter_service_stop.sh
scripts/adapter_service_status.sh
```

Validation sequence:

1. `scripts/adapter_service_start.sh`
2. `/health`
3. `/v1/models`
4. localhost-only listener check
5. `scripts/adapter_service_stop.sh`
6. no-listener confirmation

Observed result:

- `scripts/adapter_service_start.sh` passed
- service loaded and started through launchctl
- launchctl status showed state `running`
- `/health` returned status `ok`
- `/v1/models` returned model metadata including `gemma4:26b`
- listener inspection showed only `127.0.0.1:8088`
- no Hermes Desktop process was present
- no Hermes resident/autonomous process was present
- `scripts/adapter_service_stop.sh` passed
- final `scripts/adapter_service_status.sh` reported `loaded=false` and `listener=false`

The service was not left running after validation.

## Phase 5AU Hermes Validation Result

Phase 5AU used the manual adapter service procedure for one bounded Hermes prompt through the persistent local config.

Validation sequence:

1. `scripts/adapter_service_start.sh`
2. `scripts/adapter_service_status.sh`
3. `/health`
4. `/v1/models`
5. one `hermes -z` prompt
6. `scripts/adapter_service_stop.sh`
7. no-listener and no-process confirmation

Observed result:

- service started through the helper script and launchctl
- DevMonster responded at `http://100.93.120.124:11434/api/version` with version `0.30.4`
- `/health` returned status `ok`
- `/v1/models` returned model metadata including `gemma4:26b`
- listener inspection showed only `127.0.0.1:8088`
- Hermes exited `0` in `28` seconds
- Hermes stdout was `49` bytes and stderr was `0` bytes
- Hermes returned exactly `Hermes works through the manual adapter service.`
- output artifacts were written under `sandbox/output/`
- `scripts/adapter_service_stop.sh` stopped and unloaded the service
- final status reported `loaded=false` and `listener=false`
- no matching adapter, Hermes, Hermes Desktop, or resident process remained

The service was not left running after validation.

## Phase 5AZ Service Cleanup Result

Phase 5AZ started the adapter service manually for one generated context-bearing inbox task. The task did not complete with usable output after a `gemma4:26b` provider timeout and a second in-flight model call, so Codex terminated the local task process fail-closed and stopped the adapter service.

Cleanup result:

- `scripts/adapter_service_stop.sh` passed
- final `scripts/adapter_service_status.sh` reported `loaded=false` and `listener=false`
- no `8088` listener remained
- no matching adapter, Hermes, Hermes Desktop, or resident process remained
- no external integration, real credential, Agent Bus read/write, Desktop launch, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred

## Non-Goals

Phase 5AT does not approve automatic service policy changes, and Phase 5AU does not approve:

- `RunAtLoad=true`
- `KeepAlive=true`
- Hermes resident/autonomous mode
- Hermes launchd service
- leaving the adapter service running
- additional Hermes live prompt execution
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud-provider integrations
- real credentials
- Desktop launch
- `~/.hermes` modification
- sudo
- broad filesystem or privacy permission grants
