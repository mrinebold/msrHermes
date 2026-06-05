# Hermes Desktop DevMonster Plan

Planning date: 2026-06-05.

Phase DESKTOP-1 is planning only. Do not download, install, open, configure, sign in to, or grant permissions to Hermes Desktop on DevMonster in this phase.

## Scope

DevMonster is the main work machine and also hosts Ollama/Gemma over Tailscale. Hermes Desktop on DevMonster is planned as a future human-facing workstation UI after Mac mini Desktop planning and after the CLI/local adapter path has proven useful sandbox output.

DevMonster Desktop must not alter DevMonster's model-worker role. In particular, it must not change Ollama, Gemma, Tailscale, host binding, launch behavior, or firewall/network exposure.

## Official Source

Use only the official Nous Research Hermes Desktop page:

- https://hermes-agent.nousresearch.com/desktop

Observed on 2026-06-05:

- macOS 12+ is listed for the macOS Desktop build.
- Hermes Agent v0.15.2 is shown on the page.
- The page links Desktop downloads under the Nous Research Hermes Agent site.
- The page links Nous Portal; do not sign in unless explicitly approved.

## Install Timing

DevMonster Desktop may follow Mac mini Desktop planning, but must not be installed yet.

Install only after:

1. Phase 5AA success is documented.
2. Mac mini Desktop planning is complete.
3. A separate DevMonster phase explicitly approves Desktop download/install/open.

Install before:

1. resident/background Hermes operation on DevMonster
2. durable Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus credentials
3. any DevMonster Desktop connection to external integrations

## Safety Requirements

Future DevMonster Desktop install must satisfy:

- Download only from the official Nous Research Desktop page.
- Verify macOS package or app identity if possible before first launch.
- Do not sign into Nous Portal until explicitly approved.
- Do not add OpenAI, Anthropic, OpenRouter, Google, Supabase, GitHub, Home Assistant, Helio, or other live credentials.
- Do not enable background or resident operation.
- Do not grant broad filesystem permissions on first launch.
- Do not connect Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus.
- Keep Desktop pointed at a localhost OpenAI-compatible model adapter if configurable.
- Preserve ANO governance: Desktop is a UI surface, not a bypass around Helio/ANO rules, roles, permissions, approvals, or audit requirements.
- Do not change DevMonster Ollama binding.
- Do not bind Ollama or the adapter to `0.0.0.0`.
- Do not expose Ollama, Gemma, or Desktop beyond approved localhost/Tailscale boundaries.
- Do not alter Tailscale settings, reverse tunnels, SSH, launch agents, or model-worker startup behavior.

## Validation Steps For Future Install

Run these only after explicit approval to install/open Desktop on DevMonster:

1. Download Desktop from the official Nous Research Desktop page.
2. Verify package/app identity if macOS exposes a developer identity, notarization, checksum, or quarantine metadata.
3. Install/open Desktop manually, not as a background service.
4. Confirm Desktop version.
5. Confirm whether Desktop shares `~/.hermes` with any CLI install on DevMonster.
6. Confirm whether Desktop reads existing Hermes config.
7. Confirm whether Desktop starts launchd services, background services, login items, helper tools, or gateway processes.
8. Confirm whether Desktop attempts browser login, Nous Portal login, OAuth, or account pairing on first launch.
9. Confirm whether Desktop can use a localhost/OpenAI-compatible adapter without cloud credentials.
10. Confirm no cloud providers, Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or external integrations are enabled.
11. Confirm no broad filesystem permissions are granted.
12. Confirm Ollama/Gemma remains bound only as previously approved and that Tailscale behavior is unchanged.
13. Quit Desktop and confirm no residual Desktop listener, launch item, or background process remains unless separately approved.

## Rollback

Future DevMonster rollback should remove Desktop while preserving the model worker.

Rollback steps:

1. Quit Hermes Desktop.
2. Remove the Hermes Desktop app from `/Applications` or the chosen install location.
3. Remove Desktop-specific launch items or login items if any were created.
4. Remove Desktop-specific helper tools only after verifying they are not used by any approved CLI install.
5. Leave DevMonster Ollama/Gemma, Tailscale, model-worker settings, and approved host bindings intact.
6. Leave any Hermes CLI install intact unless a separate rollback phase approves CLI removal.

Do not delete model files, change Ollama config, change Tailscale config, or remove local model-worker state during Desktop rollback.

## Stop Conditions

Stop before install or launch unless a later phase explicitly approves DevMonster Desktop installation.

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
- Ollama changes
- Tailscale changes
- SSH changes
- reverse tunnel changes
