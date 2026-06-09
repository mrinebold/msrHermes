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
| Local pilot harness | Ready for bounded local reasoning | Isolated `HERMES_HOME`, dummy key, localhost base URL, sanitized env, no CLI toolsets | Separate approval for live pilot prompts |
| DevMonster Gemma worker | Conditionally ready for local reasoning | Prior adapter phases selected `gemma4:26b` and produced usable output with explicit local context | Explicit run scope, timeout, cleanup checks |
| Hermes CLI | Ready for isolated pilot use | Installed CLI works with isolated pilot home and custom localhost provider | Persistent config approval |
| Hermes Desktop | Not ready; fail-closed | Official setup bundle remains `com.nousresearch.hermes.setup` version `0.0.1` with invalid strict code-signature behavior | Release-channel clarification or explicit risk acceptance |
| Google Workspace | Not ready | No OAuth run, no token grant, no scopes approved | Credential review/rotation gate plus read-only OAuth phase |
| Supabase Agent Bus | Not ready for live access | Prior anon-key read-only validation completed, but exposed credentials remain deferred | Credential-family-specific approval and read-only scope |
| Home Assistant | Not ready | No token, URL, allowlist, or safety layer approved | Read-only telemetry phase and safety policy |
| GitHub | Not ready | No token use approved for Hermes | Token rotation/review and repository/action scope |
| Credential rotation | Deferred, not complete | Phase 5AI deferral recorded | Owner confirms rotation, revocation, review, or narrower deferral |
| Logging/audit | Partially ready locally | Adapter metadata logging avoids prompt text, file contents, model output, and secrets | Durable audit design before resident/integration use |

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
