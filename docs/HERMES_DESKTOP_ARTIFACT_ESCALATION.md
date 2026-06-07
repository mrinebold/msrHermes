# Hermes Desktop Artifact Integrity Escalation

Phase: DESKTOP-10
Date: 2026-06-07
Status: planning/documentation only

## Scope

This document records the current official Hermes Desktop macOS artifact integrity findings and prepares an escalation/release-channel clarification before any launch, replacement, reinstall, permission grant, sign-in, or Desktop configuration.

DESKTOP-10 does not approve:

- launching Hermes Desktop
- replacing, deleting, reinstalling, or recopying `/Applications/Hermes.app`
- removing quarantine or other xattrs
- killing `Hermes-Setup`
- signing in to Nous Portal
- adding credentials
- granting permissions
- modifying Hermes CLI config
- connecting Google, Supabase, Home Assistant, GitHub, Helio, Agent Bus, cloud providers, or any other external service
- sending the escalation message below

## Artifact Under Review

| Check | Result |
| --- | --- |
| Official source page | `https://hermes-agent.nousresearch.com/desktop` |
| Download URL used | `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05` |
| Local artifact path | `/Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg` |
| File name | `Hermes-Setup.dmg` |
| File size | `6752854` bytes |
| SHA-256 | `b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5` |
| Artifact xattrs | `com.apple.provenance`; no observed `com.apple.quarantine` |
| `hdiutil verify` | Passed; checksum valid, CRC32 `$9DB5F445` |
| `hdiutil imageinfo` | UDIF read-only compressed zlib / `UDZO`, APFS partition, not encrypted, checksummed, compressed |
| DMG `spctl --assess --type open` | Internal Code Signing subsystem error |

## Mounted App Findings

| Check | Result |
| --- | --- |
| Mounted app path during DESKTOP-9 | `/private/tmp/hermes-desktop-official-mount/Hermes.app` |
| Bundle identifier | `com.nousresearch.hermes.setup` |
| App name | `Hermes` |
| Bundle short version | `0.0.1` |
| Bundle version | `0.0.1` |
| Executable | `Hermes-Setup` |
| Minimum system version in `Info.plist` | `11.0` |
| Bundle size | `12M` |
| Bundle structure | Minimal setup/bootstrap bundle: `Info.plist`, `Hermes-Setup`, `icon.icns`, and code-signing resources |
| Signing display | Team ID `T2F6S8MF7C`, hardened runtime, stapled notarization ticket |
| Mounted app CDHash | `834657a498023c95ef9c48ced4ab525e1271216d` |
| Strict codesign verification | Failed: `invalid signature (code or signature have been modified)` for arm64 |
| `spctl --assess --type execute` | Internal Code Signing subsystem error |
| Mounted app xattrs | `com.apple.provenance`; no observed `com.apple.quarantine` |

## Comparison To Installed App

Existing installed app:

- `/Applications/Hermes.app`
- Current local classification: not trusted as a final Desktop runtime

| Check | Mounted official artifact app | Installed `/Applications/Hermes.app` |
| --- | --- | --- |
| Bundle identifier | `com.nousresearch.hermes.setup` | `com.nousresearch.hermes.setup` |
| App name | `Hermes` | `Hermes` |
| Version | `0.0.1` | `0.0.1` |
| Executable | `Hermes-Setup` | `Hermes-Setup` |
| Bundle size | `12M` | `12M` |
| Major structure | Minimal setup/bootstrap bundle | Minimal setup/bootstrap bundle |
| Strict codesign | Fails invalid signature | Fails invalid signature |
| spctl execute assessment | Internal Code Signing subsystem error | Internal Code Signing subsystem error |
| `Contents/MacOS/Hermes-Setup` SHA-256 | `77bc5f19ca5bb53442524b2f400a42032e2a0effa27d34b5453654fb9e53e261` | `a7bd62cf64666394b1f9d24459c9214c79c36beff25d23119eef05d27bf7d9ca` |
| `Contents/Info.plist` SHA-256 | `2d31360e01a075058a8e1713c7efd7b8175b44f5f7e243985cc920a3ec0ccab0` | `2d31360e01a075058a8e1713c7efd7b8175b44f5f7e243985cc920a3ec0ccab0` |
| `Contents/Resources/icon.icns` SHA-256 | `56c39b613d61d13671e49bf7e32fb8e80f705b9c50d8bed1c18a505f0b12be89` | `56c39b613d61d13671e49bf7e32fb8e80f705b9c50d8bed1c18a505f0b12be89` |

The mounted official artifact and installed app have the same metadata, size, structure, and signature failure pattern. The executable hash differs, consistent with a newer build query in the reacquired artifact, but the newer executable still does not pass strict code-signature verification.

## Why Desktop Remains Fail-Closed

Hermes Desktop remains fail-closed because:

1. The official artifact's DMG verifies, but the mounted app inside it fails strict code-signature verification.
2. Gatekeeper assessment does not return an acceptance result for either the DMG or mounted app.
3. The mounted bundle identifies as `com.nousresearch.hermes.setup`, version `0.0.1`, executable `Hermes-Setup`, which appears to be a setup/bootstrap app rather than a validated final Desktop runtime.
4. The installed app has the same metadata and signature failure pattern.
5. The Desktop first-launch attempt in an earlier phase did not produce a usable UI and created only a bootstrap installer log.
6. The original local Desktop state includes a pre-existing `Hermes-Setup` process, and DESKTOP-10 does not approve killing or changing that state.
7. No official checksum, detached signature, release note, or Desktop-specific release channel has been confirmed locally.

Until Nous Research clarifies whether this behavior is expected and provides a trusted Desktop release path, replacing or launching Desktop would create avoidable integrity and support risk.

## Release-Channel Questions

Ask Nous Research or check official release materials for:

1. Is `Hermes-Setup.dmg` intended to contain a bootstrap installer rather than the final Desktop app?
2. Is bundle identifier `com.nousresearch.hermes.setup` expected for the current macOS Desktop artifact?
3. Is version `0.0.1` expected for Hermes Agent v0.16.0 Desktop downloads?
4. Is executable name `Hermes-Setup` expected for the installed/runnable Desktop app?
5. Is strict `codesign --verify --deep --strict` failure expected on current macOS for this artifact?
6. Is `spctl` returning an internal Code Signing subsystem error a known issue for this build?
7. Is there a notarized macOS Desktop artifact whose app bundle passes strict signature verification?
8. Does Nous Research publish SHA-256 checksums, detached signatures, release notes, or signing metadata for Desktop artifacts?
9. Is there a stable release channel or GitHub release source for Hermes Desktop separate from the live Desktop page download?
10. Is the `build=` query string the intended way to identify a Desktop build?
11. Is Desktop supposed to share `~/.hermes` with the CLI install?
12. Can Desktop be configured to use a localhost OpenAI-compatible endpoint without Nous Portal sign-in?
13. Does Desktop require a first-run bootstrap step that creates a second, final app bundle?
14. If so, what app path, bundle identifier, version, and signature state should be expected after bootstrap?

## Draft Escalation Message

Do not send this message in DESKTOP-10. It is prepared for review only.

```text
Subject: Hermes Desktop macOS artifact signature and bootstrap-app clarification

Hello Nous Research team,

I am validating the official Hermes Desktop macOS artifact from:

https://hermes-agent.nousresearch.com/desktop

The current macOS link I received was:

https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05

Local verification details:

- File: Hermes-Setup.dmg
- Size: 6752854 bytes
- SHA-256: b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5
- hdiutil verify: passed
- Mounted app: Hermes.app
- Bundle identifier: com.nousresearch.hermes.setup
- Bundle version: 0.0.1
- Executable: Hermes-Setup
- codesign display: Team ID T2F6S8MF7C, hardened runtime, stapled notarization ticket
- codesign --verify --deep --strict: fails with "invalid signature (code or signature have been modified)" for arm64
- spctl --assess --type execute: returns an internal Code Signing subsystem error

Can you clarify whether this DMG is intended to contain a bootstrap installer app rather than the final Desktop runtime, and whether the strict codesign failure is expected for the current macOS build?

I am also looking for the recommended trusted release channel for Hermes Desktop, including any published checksums, detached signatures, release notes, or GitHub release references. If a first-run bootstrap step creates a separate final app bundle, what bundle identifier, version, executable name, and code-signature state should be expected after bootstrap?

Finally, can Hermes Desktop be configured to use a localhost OpenAI-compatible endpoint without signing into Nous Portal, and is Desktop expected to share ~/.hermes with the Hermes CLI install?

Thanks.
```

## Required Stop Conditions

Stop before any of the following unless a later phase explicitly approves the exact bounded action:

- launch Desktop
- replace or delete `/Applications/Hermes.app`
- reinstall or recopy the app
- remove quarantine or other xattrs
- kill `Hermes-Setup`
- sign in
- add credentials
- grant permissions
- modify Hermes CLI config
- connect external services
- send the escalation message
