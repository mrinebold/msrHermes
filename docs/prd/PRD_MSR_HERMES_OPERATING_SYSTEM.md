# PRD: MSR Hermes Operating System

## Status

Phase DESKTOP-10 documented Hermes Desktop artifact integrity escalation and release-channel clarification. Hermes Desktop remains fail-closed because the official DMG verifies as a disk image, but the mounted app remains a setup/bootstrap bundle with invalid strict code-signature behavior and no confirmed trusted final Desktop runtime path.

Repository status is maintained by git; this PRD records Phase DESKTOP-10 as documentation-only and complete within the approved no-launch/no-replacement/no-message-send scope.

## Architecture Decision

Hermes is the resident Mac mini operator. Helio/ANO is the governed coordination layer for the broader MSR/CivicGrantsAI agent society. Hermes must not bypass Helio/ANO to request specialist work, connect Google Workspace, control Home Assistant, or write to the Supabase agent bus.

## Machine-Boundary Gating vs ANO Governance

Hermes is gated because it can cross the Mac mini and external-system boundary. Hermes-specific gates protect the human, local files, local services, secrets, Google Workspace, Home Assistant, Supabase writes, GitHub writes, and external communication.

The broader ANO agent society is not governed by Hermes. Helio/ANO coordinates and governs agents through ANO governance rules, roles, permissions, consensus/workflow rules, and each agent's own policy framework.

Hermes may request work from Helio/ANO, but it does not own or command the ANO. Other agents are not subordinate to Hermes. Hermes approval gates protect boundary-crossing actions; they do not restrict the internal freedom of the agent society.

## Phase History

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 5A | Complete | Defined Hermes-owned Mac mini architecture with Helio as the controlled interface to the agent team. |
| Phase 5B | Complete | Documented Hermes installation, security, configuration, and approval gates without installing Hermes. |
| Phase 5C | Complete | Proposed exact install, config, and rollback commands only. Hermes was not installed. |
| Phase 5D | Complete | Installed the pinned Hermes client locally with no setup wizard, no browser bootstrap, no credentials, no launchd service, and no integrations enabled. |
| Phase 5E | Complete | Created a local sandbox and ran Hermes against sandbox prompts only; execution failed closed with no inference provider configured, so no summaries were produced. Non-zero exit was expected and acceptable. |
| Phase 5F | Complete | Planned Hermes local inference through a localhost OpenAI-compatible MSR Model Router adapter instead of direct DevMonster or cloud providers. |
| Phase 5G | Complete | Added the localhost-only OpenAI-compatible Model Router adapter scaffold with mocked tests and no Hermes configuration. |
| Phase 5H | Complete | Manually ran the adapter in the foreground on localhost and validated the end-to-end Model Router to DevMonster Gemma path after DevMonster repair. |
| Phase 5I | Complete | Ran Hermes with an isolated sandbox home pointed at the localhost adapter; runs exited 0 but produced `(empty)` summary outputs. |
| Phase 5J | Complete | Added adapter request logging and documented Hermes CLI one-shot invocation behavior without sending live prompts. |
| Phase 5K | Complete | Ran one bounded `hermes -z` diagnostic; Hermes called the adapter, including chat completions, but stdout remained `(empty)`. |
| Phase 5L | Complete | Diagnosed Hermes' chat-completions response contract and added metadata-only adapter response-shape logging. |
| Phase 5M | Complete | Added OpenAI-compatible SSE support for `stream=true` chat-completions requests with mocked tests only. |
| Phase 5N | Complete | Ran one bounded `hermes -z` diagnostic after the SSE fix; Hermes returned usable stdout. |
| Phase 5O | Complete | Ran two bounded sandbox file-summary attempts after the SSE fix; both exited 0 but returned `(empty)`. |
| Phase 5P | Complete | Added metadata-only message-structure logging and documented that the adapter reads all messages but does not execute Hermes file tools. |
| Phase 5Q | Complete | Ran one bounded sample-note metadata diagnostic; Hermes sent non-empty file-like context with tools present, but all four model calls returned zero content. |
| Phase 5R | Complete | Diagnosed tool-present payload compatibility offline and recommended local Gemma prompt flattening plus tool semantic stripping. |
| Phase 5S | Complete | Added opt-in local Gemma compatibility mode that flattens Hermes multi-message payloads and ignores tool schemas for routing. |
| Phase 5T | Complete | Ran one bounded sample-note retry with compat mode enabled; compat metadata was correct but Gemma still returned zero content. |
| Phase 5U | Complete | Added metadata-only prompt-construction diagnostics and offline Gemma prompt modes; recommended `instruction_context` for the next live retry. |
| Phase 5V | Complete | Ran one bounded sample-note retry with `instruction_context`; prompt reordering worked, but Gemma still returned zero content. |
| Phase 5W | Complete | Ran one bounded sample-note retry with `no_tool_vocab`; tool vocabulary removal worked, but Gemma still returned zero content. |
| Phase 5X | Complete | Added `local_summary` prompt mode to extract user instruction and file-like context while dropping unrelated Hermes scaffold. |
| Phase 5Y | Complete | Ran one bounded sample-note retry with `local_summary`; prompt extraction succeeded, but DevMonster/Gemma timed out after 30s on each retry. |
| Phase 5Z | Complete | Added provider timeout and local summary context-budget controls; no live prompts were run. |
| Phase 5AA | Complete | Ran one bounded tuned local-summary retry for `sample_note.md`; Hermes produced usable five-bullet output. |
| Phase DESKTOP-1 | Complete | Added planning-only Hermes Desktop install roadmaps for Mac mini and DevMonster; Desktop was not downloaded or installed. |
| Phase DESKTOP-2 | Complete | Documented exact future Mac mini Desktop download, inspection, install, first-launch validation, and rollback commands without downloading or launching Desktop. |
| Phase DESKTOP-3 | Complete | Installed Hermes Desktop on the Mac mini at `/Applications/Hermes.app`; Desktop was not launched or configured. |
| Phase DESKTOP-4 | Complete | Attempted one guarded first launch; bootstrap job/log appeared, no usable UI was observed, and the process was killed with no integrations or permissions granted. |
| Phase DESKTOP-5 | Complete | Diagnosed the installed app as a bootstrap installer bundle with invalid signature/openability state; no launch or config changes were made. |
| Phase DESKTOP-6 | Complete | Verified DMG copies and installed app metadata; mounted-bundle comparison was blocked by sandboxed `hdiutil attach`. |
| Phase DESKTOP-7A | Complete | Reran local Mac mini bundle diagnostics; confirmed `com.nousresearch.hermes.setup` / `Hermes-Setup`, invalid strict signature, no quarantine marker, no Hermes launch agents, and an existing `Hermes-Setup` process. |
| Phase DESKTOP-8 | Complete | Planned official artifact reacquisition, verification, comparison, rollback, replacement, and first-launch guardrails only; no artifact was downloaded or installed. |
| Phase DESKTOP-9 | Complete | Downloaded official macOS DMG to `~/Downloads/hermes-desktop-official/`, verified and mounted it read-only, compared mounted metadata to `/Applications/Hermes.app`, and unmounted; no install, launch, or replacement was performed. |
| Phase DESKTOP-10 | Complete | Created artifact integrity escalation record, release-channel questions, and an unsent draft support message; no Desktop state was changed. |
| Phase 6A | Complete | Discovered the Supabase Agent Bus source family and designed the Hermes-through-Helio bus plan. |
| Phase 6B | Complete | Elevated `packages/ano-messaging` as the primary canonical message bus source candidate and defined the Hermes-facing Agent Bus contract. |
| Phase 6C | Complete | Designed the Helio-facing adapter scaffold proposal with read-only-first mode, fail-closed rules, and mocked test strategy. |
| Phase 6D | Complete | Implemented the read-only `services/agent_bus` scaffold with mocked tests, no Supabase imports, no writes, and no polling worker. |
| Phase 6E | Complete | Planned the live read-only Supabase preflight, preferring anon-key RLS and defining exact read queries without connecting Supabase. |
| Phase 6G | Complete | Implemented a stdlib-only read-only preflight script and mocked tests without connecting Supabase or installing packages. |
| Phase 6H | Complete | Ran live read-only anon-key validation for org `msr`, workspace `default`, and agent `hermes`; all approved reads returned safely with zero scoped rows. |
| Phase SECURITY-1 | Complete | Documented credential exposure and created a rotation checklist without rotating credentials or calling external APIs. |
| Phase ANO-GOV-1 | Complete | Clarified that Hermes is gated at the machine boundary while ANO agents are governed by Helio/ANO and are not subordinate to Hermes. |
| Phase SECURITY-2 | Complete | Added post-exposure rotation status tracking and blocked further live bus reads/writes until rotation is confirmed or explicitly deferred. |

## Completed Work Snapshot

Completed and committed locally:

- Hermes ownership architecture: Hermes is the resident Mac mini operator, while Helio/ANO is the governed coordination layer for the broader agent society.
- Hermes install planning: install options, security model, prerequisites, config layout, rollback planning, and install-command proposal were documented without installing Hermes.
- Hermes controlled install: Hermes Agent v0.15.2 / 2026.5.29.2 was installed at `~/.hermes/hermes-agent` with command launcher `~/.local/bin/hermes`.
- Model routing and DevMonster planning: Hermes remains local-first through the existing Helio model router and DevMonster Gemma4 path.
- Google Workspace and Home Assistant planning: both remain future gated integrations; neither is connected or enabled.
- Supabase Agent Bus discovery: `packages/ano-messaging` was elevated as the primary canonical message-bus source candidate.
- Agent Bus contract: canonical tables, fields, statuses, permissions/RLS expectations, payload shapes, services, and polling behavior were documented.
- Hermes-to-Helio bus planning: Hermes may observe and request through Helio/ANO, but must not directly dispatch agents or write to the bus.
- Read-only adapter scaffold: `services/agent_bus/` was added with fail-closed mock behavior and unit tests only.
- Live read-only preflight script: `scripts/agent_bus_readonly_preflight.py` was added using Python stdlib only, process environment only, GET-only requests, and redacted output.
- Live read-only validation: anon-key validation ran for org `msr`, workspace `default`, agent `hermes`; all approved reads returned 0 scoped rows.
- Credential rotation tracking: exposed credential types were documented in the rotation checklist; no rotation was performed automatically.
- ANO governance clarification: Hermes gating is machine-boundary protection, not governance over the ANO agent society.
- SECURITY-2 rotation status: Supabase service-role, OpenAI, Anthropic/Claude, GitHub token, and Supabase anon-key review remain pending user confirmation unless the user later confirms rotation or explicit deferral.
- Phase 5D validation: install tag `v2026.5.29.2`, commit `77a1650c7`, and absent launchd plist were verified; setup, browser bootstrap, model configuration, and live integrations were not enabled.
- Phase 5E sandbox validation: `sandbox/input/` and `sandbox/output/` were created with synthetic sample docs, Hermes was run from the sandbox with an isolated `HERMES_HOME`, empty isolated `.env`, provider credential environment variables removed, no MCP servers configured, and no launchd/background service. Startup succeeded in 0.161 seconds. Summary attempts exited fail-closed in 4.989 seconds and 1.709 seconds with "No inference provider configured." No cloud credentials were provided.
- Phase 5F model-provider planning: Option C was selected as the target architecture: Hermes -> localhost OpenAI-compatible MSR Model Router adapter -> `services/model_router` -> DevMonster Gemma / future approved providers. Initial implementation should route only to DevMonster through the local adapter while cloud providers remain disabled and fail-closed.
- Phase 5G adapter scaffold: `services/model_router_adapter/` was added using Python stdlib HTTP serving, default host `127.0.0.1`, default port `8088`, allowed endpoints only, `services/model_router` delegation, and mocked unit tests.
- Phase 5H live adapter retry: the adapter was started manually in the foreground, bound only to `127.0.0.1:8088`, and stopped after validation. `GET /health` returned 200 in 0.005s. `GET /v1/models` returned 200 in 0.095s and included `gemma4:26b`. `POST /v1/chat/completions` with the single approved prompt returned `Adapter operational.` in 15.179s using `gemma4:26b` through `devmonster_ollama`. `GET /v1/embeddings` returned 404 in 0.001s.
- Phase 5I Hermes sandbox validation: Hermes startup in isolated `HERMES_HOME` took 0.394s. Initial chat runs exited 0 in 60.676s and 36.896s but did not create summary files. One-shot retries exited 0 in 105.852s and 94.954s and created `sample_note_summary.md` and `sample_prd_summary.md`, but each file was only 8 bytes and contained `(empty)`. Stderr files were empty. Adapter foreground logs emitted no per-request lines. The adapter was stopped and no listener remained on `8088`.
- Phase 5J adapter observability: `services/model_router_adapter` gained optional request metadata logging behind `MODEL_ROUTER_ADAPTER_LOG_REQUESTS=true`, with timestamp, method, path, response status, selected model, and elapsed time while redacting prompt/message content and secrets by default.
- Phase 5J Hermes CLI diagnosis: local help/docs confirm top-level `hermes -z` / `--oneshot` is the intended stdout-only scriptable prompt path; `hermes chat -q` is non-interactive chat but can include session behavior; this installed Hermes version has no `hermes run` command; local OpenAI-compatible endpoints should use `model.provider=custom` and `model.base_url=http://127.0.0.1:8088/v1`.
- Phase 5K one-shot diagnostic: one bounded `hermes -z "Reply with exactly: Hermes adapter diagnostic."` run completed in 45.539s with exit code 0, stdout 8 bytes containing `(empty)`, and stderr 0 bytes. Adapter request metadata confirmed Hermes called `GET /v1/models` twice and `POST /v1/chat/completions` four times; all chat calls returned 200 with selected model `gemma4:26b`. Hermes also probed unsupported discovery endpoints that returned 404. The adapter was stopped immediately after validation and no `8088` listener remained.
- Phase 5L response-contract diagnosis: local Hermes source inspection showed non-streaming parsing expects `choices[0].message.content`, `finish_reason`, optional tool calls, reasoning fields, and usage, which the adapter already provided. Hermes' default chat-completions path sends `stream=true` and expects SSE chunks with `choices[0].delta.content`; Phase 5L identified missing streaming support as the likely blocker and added `MODEL_ROUTER_ADAPTER_LOG_RESPONSE_SHAPES=true` for metadata-only response-shape diagnostics.
- Phase 5M streaming adapter support: `POST /v1/chat/completions` now returns OpenAI-compatible `text/event-stream` when `stream=true`, emitting one content delta chunk, one finish chunk, and `data: [DONE]` after the router completes. Requests with `stream=false` or no stream field keep the existing non-streaming JSON behavior. No live Hermes prompt was run in Phase 5M.
- Phase 5N one-shot diagnostic after SSE fix: one bounded `hermes -z "Reply with exactly: Hermes adapter diagnostic."` run completed in 18.712s with exit code 0, stdout 27 bytes containing `Hermes adapter diagnostic.`, and stderr 0 bytes. Adapter metadata confirmed one `POST /v1/chat/completions` request returned 200 with selected model `gemma4:26b`; response-shape metadata showed `streaming_requested=true`, one choice, content length 26, and finish reason `stop`. The adapter was stopped immediately and no `8088` listener remained.
- Phase 5O sandbox summaries after SSE fix: `sample_note.md` exited 0 in 36.241s with stdout 8 bytes `(empty)` and stderr 0 bytes; `sample_prd.md` exited 0 in 17.647s with stdout 8 bytes `(empty)` and stderr 0 bytes. Adapter metadata showed 8 successful chat-completion calls with selected model `gemma4:26b`, but all response-shape records had `content_length=0`. The output files are not usable summaries.
- Phase 5P file-summary prompt diagnosis: no live prompts were run. The adapter/router path was inspected and confirmed to concatenate all OpenAI-style messages in order before delegating to `services/model_router`; it does not choose only the first or last message. Hermes `-z` still uses the normal `AIAgent` chat path and may send tools, tool-choice hints, multi-message context, and repeated turns. Added `MODEL_ROUTER_ADAPTER_LOG_MESSAGE_STRUCTURE=true` for metadata-only diagnostics that log message counts, roles, character counts, final-user-message emptiness, file-content heuristic status, and tool/option presence without logging prompt text, file contents, model output, or secrets.
- Phase 5Q bounded metadata diagnostic: one `sample_note.md` file-summary diagnostic completed in 33.501s with exit code 0, stdout 8 bytes, and stderr 0 bytes. The output remained unusable. Adapter metadata showed four successful chat-completion calls, all `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`. Message-structure metadata was identical across calls: two messages, roles `system` and `user`, character counts `[5630, 71]`, final user message not empty, file-like content present by length/shape, `tools` present, `tool_choice` absent, `stream` present, and no `max_tokens` or `temperature`.
- Phase 5R tool-payload compatibility: no live Hermes prompts or live model calls were run. Local Hermes source inspection confirmed `hermes -z` includes tools because it constructs a normal `AIAgent`, uses configured CLI toolsets when no explicit toolsets are passed, and forwards `agent.tools` into chat-completion kwargs. Mocked adapter tests showed `tools` present and `tools` stripped produce the same router prompt because the adapter already excludes tool schemas; the safer local Gemma fix must also flatten Hermes multi-message payloads into a single Gemma-friendly prompt.
- Phase 5S local Gemma compatibility: added `MODEL_ROUTER_ADAPTER_LOCAL_COMPAT_MODE=true`. When enabled for local Gemma requests, the adapter ignores `tools` and `tool_choice`, flattens message content into role-labeled `[system]`, `[developer]`, `[user]`, `[assistant]`, and `[tool]` blocks, extracts only safe text from structured content parts, fails closed when no non-empty user content exists, preserves SSE behavior, and emits metadata-only flattening diagnostics without logging prompt text or file contents.
- Phase 5T live compat-mode retry: one bounded `sample_note.md` Hermes file-summary test completed in 52.126s with exit code 0, stdout 8 bytes, and stderr 0 bytes. The output remained unusable. Adapter metadata showed four successful chat-completion calls, all `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`. Compat metadata confirmed `compat_mode_enabled=true`, `flattened_message_count=2`, `flattened_prompt_chars=5724`, `tool_schemas_present=true`, and `tool_schemas_forwarded=false`.
- Phase 5U Gemma prompt construction diagnosis: no live Hermes prompts or live model calls were run. Added metadata-only diagnostics for flattened prompt character count, role sections, section order, markdown fence count, XML/tool-like tag count, JSON-looking block count, tool/function/schema/call keyword counts, final user content start index, and user/system character counts. Added `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE` with `flattened`, `user_only`, `final_user`, `instruction_context`, and `no_tool_vocab`; default behavior remains `flattened`.
- Phase 5V instruction-context retry: one bounded `sample_note.md` Hermes file-summary test completed in 58.639s with exit code 0, stdout 8 bytes, and stderr 0 bytes. The output remained unusable. Adapter metadata showed four successful chat-completion calls, all `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`. Prompt metadata confirmed `gemma_prompt_mode=instruction_context`, `compat_mode_enabled=true`, `prompt_total_chars=5729`, `message_count=2`, `tool_schemas_present=true`, `tool_schemas_forwarded=false`, and final user content starting at index 7.
- Phase 5W no-tool-vocabulary retry: one bounded `sample_note.md` Hermes file-summary test completed in 39.471s with exit code 0, stdout 8 bytes, and stderr 0 bytes. The output remained unusable. Adapter metadata showed four successful chat-completion calls, all `streaming_requested=true`, `choices_count=1`, `finish_reason=stop`, and `content_length=0`. Prompt metadata confirmed `gemma_prompt_mode=no_tool_vocab`, `compat_mode_enabled=true`, `prompt_total_chars=5689`, `message_count=2`, `tool_schemas_present=true`, `tool_schemas_forwarded=false`, final user content starting at index 5606, and tool/function/schema/call keyword counts all zero.
- Phase 5X local summary prompt mode: no live Hermes prompts or live model calls were run. Added `MODEL_ROUTER_ADAPTER_GEMMA_PROMPT_MODE=local_summary`, which extracts the latest user instruction plus file-like context, uses file-like system/developer context only when needed, omits tool schemas and tool-choice semantics, avoids role-labeled full transcripts, drops unrelated Hermes scaffold, and fails closed when no useful instruction/context pair is found. Added metadata-only logs for instruction/context character counts, dropped system characters, dropped tool schema count, and extraction success.
- Phase 5Y local summary live validation: one bounded `sample_note.md` Hermes file-summary test completed in 101.268s with exit code 0, stdout 110 bytes, and stderr 0 bytes. The output was not a usable summary; it contained a provider timeout diagnostic. Adapter metadata showed three `POST /v1/chat/completions` attempts, all `502` after about 30s, selected model `gemma4:26b`. Prompt metadata confirmed `gemma_prompt_mode=local_summary`, extraction success, `prompt_total_chars=3139`, `instruction_chars=83`, `context_chars=2899`, `dropped_system_chars=5628`, `dropped_tool_schema_count=26`, and `tool_schemas_forwarded=false`.
- Phase 5Z timeout/context tuning: no live Hermes prompts or live model calls were run. Added `MODEL_ROUTER_PROVIDER_TIMEOUT_SECONDS` as the primary local provider timeout setting with `GEMMA_TIMEOUT` preserved as a legacy fallback. Added `MODEL_ROUTER_ADAPTER_LOCAL_SUMMARY_MAX_CONTEXT_CHARS` with default 3000. `local_summary` now preserves the beginning and end of context when truncation is needed and logs metadata-only fields for original context chars, sent context chars, truncation status, and timeout seconds.
- Phase 5AA tuned local summary validation: one bounded `sample_note.md` Hermes file-summary test completed in 112.635s with exit code 0, stdout 285 bytes, and stderr 0 bytes. Output was usable. Adapter metadata showed one `POST /v1/chat/completions` call, status 200, selected model `gemma4:26b`, response content length 284, context truncated from 2899 to 1499 chars, and timeout used 120s.
- Phase DESKTOP-1 planning: added the official Nous Research Hermes Desktop roadmaps for Mac mini and DevMonster. Phase 5AA satisfied the initial useful-output gate for `sample_note.md`, but Desktop still requires a later explicit install/open approval. Desktop must be planned before resident/background operation and before durable credentials are granted. Safety gates require official download source, macOS identity verification if possible, no Nous Portal login, no cloud credentials, no broad filesystem grants, no background operation, no Google/Supabase/Home Assistant/GitHub/Helio/Agent Bus connection, localhost adapter use if configurable, ANO governance preservation, and no DevMonster Ollama/Gemma/Tailscale/model-worker changes.
- Phase DESKTOP-2 install-command proposal: documented the future Mac mini Desktop sequence using official source `https://hermes-agent.nousresearch.com/desktop` and macOS DMG target `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg`. The proposal includes checksum capture, quarantine/image inspection, Gatekeeper assessment, app bundle code-signing assessment, copy to `/Applications`, first-launch baseline checks, post-launch launchd/login/background checks, `~/.hermes` write inspection, and rollback removal commands. No Desktop download, install, launch, runtime config change, credential setup, or external service connection was performed.
- Phase DESKTOP-3 controlled install: downloaded the official macOS DMG, verified SHA-256 `be2bb2fa9b405f62ea8d5f11327c6384f979e0589ecf4caea45ebcb909c662d4`, confirmed `hdiutil verify` passed, and installed the app at `/Applications/Hermes.app` from Terminal because the Codex sandbox could not mount the DMG. Installed bundle metadata: name `Hermes`, identifier `com.nousresearch.hermes.setup`, version `0.0.1`, arm64 executable `Hermes-Setup`, Team ID `T2F6S8MF7C`, hardened runtime present, stapled notarization ticket present. Desktop was not launched or configured. No Hermes/Nous user LaunchAgent, Application Support, Preferences, or launchctl entry was found, and no `~/.hermes` files were modified during verification. Process-list and login-item checks were partly blocked by macOS sandbox permissions.
- Phase DESKTOP-4 first-launch validation: one guarded `open -a /Applications/Hermes.app` attempt was made. No observable first-run UI or screen capture was available from the Codex sandbox. A transient LaunchServices job ran `/Applications/Hermes.app/Contents/MacOS/Hermes-Setup` and wrote `~/.hermes/logs/bootstrap-installer.log` with `Hermes installer starting mode=Install force_setup=false`. A later open attempt returned `kLSNoExecutableErr`, while `codesign --verify --deep --strict` reported an invalid arm64 signature. The process could not be stopped from inside the sandbox, so the user killed it from Terminal. Afterward no Hermes app running state, launchctl entry, LaunchAgent, background-task match, Application Support artifact, or Preferences artifact remained. No Nous Portal sign-in, browser login, credentials, permission grants, external integrations, adapter start, background/resident operation, or CLI config changes occurred.
- Phase DESKTOP-5 bootstrap/openability diagnostic: no launch was attempted. `/Applications/Hermes.app` was confirmed as a minimal `com.nousresearch.hermes.setup` bundle with executable `Hermes-Setup`, version `0.0.1`, 12M size, and only `Info.plist`, executable, icon, and code-signing resources. `codesign --display` showed Team ID `T2F6S8MF7C`, hardened runtime, and stapled notarization ticket, but `codesign --verify --strict` failed for both the app and executable with `invalid signature`. `spctl` returned internal Code Signing subsystem errors. Extended attributes showed provenance/MACL but no quarantine. The bootstrap log remained the only Desktop-created artifact. No process, launchctl entry, LaunchAgent, background task, Application Support file, Preferences file, or new `~/.hermes` modification was found.
- Phase DESKTOP-6 DMG comparison: found two candidate official DMGs under `/private/tmp`, both 6.4M with SHA-256 `be2bb2fa9b405f62ea8d5f11327c6384f979e0589ecf4caea45ebcb909c662d4`, and both passed `hdiutil verify`. No Hermes DMG was already mounted. `hdiutil attach -readonly` failed inside Codex with `Device not configured`, including after additional file permissions were granted, and archive extraction was not possible. The mounted bundle could not be compared. Installed app metadata and hashes were recorded; `/Applications/Hermes.app` still has no quarantine marker, still fails signature verification, and no process, LaunchAgent, background-task, Application Support, or Preferences artifact was present.
- Phase DESKTOP-7A bundle-state clarification: reran approved local Mac mini diagnostics without launching Desktop, redownloading, reinstalling, removing quarantine, adding credentials, granting permissions, changing Hermes CLI config, or connecting external services. `/Applications/Hermes.app` remains a minimal `com.nousresearch.hermes.setup` bundle with executable `Hermes-Setup`, version `0.0.1`, Team ID `T2F6S8MF7C`, hardened runtime, stapled notarization ticket, invalid strict arm64 code signature, `spctl` Code Signing subsystem error, provenance/MACL xattrs, and no observed quarantine xattr. No Hermes launch agent or daemon file was found, but login/background-item inspection remained blocked by macOS authorization. A pre-existing `Hermes-Setup` process was observed as PID `18152`, parent PID `1`, started `Sat Jun 6 13:49:34 2026`; the process was not killed because DESKTOP-7A did not approve state changes. Hermes CLI config/reference hashes remained unchanged from the recorded June 4 state.
- Phase DESKTOP-8 official artifact reacquisition plan: documented that the original installer artifact is missing from normal user download locations and that `/Applications/Hermes.app` is not trusted as a final Desktop runtime. Reconfirmed the official source page `https://hermes-agent.nousresearch.com/desktop`, observed macOS 12+, Hermes Agent v0.16.0, and a macOS download link under `hermes-assets.nousresearch.com`; no artifact was downloaded. Planned safe future download to `~/Downloads/hermes-desktop-official/`, expected artifact types (`dmg`, `zip`, `pkg`, `.app`), verification steps, comparison steps against `/Applications/Hermes.app`, rollback-before-replacement backup steps, replacement steps requiring separate approval, and first-launch guardrails. Hermes CLI config and the localhost model adapter path remained untouched.
- Phase DESKTOP-9 official artifact verification: downloaded `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05` to `/Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg`, size `6752854` bytes, SHA-256 `b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5`. `hdiutil verify` passed and the DMG mounted read-only. The mounted bundle `/private/tmp/hermes-desktop-official-mount/Hermes.app` matched the installed app's bundle identifier, name, version, executable name, bundle size, and minimal setup-bundle structure, but the mounted executable hash differed from the installed executable hash. The mounted app still failed `codesign --verify --deep --strict` with `invalid signature (code or signature have been modified)` for arm64, and `spctl` returned an internal Code Signing subsystem error. The DMG was unmounted after verification. Hermes CLI hashes remained unchanged.
- Phase DESKTOP-10 artifact integrity escalation: added `docs/HERMES_DESKTOP_ARTIFACT_ESCALATION.md` with the official artifact URL, SHA-256, file size, app identifier, version, executable, `hdiutil`, `codesign`, and `spctl` results, comparison to `/Applications/Hermes.app`, fail-closed rationale, release-channel questions, and a draft support/escalation message. The message was not sent. No Desktop launch, replacement, deletion, quarantine removal, reinstall, recopy, permission grant, sign-in, process kill, Hermes CLI config change, external connection, or background-service change was performed.

Not completed or not approved:

- Hermes is installed as a local client only.
- Hermes Desktop is installed but not launched or configured.
- Autonomous execution is not enabled.
- Hermes setup was not run.
- Hermes model configuration was not enabled.
- Hermes did not produce local summaries in Phase 5E because no credential-free inference provider was configured.
- Hermes is not persistently configured to use the MSR Model Router adapter yet.
- The Model Router adapter was not started as a background service.
- Hermes sandbox retry through the adapter did not produce usable summaries.
- Hermes background gateway/launchd operation is not enabled.
- Google Workspace is not connected.
- Home Assistant is not installed or connected.
- Supabase writes are not enabled.
- Agent dispatch is not enabled.
- Service-role access is not approved for Hermes.
- Further live Agent Bus reads are blocked until high-risk exposed credentials are rotated and a new phase is approved.
- Further live Agent Bus writes are blocked until exposed credential rotation is confirmed or explicitly deferred.

## Phase 6A Finding

No single canonical Supabase Agent Bus PRD exists for the full Hermes need. The implemented system spans the `agent_messages` queue, `agent_tasks` accountability layer, outbound bot bus, org-scoped config, approvals, and audit logs across multiple PRDs, migrations, runtime services, and exported architecture docs.

The current Phase 6A references are:

- [Supabase Agent Bus Source Map](../SUPABASE_AGENT_BUS_SOURCE_MAP.md)
- [Hermes + Helio Agent Bus Plan](../HERMES_HELIO_AGENT_BUS_PLAN.md)

## Phase 6B Finding

`packages/ano-messaging` is the primary canonical source candidate for the portable Agent Bus message layer. It defines `agent_messages`, `bot_outbound_messages`, `org_messaging_config`, message service methods, outbound polling, directive scanning, and baseline computation.

It does not define the full task bus. `agent_tasks`, task events, approvals, and immutable audit still need Helio-owned normalization before Hermes may dispatch agent work.

Phase 6B reference:

- [Canonical Agent Bus Contract](../AGENT_BUS_CONTRACT.md)

## Next Recommended Work

Phase 5AB should run one bounded `sample_prd.md` retry with the validated tuned local-summary settings. Hermes Desktop must remain fail-closed until a later phase resolves the Desktop bootstrap/signature/openability issue and explicitly approves another launch/configuration attempt. Recommended Desktop follow-up is Phase DESKTOP-7: unsandboxed Terminal/Finder DMG mount and bundle-integrity comparison before any launch or recopy. Do not start background services, expose the adapter externally, use cloud providers, or send sensitive prompts without a new explicit phase approval. Also confirm or explicitly defer exposed credential rotation before any additional live Agent Bus reads or writes.

Security reference:

- [Credential Rotation Checklist](../security/CREDENTIAL_ROTATION_CHECKLIST.md)

Inference reference:

- [Hermes Model Provider Plan](../HERMES_MODEL_PROVIDER_PLAN.md)

After rotation confirmation or explicit deferral, run local tests and `verify-config` only. Do not run `list-org-configs`, `read-hermes-messages`, `read-outbound-audit`, or any write-oriented bus operation until the exposed high-risk credentials are revoked, rotated, or explicitly deferred by the user and a new phase is explicitly approved.

Phase 5E showed that a credential-free Hermes client can start locally but cannot complete agent summarization without a configured inference provider. The sandbox run did not connect Google Workspace, Supabase, Home Assistant, Helio, or the agent bus. The non-zero exit is expected and acceptable for this phase. Hermes did perform plugin discovery in the isolated runtime and logged provider registration plus a lazy dependency attempt for a Bedrock provider; this is a security review item before resident operation.

Phase 5F determined that Hermes can treat the MSR Model Router as its sole inference provider if the router exposes a local OpenAI-compatible endpoint and Hermes is later configured with `model.provider=custom` and a loopback-only `model.base_url`. No Hermes config changes were made in Phase 5F. No live prompts, cloud provider config, external exposure, or background service setup was performed.

Phase 5H retry confirmed the adapter can run manually on localhost, reject unknown endpoints, list DevMonster models, and complete the single approved non-sensitive prompt through `devmonster_ollama` and `gemma4:26b`. The adapter was stopped after validation and no listener remained on port `8088`.

Phase 5I confirmed Hermes can be pointed at the local adapter in an isolated home using `model.provider=custom`, `model.default=gemma4:26b`, `model.base_url=http://127.0.0.1:8088/v1`, and a dummy local API key. Hermes used no real cloud credentials and no Google, Supabase, Home Assistant, GitHub, or Helio credentials. The outputs are not usable yet because Hermes wrote only `(empty)`.

Phase 5J confirmed the next diagnostic should use top-level `hermes -z` / `--oneshot` for stdout capture, because it is documented as the scriptable one-shot path. Adapter request logging should be enabled for that diagnostic so the team can confirm whether Hermes calls `/v1/chat/completions`, which model is selected, and what status the adapter returns without logging prompt text.

Phase 5K proved `hermes -z` reaches the localhost adapter and receives 200 responses from `/v1/chat/completions`, but it still prints `(empty)`. The remaining investigation should focus on Hermes' custom-provider wire contract, streaming expectations, response parsing, and model capability discovery probes before expanding the adapter or rerunning prompts.

Phase 5L determined the adapter's non-streaming response shape matches Hermes' non-streaming parser, but Hermes prefers streaming by default. The recommended adapter fix is to support OpenAI-compatible SSE chunks for `stream=true` within the already-approved chat-completions endpoint, while leaving unsupported discovery endpoints out of scope until separately approved.

Phase 5M implemented that SSE fix in the adapter using mocked tests only. The endpoint surface remains limited to `GET /health`, `GET /v1/models`, and `POST /v1/chat/completions`.

Phase 5N confirmed the SSE fix works for the bounded one-shot path: Hermes now returns usable stdout through the localhost adapter. Unsupported Hermes discovery probes still return 404 and should remain separate from the sandbox file-summary validation decision.

Phase 5O showed sandbox file-summary attempts still fail to produce visible content even though the adapter SSE path is used successfully. This points to Hermes one-shot file-summary workflow behavior or model/tool prompting rather than adapter transport.

Phase 5P added metadata-only message-structure logging to distinguish whether Hermes sends actual sandbox file contents, a blank final user message, or a tool-oriented multi-turn transcript during file-summary attempts. The adapter still does not execute Hermes file tools; if no file content reaches the model, the next fix should be an explicit content-injection summary pattern or an approved local-only Hermes file-read invocation pattern.

Phase 5Q confirmed file-like context reaches the adapter by length/shape and the final user message is not empty. The remaining blocker is likely prompt/tool shape rather than transport or missing file content alone: Hermes sends `tools`, while the constrained adapter forwards text to DevMonster but does not execute Hermes tools or complete a tool loop.

Phase 5R showed the adapter already omits tool schemas from the router prompt, so stripping tools alone will not change DevMonster input. The recommended fix is an explicit local Gemma compatibility prompt that flattens Hermes multi-message payloads into a simpler single-task prompt while preserving future room for tool-capable providers.

Phase 5S implemented that compatibility prompt behind an explicit flag. It was verified with mocked tests only; no Hermes live prompt or live model call was run.

Phase 5T confirmed the compatibility flag activates during a live Hermes sample-note run and that tool schemas are not forwarded, but Gemma still returns zero content. The remaining blocker is likely the Gemma-facing prompt content/order or Hermes system scaffold, not tool-schema forwarding.

Phase 5U added prompt-construction diagnostics and tested prompt construction modes offline. The recommended next live mode is `instruction_context`, because it preserves the available file-like context while moving the final user instruction ahead of Hermes' large system scaffold.

Phase 5V confirmed `instruction_context` changes prompt ordering as intended, but Gemma still returns zero content. The remaining blocker is likely remaining Hermes tool/call vocabulary or agent scaffold text inside message content.

Phase 5W confirmed `no_tool_vocab` removes plain tool/function/schema/call vocabulary as intended, but Gemma still returns zero content. The remaining blocker is likely the large Hermes scaffold itself and the lack of a compact local summary prompt.

Phase 5X implemented that compact local summary prompt mode with mocked tests only. The next validation should be a single bounded `sample_note.md` live retry.

Phase 5Y confirmed local summary extraction works and changes the failure mode from zero-content 200s to 30-second provider timeouts. The next blocker is router/provider timeout or context budgeting.

Phase 5Z added the timeout and context-budget controls needed for the next bounded live retry.

Phase 5AA confirmed the tuned settings produce usable Hermes summary output for `sample_note.md`.

Phase DESKTOP-1 added Hermes Desktop to the roadmap as a future official Nous Research install only for both Mac mini and DevMonster. Desktop remains a UI surface under Helio/ANO governance, is gated before resident/background operation or durable credentials, and must not alter DevMonster Ollama/Gemma/Tailscale/model-worker configuration.

Phase DESKTOP-2 documented the Mac mini Desktop install command proposal only. The future install must use the official DMG, inspect quarantine/signature/notarization state, validate first-launch behavior, avoid portal/cloud/integration setup, preserve existing CLI config, and keep rollback limited to Desktop artifacts unless separately approved.

Phase DESKTOP-3 installed Hermes Desktop from the official DMG at `/Applications/Hermes.app` without launching it. First launch, provider setup, portal login, permission grants, external integrations, background/resident operation, and CLI config changes remain unapproved.

Phase DESKTOP-4 attempted one guarded first launch and failed closed before usable UI validation. The app behaved like a bootstrap installer bundle, wrote only a bootstrap log under `~/.hermes/logs`, and exposed a signature/openability issue that should be resolved before another Desktop launch attempt.

Phase DESKTOP-5 confirmed the Desktop blocker is not quarantine and not a persistent background-service issue. The installed bundle appears to be a minimal bootstrap installer app with an invalid current signature/openability state. The next Desktop phase should compare the mounted DMG bundle to the installed bundle and verify signature before/after copy without launching.

Phase DESKTOP-6 confirmed the downloaded DMGs are valid and identical, but Codex cannot mount the APFS DMG for mounted-bundle comparison. Phase DESKTOP-7A reconfirmed the installed bundle is not healthy enough for launch retry and found a pre-existing `Hermes-Setup` process. Phase DESKTOP-8 planned safe official artifact reacquisition and later replacement guardrails only. Phase DESKTOP-9 verified the reacquired official DMG and mounted app, but the mounted app still fails strict code-signature verification and Gatekeeper assessment. Phase DESKTOP-10 documented the escalation package and draft support message. The next Desktop phase should wait for official clarification or explicitly approve a bounded support-contact phase. Do not install, replace, launch, remove quarantine, sign in, grant permissions, connect integrations, kill `Hermes-Setup`, modify Hermes CLI config, or send the escalation message until a later explicit phase approves it.

Phase 6I remains the next architecture investigation after rotation: determine whether empty Agent Bus metadata results mean the `msr` Agent Bus config has not been seeded, the anon key is constrained to empty scoped visibility, or Helio should expose an explicit read-only gateway/view.

Phase 6H validated the approved read-only path using `SUPABASE_URL` and `SUPABASE_ANON_KEY` only. The service-role key was not used. No messages were sent, no polling workers were created, and no writes were enabled.

Phase 6H read only:

- `org_messaging_config`
- `agent_messages` addressed to `hermes`
- `bot_outbound_messages` for audit inspection only

Live validation result:

| Check | Org | Workspace | Agent | Row count | Statuses | Latest timestamp |
| --- | --- | --- | --- | --- | --- | --- |
| `verify-config` | `msr` | `default` | `hermes` | n/a | `ok` | n/a |
| `org_messaging_config` | `msr` | `default` | n/a | 0 | none | none |
| `agent_messages` addressed to Hermes | `msr` | `default` | `hermes` | 0 | none | none |
| `bot_outbound_messages` audit | `msr` | `default` | n/a | 0 | none | none |

Phase 6I should determine whether zero rows means the `msr` Agent Bus config has not been seeded, the anon key is constrained to empty scoped visibility, or Helio should expose an explicit read-only gateway/view. The follow-up must not use direct Hermes service-role access.

Phase 6G reference:

- [Read-only preflight script](../../scripts/agent_bus_readonly_preflight.py)
- [Read-only preflight mocked tests](../../tests/agent_bus/test_readonly_preflight.py)

Phase 6E reference:

- [Hermes Helio Adapter Design](../HERMES_HELIO_ADAPTER_DESIGN.md)

## Non-Goals

- Do not run Hermes setup.
- Do not start Hermes as a background or resident service.
- Do not enable Hermes autonomous execution.
- Do not connect Supabase.
- Do not store real secrets.
- Do not send messages to agents.
- Do not connect the scaffold to live services until a later approval is explicit.
- Do not use `SUPABASE_SERVICE_ROLE_KEY` in the Hermes adapter.
- Do not run further live reads until exposed high-risk credentials are rotated.
