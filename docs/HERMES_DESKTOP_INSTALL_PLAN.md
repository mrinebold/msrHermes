# Hermes Desktop Install Plan

Planning date: 2026-06-05.

Phase DESKTOP-1 is planning only. Do not download, install, open, configure, sign in to, or grant permissions to Hermes Desktop in this phase.

## Official Source

Use only the official Nous Research Hermes Desktop page:

- https://hermes-agent.nousresearch.com/desktop

Observed on 2026-06-05:

- macOS 12+ is listed for the macOS Desktop build.
- Hermes Agent v0.15.2 is shown on the page.
- The page links Desktop downloads under the Nous Research Hermes Agent site and references Nous Portal plans.

Current local CLI install:

- Hermes Agent v0.15.2 / 2026.5.29.2
- CLI path: `~/.local/bin/hermes`
- Install path: `~/.hermes/hermes-agent`

## Install Timing

Hermes Desktop should be added to the roadmap, but not installed yet.

Install only after:

1. Hermes CLI is installed and stable.
2. The localhost OpenAI-compatible MSR Model Router adapter is stable.
3. Phase 5T or Phase 5U confirms Hermes CLI can produce useful sandbox output through the localhost adapter.

Install before:

1. resident/background Hermes operation
2. Google Workspace connection
3. Supabase connection
4. Home Assistant connection
5. Helio connection
6. any durable credentials are granted to Hermes Desktop

Desktop must not become the first place where Hermes receives durable credentials or external integration authority.

## Safety Requirements

Future Desktop install must satisfy:

- Download only from the official Nous Research Desktop page.
- Verify macOS package or app identity if possible before first launch.
- Do not sign into Nous Portal until explicitly approved.
- Do not add OpenAI, Anthropic, OpenRouter, Google, Supabase, GitHub, Home Assistant, Helio, or other live credentials.
- Do not enable background or resident operation.
- Do not grant broad filesystem permissions on first launch.
- Do not connect Google, Supabase, Home Assistant, Helio, or Agent Bus.
- Keep Desktop pointed at the localhost model adapter if configurable.
- Keep cloud model providers fail-closed.
- Keep Hermes Desktop validation read-only and synthetic until a later phase approves more authority.

## Validation Steps For Future Install

Run these only after explicit approval to install/open Desktop:

1. Download Desktop from the official page.
2. Verify package/app identity if macOS exposes a developer identity, notarization, checksum, or quarantine metadata.
3. Install/open Desktop manually, not as a background service.
4. Confirm Desktop version.
5. Confirm whether Desktop shares `~/.hermes` with the CLI.
6. Confirm whether Desktop reads existing Hermes CLI config.
7. Confirm whether Desktop starts background services, launch items, login items, helper tools, or gateway processes.
8. Confirm whether Desktop attempts browser login, Nous Portal login, OAuth, or account pairing on first launch.
9. Confirm whether Desktop can use `http://127.0.0.1:8088/v1` as its only model provider.
10. Confirm no cloud providers, Google, Supabase, Home Assistant, Helio, Agent Bus, or external integrations are enabled.
11. Confirm no broad filesystem permissions are granted.
12. Quit Desktop and confirm no residual Desktop listener, launch item, or background process remains unless separately approved.

## Rollback

Future rollback should remove Desktop while leaving the CLI install intact unless separately approved.

Rollback steps:

1. Quit Hermes Desktop.
2. Remove the Hermes Desktop app from `/Applications` or the chosen install location.
3. Remove Desktop-specific launch items or login items if any were created.
4. Remove Desktop-specific helper tools only after verifying they are not used by the CLI.
5. Leave `~/.local/bin/hermes`, `~/.hermes/hermes-agent`, and CLI state intact unless a separate rollback phase approves CLI removal.

Do not delete `~/.hermes` during Desktop rollback unless a separate state-removal phase is approved.

## Open Questions

- Does Hermes Desktop share `~/.hermes` with the CLI?
- Does Desktop read CLI `config.yaml` and `.env` automatically?
- Can Desktop use a custom OpenAI-compatible localhost provider without a portal login?
- Does Desktop start any launch agent, login item, helper process, or background gateway by default?
- What macOS identity, signing, notarization, or checksum information is exposed for the Desktop package?

## Stop Conditions

Stop before install or launch unless a later phase explicitly approves Desktop installation.

Phase DESKTOP-1 does not approve:

- Desktop download
- Desktop install
- Desktop launch
- Nous Portal login
- cloud provider credentials
- durable credentials
- external integrations
- broad filesystem access
- background service or resident operation
