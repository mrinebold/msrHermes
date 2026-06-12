# Hermes Local Operations Runbook

Phase: 5BA
Status: manual local-only operations documented; local-only readiness certified in Phase 5BB

## Current Approved Mode

Hermes is approved for manual local-only use through the validated adapter service and local task inbox.

Approved operating shape:

- manual adapter service start and stop only
- Hermes CLI local-only inference through `http://127.0.0.1:8088/v1`
- context-bearing inbox tasks only
- outputs written under `sandbox/hermes_outbox/`
- Codex or the human operator reviews Hermes output before any action

Not approved:

- Hermes Desktop; it remains fail-closed
- external integrations
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud providers
- real credentials
- Hermes resident/autonomous mode
- `RunAtLoad=true`
- `KeepAlive=true`
- Hermes shell execution
- Hermes file edits outside `sandbox/hermes_outbox/`

## Daily Manual Workflow

Use this sequence when a local-only Hermes recommendation is explicitly approved.

1. Start the adapter service:

```sh
scripts/adapter_service_start.sh
```

2. Check adapter status:

```sh
scripts/adapter_service_status.sh
```

Expected status:

- LaunchAgent loaded only because it was manually started
- listener present only on `127.0.0.1:8088`
- no `0.0.0.0` listener
- no LAN or Tailscale adapter exposure

3. Build a compact context-bearing task:

```sh
python3 scripts/build_hermes_local_task.py --compact --task-type next_phase_recommendation --output sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

4. Run the task:

```sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

5. Read the outbox result:

```text
sandbox/hermes_outbox/next_phase_recommendation_compact.out.md
sandbox/hermes_outbox/next_phase_recommendation_compact.stderr
sandbox/hermes_outbox/next_phase_recommendation_compact.metrics
```

6. Stop the adapter service:

```sh
scripts/adapter_service_stop.sh
```

7. Verify cleanup:

```sh
scripts/adapter_service_status.sh
```

Expected cleanup:

- LaunchAgent loaded state is false
- no `8088` listener remains
- no adapter process remains
- no Hermes Desktop process remains
- no Hermes resident/autonomous process remains

## Safe Boundaries

Hermes may:

- summarize embedded local context
- recommend next local-only actions
- produce advisory text in `sandbox/hermes_outbox/`

Hermes may not:

- execute shell commands independently
- install software
- send messages
- access Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud providers
- use real credentials
- launch Hermes Desktop
- run as a resident/background agent
- modify `~/.hermes`
- modify files outside `sandbox/hermes_outbox/`

## Troubleshooting

### Port 8088 Already In Use

Run:

```sh
scripts/adapter_service_status.sh
```

If the listener is not the approved adapter bound only to `127.0.0.1:8088`, stop and investigate. Do not run Hermes against an unknown listener.

### DevMonster Unreachable

The adapter depends on DevMonster at:

```text
http://100.93.120.124:11434
```

If model calls fail because DevMonster is unavailable, stop the adapter service and leave Hermes tasks unrun.

### Gemma Timeout

Use compact tasks first. Phase 5AZ showed the full context task can time out. Phase 5AZ-R validated the compact task with a `1100` character embedded context budget.

### Empty Or Unusable Output

Treat empty output as fail-closed. Do not rerun repeatedly. Reduce context, narrow the task, or open a new phase with explicit approval.

### Service Fails To Start

Check:

```sh
scripts/adapter_service_status.sh
```

Then inspect logs without exposing prompt text or secrets:

```text
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stdout.log
/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/logs/model-router-adapter.stderr.log
```

Do not grant broad macOS privacy permissions as a first response.

### Credential Freeze Reminder

Credentialed integrations remain frozen. Do not use Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud provider credentials during local-only Hermes operation.

## Rollback

Stop the adapter service first:

```sh
scripts/adapter_service_stop.sh
```

If needed, unload the LaunchAgent manually:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist"
```

If removal is explicitly approved later, preserve backups and disable rather than delete first:

```sh
mv "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist" "$HOME/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist.disabled.$(date +%Y%m%dT%H%M%S)"
mv "$HOME/.local/bin/msr-hermes-model-router-adapter" "$HOME/.local/bin/msr-hermes-model-router-adapter.disabled.$(date +%Y%m%dT%H%M%S)"
```

Persistent Hermes config backup remains:

```text
/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak
```

Do not restore or modify `~/.hermes` without a separate approved phase.

## What Is Ready

- persistent Hermes config points to the localhost adapter
- adapter LaunchAgent can be manually started and stopped
- adapter binds only to `127.0.0.1:8088`
- compact context-bearing inbox task completed successfully
- local outbox artifacts capture stdout, stderr, and metrics
- service cleanup after local tasks is validated
- final local-only readiness is certified in `docs/HERMES_LOCAL_ONLY_READY_REPORT.md`

## What Is Not Ready

- Hermes resident/autonomous mode
- automatic adapter start at login
- persistent keepalive service operation
- Hermes Desktop
- external integrations
- Agent Bus reads or writes
- credentialed workflows
- Hermes shell execution
- broad filesystem authority

## Next Recommended Phase

Proceed with a read-only local status command. That phase should give the operator a quick status check without starting services, modifying files, launching Desktop, connecting integrations, or enabling resident mode.
