# Hermes Desktop Install Plan

Planning date: 2026-06-05.

Phase DESKTOP-8 planned official artifact reacquisition only. Hermes Desktop remains fail-closed: `/Applications/Hermes.app` is not trusted as a final Desktop runtime, and no new download, install, launch, replacement, quarantine change, permission grant, credential setup, or external connection has been approved.

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

Observed on 2026-06-06 during DESKTOP-8 planning:

- The official page still lists macOS 12+ for Mac OS.
- The page now shows Hermes Agent v0.16.0.
- The macOS download link is under `hermes-assets.nousresearch.com`; one observed target shape was `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=c37c6eaf296a`.
- No artifact was downloaded in DESKTOP-8.

Current Mac mini CLI state:

- Hermes Agent v0.15.2 / 2026.5.29.2
- CLI path: `~/.local/bin/hermes`
- Install path: `~/.hermes/hermes-agent`
- Phase 5AA confirmed usable `sample_note.md` summary output through the localhost MSR Model Router adapter.
- Phase DESKTOP-3 installed Hermes Desktop at `/Applications/Hermes.app` without launching it.
- Phase DESKTOP-5 diagnosed `/Applications/Hermes.app` as a bootstrap installer bundle with unresolved signature/openability issues.
- Phase DESKTOP-6 confirmed the official DMG copies are valid and identical, but mounted-bundle comparison requires an unsandboxed Terminal or Finder because `hdiutil attach` fails inside Codex.
- Phase DESKTOP-7A reconfirmed the installed bundle state and found a pre-existing `Hermes-Setup` process; no launch/configuration changes were made.
- Phase DESKTOP-8 planned official artifact reacquisition and later comparison/replacement safeguards only; no download or replacement was performed.

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

DESKTOP-3 did not approve first launch. Phase DESKTOP-4 approved one guarded first-launch validation only.

## Phase DESKTOP-4 First-Launch Validation Result

Status: complete on 2026-06-05.

Pre-launch baseline:

- `/Applications/Hermes.app` existed.
- Bundle metadata still reported name `Hermes`, identifier `com.nousresearch.hermes.setup`, and version `0.0.1`.
- No Hermes/Nous user LaunchAgent was found in `~/Library/LaunchAgents`.
- No Hermes/Nous `launchctl print gui/$(id -u)` entry was present before launch.
- No Hermes/Nous background-task match was visible through `sfltool dumpbtm`.

Launch attempt:

- `open -a /Applications/Hermes.app` returned exit code 0 on the first attempt.
- No visible first-run screen could be captured from the Codex sandbox; `screencapture` returned `could not create image from display`.
- AppleScript and LaunchServices UI metadata could not expose a window title or first-screen text from the sandbox.
- A later `open /Applications/Hermes.app` attempt returned `kLSNoExecutableErr`, even though `Contents/MacOS/Hermes-Setup` exists.
- `codesign --verify --deep --strict --verbose=4 /Applications/Hermes.app` reported `invalid signature (code or signature have been modified)` for arm64.
- `launchctl` showed a transient submitted UI job for `application.com.nousresearch.hermes.setup...` running `/Applications/Hermes.app/Contents/MacOS/Hermes-Setup`.
- The launch created `~/.hermes/logs/bootstrap-installer.log` with one line: `Hermes installer starting mode=Install force_setup=false`.

Observed first-run behavior:

| Question | Result |
| --- | --- |
| First screen visible | No observable UI from the Codex sandbox |
| Nous Portal sign-in prompt | Not observed |
| Browser login prompt | Not observed |
| Model/provider credential prompt | Not observed |
| Filesystem permission prompt | Not observed |
| Accessibility permission prompt | Not observed |
| Screen Recording permission prompt | Not observed |
| Automation permission prompt | Not observed |
| Launch/login item prompt | Not observed |
| App version visible in UI | Not observed; bundle version remained `0.0.1` |
| Shares `~/.hermes` with CLI | Inconclusive; only `~/.hermes/logs/bootstrap-installer.log` was written |
| Reads existing Hermes config | Inconclusive; no UI/config state was observed |
| Localhost adapter configurable | Not observed |

Post-launch shutdown and safety checks:

- The transient LaunchServices job did not stop from inside the Codex sandbox with `launchctl kill`, `launchctl bootout`, or `kill -9`.
- The user killed the process from an unsandboxed Terminal.
- After user kill, `launchctl print gui/$(id -u)/application.com.nousresearch.hermes.setup...` returned service not found.
- AppleScript reported `application "Hermes" is running` as `false`.
- No Hermes/Nous `launchctl print gui/$(id -u)` entries remained.
- No Hermes/Nous user LaunchAgent was found.
- No Hermes/Nous background-task match was visible through `sfltool dumpbtm`.
- No Hermes/Nous user Application Support or Preferences files were found during verification.
- No cloud provider credentials were added.
- No Nous Portal sign-in was performed.
- No broad filesystem, Accessibility, Screen Recording, Automation, or Full Disk Access permission was granted.
- No Google, Supabase, Home Assistant, GitHub, Helio, or Agent Bus connection was configured.
- Existing Hermes CLI config was not intentionally modified.
- The model router adapter was not started.

Conclusion:

DESKTOP-4 failed closed before usable first-run UI validation. The installed app appears to be a bootstrap installer bundle rather than the final Desktop runtime. Before another Desktop launch attempt, inspect the official DMG install flow from an unsandboxed Terminal or Finder, resolve the app bundle signature/openability issue, and confirm whether a completed bootstrap install creates a different signed Desktop app bundle.

## Phase DESKTOP-5 Bootstrap/Openability Diagnostic

Status: complete on 2026-06-05.

Scope:

- No Desktop launch was attempted.
- No Nous Portal sign-in was attempted.
- No credentials, permissions, integrations, background services, or launch/login items were added.
- Hermes CLI config and the localhost model adapter path were not modified.

Installed bundle findings:

| Check | Result |
| --- | --- |
| App path | `/Applications/Hermes.app` |
| Bundle name | `Hermes` |
| Bundle identifier | `com.nousresearch.hermes.setup` |
| Bundle version | `0.0.1` |
| Executable | `/Applications/Hermes.app/Contents/MacOS/Hermes-Setup` |
| Executable file type | Mach-O 64-bit executable arm64 |
| Bundle size | 12M |
| File count | Minimal: `Info.plist`, `Hermes-Setup`, `icon.icns`, and code-signing resources |
| App type assessment | Bootstrap installer app, not the final Desktop runtime |

Signature and openability findings:

- `codesign --display --verbose=4` reported Team ID `T2F6S8MF7C`, hardened runtime, and a stapled notarization ticket.
- `codesign --verify --strict --verbose=4 /Applications/Hermes.app` failed with `invalid signature (code or signature have been modified)`.
- Direct executable verification also failed with `invalid signature (code or signature have been modified)`.
- `spctl --assess --type execute` and `spctl --assess --type open` returned an internal Code Signing subsystem error in the Codex environment.
- `xattr -lr /Applications/Hermes.app` showed `com.apple.provenance` and `com.apple.macl`, but no `com.apple.quarantine`.
- The sealed resource manifest covered `Resources/icon.icns`; its SHA-1 and SHA-256 matched the manifest values.
- The current blocker does not appear to be quarantine. The blocker is signature/openability plus the fact that the installed app is a bootstrap installer bundle.

Log findings:

- `~/.hermes/logs/bootstrap-installer.log` contains a single bootstrap line:

```text
2026-06-05T16:51:43.309535Z  INFO hermes_bootstrap_lib: Hermes installer starting mode=Install force_setup=false
```

- No additional Hermes Desktop logs were found under `~/.hermes/logs`.
- `agent.log` and `errors.log` existed from earlier Hermes CLI work and remained empty.
- macOS `log show` exposed no useful Hermes Desktop entries without elevated access.

Process, launch, and persistence findings:

- AppleScript reported `application "Hermes" is running` as `false`.
- No Hermes/Nous entry was present in `launchctl print gui/$(id -u)`.
- No Hermes/Nous user LaunchAgent was found in `~/Library/LaunchAgents`.
- No Hermes/Nous background-task match was visible through `sfltool dumpbtm`.
- No Hermes/Nous files were found under user `Application Support`, `Preferences`, or `Logs` during this diagnostic.
- No new `~/.hermes` files were modified during this diagnostic.

Conclusion:

The installed `/Applications/Hermes.app` is best classified as a bootstrap installer app with a damaged or invalid current code-signing/openability state. It is not yet a validated final Desktop runtime. The first-run bootstrap likely requires a secondary install step, but that step must not be attempted again until the signature/openability problem is resolved.

Recommended next action:

Start Phase DESKTOP-6 as an offline install-source and bundle-integrity investigation only. Re-mount the official DMG from an unsandboxed Terminal or Finder, compare the mounted app bundle to `/Applications/Hermes.app`, verify signature before and after copy, and determine whether the app must be run from the mounted DMG to complete a secondary install. Do not launch the app or remove quarantine/signature controls until that phase explicitly approves the exact next step.

## Phase DESKTOP-6 DMG vs Installed App Comparison

Status: complete as far as the Codex sandbox allowed on 2026-06-06.

Scope:

- No Desktop launch was attempted.
- No quarantine attributes were removed.
- No app reinstall, recopy, or mutation was performed.
- No credentials, permissions, integrations, background services, or launch/login items were added.
- Hermes CLI config and the localhost model adapter path were not modified.

DMG source findings:

| Check | Result |
| --- | --- |
| Candidate DMGs found | `/private/tmp/hermes-desktop-install.6u5AY2/Hermes-Setup.dmg`, `/private/tmp/hermes-desktop-install.p4dE54/Hermes-Setup.dmg` |
| DMG file size | 6.4M each |
| DMG SHA-256 | `be2bb2fa9b405f62ea8d5f11327c6384f979e0589ecf4caea45ebcb909c662d4` for both |
| DMG verification | `hdiutil verify` reported checksum valid for both |
| DMG file type | `file` reported `zlib compressed data`; `hdiutil verify` identified it as a valid disk image |
| DMG quarantine | No `com.apple.quarantine` observed |
| DMG xattrs | one copy had `com.apple.provenance`; one had `com.apple.diskimages.recentcksum` |

Mount result:

- No Hermes Desktop DMG was already mounted.
- `hdiutil attach -readonly -nobrowse -mountpoint ... /private/tmp/hermes-desktop-install.6u5AY2/Hermes-Setup.dmg` failed inside Codex with `Device not configured`.
- A retry after additional file permissions were granted still failed with `Device not configured`, confirming the blocker is the Codex app sandbox rather than ordinary file read access.
- Converting the DMG to CDR succeeded, but `bsdtar` could not list either the DMG or CDR because they are not archive formats.
- Therefore the mounted app bundle inside the DMG could not be inspected from this sandbox.
- No DMG was mounted by this phase, so there was nothing to unmount.

Installed app comparison facts:

| Check | `/Applications/Hermes.app` |
| --- | --- |
| Bundle identifier | `com.nousresearch.hermes.setup` |
| Bundle name/display name | `Hermes` |
| Bundle version | `0.0.1` |
| Executable | `Contents/MacOS/Hermes-Setup` |
| Executable type | Mach-O 64-bit executable arm64 |
| Major directories | `Contents`, `Contents/MacOS`, `Contents/Resources`, `Contents/_CodeSignature` |
| Files | `CodeResources`, `Info.plist`, `Hermes-Setup`, `icon.icns`, `_CodeSignature/CodeResources` |
| App signature display | Team ID `T2F6S8MF7C`, hardened runtime, stapled notarization ticket |
| App signature verification | failed with `invalid signature (code or signature have been modified)` |
| Executable signature verification | failed with `invalid signature (code or signature have been modified)` |
| `spctl` assessment | internal Code Signing subsystem error |
| Installed app xattrs | `com.apple.provenance`, `com.apple.macl`; no `com.apple.quarantine` |

Installed file hashes:

```text
a7bd62cf64666394b1f9d24459c9214c79c36beff25d23119eef05d27bf7d9ca  /Applications/Hermes.app/Contents/MacOS/Hermes-Setup
2d31360e01a075058a8e1713c7efd7b8175b44f5f7e243985cc920a3ec0ccab0  /Applications/Hermes.app/Contents/Info.plist
56c39b613d61d13671e49bf7e32fb8e80f705b9c50d8bed1c18a505f0b12be89  /Applications/Hermes.app/Contents/Resources/icon.icns
```

Process, launch, and persistence findings:

- AppleScript reported `application "Hermes" is running` as `false`.
- No Hermes/Nous entry was present in `launchctl print gui/$(id -u)`.
- No Hermes/Nous user LaunchAgent was found in `~/Library/LaunchAgents`.
- No Hermes/Nous background-task match was visible through `sfltool dumpbtm`.
- No Hermes/Nous user Application Support or Preferences files were found.

Conclusion:

Phase DESKTOP-6 did not prove whether `/Applications/Hermes.app` is identical to the mounted DMG bundle because the sandbox could not mount the APFS DMG. It did prove the downloaded DMG copies are valid and identical, and it reconfirmed the installed app remains a minimal bootstrap installer bundle with invalid signature/openability state and no quarantine marker.

Recommended next action:

Run Phase DESKTOP-7 from an unsandboxed Terminal or Finder: mount the official DMG, inspect the mounted `.app` before copying, compare file hashes and `codesign --verify --strict` results against `/Applications/Hermes.app`, then unmount. Do not launch, recopy, remove quarantine, or complete any bootstrap install unless a later phase explicitly approves those actions.

## Phase DESKTOP-7A Installed Bundle State Clarification

Status: complete on 2026-06-06.

Scope:

- No Desktop launch was attempted.
- No DMG redownload, app reinstall, recopy, quarantine removal, signing change, credential setup, permission grant, or integration connection was performed.
- Hermes CLI config and the localhost model adapter path were not modified.
- The observed running process was not killed because this phase did not approve Desktop state changes.

Installed bundle findings:

| Check | Result |
| --- | --- |
| App path | `/Applications/Hermes.app` |
| Bundle directory | Present, `drwxr-xr-x@`, owner `michaelrinebold`, group `staff` |
| Bundle identifier | `com.nousresearch.hermes.setup` |
| Bundle name/display name | `Hermes` |
| Bundle short version | `0.0.1` |
| Bundle version | `0.0.1` |
| Executable | `Contents/MacOS/Hermes-Setup` |
| Executable type | Mach-O thin arm64 |
| Major directories | `Contents`, `Contents/MacOS`, `Contents/Resources`, `Contents/_CodeSignature` |
| Files | `CodeResources`, `Info.plist`, `Hermes-Setup`, `icon.icns`, `_CodeSignature/CodeResources` |
| App type assessment | Bootstrap/setup app bundle, not validated final Desktop runtime |

Info.plist fields:

| Field | Value |
| --- | --- |
| `CFBundleIdentifier` | `com.nousresearch.hermes.setup` |
| `CFBundleName` | `Hermes` |
| `CFBundleShortVersionString` | `0.0.1` |
| `CFBundleVersion` | `0.0.1` |
| `CFBundleExecutable` | `Hermes-Setup` |

Signature, Gatekeeper, and quarantine findings:

- `codesign -dv --verbose=4 /Applications/Hermes.app` reported Team ID `T2F6S8MF7C`, hardened runtime, and a stapled notarization ticket.
- `codesign --verify --deep --strict --verbose=4 /Applications/Hermes.app` failed with `invalid signature (code or signature have been modified)` for arm64.
- `spctl -a -vvv --type execute /Applications/Hermes.app` failed with `internal error in Code Signing subsystem`.
- Recursive xattrs showed `com.apple.provenance` across the bundle and `com.apple.macl` on `/Applications/Hermes.app`.
- No `com.apple.quarantine` xattr was observed in the recursive xattr listing.

Installed file hashes:

```text
a7bd62cf64666394b1f9d24459c9214c79c36beff25d23119eef05d27bf7d9ca  /Applications/Hermes.app/Contents/MacOS/Hermes-Setup
2d31360e01a075058a8e1713c7efd7b8175b44f5f7e243985cc920a3ec0ccab0  /Applications/Hermes.app/Contents/Info.plist
56c39b613d61d13671e49bf7e32fb8e80f705b9c50d8bed1c18a505f0b12be89  /Applications/Hermes.app/Contents/Resources/icon.icns
```

Process, launch, and persistence findings:

- `pgrep -fl Hermes` found a pre-existing Desktop process:
  - PID `18152`
  - command `/Applications/Hermes.app/Contents/MacOS/Hermes-Setup`
  - parent PID `1`
  - started `Sat Jun 6 13:49:34 2026`
- No matching Hermes launch agent or daemon files were found in:
  - `/Users/michaelrinebold/Library/LaunchAgents`
  - `/Library/LaunchAgents`
  - `/Library/LaunchDaemons`
- Login/background item inspection was not fully checkable without authorization:
  - `osascript` against System Events returned error `-10827`.
  - `sfltool dumpbtm` requested admin authorization and failed without it.

Hermes CLI config guardrail:

No Hermes CLI commands were run and no Hermes CLI config files were edited. Reference hashes recorded during this phase:

| Path | SHA-256 |
| --- | --- |
| `/Users/michaelrinebold/.hermes/config.yaml` | `6d1df617b9de6fa0f66c0accc125622d5f2dcd15b98ea0373b453f51c4c9da00` |
| `/Users/michaelrinebold/.hermes/.env` | `be9e3b0d38b6203033ac78a120f85601720e9c3f65225b6528974e2c33cc0ef1` |
| `/Users/michaelrinebold/.hermes/.install_method` | `d21cc3b88a7ca1bbfadb85771a66eab1a8015a493ca21b4653e05cd4f9934f4a` |
| `/Users/michaelrinebold/.local/bin/hermes` | `273cbb766b7a79a5840b33498bb03288e66c9cc9353163e791ef9f43c2ebab02` |

Conclusion:

`/Applications/Hermes.app` appears to be a bootstrap/setup app bundle rather than a validated final Desktop runtime. It is not healthy enough for a controlled launch retry because strict code-signature verification fails, Gatekeeper assessment does not produce an acceptance result, and a `Hermes-Setup` process is already resident.

Current classification:

- Normal app bundle: no.
- Bootstrap installer bundle: yes, based on `com.nousresearch.hermes.setup` and executable `Hermes-Setup`.
- Incomplete/damaged: possible, because strict code-signature verification reports modified code/signature.
- Blocked by signature/notarization/quarantine: blocked by signature/Gatekeeper assessment; not blocked by observed quarantine xattr.
- Unclear requiring official artifact comparison or reacquisition plan: yes.

Recommended next action:

Proceed with Phase DESKTOP-8: official Hermes Desktop artifact reacquisition plan only. Do not download, install, launch Desktop, remove quarantine, recopy, sign in, grant permissions, connect integrations, or modify Hermes CLI config until a later phase explicitly approves those actions.

## Phase DESKTOP-8 Official Artifact Reacquisition Plan

Status: complete as planning only on 2026-06-06.

Scope:

- No Hermes Desktop artifact was downloaded.
- `/Applications/Hermes.app` was not replaced, deleted, recopied, relaunched, or modified.
- No quarantine attributes were removed.
- The pre-existing `Hermes-Setup` process was not killed.
- Hermes CLI config and the localhost model adapter path were not modified.
- No credentials, permissions, sign-in, background/resident operation, or external service connections were added.

### Current Trust State

- The original installer artifact is missing from the normal user download locations checked earlier: Downloads, Desktop, and Documents.
- Existing `/Applications/Hermes.app` is not trusted as the final Desktop runtime.
- Current app classification from DESKTOP-7A:
  - bootstrap/setup bundle: yes
  - normal final runtime bundle: not validated
  - strict code signing: fails
  - Gatekeeper/spctl acceptance: not recorded as passing
  - quarantine marker: not observed
  - existing resident process: `Hermes-Setup` PID `18152`

### Safest Official Reacquisition Workflow

Future reacquisition must be manual and source-controlled by the user:

1. Open the official Nous Research Desktop page manually in a browser:
   - `https://hermes-agent.nousresearch.com/desktop`
2. Use only the macOS download link exposed by that official page.
3. Save the artifact to:
   - `~/Downloads/hermes-desktop-official/`
4. Do not open, launch, mount for install, or run the artifact immediately after download.
5. Record the exact final browser-downloaded filename and URL, including any query string such as a `build=` parameter.
6. Keep the downloaded artifact untouched until verification is complete.

Expected possible artifact types:

| Artifact type | Expected handling |
| --- | --- |
| `.dmg` | Verify image metadata, checksum, quarantine, mounted bundle metadata, signature, and spctl before any copy. |
| `.zip` | Verify archive metadata, checksum, quarantine, extracted bundle metadata, signature, and spctl before any copy. |
| `.pkg` | Verify package metadata, installer signature, checksum, quarantine, and spctl before any install. |
| `.app` bundle | Verify bundle metadata, executable, signature, spctl, quarantine, and directory structure before any copy or launch. |

### Verification Before Any Install Or Replacement

Run only after a later phase explicitly approves download/inspection. Do not launch during verification.

Suggested artifact capture:

```sh
mkdir -p "$HOME/Downloads/hermes-desktop-official"
ls -lah "$HOME/Downloads/hermes-desktop-official"
find "$HOME/Downloads/hermes-desktop-official" -maxdepth 1 -print
```

Verify file type and size:

```sh
ARTIFACT="$HOME/Downloads/hermes-desktop-official/<downloaded artifact>"
file "$ARTIFACT"
stat -f '%N %z bytes mtime=%Sm' "$ARTIFACT"
```

Record checksum:

```sh
shasum -a 256 "$ARTIFACT"
```

If the official page publishes a checksum later, compare against that published value before any mount, extraction, install, or copy. If no checksum is published, record the local checksum and treat it as a provenance note, not as authenticity proof.

Inspect quarantine and other xattrs:

```sh
xattr -l "$ARTIFACT" || true
```

For a DMG:

```sh
hdiutil imageinfo "$ARTIFACT"
hdiutil verify "$ARTIFACT"
spctl --assess --type open --verbose=4 "$ARTIFACT"
MOUNT_DIR="$(mktemp -d /tmp/hermes-desktop-official.XXXXXX)"
hdiutil attach -readonly -nobrowse -mountpoint "$MOUNT_DIR" "$ARTIFACT"
find "$MOUNT_DIR" -maxdepth 3 -print
find "$MOUNT_DIR" -maxdepth 2 -name "*.app" -print
```

For a ZIP:

```sh
ditto -x -k "$ARTIFACT" "$HOME/Downloads/hermes-desktop-official/extracted"
find "$HOME/Downloads/hermes-desktop-official/extracted" -maxdepth 3 -print
find "$HOME/Downloads/hermes-desktop-official/extracted" -maxdepth 2 -name "*.app" -print
```

For a PKG:

```sh
pkgutil --check-signature "$ARTIFACT"
pkgutil --payload-files "$ARTIFACT" | head -100
spctl --assess --type install --verbose=4 "$ARTIFACT"
```

For an app bundle found in a mounted/extracted artifact:

```sh
DOWNLOADED_APP="<path to downloaded, mounted, or extracted .app>"
plutil -p "$DOWNLOADED_APP/Contents/Info.plist"
du -sh "$DOWNLOADED_APP"
find "$DOWNLOADED_APP" -maxdepth 3 -print
codesign -dv --verbose=4 "$DOWNLOADED_APP"
codesign --verify --deep --strict --verbose=4 "$DOWNLOADED_APP"
spctl --assess --type execute --verbose=4 "$DOWNLOADED_APP"
xattr -lr "$DOWNLOADED_APP" || true
```

### Comparison Against Existing `/Applications/Hermes.app`

Compare before any replacement:

```sh
INSTALLED_APP="/Applications/Hermes.app"
DOWNLOADED_APP="<path to downloaded, mounted, or extracted .app>"

plutil -extract CFBundleIdentifier raw "$DOWNLOADED_APP/Contents/Info.plist"
plutil -extract CFBundleIdentifier raw "$INSTALLED_APP/Contents/Info.plist"
plutil -extract CFBundleShortVersionString raw "$DOWNLOADED_APP/Contents/Info.plist"
plutil -extract CFBundleShortVersionString raw "$INSTALLED_APP/Contents/Info.plist"
plutil -extract CFBundleVersion raw "$DOWNLOADED_APP/Contents/Info.plist"
plutil -extract CFBundleVersion raw "$INSTALLED_APP/Contents/Info.plist"
plutil -extract CFBundleExecutable raw "$DOWNLOADED_APP/Contents/Info.plist"
plutil -extract CFBundleExecutable raw "$INSTALLED_APP/Contents/Info.plist"

du -sh "$DOWNLOADED_APP" "$INSTALLED_APP"
find "$DOWNLOADED_APP" -maxdepth 2 -type d -print
find "$INSTALLED_APP" -maxdepth 2 -type d -print
find "$DOWNLOADED_APP" -maxdepth 3 -type f -print | sort
find "$INSTALLED_APP" -maxdepth 3 -type f -print | sort
```

Required comparison points:

- bundle identifier
- bundle name/display name
- short version and build version
- executable name
- executable architecture and file type
- bundle size
- major directories
- file inventory shape
- signature display metadata
- strict signature verification result
- spctl assessment result
- quarantine/xattr differences

The downloaded/mounted app must not be considered safer merely because it is newer. It must pass signature and Gatekeeper checks before any replacement is proposed.

### Rollback Plan Before Any Future Replacement

Run only after a later phase explicitly approves replacement preparation.

1. If any `Hermes-Setup` or Hermes Desktop process is running, ask the user for explicit approval to quit it.
2. Quit gently first if approved; use force only after separate approval if the process does not exit.
3. Copy the existing installed app to a timestamped backup before replacement:

```sh
BACKUP_DIR="$HOME/Downloads/hermes-desktop-official/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
ditto "/Applications/Hermes.app" "$BACKUP_DIR/Hermes.app"
du -sh "$BACKUP_DIR/Hermes.app"
codesign --verify --deep --strict --verbose=4 "$BACKUP_DIR/Hermes.app" || true
```

4. Do not delete the backup until the replacement app is verified, launched under a later approved first-launch phase, and confirmed not to break Hermes CLI state.
5. Preserve `~/.local/bin/hermes`, `~/.hermes/hermes-agent`, `~/.hermes/config.yaml`, and the localhost model adapter path unless a separate phase explicitly approves CLI state changes.

### Future Replacement Plan

This phase does not approve replacement. Replacement may be proposed only after a later phase approves it and after the official artifact is verified.

Future replacement sequence:

1. Confirm user approval to replace `/Applications/Hermes.app`.
2. Confirm no unapproved Hermes Desktop process is running.
3. Confirm timestamped backup exists.
4. Remove or replace `/Applications/Hermes.app` only after explicit approval.
5. Copy the verified official app bundle to `/Applications`.
6. Re-run:
   - `plutil` Info.plist metadata checks
   - `du -sh`
   - `codesign -dv --verbose=4`
   - `codesign --verify --deep --strict --verbose=4`
   - `spctl --assess --type execute --verbose=4`
   - `xattr -lr`
7. Stop if strict signature verification or spctl assessment fails.

### First-Launch Guardrails After Future Replacement

First launch remains a separate phase. Even after a verified replacement:

- Do not sign into Nous Portal unless explicitly approved.
- Do not add OpenAI, Anthropic, OpenRouter, Google, Supabase, GitHub, Home Assistant, Helio, or cloud provider credentials.
- Do not grant broad filesystem permissions.
- Do not grant Accessibility, Screen Recording, Automation, or Full Disk Access without explicit approval.
- Do not enable background/resident operation.
- Do not connect Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, or cloud providers.
- Do not modify Hermes CLI config.
- Do not start the localhost model adapter unless separately approved.
- Quit Desktop after observation unless a later phase explicitly approves resident operation.

Recommended next action:

Phase DESKTOP-9 should be a download/verification-only phase for the official artifact, or a narrower unsandboxed manual comparison phase if the already-downloaded DMG can be mounted by the user outside Codex. It must still stop before install, replacement, launch, sign-in, permission grants, credentials, integrations, and Hermes CLI config changes.

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
