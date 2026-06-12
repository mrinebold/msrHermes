# Hermes Local Task Inbox

Phase: 5AW-5AZ-R
Status: local-only task inbox scaffold, first sample task validated, context-bearing task builder added, and compact retry validated

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

## Context-Bearing Task Builder

Phase 5AY added:

```text
scripts/build_hermes_local_task.py
sandbox/hermes_inbox/next_phase_recommendation_with_context.task.md
```

Build the default context-bearing task:

```sh
python3 scripts/build_hermes_local_task.py --output sandbox/hermes_inbox/next_phase_recommendation_with_context.task.md
```

The builder:

- writes task files only under `sandbox/hermes_inbox/`
- refuses output paths outside `sandbox/hermes_inbox/`
- supports default task type `next_phase_recommendation`
- embeds only bounded excerpts from approved local files
- labels every embedded source path
- records the character limit for every source
- refuses source paths that look like env, secret, token, key, or credential files
- refuses real-looking secret markers before writing the generated task
- asks Hermes to use only embedded context and not browse files or use tools
- does not start the adapter service
- does not run Hermes
- supports compact mode with `--compact`

Default approved context sources:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`
- `docs/HERMES_OPERATIONAL_READINESS_REVIEW.md`
- `docs/HERMES_LOCAL_TASK_INBOX.md`
- `docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md`
- `docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md`

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

## Phase 5AX Sample Task Result

Phase 5AX ran exactly one local inbox task through the manual adapter service procedure:

```sh
scripts/adapter_service_start.sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_step_review.task.md
scripts/adapter_service_stop.sh
```

Output artifacts:

```text
sandbox/hermes_outbox/next_step_review.out.md
sandbox/hermes_outbox/next_step_review.stderr
sandbox/hermes_outbox/next_step_review.metrics
```

Observed result:

- adapter service started manually and listened only on `127.0.0.1:8088`
- runner accepted the approved inbox task path
- runner wrote only to `sandbox/hermes_outbox/`
- Hermes exited `0`
- elapsed time was `65` seconds
- stdout was `148` bytes
- stderr was `0` bytes
- adapter metadata showed selected model `gemma4:26b`
- adapter response content length was `147`
- adapter chat-completions request completed with status `200` in `64.204` seconds
- `scripts/adapter_service_stop.sh` stopped/unloaded the service
- final status showed no `8088` listener and no matching adapter, Hermes, Desktop, or resident process

Hermes output was usable as a fail-closed local task result. Because the sample task contained no embedded PRD or changelog context, Hermes did not fabricate a recommendation and returned:

```text
The provided local context does not contain information regarding Hermes phases or their safety levels; therefore, I cannot recommend a next phase.
```

Phase 5AX does not broaden authority. It does not approve additional live tasks, automatic adapter start/stop, resident mode, Desktop launch, credentials, integrations, Agent Bus reads/writes, shell execution by Hermes, or file writes outside the local task outbox.

## Phase 5AY Context-Bearing Builder Result

Phase 5AY created `scripts/build_hermes_local_task.py` and generated `sandbox/hermes_inbox/next_phase_recommendation_with_context.task.md`.

The generated task asks Hermes to recommend the next safest local-only Hermes phase using only embedded context and to return:

- recommended phase name
- objective
- why it is safe
- required human approval
- non-goals
- acceptance criteria

No adapter service was started, no Hermes live task was run, no external integration or real credential was used, no Agent Bus read/write occurred, no Desktop launch occurred, no `~/.hermes` file was modified, and no RunAtLoad, KeepAlive, resident mode, background service, or authority broadening occurred.

Phase 5AY makes the inbox ready for a later separately approved context-bearing task run. It does not approve running that task.

## Phase 5AZ Context-Bearing Task Attempt

Phase 5AZ attempted exactly one generated context-bearing inbox task through the manual adapter service procedure:

```sh
scripts/adapter_service_start.sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_with_context.task.md
scripts/adapter_service_stop.sh
```

Output artifacts:

```text
sandbox/hermes_outbox/next_phase_recommendation_with_context.out.md
sandbox/hermes_outbox/next_phase_recommendation_with_context.stderr
sandbox/hermes_outbox/next_phase_recommendation_with_context.metrics
```

Observed result:

- adapter service started manually and listened only on `127.0.0.1:8088`
- `/health` and `/v1/models` worked before the task run
- runner accepted the approved inbox task path
- runner wrote only to `sandbox/hermes_outbox/`
- the task did not complete with usable output
- stdout was `0` bytes
- stderr was `0` bytes
- adapter metadata showed selected model `gemma4:26b`
- first model call timed out at `120.016` seconds with status `502`
- a second model call was still in flight when Codex terminated the hanging local task fail-closed
- `scripts/adapter_service_stop.sh` stopped/unloaded the service
- final status showed no `8088` listener and no matching adapter, Hermes, Desktop, or resident process

Phase 5AZ did not meet the continuation gate because output was not usable. The likely next fix is to reduce the generated task context size or build a more compact task-specific context prompt before retrying in a separately approved phase.

Phase 5AZ does not broaden authority. It does not approve additional live tasks, automatic adapter start/stop, resident mode, Desktop launch, credentials, integrations, Agent Bus reads/writes, shell execution by Hermes, or file writes outside the local task outbox.

## Phase 5AZ-R Compact Context-Bearing Retry

Phase 5AZ-R added compact mode to `scripts/build_hermes_local_task.py` and generated:

```text
sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
```

The compact task is much smaller than the prior generated context task. It uses a compact embedded context budget of `1100` characters, asks for one next-phase recommendation only, and asks for an answer under `250` words.

Phase 5AZ-R then ran exactly one compact inbox task through the manual adapter service procedure:

```sh
scripts/adapter_service_start.sh
scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_phase_recommendation_compact.task.md
scripts/adapter_service_stop.sh
```

Output artifacts:

```text
sandbox/hermes_outbox/next_phase_recommendation_compact.out.md
sandbox/hermes_outbox/next_phase_recommendation_compact.stderr
sandbox/hermes_outbox/next_phase_recommendation_compact.metrics
```

Observed result:

- adapter service started manually and listened only on `127.0.0.1:8088`
- runner accepted the approved compact inbox task path
- runner wrote only to `sandbox/hermes_outbox/`
- Hermes exited `0`
- elapsed time was `101` seconds
- stdout was `548` bytes
- stderr was `0` bytes
- adapter metadata showed selected model `gemma4:26b`
- adapter response content length was `547`
- adapter chat-completions request completed with status `200` in `99.079` seconds
- `scripts/adapter_service_stop.sh` stopped/unloaded the service
- final status showed no `8088` listener and no matching adapter, Hermes, Desktop, or resident process

Hermes output was usable as a compact local-only recommendation, with one caveat: it recommended a conservative validation-style phase rather than broader local-only readiness certification. Treat that as advisory text requiring Codex/human review, not as autonomous authority.

Phase 5AZ-R does not broaden authority. It does not approve additional live tasks, automatic adapter start/stop, resident mode, Desktop launch, credentials, integrations, Agent Bus reads/writes, shell execution by Hermes, or file writes outside the local task outbox.
