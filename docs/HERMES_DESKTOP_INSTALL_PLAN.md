# Hermes Desktop Install Plan

Planning date: 2026-06-05.

Phase DESKTOP-1 is planning only. Do not download, install, open, configure, sign in to, or grant permissions to Hermes Desktop in this phase.

## Scope

This plan covers the Mac mini Hermes Desktop roadmap. The Mac mini remains the primary resident Hermes operator target. Hermes Desktop is a future human-facing UI surface for the already-installed Hermes CLI and localhost model-router path, not a replacement for Helio/ANO governance.

DevMonster has a separate workstation plan:

- [Hermes Desktop DevMonster Plan](HERMES_DESKTOP_DEVMONSTER_PLAN.md)

## Official Source

Use only the official Nous Research Hermes Desktop page:

- https://hermes-agent.nousresearch.com/desktop

Observed on 2026-06-05:

- macOS 12+ is listed for the macOS Desktop build.
- Hermes Agent v0.15.2 is shown on the page.
- The page links Desktop downloads under the Nous Research Hermes Agent site.
- The page links Nous Portal, so portal login behavior must be treated as a validation item, not assumed safe.

Current Mac mini CLI state:

- Hermes Agent v0.15.2 / 2026.5.29.2
- CLI path: `~/.local/bin/hermes`
- Install path: `~/.hermes/hermes-agent`
- Phase 5AA confirmed usable `sample_note.md` summary output through the localhost MSR Model Router adapter.

## Install Timing

Hermes Desktop is now on the roadmap, but must not be installed yet.

Install only after:

1. Phase 5AA success is documented.
2. Hermes CLI/local adapter path remains stable.
3. A separate phase explicitly approves Desktop download/install/open.

Install before:

1. resident/background Hermes operation
2. Google Workspace credentials
3. Supabase credentials
4. Home Assistant credentials
5. durable GitHub, Helio, or Agent Bus credentials

Desktop must not become the first place where Hermes receives durable credentials or external integration authority.

## Safety Requirements

Future Mac mini Desktop install must satisfy:

- Download only from the official Nous Research Desktop page.
- Verify macOS package or app identity if possible before first launch.
- Do not sign into Nous Portal until explicitly approved.
- Do not add OpenAI, Anthropic, OpenRouter, Google, Supabase, GitHub, Home Assistant, Helio, or other live credentials.
- Do not enable background or resident operation.
- Do not grant broad filesystem permissions on first launch.
- Do not connect Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus.
- Keep Desktop pointed at the localhost model adapter if configurable.
- Keep cloud model providers fail-closed.
- Preserve ANO governance: Desktop is a UI surface, not a bypass around Helio/ANO rules, roles, permissions, approvals, or audit requirements.

## Validation Steps For Future Install

Run these only after explicit approval to install/open Desktop:

1. Download Desktop from the official Nous Research Desktop page.
2. Verify package/app identity if macOS exposes a developer identity, notarization, checksum, or quarantine metadata.
3. Install/open Desktop manually, not as a background service.
4. Confirm Desktop version.
5. Confirm whether Desktop shares `~/.hermes` with the CLI.
6. Confirm whether Desktop reads existing Hermes CLI config.
7. Confirm whether Desktop starts launchd services, background services, login items, helper tools, or gateway processes.
8. Confirm whether Desktop attempts browser login, Nous Portal login, OAuth, or account pairing on first launch.
9. Confirm whether Desktop can use `http://127.0.0.1:8088/v1` as its only model provider.
10. Confirm no cloud providers, Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or external integrations are enabled.
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
