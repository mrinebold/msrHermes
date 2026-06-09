# Hermes Persistent Local Config Plan

Phase: 5AN
Status: persistent local config live-local validated

## Purpose

Define and record the persistent local Hermes configuration needed for a future resident-readiness path.

Phase 5AM applied only the approved local adapter config to `~/.hermes/config.yaml`. Phase 5AN then validated that config with one harmless live local prompt through the foreground localhost adapter. No background services, Desktop launch, real credentials, integrations, credential file modifications, Agent Bus operations, or broader Hermes authority were used.

## Proposed Persistent Scope

The future persistent config should give Hermes one local model path only:

- provider: `custom`
- model: `gemma4:26b`
- base URL: `http://127.0.0.1:8088/v1`
- API key: `dummy-local-adapter-key` only if Hermes requires an API-key-shaped value syntactically
- platform tools: disabled unless a separate phase explicitly approves a specific toolset
- Desktop dependency: none

No real provider or integration credentials are allowed:

- no real OpenAI key
- no real Anthropic key
- no real OpenRouter key
- no Google credentials
- no Supabase credentials
- no GitHub token
- no Home Assistant token
- no Helio gateway or dispatcher token

## Proposed Config Content

Persistent Hermes `config.yaml` target:

```yaml
model:
  provider: custom
  default: gemma4:26b
  base_url: http://127.0.0.1:8088/v1
  api_key: dummy-local-adapter-key
platform_toolsets:
  cli: []
```

If Hermes supports a local model alias later, a future phase may replace `gemma4:26b` with a local alias only after verifying that the alias still resolves through the localhost adapter and not a cloud provider.

## Future Files And Paths

Phase 5AM created or modified only these paths:

| Path | Action | Notes |
| --- | --- | --- |
| `~/.hermes/config.yaml` | Modified | Primary persistent Hermes config. Mode set to owner read/write. |
| `~/.hermes/backups/phase5am-20260608T232816/config.yaml.bak` | Created | Timestamped backup of pre-Phase 5AM config. |

Phase 5AM did not modify:

- `~/.hermes/.env`
- `~/.local/bin/hermes-local`
- launchd plists
- Desktop app files
- Google, Supabase, GitHub, Home Assistant, or Helio credential files

Do not modify:

- `config/hermes-pilot.example.env`
- repository-tracked config files except documentation in an approved phase
- launchd plists
- Desktop app files
- Google, Supabase, GitHub, Home Assistant, or Helio credential files

## Phase 5AM Inspection Result

Metadata-only inspection found:

- `~/.hermes/config.yaml` existed before modification.
- `~/.hermes/.env` existed and was not modified.
- Candidate config files included `~/.hermes/config.yaml` and `~/.hermes/.env`.
- Secret-like names appeared by name only in inspected files; no values were printed.
- `~/.hermes/config.yaml` name matches included `ANTHROPIC_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `api_key`, `credential`, `password`, `secret`, and `token`.
- `~/.hermes/.env` name matches included `OPENROUTER_API_KEY`, `credential`, `password`, `secret`, and `token`.

Because `.env` had secret-like names, Phase 5AM did not read, print, copy into the repo, edit, or replace `.env`.

## Backup Plan Used

Before modifying `~/.hermes/config.yaml`, Phase 5AM:

1. Listed current `~/.hermes` state without printing file contents.
2. Identified `~/.hermes/config.yaml` as the only file to modify.
3. Created `~/.hermes/backups/phase5am-20260608T232816/config.yaml.bak`.
4. Set backup directory permissions to owner-only.
5. Avoided printing secrets, tokens, OAuth material, config contents, or environment dumps.
6. Left `~/.hermes/.env` untouched.

Backup metadata:

```text
backup_file=/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak
backup_size=60646
```

## Phase 5AM Validation Result

Phase 5AM validated:

- config syntax is valid YAML
- `model.provider` is `custom`
- `model.default` is `gemma4:26b`
- `model.base_url` is exactly `http://127.0.0.1:8088/v1`
- `model.api_key` is `dummy-local-adapter-key`
- `platform_toolsets.cli` is disabled with `[]`
- modified config mode is owner read/write only
- no real-looking secret markers were detected in the modified config
- no adapter or Hermes live run was started
- no cloud provider, Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus integration was contacted
- no background or resident process was started
- Hermes Desktop was not launched
- no credentials were added, modified, printed, or stored
- no files outside `~/.hermes/config.yaml` and the timestamped backup were modified
- no `8088` listener remained after validation

Config metadata after application:

```text
config_file=/Users/michaelrinebold/.hermes/config.yaml
config_mode=-rw-------
config_size=4670
```

## Phase 5AN Live Local Validation Result

Phase 5AN started `scripts/run_model_router_adapter.sh` manually in the foreground and ran exactly one Hermes prompt through the persistent config:

```text
Reply with exactly: Persistent local Hermes config works.
```

Captured files:

- `sandbox/output/hermes_persistent_config_phase5an.stdout`
- `sandbox/output/hermes_persistent_config_phase5an.stderr`
- `sandbox/output/hermes_persistent_config_phase5an.metrics`

Run result:

| Field | Value |
| --- | --- |
| Exit code | `0` |
| Elapsed time | `74` seconds |
| Stdout bytes | `38` |
| Stderr bytes | `0` |
| Stdout text | `Persistent local Hermes config works.` |

Adapter evidence:

- runner bound only to `127.0.0.1:8088`
- DevMonster endpoint was `http://100.93.120.124:11434`
- default model was `gemma4:26b`
- provider timeout was `120` seconds
- prompt/file/model-output/secret logging remained disabled
- `GET /v1/models` returned `200`
- `POST /v1/chat/completions` returned `200`
- selected model was `gemma4:26b`
- response content length was `37`
- chat completion elapsed time was `72.634` seconds

Post-run validation:

- adapter was stopped immediately after the run
- no `8088` listener remained
- no Hermes, adapter, or Desktop process remained
- no Hermes launchd, LaunchAgent, or LaunchDaemon match was found
- no Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud-provider integration was touched
- no real API keys were inherited by the Hermes child process
- `~/.hermes/.env` remained unmodified with modified time `Jun 4 11:35:14 2026`
- `~/.hermes/config.yaml` still validated with localhost base URL, `gemma4:26b`, dummy local key, and disabled CLI platform toolset

## Rollback

Rollback steps:

1. Stop the adapter if it was manually running in the foreground.
2. Confirm no Hermes process remains.
3. Restore `/Users/michaelrinebold/.hermes/backups/phase5am-20260608T232816/config.yaml.bak` to `/Users/michaelrinebold/.hermes/config.yaml`.
4. Confirm config file permissions are owner-only or match the restored backup policy.
5. Remove no optional wrapper file; none was created in Phase 5AM.
6. Confirm no `8088` listener remains.
7. Confirm no Desktop launch occurred.
8. Confirm no Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud-provider credentials were added.
9. Record rollback evidence in the PRD and changelog.

## Non-Goals

Phase 5AM does not approve:

- launchd
- background service
- resident mode
- Google Workspace
- Supabase
- Home Assistant
- GitHub
- Helio gateway or dispatcher use
- Agent Bus reads or writes
- Desktop launch
- credential rotation action
- external service connection
- real OpenAI, Anthropic, OpenRouter, Supabase, Google, GitHub, Home Assistant, or Helio credentials
- broad filesystem authority
- Hermes shell or file-edit authority expansion

## Approval Required Before Applying

Any future change beyond the applied local adapter config requires explicit human approval for:

- exact file paths
- exact config content or patch beyond the Phase 5AM local adapter config
- backup paths
- whether the adapter may be started manually
- whether one harmless Hermes prompt may be run
- validation evidence to capture
- rollback trigger and rollback command sequence

The applied persistent config is limited to local adapter inference only.
