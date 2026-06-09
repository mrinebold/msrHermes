# Hermes Persistent Local Config Plan

Phase: 5AL
Status: proposal only

## Purpose

Define the exact persistent local Hermes configuration plan needed for a future resident-readiness path without applying it.

Phase 5AL does not modify `~/.hermes`, run Hermes, start the adapter, create background services, launch Desktop, use credentials, connect integrations, or broaden Hermes authority.

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

Future persistent Hermes `config.yaml` candidate:

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

Future application phase may create or modify only these paths after explicit approval:

| Path | Future action | Notes |
| --- | --- | --- |
| `~/.hermes/config.yaml` | Create or update | Primary persistent Hermes config candidate. Must be backed up first if present. |
| `~/.hermes/config.yaml.<timestamp>.bak` | Create | Timestamped backup of existing config before modification. |
| `~/.hermes/.env` | Prefer no change | Should not be created unless a later phase proves Hermes requires it. Must not contain real cloud/integration credentials. |
| `~/.hermes/.env.<timestamp>.bak` | Create only if `.env` would be modified | Backup before any approved modification. |
| `~/.local/bin/hermes-local` | Optional wrapper proposal only | Future wrapper could set isolated local env, but should not be created in this phase. |
| `~/.local/bin/hermes-local.<timestamp>.bak` | Create only if wrapper already exists and would be modified | Backup before any approved modification. |

Do not modify:

- `config/hermes-pilot.example.env`
- repository-tracked config files except documentation in an approved phase
- launchd plists
- Desktop app files
- Google, Supabase, GitHub, Home Assistant, or Helio credential files

## Backup Plan Before Future Application

Before any future persistent config application:

1. List current `~/.hermes` state without printing file contents.
2. Identify each file that would be created or modified.
3. Create timestamped backups for existing files before modification.
4. Use owner-only permissions for backup and config files.
5. Never print secrets, tokens, OAuth material, config contents that may contain credentials, or environment dumps.
6. Abort if unexpected credential material is detected in a file that would be copied, edited, or logged.

Example backup naming convention:

```text
~/.hermes/config.yaml.20260608T230000.bak
```

## Future Application Validation

After a separately approved future application, validate:

- config file exists at the approved path only
- config syntax is valid YAML if a parser is available
- `model.provider` is `custom`
- `model.default` is `gemma4:26b` or an approved local alias
- `model.base_url` is exactly `http://127.0.0.1:8088/v1`
- `model.api_key` is dummy/local-only, not a real cloud or integration key
- `platform_toolsets.cli` remains disabled
- Hermes can run one harmless prompt only after explicit approval
- only the localhost adapter is called
- no cloud provider, Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus integration is contacted
- DevMonster is reached only through the localhost adapter path
- no background or resident process is started
- Hermes Desktop is not launched
- no credentials are added, modified, printed, or stored
- no files outside approved paths are modified
- no `8088` listener remains unless the adapter is intentionally still running in the foreground for that approved validation

## Future Rollback

Rollback steps for a future application phase:

1. Stop the adapter if it was manually running in the foreground.
2. Confirm no Hermes process remains.
3. Restore timestamped backups for modified files.
4. Remove newly created persistent config files if no prior file existed.
5. Remove any optional wrapper file created by the future phase.
6. Confirm no `8088` listener remains.
7. Confirm no Desktop launch occurred.
8. Confirm no Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud-provider credentials were added.
9. Record rollback evidence in the PRD and changelog.

## Non-Goals

Phase 5AL and the future persistent-config proposal do not approve:

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

A future application phase must include explicit human approval for:

- exact file paths
- exact config content or patch
- backup paths
- whether the adapter may be started manually
- whether one harmless Hermes prompt may be run
- validation evidence to capture
- rollback trigger and rollback command sequence

Until then, this document is planning only.
