# PRD: MSR Hermes Operating System

## Status

Phase 5K complete. A bounded Hermes one-shot diagnostic proved `hermes -z` calls the localhost Model Router adapter, but Hermes still returned unusable stdout containing only `(empty)`.

Local repository status: complete work through Phase 5H retry has been published. Phase 5I through Phase 5K are local until the next approved push.

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

Not completed or not approved:

- Hermes is installed as a local client only.
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

Phase 5L should inspect Hermes custom-provider response parsing and model capability discovery locally before another live prompt. Do not start background services, expose the adapter externally, use cloud providers, or send sensitive prompts without a new explicit phase approval. Also confirm or explicitly defer exposed credential rotation before any additional live Agent Bus reads or writes.

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
