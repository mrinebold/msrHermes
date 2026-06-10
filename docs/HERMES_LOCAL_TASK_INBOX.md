# Hermes Local Task Inbox

Phase: 5AW
Status: local-only task inbox scaffold

## Purpose

The local task inbox is a file-based handoff mechanism for explicitly approved Hermes tasks. It is local-only and does not connect Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, Desktop, cloud providers, or credentialed integrations.

No external integrations are approved by this scaffold.

Hermes remains a reasoning participant only. Codex and the human operator retain execution, verification, commits, pushes, and boundary decisions.

## Directories

```text
sandbox/hermes_inbox/
sandbox/hermes_outbox/
sandbox/hermes_archive/
```

Rules:

- inbox tasks are local files only
- the runner accepts only a specific task file under `sandbox/hermes_inbox/`
- Hermes may read only the task file passed to the runner
- Hermes may write output only through the runner to `sandbox/hermes_outbox/`
- archive movement is not automatic in Phase 5AW
- the adapter service must already be manually started and healthy
- the runner does not start or stop the adapter service
- the runner uses persistent Hermes config, which must remain localhost-only
- Hermes may not execute shell commands independently
- Hermes may not install software
- Hermes may not send messages
- Hermes may not write Supabase or Agent Bus state
- Hermes may not connect Google, GitHub, Home Assistant, Helio, cloud providers, or external services
- Hermes may not launch Desktop
- Hermes may not modify credentials
- Hermes may not modify files outside `sandbox/hermes_outbox/` in local task mode

## Runner

Run only after starting the adapter service manually:

```sh
scripts/adapter_service_start.sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_step_review.task.md
scripts/adapter_service_stop.sh
```

The runner:

- refuses paths outside `sandbox/hermes_inbox/`
- requires `http://127.0.0.1:8088/health` to pass before invoking Hermes
- uses `/Users/michaelrinebold/.local/bin/hermes` by default
- uses the persistent local Hermes config
- runs Hermes with a sanitized `env -i` child environment
- passes no real cloud or integration credentials
- writes stdout to `sandbox/hermes_outbox/<task-name>.out.md`
- writes stderr to `sandbox/hermes_outbox/<task-name>.stderr`
- writes metrics to `sandbox/hermes_outbox/<task-name>.metrics`
- prints simple terminal-compatible status
- fails closed if the adapter health check fails

## Sample Task

```text
sandbox/hermes_inbox/next_step_review.task.md
```

The sample task asks for the next safest local-only Hermes phase and explicitly forbids external integrations, credentials, and Desktop launch.

## Acceptance Criteria

- task runner refuses paths outside `sandbox/hermes_inbox/`
- task runner checks adapter health before Hermes invocation
- task runner writes only to `sandbox/hermes_outbox/`
- task runner strips sensitive environment variables by using `env -i`
- no real-looking secrets are present in docs, scripts, or sample tasks
- no external integrations are approved
- no shell execution by Hermes is approved
- Desktop launch remains blocked
- adapter service is stopped after any live task run

## Non-Goals

Phase 5AW does not approve:

- automatic adapter start
- automatic adapter stop
- `RunAtLoad=true`
- `KeepAlive=true`
- Hermes resident/autonomous mode
- Hermes launchd service
- external integrations
- real credentials
- Agent Bus reads or writes
- Google, Supabase, GitHub, Home Assistant, or Helio access
- Desktop launch
- Hermes shell execution
- Hermes file edits outside `sandbox/hermes_outbox/`
- modification of `~/.hermes`
