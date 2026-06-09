# Hermes Adapter Service Path Remediation

Phase: 5AR
Status: proposal only

## Purpose

Choose the safest remediation for the Phase 5AQ LaunchAgent failure.

Phase 5AQ proved the foreground adapter works, but launchd could not execute `/Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh` from the `Documents` repo path and exited `126` with `Operation not permitted`.

Phase 5AR does not create a wrapper, modify the LaunchAgent plist, load or start a service, grant macOS privacy permissions, move the repo, start the adapter, run Hermes, connect external services, use credentials, launch Desktop, or modify `~/.hermes`.

## Current Boundary

Current known state:

- foreground adapter validation passed
- LaunchAgent plist exists at `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist`
- LaunchAgent service is unloaded and stopped
- no `8088` listener remains
- no adapter, Hermes, Hermes Desktop, or Hermes resident process remains
- `~/.hermes` was not modified
- failure source is the macOS privacy boundary around executing from the `Documents` repo path

Any remediation must preserve:

- adapter binds only to `127.0.0.1:8088`
- no `0.0.0.0`, LAN, public, or Tailscale listener
- no real credentials in plist, wrapper, logs, or process environment
- metadata-only logs
- Hermes remains manually invoked
- Hermes resident/autonomous mode remains disabled
- Hermes Desktop remains fail-closed
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen

## Option Comparison

| Option | Security implications | Operational complexity | Rollback | Repo workflow impact | Secret / broad permission risk | Localhost-only preserved | Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Minimal wrapper at `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter` | Keeps launchd executable outside protected `Documents` while delegating to the reviewed repo runner; avoids broad privacy grants | Low; create one small wrapper and update one plist field | Remove wrapper or restore previous plist ProgramArguments | Low; repo stays in place | Low if wrapper contains no secrets and only execs the repo runner with approved env inherited from plist | Yes, because runner still enforces localhost/port checks | Recommended |
| B. Move whole repo outside `Documents` | Avoids current TCC path issue for all repo files | High; changes local paths, docs, scripts, git workflows, and existing references | Difficult; move repo back and update paths again | High | Medium; more files become service-accessible and many path references must be audited | Yes if runner/plist remain unchanged | Not recommended unless wrapper fails |
| C. Grant macOS privacy permission / Full Disk Access / Files and Folders | Lets launchd execute from protected path | Medium; requires GUI/privacy decision and ongoing tracking | Harder; permissions are broad and must be manually revoked | Low direct repo path churn | High; broad access may expose unrelated Desktop/Documents data to launched processes | Yes technically, but with broader filesystem authority | Not recommended |
| D. Foreground-only adapter and defer launchd | Avoids background service risk entirely | Low | No service state to rollback | None | Lowest | Yes | Safe fallback, but does not meet resident adapter service goal |
| E. Other user-owned non-protected service directory | Similar to wrapper but may require choosing and documenting a new application-support path | Medium | Remove wrapper/app-support files and restore plist | Low to medium | Low if minimal and no secrets | Yes | Acceptable alternative if `.local/bin` is unsuitable |

## Recommendation

Recommend Option A: create a minimal adapter service wrapper at:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

Rationale:

- avoids broad macOS privacy permissions
- avoids moving the entire repo
- keeps the launchd executable in a normal user-owned command directory
- keeps the canonical adapter logic in `scripts/run_model_router_adapter.sh`
- preserves the runner's built-in localhost-only and port-only refusal checks
- keeps real credentials out of the wrapper and plist
- can be rolled back by restoring the previous plist `ProgramArguments` and removing the wrapper

## Proposed Wrapper

Future wrapper path:

```text
/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

Future permissions:

```text
-rwx------ michaelrinebold staff
```

Future wrapper content:

```sh
#!/usr/bin/env bash
set -euo pipefail

cd /Users/michaelrinebold/Documents/Helio/helio-command-center
exec /Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh
```

Wrapper rules:

- no secrets
- no provider keys
- no credential loading
- no `~/.hermes` modification
- no shell arguments required
- no backgrounding inside the wrapper
- no `sudo`
- no permissions changes outside the wrapper file
- no connection to Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, Desktop, or cloud providers

## Future Plist Change

Only this plist field should change in the next approved remediation phase:

```xml
<key>ProgramArguments</key>
<array>
  <string>/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter</string>
</array>
```

Keep unchanged:

- label `com.msr.hermes.model-router-adapter`
- user LaunchAgent path
- working directory `/Users/michaelrinebold/Documents/Helio/helio-command-center`
- `RunAtLoad=false`
- `KeepAlive=false`
- stdout/stderr paths under `/Users/michaelrinebold/Documents/Helio/helio-command-center/logs/`
- `MODEL_ROUTER_ADAPTER_HOST=127.0.0.1`
- `MODEL_ROUTER_ADAPTER_PORT=8088`
- DevMonster endpoint and model
- metadata-only logging flags

If launchd still cannot use the repo working directory, the next fallback should be a second proposal that changes `WorkingDirectory` to `/Users/michaelrinebold` or another non-protected user directory while the wrapper `cd`s into the repo. Do not apply that fallback without separate approval.

## Future Validation Plan

Before creating the wrapper:

```sh
lsof -nP -iTCP:8088 -sTCP:LISTEN
pgrep -fl 'model_router_adapter|run_model_router_adapter|Hermes|Hermes-Setup|com.nousresearch.hermes'
curl --max-time 10 http://100.93.120.124:11434/api/version
scripts/run_model_router_adapter.sh
```

Foreground runner validation:

```sh
curl -fsS http://127.0.0.1:8088/health
curl -fsS http://127.0.0.1:8088/v1/models
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

After wrapper creation:

```sh
bash -n /Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
ls -l /Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter
```

After plist update:

```sh
plutil -lint /Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
launchctl print "gui/$(id -u)/com.msr.hermes.model-router-adapter"
launchctl kickstart "gui/$(id -u)/com.msr.hermes.model-router-adapter"
curl -fsS http://127.0.0.1:8088/health
curl -fsS http://127.0.0.1:8088/v1/models
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Validation must prove:

- service starts only after explicit manual `kickstart`
- service binds only `127.0.0.1:8088`
- no `0.0.0.0`, LAN, public, or Tailscale listener exists
- `/health` works
- `/v1/models` works and includes `gemma4:26b`
- no cloud fallback is selected
- no real credentials are present in wrapper, plist, logs, or process environment
- no Hermes Desktop process exists
- no Hermes resident/autonomous process exists
- service stops cleanly
- no `8088` listener remains after stop

## Future Stop And Rollback

Stop:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" || true
lsof -nP -iTCP:8088 -sTCP:LISTEN
```

Rollback plist `ProgramArguments` to the Phase 5AQ path:

```text
/Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh
```

Disable wrapper:

```sh
mv /Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter /Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)
```

Rollback acceptance:

- LaunchAgent unloaded
- no `8088` listener
- wrapper disabled or removed
- plist restored or disabled
- no adapter, Hermes, Hermes Desktop, or resident process
- no `~/.hermes` modification

## Non-Goals

Phase 5AR does not approve:

- creating the wrapper
- modifying the LaunchAgent plist
- loading or starting launchd
- granting Full Disk Access or Files and Folders permission
- moving the repo
- starting the adapter live
- running Hermes live
- connecting external services
- using real credentials
- launching Hermes Desktop
- modifying `~/.hermes`
- enabling Hermes resident/autonomous mode

## Conclusion

The safest remediation is a minimal, no-secret wrapper in `/Users/michaelrinebold/.local/bin/` with only `ProgramArguments` changed in a future approved phase. Broad macOS privacy permissions and moving the full repo should remain fallback options only if the wrapper path fails under controlled validation.
