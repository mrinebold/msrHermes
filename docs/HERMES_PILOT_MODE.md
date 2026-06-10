# Hermes Pilot Mode

Phase: 5AW
Status: local-only task inbox scaffold complete

## Purpose

Hermes pilot mode is a limited local reasoning harness for the Mac mini. It lets Hermes summarize approved local repo documents and recommend next actions through the localhost MSR Model Router Adapter while Codex or the human operator retains execution control.

Pilot mode is not resident mode, not autonomous execution, and not Desktop validation.

## Components

| Component | Path | Purpose |
| --- | --- | --- |
| Adapter runner | `scripts/run_model_router_adapter.sh` | Starts the localhost OpenAI-compatible MSR Model Router Adapter manually in the foreground. |
| Hermes pilot harness | `scripts/run_hermes_pilot.sh` | Runs one isolated Hermes prompt against the localhost adapter. |
| Example env | `config/hermes-pilot.example.env` | Documents safe pilot variables with dummy local key only. |
| Next-action prompt | `sandbox/input/hermes_pilot_next_action_prompt.md` | Template prompt for the PRD/changelog summary run. |
| Local validation checklist | `docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md` | Records local-only readiness checks under the credential deferral boundary. |
| Local task runner | `scripts/run_hermes_local_task.sh` | Runs one explicit inbox task through persistent localhost-only Hermes config when the adapter is already healthy. |
| Local task inbox | `sandbox/hermes_inbox/` | Holds approved local-only task files. |
| Local task outbox | `sandbox/hermes_outbox/` | Receives task stdout, stderr, and metrics. |

## Adapter Runner

Run manually only:

```sh
scripts/run_model_router_adapter.sh
```

The runner:

- binds only to `127.0.0.1`
- uses port `8088`
- points `DEVMONSTER_OLLAMA_URL` to `http://100.93.120.124:11434`
- uses `DEVMONSTER_DEFAULT_MODEL=gemma4:26b`
- sets `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120`
- enables `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`
- defaults `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=instruction_context`
- sets `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500`
- enables metadata-only request, response-shape, and message-structure logging
- refuses non-localhost bind
- refuses non-`8088` pilot port
- prints startup config with dummy/secrets redacted
- runs in the foreground only
- exits on Ctrl-C

The adapter logging contract remains metadata-only. It must not log prompt text, file contents, model output text, API keys, OAuth tokens, Supabase keys, Home Assistant tokens, GitHub tokens, or Helio credentials.

Dry-run guardrail check:

```sh
scripts/run_model_router_adapter.sh --dry-run
```

## Hermes Pilot Harness

Run one explicit prompt:

```sh
scripts/run_hermes_pilot.sh --prompt "Summarize the approved local docs." --stdout
```

Run one explicit prompt file:

```sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md
```

By default, generated stdout is written to:

```text
sandbox/output/hermes_pilot_output.md
```

Use `--stdout` when the task should print to terminal only. Use `--output <path>` only for approved local outputs; by default the harness refuses output outside `sandbox/output`.

The harness:

- uses isolated `HERMES_HOME=/private/tmp/hermes-pilot-home` by default
- writes only the isolated pilot `config.yaml`
- configures Hermes with `model.provider=custom`
- points Hermes only at `http://127.0.0.1:8088/v1`
- uses only `gemma4:26b`
- uses dummy local API key `dummy-local-adapter-key`
- disables CLI platform toolsets with `platform_toolsets.cli: []`
- starts no resident mode
- starts no background service
- does not start the adapter
- requires explicit `--prompt` or `--prompt-file`
- runs Hermes in a sanitized child environment

The sanitized Hermes child process removes real provider and integration variables by using an allowlisted environment. These variables are not passed through:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `HASS_URL`
- `HASS_TOKEN`
- `HELIO_GATEWAY_URL`
- `HELIO_DISPATCHER_MCP_URL`

Phase 5AJ validates that the example env, pilot harness, security model, and local validation checklist stay aligned on this credential-stripping set. The harness may pass only the dummy local adapter key as `OPENAI_API_KEY` inside the isolated child process because Hermes requires an OpenAI-compatible API-key-shaped value syntactically.

Dry-run guardrail check:

```sh
scripts/run_hermes_pilot.sh --dry-run --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md
```

## Local Validation Mode

Phase 5AJ local validation is documentation and test validation only. It does not start the adapter, run Hermes, launch Desktop, connect integrations, use live credentials, or run Agent Bus reads/writes.

Use the checklist:

```text
docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md
```

Local validation confirms:

- localhost-only adapter and pilot configuration
- no cloud-provider fallback
- no real API keys in committed examples
- no Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus credential use
- no Desktop launch
- no background/resident service setup
- human approval remains required before boundary-crossing actions

## Allowed Pilot Behavior

Hermes may:

- perform safe local reasoning
- summarize explicitly supplied local repo docs
- recommend next actions
- write generated output only to `sandbox/output` unless separately overridden
- print to stdout when `--stdout` is explicitly used

## Disallowed Pilot Behavior

Hermes may not:

- execute shell commands independently
- install software
- send messages
- write Supabase
- connect Google
- control Home Assistant
- launch Hermes Desktop
- modify credentials
- modify persistent Hermes CLI config
- modify files outside `sandbox/output` in pilot mode
- create launchd plists
- run as a background or resident service
- connect GitHub, Helio, Agent Bus, cloud providers, or other external services

## Phase 5AD Controlled Pilot Result

Phase 5AD ran the first bounded pilot task on 2026-06-08.

Approved command sequence:

```sh
scripts/run_model_router_adapter.sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/input/hermes_pilot_next_action_prompt.md --stdout
```

Capture files:

- `sandbox/output/hermes_pilot_next_action.md`
- `sandbox/output/hermes_pilot_next_action.stderr`
- `sandbox/output/hermes_pilot_next_action.metrics`

Observed result:

| Check | Result |
| --- | --- |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Selected model | `gemma4:26b` |
| Timeout | 120 seconds |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| Response content length | repeated `0` byte completions |
| Pilot stdout bytes | 471 |
| Pilot stderr bytes | 0 |
| Pilot output usable | no; stdout contained only redacted harness config |
| Pilot exit | operator-terminated stuck tool session after repeated empty responses |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |
| Residual Hermes pilot process | none observed |
| Desktop launch | no new launch; a pre-existing `Hermes-Setup` process remained outside this phase |
| External integrations | not touched |
| Real API keys | not used |
| Hermes file writes | no Hermes-generated writes outside `sandbox/output` observed |

Guardrail review:

- Hermes stayed within pilot boundaries.
- The harness used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`.
- The harness used the localhost adapter URL only.
- The child process used a dummy local API key.
- No Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud provider integration was connected.
- No Hermes Desktop launch, install, replacement, permission grant, credential modification, background service, resident mode, or message send occurred.

The pilot did not produce a usable recommendation. Adapter metadata showed the prompt reached the model path with `instruction_context`, but DevMonster/Gemma returned empty content repeatedly. This differs from the earlier Phase 5AA useful-output baseline, which used `local_summary` against a file-summary task.

Recommendation:

Do not expand Hermes authority or run additional open-ended pilot tasks yet. The next phase should either adjust the pilot harness to use the validated `local_summary` path with explicit file-like context, or add a narrower next-action prompt mode that supplies the PRD/changelog content as bounded context while preserving the same no-tools/no-integrations/no-background guardrails.

## Phase 5AE Explicit Local Context Pilot Result

Phase 5AE ran a second bounded pilot task on 2026-06-08 using explicit local context.

Phase 5AE added:

- `scripts/build_hermes_pilot_context_prompt.py`
- `scripts/run_hermes_pilot.sh --config-to-stderr`
- `sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md`

The prompt builder reads the master PRD and changelog locally, creates a bounded prompt with a short instruction, includes compact PRD/changelog excerpts after a `Document/context:` marker, and tells Hermes to return only recommendation text. It does not ask Hermes to read paths, use tools, connect integrations, or modify files.

Approved command sequence:

```sh
python3 scripts/build_hermes_pilot_context_prompt.py --output sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary \
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120 \
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500 \
  scripts/run_model_router_adapter.sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md --stdout --config-to-stderr
```

Capture files:

- `sandbox/output/hermes_pilot_next_action_phase5ae.md`
- `sandbox/output/hermes_pilot_next_action_phase5ae.stderr`
- `sandbox/output/hermes_pilot_next_action_phase5ae.metrics`
- `sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md`

Observed result:

| Check | Result |
| --- | --- |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter prompt mode | `local_summary` |
| Context budget | 1500 chars |
| Extracted context | 1426 chars; not truncated |
| Selected model | `gemma4:26b` |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| First model call | timed out after 120.011 seconds with status `502` |
| Successful retry | status `200`, response content length `637`, elapsed `49.883s` |
| Pilot exit code | 0 |
| Pilot elapsed time | 174 seconds |
| Pilot stdout bytes | 638 |
| Pilot stderr bytes | 471 |
| Pilot output usable | yes |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |
| Residual Hermes process | none observed |
| Desktop launch | none observed |
| External integrations | not touched |
| Real API keys | not used |
| Hermes file writes | no Hermes-generated writes outside `sandbox/output` observed |

The usable stdout recommendation was:

```text
Status: Phase 5AD completed its first controlled pilot task with successful guardrail adherence, but the output was unusable due to pending approvals.
Next safest phase: Phase 5AE involves a prompt and harness adjustment that supplies PRD and changelog content as explicit bounded local context before any additional pilot run.
Guardrails: Do not start background services, expose the adapter externally, use cloud providers, or broaden Hermes authority without new explicit phase approval.
Recommendation: Implement Phase 5AE to provide validated local context through the `local_summary` path before proceeding with further pilot runs.
```

Guardrail review:

- Hermes stayed within pilot boundaries.
- The harness used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`.
- The harness used the localhost adapter URL only.
- The child process used a dummy local API key.
- `platform_toolsets.cli` remained disabled.
- Adapter metadata showed `tools_present=false` and `tool_schemas_forwarded=false`.
- No Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, message send, Desktop launch, install, permission grant, credential modification, background service, or resident mode occurred.

Recommendation:

Treat Phase 5AE as the first usable controlled next-action pilot. The next phase should preserve the explicit-context and `local_summary` pattern, then either refine the recommendation prompt to produce forward-looking Phase 5AF text or use the same harness for one bounded PRD-review task. Do not broaden Hermes authority.

## Phase 5AF Forward-Looking Pilot Recommendation

Phase 5AF ran one bounded forward-looking pilot on 2026-06-08 using the proven explicit-context and `local_summary` baseline.

Phase 5AF updated:

- `scripts/build_hermes_pilot_context_prompt.py --phase5af`
- `sandbox/output/hermes_pilot_phase5af_next_phase_prompt.md`

The Phase 5AF prompt includes bounded context from:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`
- `docs/HERMES_PILOT_MODE.md`
- `docs/HERMES_SECURITY_MODEL.md`

It asked Hermes to recommend the next safest Hermes operating-system phase after Phase 5AE, and to return only:

- recommended phase name
- objective
- why this is safest
- explicit non-goals
- acceptance criteria
- whether human approval is required before execution

Approved command sequence:

```sh
python3 scripts/build_hermes_pilot_context_prompt.py --phase5af --output sandbox/output/hermes_pilot_phase5af_next_phase_prompt.md
MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary \
MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS=120 \
MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS=1500 \
  scripts/run_model_router_adapter.sh
scripts/run_hermes_pilot.sh --prompt-file sandbox/output/hermes_pilot_phase5af_next_phase_prompt.md --stdout --config-to-stderr
```

Capture files:

- `sandbox/output/hermes_pilot_phase5af_next_phase.md`
- `sandbox/output/hermes_pilot_phase5af_next_phase.stderr`
- `sandbox/output/hermes_pilot_phase5af_next_phase.metrics`
- `sandbox/output/hermes_pilot_phase5af_next_phase_prompt.md`

Observed result:

| Check | Result |
| --- | --- |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter prompt mode | `local_summary` |
| Context budget | 1500 chars |
| Extracted context | 1480 chars; not truncated |
| Selected model | `gemma4:26b` |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| Successful model call | status `200`, response content length `979`, elapsed `115.191s` |
| Pilot exit code | 0 |
| Pilot elapsed time | 116 seconds |
| Pilot stdout bytes | 980 |
| Pilot stderr bytes | 471 |
| Pilot output usable | yes |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |
| Residual Hermes process | none observed |
| Desktop launch | none observed |
| External integrations | not touched |
| Real API keys | not used |
| Hermes file writes | no Hermes-generated writes outside `sandbox/output` observed |

The usable stdout recommendation was:

```text
recommended phase name: Phase 5AF
objective: Execute one bounded PRD-review task using the established explicit local context harness.
why this is safest: It adheres to the proven `local_summary` baseline from Phase 5AE, utilizes the existing bounded prompt mode, and operates under Codex control without broadening Hermes authority or expanding into new scopes.
explicit non-goals: Broadening Hermes authority; expanding scope to include shell command execution, file edit scope, gateway service behavior, Google scopes, Home Assistant token access, or agent dispatch interface modifications; performing live Agent Bus reads or writes before confirmed credential rotation.
acceptance criteria: Successful completion of a single bounded PRD-review task within the existing security constraints and without any expansion of agent authority.
whether human approval is required before execution: Yes (to ensure continued Codex control and prevent unauthorized authority broadening).
```

Guardrail review:

- Hermes stayed within pilot boundaries.
- The harness used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`.
- The harness used the localhost adapter URL only.
- The child process used a dummy local API key.
- `platform_toolsets.cli` remained disabled.
- Adapter metadata showed `tools_present=false` and `tool_schemas_forwarded=false`.
- No Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, message send, Desktop launch, install, permission grant, credential modification, background service, or resident mode occurred.

Recommendation:

Treat Phase 5AF as a successful forward-looking pilot. The next phase should execute the recommended single bounded PRD-review task using the same explicit-context, `local_summary`, no-tools, no-integrations, foreground-only guardrails, with explicit human approval before execution.

## Phase 5AG Bounded PRD-Review Pilot

Phase 5AG ran one bounded PRD-review pilot on 2026-06-08 using the established explicit-context and `local_summary` baseline.

Phase 5AG updated:

- `scripts/build_hermes_pilot_context_prompt.py --phase5ag`
- `sandbox/output/hermes_pilot_phase5ag_prd_review_prompt.md`

The Phase 5AG prompt includes bounded context from:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`
- `docs/HERMES_PILOT_MODE.md`
- `docs/HERMES_SECURITY_MODEL.md`
- `docs/HERMES_MODEL_PROVIDER_PLAN.md`

It asked Hermes to review the current Hermes Operating System PRD and supporting context for consistency, missing gates, stale status, and unclear next steps, and to return only:

- PRD consistency findings
- missing or weak guardrails
- stale or contradictory status statements
- recommended PRD updates
- next safest phase recommendation
- whether human approval is required before execution

Capture files:

- `sandbox/output/hermes_pilot_phase5ag_prd_review.md`
- `sandbox/output/hermes_pilot_phase5ag_prd_review.stderr`
- `sandbox/output/hermes_pilot_phase5ag_prd_review.metrics`
- `sandbox/output/hermes_pilot_phase5ag_prd_review_prompt.md`

Observed result:

| Check | Result |
| --- | --- |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter prompt mode | `local_summary` |
| Context budget | 1500 chars |
| Extracted context | 1459 chars; not truncated |
| Selected model | `gemma4:26b` |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| Successful model call | status `200`, response content length `1730`, elapsed `110.172s` |
| Pilot exit code | 0 |
| Pilot elapsed time | 111 seconds |
| Pilot stdout bytes | 1731 |
| Pilot stderr bytes | 471 |
| Pilot output usable | yes |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |
| Residual Hermes process | none observed |
| Desktop launch | none observed |
| External integrations | not touched |
| Real API keys | not used |
| Hermes file writes | no Hermes-generated writes outside `sandbox/output` observed |

Hermes found the Phase 5AF completion status consistent across the PRD, changelog, and model-provider plan. It identified two areas for future clarification: concrete triggers for re-enabling disabled authorities, and procedural requirements for credential rotation before Agent Bus reads or writes resume. It did not identify stale or contradictory status statements in the supplied excerpts.

Guardrail review:

- Hermes stayed within pilot boundaries.
- The harness used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`.
- The harness used the localhost adapter URL only.
- The child process used a dummy local API key.
- `platform_toolsets.cli` remained disabled.
- Adapter metadata showed `tools_present=false` and `tool_schemas_forwarded=false`.
- No Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, message send, Desktop launch, install, permission grant, credential modification, background service, or resident mode occurred.

Recommendation:

Treat Phase 5AG as a successful bounded PRD-review pilot. The next phase should be documentation-only: clarify authority re-enable gates and credential-rotation requirements in the PRD/security docs before any broader Hermes authority, Agent Bus activity, Desktop retry, or resident-mode work.

Phase 5AH completed that documentation-only clarification. Future pilot phases must preserve the explicit-context, `local_summary`, no-tools, no-integrations, foreground-only baseline unless a later phase explicitly changes the pilot boundary.

## Phase 5AV Local PRD Review Through Manual Adapter Service

Phase 5AV ran one bounded local-only Hermes PRD review on 2026-06-10 using the manual adapter service procedure and the locked-down pilot harness.

Phase 5AV updated:

- `scripts/build_hermes_pilot_context_prompt.py --phase5av`
- `sandbox/output/hermes_phase5av_prd_review_prompt.md`

The Phase 5AV prompt includes bounded context from:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`
- `docs/HERMES_OPERATIONAL_READINESS_REVIEW.md`
- `docs/HERMES_LOCAL_VALIDATION_CHECKLIST.md`
- `docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md`

It asked Hermes to review the current local-only operating setup and return only:

- what is ready
- what is not ready
- top 5 risks
- next safest phase
- exact non-goals
- whether human approval is required

Capture files:

- `sandbox/output/hermes_phase5av_prd_review.md`
- `sandbox/output/hermes_phase5av_prd_review.stderr`
- `sandbox/output/hermes_phase5av_prd_review.metrics`
- `sandbox/output/hermes_phase5av_prd_review_prompt.md`

Observed result:

| Check | Result |
| --- | --- |
| Adapter start | `scripts/adapter_service_start.sh` |
| Adapter bind | `127.0.0.1:8088` only |
| DevMonster endpoint | `http://100.93.120.124:11434` |
| Adapter prompt mode | LaunchAgent default `instruction_context` |
| Selected model | `gemma4:26b` |
| Cloud fallback | none configured |
| Adapter model calls | yes |
| First model call | status `502`, provider timeout after `120.011s` |
| Successful model call | status `200`, response content length `1586`, elapsed `102.852s` |
| Pilot exit code | 0 |
| Pilot elapsed time | 227 seconds |
| Pilot stdout bytes | 1587 |
| Pilot stderr bytes | 471 |
| Pilot output usable | yes, with one stale readiness caveat |
| Adapter shutdown | stopped immediately after pilot run |
| Post-run listener | no `8088` listener remained |
| Residual Hermes process | none observed |
| Desktop launch | none observed |
| External integrations | not touched |
| Real API keys | not used |
| Hermes file writes | no Hermes-generated writes outside `sandbox/output` observed |

Hermes returned structured review text within the requested labels. It correctly kept non-goals around sensitive prompts, shell/file-edit authority expansion, Hermes resident mode, Agent Bus activity, real credentials, Desktop launch, `~/.hermes` modification, sudo, cloud-provider integrations, RunAtLoad, and KeepAlive.

Caveat: Hermes listed "Task inbox usage" under ready capabilities even though the local task inbox is not created until Phase 5AW. Codex records that statement as stale and does not treat it as authority or readiness evidence.

Guardrail review:

- Hermes stayed within pilot boundaries.
- The harness used isolated `HERMES_HOME=/private/tmp/hermes-pilot-home`.
- The harness used the localhost adapter URL only.
- The child process used a dummy local API key.
- `platform_toolsets.cli` remained disabled.
- Adapter metadata showed selected model `gemma4:26b`.
- No Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud provider, message send, Desktop launch, install, permission grant, credential modification, background service, resident mode, RunAtLoad, or KeepAlive occurred.

Recommendation:

Treat Phase 5AV as a successful bounded local PRD-review run, with the stale task-inbox statement documented as a caveat. The next phase may create the local-only task inbox scaffold without granting Hermes new authority to execute shell commands, edit files outside approved sandbox outputs, connect integrations, launch Desktop, or use credentials.

## Phase 5AW Local Task Inbox Scaffold

Phase 5AW added a local-only task inbox/outbox scaffold. It did not run Hermes live and did not start the adapter service.

Created paths:

- `sandbox/hermes_inbox/`
- `sandbox/hermes_outbox/`
- `sandbox/hermes_archive/`
- `sandbox/hermes_inbox/next_step_review.task.md`
- `scripts/run_hermes_local_task.sh`
- `docs/HERMES_LOCAL_TASK_INBOX.md`

The local task runner:

- accepts only task files under `sandbox/hermes_inbox/`
- refuses paths outside the inbox
- requires `http://127.0.0.1:8088/health` before invoking Hermes
- does not start or stop the adapter service
- uses persistent Hermes config
- runs Hermes with a sanitized `env -i` child environment
- writes stdout only to `sandbox/hermes_outbox/<task-name>.out.md`
- writes stderr and metrics beside the output
- does not pass real credentials
- does not launch Desktop

Guardrail review:

- no live Hermes task was run in Phase 5AW
- no adapter service was started
- no external integration was connected
- no real credential was used
- no Agent Bus read/write occurred
- no Desktop launch occurred
- no `~/.hermes` file was modified
- no RunAtLoad, KeepAlive, resident mode, or background service was enabled

Recommendation:

Treat Phase 5AW as a scaffold-only completion. The next phase may run exactly one sample inbox task through the manual adapter service procedure, then stop the adapter and verify no listener or process remains.

## First Pilot Task Template

The original path-reading pilot task template is:

```text
sandbox/input/hermes_pilot_next_action_prompt.md
```

It asks Hermes to read only:

- `docs/prd/PRD_MSR_HERMES_OPERATING_SYSTEM.md`
- `docs/prd/CHANGELOG.md`

and then summarize status, identify the next safest phase, and write recommendation text to stdout only.

The first live run was attempted in Phase 5AD and did not produce usable output. Phase 5AE replaced this shape with `sandbox/output/hermes_pilot_next_action_phase5ae_prompt.md`, which embeds bounded local context and produced usable output through `local_summary`. Do not rerun the original path-reading template unchanged.

## Stop Conditions

Stop immediately if Hermes:

- asks for a real API key
- attempts setup/login
- attempts a tool call
- attempts file writes outside `sandbox/output`
- attempts to connect external services
- recommends launching Desktop despite the current fail-closed signing state
- tries to use a provider other than the localhost adapter
