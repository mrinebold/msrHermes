# Hermes Desktop Install Plan

Planning date: 2026-06-05.

Phase DESKTOP-3 completed a controlled Mac mini install. Hermes Desktop was downloaded from the official Nous Research source and copied to `/Applications`, but it was not launched, configured, signed in, granted permissions, or connected to external services.

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
- The visible macOS download target is a DMG named `Hermes-Setup.dmg` at `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg`.
- The page links Nous Portal, so portal login behavior must be treated as a validation item, not assumed safe.
- The rendered official page does not publish a checksum, detached signature, notarization ticket, installer identifier, or admin privilege requirement.

Current Mac mini CLI state:

- Hermes Agent v0.15.2 / 2026.5.29.2
- CLI path: `~/.local/bin/hermes`
- Install path: `~/.hermes/hermes-agent`
- Phase 5AA confirmed usable `sample_note.md` summary output through the localhost MSR Model Router adapter.
- Phase DESKTOP-3 installed Hermes Desktop at `/Applications/Hermes.app` without launching it.

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

## Phase DESKTOP-2 Proposed Mac mini Install Commands

Status: proposal only. Do not run these commands until a later phase explicitly approves Desktop download/install/open.

Known and unknown package facts:

| Item | Current finding |
| --- | --- |
| Official page | `https://hermes-agent.nousresearch.com/desktop` |
| macOS download URL | `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg` |
| Visible filename | `Hermes-Setup.dmg` |
| Package type | DMG |
| Visible version | Hermes Agent v0.15.2 |
| Checksum | Not visible on the rendered official page |
| Signature/notarization info | Not visible on the rendered official page; must be inspected locally before launch |
| Admin privileges | Unknown; copying to `/Applications` may require admin depending local permissions, while `~/Applications` can avoid admin if approved |
| `~/.hermes` writes | Likely possible because Desktop is expected to share or inspect Hermes state, but unconfirmed until first-launch validation |
| Launch/login/background items | Unknown; must be checked because Hermes advertises unattended gateway-style operation |

Future controlled download:

```sh
mkdir -p "$HOME/Downloads/hermes-desktop"
curl --fail --location --proto '=https' --tlsv1.2 \
  --output "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg" \
  "https://hermes-assets.nousresearch.com/Hermes-Setup.dmg"
shasum -a 256 "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg"
```

Future quarantine and image inspection:

```sh
xattr -l "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg" || true
hdiutil imageinfo "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg"
spctl --assess --type open --verbose=4 "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg"
```

Future mount and app identity inspection:

```sh
MOUNT_DIR="$(mktemp -d /tmp/hermes-desktop-dmg.XXXXXX)"
hdiutil attach -readonly -nobrowse \
  -mountpoint "$MOUNT_DIR" \
  "$HOME/Downloads/hermes-desktop/Hermes-Setup.dmg"
find "$MOUNT_DIR" -maxdepth 2 -name "*.app" -print
codesign --display --verbose=4 "$MOUNT_DIR/Hermes Desktop.app"
spctl --assess --type execute --verbose=4 "$MOUNT_DIR/Hermes Desktop.app"
```

If the app bundle name differs from `Hermes Desktop.app`, stop and update this plan before install.

Future install or copy step:

```sh
ditto "$MOUNT_DIR/Hermes Desktop.app" "/Applications/Hermes Desktop.app"
hdiutil detach "$MOUNT_DIR"
```

If `/Applications` requires admin privileges, stop and ask whether to use an admin-approved copy or a user-local `"$HOME/Applications"` install. Do not use `sudo` unless a later phase explicitly approves it.

Future pre-launch baseline:

```sh
pgrep -af -i "hermes|nous" || true
launchctl print "gui/$(id -u)" | rg -i "hermes|nous" || true
ls "$HOME/Library/LaunchAgents" | rg -i "hermes|nous" || true
osascript -e 'tell application "System Events" to get the name of every login item' | tr ',' '\n' | rg -i "hermes|nous" || true
```

Future first launch validation:

```sh
open -a "Hermes Desktop"
```

Immediately after first launch, validate:

```sh
pgrep -af -i "hermes|nous" || true
launchctl print "gui/$(id -u)" | rg -i "hermes|nous" || true
ls "$HOME/Library/LaunchAgents" | rg -i "hermes|nous" || true
osascript -e 'tell application "System Events" to get the name of every login item' | tr ',' '\n' | rg -i "hermes|nous" || true
find "$HOME/.hermes" -maxdepth 2 -type f -mtime -1 -print
```

First launch must stop before chat, setup, portal login, external integration setup, broad permission grants, or background/resident enablement. If Desktop exposes provider configuration, select only a custom OpenAI-compatible localhost adapter endpoint, and only if doing so does not alter existing Hermes CLI config.

## Phase DESKTOP-3 Controlled Mac mini Install Result

Status: complete on 2026-06-05.

Install method:

- The official macOS DMG was downloaded from `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg`.
- The downloaded file SHA-256 was `be2bb2fa9b405f62ea8d5f11327c6384f979e0589ecf4caea45ebcb909c662d4`.
- `hdiutil verify` reported the DMG checksum as valid.
- The Codex app sandbox could not mount the DMG with `hdiutil attach` because the disk image helper returned `Device not configured`, so the final mount/copy was performed by the user from Terminal with the documented commands.
- The app was copied to `/Applications/Hermes.app`.

Installed app verification:

| Check | Result |
| --- | --- |
| App path | `/Applications/Hermes.app` |
| App exists | Yes |
| App bundle size | 12M |
| Bundle name | `Hermes` |
| Bundle identifier | `com.nousresearch.hermes.setup` |
| Bundle short version | `0.0.1` |
| Bundle version | `0.0.1` |
| Bundle minimum system version | `11.0` in `Info.plist`; official page states macOS 12+ |
| Executable | `/Applications/Hermes.app/Contents/MacOS/Hermes-Setup` |
| Architecture | arm64 |
| Team identifier | `T2F6S8MF7C` |
| Hardened runtime | Present |
| Notarization ticket | Stapled |
| Gatekeeper assessment | `spctl --assess --type execute` returned an internal Code Signing subsystem error in this sandbox, so it was not recorded as passing |

Post-install safety checks:

- Desktop was not launched.
- No Nous Portal sign-in was performed.
- No provider credentials were added.
- No broad filesystem permission grant was performed.
- No Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus connection was configured.
- Existing Hermes CLI config was not altered.
- No Hermes/Nous user LaunchAgent was found in `~/Library/LaunchAgents`.
- No Hermes/Nous user Application Support or Preferences files were found during verification.
- `launchctl print gui/$(id -u)` returned no Hermes/Nous match.
- No `~/.hermes` files were modified in the verification window.
- The installed app bundle and executable had `com.apple.provenance` extended attributes.
- Process-list checks from the Codex sandbox were blocked by macOS sandbox permissions, so absence of a running Desktop process is based on the user not launching the app plus no launchd/LaunchAgent evidence.
- Login item inspection from the Codex sandbox returned macOS error `-10827`; re-check from an unsandboxed Terminal before first launch if needed.

DESKTOP-3 does not approve first launch. A later phase must explicitly approve opening Desktop and must preserve the guardrails below.

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

Future rollback command proposal:

```sh
osascript -e 'quit app "Hermes Desktop"' || true
rm -rf "/Applications/Hermes Desktop.app"
rm -rf "$HOME/Applications/Hermes Desktop.app"
```

After removing the app, inspect launch/login/background items before deleting anything else:

```sh
launchctl print "gui/$(id -u)" | rg -i "hermes|nous" || true
ls "$HOME/Library/LaunchAgents" | rg -i "hermes|nous" || true
osascript -e 'tell application "System Events" to get the name of every login item' | tr ',' '\n' | rg -i "hermes|nous" || true
```

Remove launch agents, login items, or helper files only after confirming they belong to Desktop and are not used by the CLI.

## Open Questions

- Does Hermes Desktop share `~/.hermes` with the CLI?
- Does Desktop read CLI `config.yaml` and `.env` automatically?
- Can Desktop use a custom OpenAI-compatible localhost provider without a portal login?
- Does Desktop start any launch agent, login item, helper process, or background gateway by default?
- What macOS identity, signing, notarization, or checksum information is exposed for the Desktop package?

## Stop Conditions

Stop before install or launch unless a later phase explicitly approves Desktop installation.

Phase DESKTOP-2 does not approve:

- Desktop download
- Desktop install
- Desktop launch
- Nous Portal login
- cloud provider credentials
- durable credentials
- external integrations
- broad filesystem access
- background service or resident operation
