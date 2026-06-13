# Hermes Operational Readiness Review

Phase: 5AK
Status: local-only readiness review

## Purpose

Review Hermes local operating-system readiness before any future credentialed or read-only integration phase.

Phase 5AK is local-only. It does not approve live credentials, live Agent Bus reads/writes, integrations, Hermes Desktop launch, background services, resident operation, or broader Hermes authority.

## Current Proven Capabilities

- Hermes CLI is installed locally and can run in isolated `HERMES_HOME` profiles.
- The managed adapter runner is configured for foreground-only local operation on `127.0.0.1:8088`.
- The pilot harness writes isolated Hermes config, points only to `http://127.0.0.1:8088/v1`, uses `gemma4:26b`, and uses only `dummy-local-adapter-key`.
- The pilot harness strips real OpenAI, Anthropic, OpenRouter, Supabase, Google, GitHub, Home Assistant, and Helio environment variables from the Hermes child process.
- The local adapter path has produced usable bounded recommendations when explicit local context is supplied through the validated `local_summary` pattern.
- Local tests cover shell syntax, non-localhost refusal, localhost-only pilot config, sensitive env stripping, and real-looking secret marker avoidance.
- Codex remains the execution, verification, commit, push, and external-contact controller.

## Current Blocked Capabilities

- Persistent Hermes configuration.
- Background adapter service or launchd setup.
- Hermes resident operation.
- Google Workspace authentication or reads.
- Supabase live Agent Bus reads.
- Agent Bus writes, dispatch, acknowledgements, or task updates.
- Home Assistant reads or control.
- GitHub token use.
- Cloud model provider use.
- Hermes Desktop relaunch or replacement.
- Credential rotation, credential storage, or credential modification.

## Remaining Risks

- Credential rotation remains deferred; exposed credential families are not proven rotated, revoked, reviewed, or safe.
- The local adapter reaches DevMonster over Tailscale, so any future live run still needs explicit scope, timeout, logging, and cleanup evidence.
- Hermes Desktop remains fail-closed because the official setup bundle has invalid strict code-signature behavior and no confirmed final runtime artifact.
- Persistent Hermes config could accidentally inherit real environment variables or provider/plugin surfaces unless isolated and reviewed first.
- Background or resident operation would introduce startup, logging, shutdown, recovery, and authority risks not yet designed.
- Read-only integrations can still expose sensitive data and require credential-family-specific approval, redaction, audit, and scope limits.
- Agent Bus writes affect durable shared state and must remain behind Helio/ANO governance and human approval.

## Readiness Matrix

| Area | Readiness | Evidence | Blocked Until |
| --- | --- | --- | --- |
| Local adapter | Ready for manual local-only pilot runs | Runner binds `127.0.0.1:8088`, refuses non-localhost/non-8088 settings, logs metadata only | Separate approval for each live run; no background service |
| Local pilot harness | Ready for bounded local reasoning | Isolated `HERMES_HOME`, dummy key, localhost base URL, sanitized env, no CLI toolsets; Phase 5AV produced usable local PRD review output through the manual adapter service | Separate approval for each live pilot prompt |
| Local task inbox | Ready for bounded context-bearing task trials | Phase 5AW added inbox/outbox/archive directories, sample task, docs, and fail-closed runner; Phase 5AX validated one sample task and stopped the service; Phase 5AY added a context-bearing task builder | Separate approval to run the generated context-bearing task |
| DevMonster Gemma worker | Conditionally ready for local reasoning | Prior adapter phases selected `gemma4:26b` and produced usable output with explicit local context | Explicit run scope, timeout, cleanup checks |
| Hermes CLI | Ready for bounded local prompt use; not resident | Persistent config produced the exact approved Phase 5AN stdout through foreground adapter and Phase 5AU stdout through manual adapter service | Resident operation approval |
| Hermes Desktop | Not ready; fail-closed | Official setup bundle remains `com.nousresearch.hermes.setup` version `0.0.1` with invalid strict code-signature behavior | Release-channel clarification or explicit risk acceptance |
| Google Workspace | Not ready | No OAuth run, no token grant, no scopes approved | Credential review/rotation gate plus read-only OAuth phase |
| Supabase Agent Bus | Not ready for live access | Prior anon-key read-only validation completed, but exposed credentials remain deferred | Credential-family-specific approval and read-only scope |
| Home Assistant | Not ready | No token, URL, allowlist, or safety layer approved | Read-only telemetry phase and safety policy |
| GitHub | Not ready | No token use approved for Hermes | Token rotation/review and repository/action scope |
| Credential rotation | Deferred, not complete | Phase 5AI deferral recorded | Owner confirms rotation, revocation, review, or narrower deferral |
| Logging/audit | Partially ready locally | Adapter metadata logging avoids prompt text, file contents, model output, and secrets | Durable audit design before resident/integration use |
| Resident mode | Manual adapter service operation validated; Hermes resident disabled | Phase 5AT validates helper-driven manual adapter service start/status/stop and Phase 5AU validates one Hermes prompt through that procedure while preserving `RunAtLoad=false` and `KeepAlive=false` | Separate approval for RunAtLoad, KeepAlive, or Hermes resident mode |

## Required Gates Before Narrow Capabilities

### Persistent Hermes Config

- Human approval for exact config file path and contents.
- Confirm isolated/persistent `HERMES_HOME` boundary.
- Confirm only localhost adapter provider is configured.
- Confirm cloud providers and platform tools remain disabled.
- Confirm no real credentials are written.
- Review diff before commit or local persistence.

### Background Adapter Service

- Human approval for service design.
- Define launchd plist path, environment, logs, health checks, shutdown command, and rollback.
- Keep bind restricted to `127.0.0.1`.
- Prove no prompt text, file contents, model output, or secrets are logged.
- Add monitoring and residue checks.

### Hermes Resident Operation

- Human approval for resident-mode scope.
- Persistent config must already be reviewed.
- Background adapter policy must already be approved or explicitly excluded.
- Define action classes Hermes may and may not take.
- Define audit logging, stop procedure, rollback, and post-run cleanup.

### Google Read-Only Auth

- Human approval for OAuth client/token path and exact read scopes.
- Credential rotation/review gate must be satisfied or explicitly deferred for Google credentials.
- Run read-only only; no send, edit, share, delete, or permission changes.
- Capture redacted evidence and token cleanup expectations.

### Supabase Read-Only Agent Bus Access

- Human approval for credential family, org, workspace, agent, command, and redaction behavior.
- Service-role key remains disallowed for Hermes.
- Use anon-key read-only mode only if RLS assumptions and credential deferral are explicitly accepted.
- Run config validation before any live read.
- Do not run writes, dispatch, acknowledgements, or task updates.

### Agent Bus Writes

- Human approval for each write class.
- Credential rotation or narrow deferral must be documented.
- Helio/ANO governance, approval IDs, payload schema, rollback, and audit path must be in place.
- Read-only phase must be stable first.

### Home Assistant Read-Only Access

- Human approval for URL, token handling, entity/domain read allowlist, and redaction.
- No service calls.
- No lock, alarm, garage, HVAC, appliance, power, or security control.
- Capture read-only telemetry evidence only.

### Home Assistant Control

- Human approval for each control domain and entity allowlist.
- Read-only phase must be stable first.
- Require dry-run/proposal mode before service calls.
- Require explicit approval for physical-world side effects.
- Define emergency stop and rollback.

### GitHub Token Use

- Human approval for token family, repository, operation class, and scope.
- Token rotation/review gate must be satisfied or explicitly deferred.
- Start with read-only repository metadata if needed.
- Mutations, pushes, PRs, issue updates, and merges require separate approval.

### Desktop Relaunch

- Human approval for controlled Desktop phase.
- Resolve release-channel/signature questions or explicitly accept documented risk.
- Confirm no adapter, credential, sign-in, broad permission, background item, or integration is approved by default.
- Define observation-only checklist and quit/cleanup checks.

## Recommended Next 3 Phases

1. Phase 5AL: persistent Hermes local config proposal only. Draft the exact isolated config and rollback plan in `docs/HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md`, but do not apply it.
2. Phase 5AM: read-only Agent Bus configuration gate. Decide whether anon-key read-only config validation is allowed under the credential deferral boundary, then run config validation only if approved.
3. Phase DESKTOP-13 or 5AN: either send the prepared Desktop support clarification after approval, or continue local-only pilot hardening with no live integrations.

## Explicit Human Approval Points

Human approval is required before:

- starting the adapter live
- running Hermes live
- writing persistent Hermes config
- creating launchd or background services
- using any real credential
- reading Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus data
- writing Agent Bus, Supabase, Google, GitHub, Home Assistant, or Helio state
- launching or replacing Hermes Desktop
- granting filesystem, Accessibility, Screen Recording, Automation, Full Disk Access, OAuth, or token permissions
- sending support messages, emails, issues, or external posts
- broadening Hermes shell, file-edit, gateway, resident, or dispatch authority

## Phase 5AK Conclusion

Hermes is ready only for continued local-only planning, documentation, tests, and separately approved bounded local reasoning. It is not ready for credentialed integrations, live Agent Bus access, resident operation, background services, or Desktop relaunch without a new phase-specific human approval gate.

## Phase 5AL Proposal Result

Phase 5AL added `docs/HERMES_PERSISTENT_LOCAL_CONFIG_PLAN.md` as a proposal-only plan for future persistent Hermes local configuration. The plan keeps Hermes pointed only at `http://127.0.0.1:8088/v1`, uses `gemma4:26b`, permits only a dummy/local syntactic key if required, keeps platform tools disabled, defines future `~/.hermes` backup and rollback paths, and preserves Desktop fail-closed status. It does not apply persistent config or approve live Hermes runs, launchd, resident mode, credentials, Agent Bus access, integrations, or Desktop launch.

## Phase 5AM Application Result

Phase 5AM applied the approved persistent local config to `~/.hermes/config.yaml` after creating `/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak`. The applied config uses `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, `model.api_key=dummy-local-adapter-key`, and `platform_toolsets.cli=[]`.

No `~/.hermes/.env` change was made. No adapter, Hermes live run, Desktop launch, credentialed operation, integration, Agent Bus read/write, launchd plist, background service, resident mode, or authority broadening occurred. Hermes remains not ready for resident operation until a later explicit phase approves a live validation and resident-mode design.

## Phase 5AN Live Local Validation Result

Phase 5AN validated the persistent config with one harmless prompt through the manually started foreground adapter. Hermes exited `0` after `74` seconds, wrote `38` stdout bytes, wrote `0` stderr bytes, and returned exactly `Persistent local Hermes config works.` Adapter metadata showed selected model `gemma4:26b`, response content length `37`, and a successful `POST /v1/chat/completions` in `72.634` seconds.

The adapter was stopped immediately afterward. No `8088` listener, Hermes/adapter/Desktop process, launchd plist, LaunchAgent, or LaunchDaemon match remained. `~/.hermes/.env` stayed untouched. No real API keys, Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud-provider integration, Desktop launch, background service, resident mode, or authority broadening was used.

## Phase 5AO Resident Design Result

Phase 5AO added `docs/HERMES_RESIDENT_MODE_PLAN.md` as a design proposal only. The proposed path is adapter service first, with Hermes remaining manually invoked until a later explicit approval. The future adapter LaunchAgent proposal keeps bind `127.0.0.1:8088`, uses DevMonster Gemma through the existing local adapter path, writes metadata-only logs under `~/.hermes/logs/`, and defines health checks, stop, rollback, and resident-mode gates.

No launchd plist was created, no service was started, no adapter or Hermes process was run, no `~/.hermes` file was modified, no Desktop launch occurred, no integrations or credentials were used, and Hermes autonomous resident mode remains unapproved.

## Phase 5AP Adapter Service Install Proposal Result

Phase 5AP added `docs/HERMES_ADAPTER_SERVICE_INSTALL_PLAN.md` as proposal-only documentation for a future user-level LaunchAgent install. The plan defines label `com.msr.hermes.model-router-adapter`, path `~/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist`, exact future plist XML, working directory `/Users/michaelrinebold/Documents/Helio/helio-command-center`, `RunAtLoad=false`, `KeepAlive=false`, metadata-only log paths, localhost-only bind settings, DevMonster Gemma environment variables, health checks, status commands, stop commands, and rollback/removal commands.

The readiness position does not change: background adapter service installation remains blocked until a separate explicit phase approves plist creation and launchctl operations. Hermes remains manually invoked, Hermes autonomous resident mode is not approved, Hermes Desktop remains fail-closed, and Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, and cloud-provider integrations remain frozen.

No launchd plist was created, installed, bootstrapped, loaded, kickstarted, or started. No adapter or Hermes live run occurred. No `~/Library/LaunchAgents` or `~/.hermes` file was modified. No credentials, integrations, Desktop launch, Agent Bus reads/writes, background service, resident mode, or authority broadening occurred.

## Phase 5AQ Controlled Adapter LaunchAgent Validation Result

Phase 5AQ approved and attempted the controlled user LaunchAgent installation. Preflight and foreground validation passed: no prior `8088` listener or adapter/Desktop process was present, DevMonster returned version `0.30.4`, foreground `/health` worked, foreground `/v1/models` worked, and listener inspection showed only `127.0.0.1:8088`.

The plist was installed at `/Users/michaelrinebold/Library/LaunchAgents/com.msr.hermes.model-router-adapter.plist`, validated with `plutil`, bootstrapped as a user LaunchAgent, and manually started once. The manual launch failed closed with exit code `126` before binding. The stderr log recorded `Operation not permitted` when launchd attempted to execute `/Users/michaelrinebold/Documents/Helio/helio-command-center/scripts/run_model_router_adapter.sh` from the `Documents` repo path.

Final readiness state: plist remains installed on disk for inspection, but the service is unloaded and stopped; no `8088` listener remains; no adapter, Hermes, Hermes Desktop, or Hermes resident process remains. No `~/.hermes` file was modified, no credentials or integrations were used, and no Agent Bus read/write occurred. The next gate should remediate the launchd execution path or make an explicit macOS privacy permission decision before any service retry.

## Phase 5AR Adapter Service Path Remediation Proposal Result

Phase 5AR added `docs/HERMES_ADAPTER_SERVICE_PATH_REMEDIATION.md` as proposal-only documentation. It compares a minimal wrapper under `/Users/michaelrinebold/.local/bin/`, moving the whole repo, granting macOS privacy permissions, foreground-only deferral, and another user-owned non-protected directory.

The recommended remediation is the minimal wrapper path `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`. This avoids broad macOS privacy permissions, avoids moving the whole repo, keeps adapter logic in the reviewed runner, preserves localhost-only enforcement, and keeps real credentials out of the wrapper and plist.

No wrapper was created, no plist was modified, no launchd operation was retried, no adapter or Hermes process was started, no privacy permissions were granted, no repo move occurred, no integrations or credentials were used, and no `~/.hermes` file was modified.

## Phase 5AS Adapter LaunchAgent Wrapper Service Result

Phase 5AS created `/Users/michaelrinebold/.local/bin/msr-hermes-model-router-adapter`, copied the minimal adapter runtime to `/Users/michaelrinebold/Library/Application Support/Helio/hermes-adapter-service/current`, and updated the LaunchAgent to use that non-`Documents` runtime. The plist retained `RunAtLoad=false`, `KeepAlive=false`, localhost-only environment variables, and no real credentials.

The first wrapper-only attempt failed closed because the service still depended on the `Documents` repo path. The final self-contained runtime fix succeeded: manual `launchctl kickstart` started the adapter, `/health` returned status `ok`, `/v1/models` returned model metadata including `gemma4:26b`, and listener inspection showed only `127.0.0.1:8088`.

The service was stopped and unloaded after validation. No `8088` listener remains, no adapter/Hermes/Desktop/resident process remains, no `~/.hermes` file was modified, no credentials or integrations were used, and no Agent Bus read/write occurred.

## Phase 5AT Manual Adapter Service Runbook Result

Phase 5AT added `docs/HERMES_ADAPTER_SERVICE_RUNBOOK.md` plus `scripts/adapter_service_start.sh`, `scripts/adapter_service_stop.sh`, and `scripts/adapter_service_status.sh`.

The helpers use the existing user LaunchAgent only, do not use sudo, do not modify the plist, do not create services, and fail closed on unsafe listener or plist-policy drift. Validation showed manual start succeeded, `/health` worked, `/v1/models` returned `gemma4:26b`, listener inspection showed only `127.0.0.1:8088`, stop succeeded, and final status reported `loaded=false` and `listener=false`.

Readiness position: manual adapter service start/stop is ready as an operator procedure. Hermes resident mode, automatic RunAtLoad, KeepAlive, Desktop, credentials, integrations, and Agent Bus activity remain unapproved.

## Phase 5AU Manual-Service Hermes Validation Result

Phase 5AU validated the approved manual adapter service procedure with one harmless Hermes prompt through the persistent localhost-only config. The adapter service started through `scripts/adapter_service_start.sh`, `/health` returned status `ok`, `/v1/models` returned model metadata including `gemma4:26b`, and listener inspection showed only `127.0.0.1:8088`.

Hermes exited `0` after `28` seconds, wrote `49` stdout bytes, wrote `0` stderr bytes, and returned exactly `Hermes works through the manual adapter service.` The service was stopped with `scripts/adapter_service_stop.sh`; final status reported `loaded=false` and `listener=false`, with no matching adapter, Hermes, Desktop, or resident process remaining.

Readiness position: the manual adapter service is now validated for bounded local Hermes prompt execution. Additional prompts, PRD review, task inbox usage, resident mode, automatic RunAtLoad, KeepAlive, Desktop, credentials, integrations, and Agent Bus activity still require explicit phase approval.

## Phase 5AV Local PRD Review Result

Phase 5AV ran one bounded local PRD review through the manual adapter service and locked-down pilot harness. `scripts/adapter_service_start.sh` started the adapter service, `/health` returned status `ok`, `/v1/models` returned model metadata including `gemma4:26b`, and listener inspection showed only `127.0.0.1:8088`.

Hermes exited `0` after `227` seconds, wrote `1587` stdout bytes, wrote `471` stderr bytes, and returned structured review text under the requested labels. Adapter metadata showed one provider timeout at `120.011` seconds followed by a successful `gemma4:26b` response with content length `1586` in `102.852` seconds.

Caveat: Hermes prematurely listed "Task inbox usage" as ready even though the local task inbox is not created until Phase 5AW. Codex treats that as a stale statement, not as approval or readiness evidence.

The service was stopped immediately afterward. No `8088` listener, adapter, Hermes, Desktop, or resident process remained. No external integration, real credential, Agent Bus read/write, Desktop launch, background service, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred.

Readiness position: bounded local review is viable through the manual adapter service, but Hermes output still requires Codex review before it informs the next phase. The next narrow capability should be a local-only task inbox/outbox scaffold with strict path and output controls.

## Phase 5AW Local Task Inbox Scaffold Result

Phase 5AW created `sandbox/hermes_inbox/`, `sandbox/hermes_outbox/`, `sandbox/hermes_archive/`, `sandbox/hermes_inbox/next_step_review.task.md`, `scripts/run_hermes_local_task.sh`, and `docs/HERMES_LOCAL_TASK_INBOX.md`.

The runner refuses task paths outside `sandbox/hermes_inbox/`, requires `http://127.0.0.1:8088/health` before invoking Hermes, uses persistent localhost-only Hermes config, strips sensitive environment variables through `env -i`, writes stdout only to `sandbox/hermes_outbox/<task-name>.out.md`, and writes stderr/metrics beside that output. It does not start or stop the adapter automatically.

No live inbox task was run in Phase 5AW. No adapter service was started, no Hermes live prompt was run, no external integration or real credential was used, no Agent Bus read/write occurred, no Desktop launch occurred, no `~/.hermes` file was modified, and no RunAtLoad, KeepAlive, resident mode, background service, or authority broadening occurred.

Readiness position: the local task scaffold is ready for exactly one Phase 5AX sample task run through the manual adapter service procedure.

## Phase 5AX Local Inbox Task Execution Result

Phase 5AX ran one sample inbox task through the manual adapter service procedure. `scripts/adapter_service_start.sh` started the adapter service, verified `/health`, verified `/v1/models`, and showed only `127.0.0.1:8088` listening.

`scripts/run_hermes_local_task.sh sandbox/hermes_inbox/next_step_review.task.md` exited `0`, wrote stdout to `sandbox/hermes_outbox/next_step_review.out.md`, stderr to `sandbox/hermes_outbox/next_step_review.stderr`, and metrics to `sandbox/hermes_outbox/next_step_review.metrics`. Metrics recorded `65` elapsed seconds, `148` stdout bytes, and `0` stderr bytes.

Adapter metadata showed selected model `gemma4:26b`, response content length `147`, and successful `POST /v1/chat/completions` status `200` in `64.204` seconds.

Hermes output was a safe fail-closed answer: it did not recommend a phase because the task file did not include enough local context. This confirms the inbox runner works but also shows that future recommendation tasks need bounded context embedded in the task file.

The service was stopped immediately afterward. No `8088` listener, adapter, Hermes, Desktop, or resident process remained. No external integration, real credential, Agent Bus read/write, Desktop launch, background service, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred.

Readiness position: the local inbox/outbox path is validated for a single bounded task. The next improvement should be a context-bearing task template, not resident mode or external integrations.

## Phase 5AY Context-Bearing Task Builder Result

Phase 5AY added `scripts/build_hermes_local_task.py` and generated `sandbox/hermes_inbox/next_phase_recommendation_with_context.task.md`.

The builder writes only under `sandbox/hermes_inbox/`, refuses output paths outside the inbox, includes bounded excerpts from approved local docs, labels every source path, records character limits per source, refuses env/secret/token/key/credential-like source paths, and refuses real-looking secret markers before writing a task.

The generated default task asks Hermes to recommend the next safest local-only Hermes phase using only embedded context and explicitly forbids external integrations, credentials, Desktop launch, Agent Bus access, Google, Supabase, Home Assistant, GitHub, and Helio.

No adapter service was started, no Hermes live task was run, no external integration or real credential was used, no Agent Bus read/write occurred, no Desktop launch occurred, no `~/.hermes` file was modified, and no RunAtLoad, KeepAlive, resident mode, background service, or authority broadening occurred.

Readiness position: the inbox now has a context-bearing task ready for a later separately approved single live task run.

## Phase 5AZ Context-Bearing Task Attempt Result

Phase 5AZ attempted one generated context-bearing inbox task through the manual adapter service. The adapter service started manually, `/health` worked, `/v1/models` worked, and listener inspection showed only `127.0.0.1:8088`.

The task did not complete with usable output. Outbox stdout and stderr were both `0` bytes. Adapter metadata showed selected model `gemma4:26b`, first chat-completions call timed out after `120.016` seconds with status `502`, and a second model call was still in flight when Codex terminated the hanging local task fail-closed after more than 180 seconds.

The service was stopped immediately afterward. No `8088` listener, adapter, Hermes, Desktop, or resident process remained. No external integration, real credential, Agent Bus read/write, Desktop launch, background service, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred.

Readiness position: local-only operations remain safe but Phase 5AZ did not validate the generated context-bearing task as usable. Do not continue to operational runbook/readiness certification until a compact context-bearing task retry succeeds in a separately approved phase.

## Phase 5AZ-R Compact Context-Bearing Retry Result

Phase 5AZ-R remediated the Phase 5AZ timeout by adding compact mode to `scripts/build_hermes_local_task.py` and generating `sandbox/hermes_inbox/next_phase_recommendation_compact.task.md`. The compact task used a `1100` character embedded context budget and asked for one next-phase recommendation under `250` words.

The compact inbox task ran through the manual adapter service and exited `0`. Metrics recorded `101` elapsed seconds, `548` stdout bytes, `0` stderr bytes, selected model `gemma4:26b`, response content length `547`, and adapter chat-completions time `99.079` seconds.

Hermes returned structured output with the requested fields. The recommendation was conservative: another validation-style local-only phase rather than readiness certification. Treat that output as useful but advisory; Codex/human review remains required before promoting the local-only loop to final readiness.

The service was stopped immediately afterward. No `8088` listener, adapter, Hermes, Desktop, or resident process remained. No external integration, real credential, Agent Bus read/write, Desktop launch, background service, RunAtLoad, KeepAlive, `~/.hermes` modification, or authority broadening occurred.

Readiness position: compact context-bearing inbox tasks are now viable. The next phase may create the human operations runbook, while still keeping resident mode and integrations frozen.

## Phase 5BA Local Operations Runbook Result

Phase 5BA created `docs/HERMES_LOCAL_OPERATIONS_RUNBOOK.md` as the human-facing runbook for safe manual local-only Hermes use.

The documented operating loop is:

1. start the adapter service manually
2. verify status and localhost-only binding
3. build a compact context-bearing inbox task
4. run the local task through Hermes
5. review outbox output and metrics
6. stop the adapter service
7. verify no `8088` listener or adapter/Hermes/Desktop/resident process remains

The runbook also documents troubleshooting, credential-free boundaries, rollback, what is ready, and what is not ready. Phase 5BA did not start the adapter service, run Hermes live, launch Desktop, use credentials, connect integrations, perform Agent Bus reads/writes, modify `~/.hermes`, enable RunAtLoad, enable KeepAlive, create resident mode, or broaden authority.

Readiness position: manual local-only operations are now documented for human use. The next phase may produce final local-only readiness certification, but resident mode and external integrations remain frozen.

## Phase 5BB Local-Only Readiness Certification Result

Phase 5BB added `docs/HERMES_LOCAL_ONLY_READY_REPORT.md`.

The report certifies Hermes for manual local-only use only. The certified operating mode is manual adapter service start/stop, Hermes CLI local-only inference, context-bearing or compact inbox tasks, outbox review, and cleanup verification.

The report explicitly keeps these capabilities unapproved:

- resident Hermes
- `RunAtLoad=true`
- `KeepAlive=true`
- Desktop launch
- Google, Supabase, GitHub, Home Assistant, Helio, Agent Bus, or cloud-provider integrations
- real credentials
- broad filesystem authority
- shell execution by Hermes

The report also records the expected final state: LaunchAgent installed but stopped/unloaded, no `8088` listener, no Hermes process, no adapter process, no Desktop process, and repo clean.

Phase 5BB did not start the adapter service, run Hermes live, launch Desktop, use credentials, connect integrations, perform Agent Bus reads/writes, modify `~/.hermes`, enable RunAtLoad, enable KeepAlive, create resident mode, or broaden authority.

Readiness position: the manual local-only milestone is certified. The next step may add a read-only local status command for operator checks without starting services or widening authority.

## Phase 5BC Local Status Command Result

Phase 5BC added `scripts/hermes_local_status.sh`.

The status command is read-only. It reports repo state, adapter LaunchAgent state, local listener state, local `/health` and `/v1/models` only when a listener is present, Hermes CLI path/version, Hermes/Desktop/resident-like process presence, localhost config booleans, and forbidden environment variable names without values.

The command does not start or stop services, modify files, launch Desktop, connect integrations, print secret values, create launchd files, or broaden authority.

Readiness position: the local-only milestone now has an operator status check. The next phase should be a proposal-only resident Hermes authority model, not runtime enablement.

## Phase 6A Resident Authority Model Result

Phase 6A created `docs/HERMES_RESIDENT_AUTHORITY_MODEL.md`.

The authority model is proposal-only. It defines tiers 0 through 7:

- observe only
- recommend
- draft
- local approved execution
- external read-only
- external draft/propose
- external approved action
- resident delegated operator

It also defines human approval rules, audit log requirements, emergency stop requirements, allowed and forbidden file zones, command allowlist and denylist concepts, credential handling, network access, process/service management, Hermes-to-Helio delegation boundaries, Hermes-to-DevMonster inference boundaries, Desktop fail-closed behavior, later RunAtLoad/KeepAlive consideration, and minimum acceptance criteria before resident mode.

Phase 6A did not enable resident mode, create a Hermes launchd service, set `RunAtLoad=true`, set `KeepAlive=true`, start the adapter service, run Hermes live, connect integrations, use credentials, perform Agent Bus reads/writes, launch Desktop, modify `~/.hermes`, or broaden Hermes authority in code.

Readiness position: resident authority is now defined as a tiered proposal. The next safe phase is audit log design for Hermes actions, still proposal-only unless separately approved.

## Phase 6B Audit Log Design Result

Phase 6B created `docs/HERMES_AUDIT_LOG_DESIGN.md`.

The design defines audit principles, event categories, required event fields, local append-only JSONL storage under `logs/hermes_audit/`, rotation and retention policy, redaction rules, approval logging, fail-closed logging, rollback logging, and human/raw/daily/phase audit views.

The design explicitly requires no secrets in logs, prompt/file contents redacted by default, metadata-first logging, local storage by default, no cloud sync by default, no external writes, emergency_stop events, approval events, and fail_closed events.

Phase 6B did not create audit directories, implement audit writes, enable resident mode, create a Hermes launchd service, set `RunAtLoad=true`, set `KeepAlive=true`, start the adapter service, run Hermes live, connect integrations, use credentials, perform Agent Bus reads/writes, launch Desktop, modify `~/.hermes`, or broaden authority.

Readiness position: audit logging is designed but not implemented. The next safe phase is emergency stop design, still proposal-only.

## Phase 6C Emergency Stop Design Result

Phase 6C created `docs/HERMES_EMERGENCY_STOP_DESIGN.md`.

The design defines emergency stop goals, triggers, stop levels, future command proposal, required behavior, audit interaction, and acceptance criteria before resident mode. It explicitly requires no sudo, no deletion, no credential printing, no external calls, safe repeated runs, preserved logs/artifacts/backups, adapter stop capability, resident process stop only after resident mode exists, inbox freeze behavior, and `emergency_stop` audit events after audit logging is implemented.

Phase 6C did not create `scripts/hermes_emergency_stop.sh`, create freeze flags, stop services, start services, enable resident mode, create a Hermes launchd service, change RunAtLoad/KeepAlive, launch Desktop, connect integrations, use credentials, perform Agent Bus reads/writes, modify `~/.hermes`, or broaden authority.

Readiness position: emergency stop is designed but not implemented. The next safe phase is resident service design, proposal-only.

## Phase 6D Resident Service Proposal Result

Phase 6D created `docs/HERMES_RESIDENT_SERVICE_PROPOSAL.md`.

The proposal defines the future resident service purpose, label `com.msr.hermes.resident`, user LaunchAgent execution model, proposed future script `scripts/hermes_resident_loop.sh`, loop responsibilities, non-goals, allowed file zones, forbidden zones, processing flow, acceptance criteria, and rollback concept.

The proposal keeps first validation manual-start only, `RunAtLoad=false`, `KeepAlive=false`, no sudo, audit logging required before any execution, emergency stop compatibility, no shell execution, no external integrations, no Desktop, no credentials, no broad filesystem scanning, and human approval before install.

Phase 6D did not create `scripts/hermes_resident_loop.sh`, create a resident LaunchAgent, set RunAtLoad/KeepAlive, start services, run Hermes live, connect integrations, use credentials, perform Agent Bus reads/writes, launch Desktop, modify `~/.hermes`, or broaden authority.

Readiness position: the future resident service is designed but not implemented. The next safe phase is Hermes-to-Helio delegation interface design, proposal-only.

## Phase 6E Hermes-To-Helio Delegation Interface Result

Phase 6E created `docs/HERMES_HELIO_DELEGATION_INTERFACE.md`.

The proposal defines the boundary between Hermes, Helio/ANO, DevMonster, and Agent Bus. Hermes owns the Mac mini local operator role; Helio/ANO owns agent society and governance; DevMonster supplies inference, not operational authority; and Agent Bus remains frozen until approved.

The proposal defines delegation types, non-goals, a future message shape, staged rollout from documentation-only through resident delegated operator, audit requirements, and acceptance criteria before any Helio or Agent Bus integration.

Phase 6E did not connect Helio, write Supabase, read live Agent Bus records, use credentials, dispatch agents, start services, run Hermes live, launch Desktop, modify `~/.hermes`, or broaden authority.

Readiness position: resident-readiness proposals now cover authority, audit, emergency stop, resident service, and Helio delegation boundaries. The next safe phase is command allowlist and denylist proposal, or audit/emergency-stop implementation planning if explicitly approved.

## Phase 6F Command Policy Result

Phase 6F created `docs/HERMES_COMMAND_POLICY.md`.

The proposal defines command policy principles, command categories, initial allowlist candidates, initial denylist entries, approval classes, future enforcement components, and acceptance criteria before command execution.

The policy states that Hermes cannot execute commands yet and may only draft or recommend commands. Future execution requires human approval, audit logging, emergency stop, file zone policy, approval record lookup, dry-run tests, and allowlist/denylist enforcement.

Phase 6F did not create a command executor, enable resident mode, start the adapter service, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or broaden Hermes authority.

Readiness position: command policy is proposed but not enforced. The next safe phase is file zone policy proposal.

## Phase 6G File Zone Policy Result

Phase 6G created `docs/HERMES_FILE_ZONE_POLICY.md`.

The proposal defines green read/write zones, yellow read-only zones, orange approval-required zones, and red forbidden zones. It identifies approved sandbox and audit paths, read-only docs/scripts/tests context, approval-required writes, and forbidden secret/system/private paths.

The policy includes secret detection rules, symlink refusal or resolution, path traversal refusal, zone classification, read/write gates, audit events for every file read/write, and fail-closed behavior on ambiguity.

Phase 6G did not implement path enforcement, scan files, start services, run Hermes live, connect integrations, use credentials, modify `~/.hermes`, launch Desktop, or broaden Hermes authority.

Readiness position: file zone policy is proposed but not enforced. The next safe phase is human approval record model.

## Phase 6H Approval Record Model Result

Phase 6H created `docs/HERMES_APPROVAL_RECORD_MODEL.md`.

The proposal defines approval purpose, required fields, approval types, local JSONL storage under `logs/hermes_approvals/`, lifecycle, non-goals, audit integration, command policy integration, emergency stop integration, and acceptance criteria before execution.

The model requires scoped, expiring, auditable approval records before future execution, writes, sends, commits, service starts, resident starts, or external actions. It forbids blanket permanent approval, approval by model alone, hidden approvals, external approval stores, and credentials inside approval records.

Phase 6H did not implement approval storage, enable command execution, enable resident mode, start services, run Hermes live, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

Readiness position: resident safety policies now cover command policy, file zones, and approval records as proposals. The next safe phase is implementation planning for audit logs, approval records, file-zone enforcement, and emergency stop, still without enabling resident mode.

## Phase 6I Safety Implementation Roadmap Result

Phase 6I created `docs/HERMES_SAFETY_IMPLEMENTATION_ROADMAP.md`.

The roadmap defines the staged implementation order for the safety infrastructure required before resident Hermes can be enabled:

- audit log writer
- approval record writer/reader
- file-zone classifier
- command-policy classifier
- emergency stop script
- dry-run resident loop
- resident loop proposal validation
- manual resident dry-run
- future resident LaunchAgent proposal
- final resident enablement gate

Each stage documents objective, likely files/scripts, risks, tests, rollback, acceptance criteria, and what remains forbidden.

Phase 6I did not implement safety modules, enable command execution, enable resident mode, create a Hermes launchd service, start services, run Hermes live, connect integrations, use credentials, write Agent Bus records, launch Desktop, modify `~/.hermes`, or broaden Hermes authority.

Readiness position: the implementation order is now defined. The next safe phase is the audit and approval implementation plan, still proposal-only and still without runtime enforcement.

## Phase 6R Emergency Stop Script Result

Phase 6R created `scripts/hermes_emergency_stop.sh`.

The script is a no-sudo, repeat-safe local emergency stop entrypoint. It creates or refreshes `sandbox/hermes_control/FROZEN`, writes `sandbox/hermes_control/FROZEN.reason`, detects adapter/Hermes/Desktop/resident-like state, stops the approved adapter service only if it is already running, and writes a metadata-only audit event when the local audit writer is importable.

The script does not kill arbitrary processes, delete artifacts, start services, run Hermes live, launch Desktop, modify `~/.hermes`, connect integrations, print secrets, or enable resident mode.

Readiness position: emergency stop now exists for local freeze/approved-adapter-stop behavior. The next safe phase is a dry-run policy check script, still without command execution or resident mode.
