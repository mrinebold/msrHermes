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
| Local task inbox | Ready for bounded context-bearing task trials | Phase 5AW added inbox/outbox/archive directories, sample task, docs, and fail-closed runner; Phase 5AX validated one sample task and stopped the service | Future task must include bounded local context if a recommendation is expected |
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
