# Hermes Desktop Support Clarification Package

Phase: DESKTOP-12
Date: 2026-06-08
Status: prepared only; not sent

## Summary

We are validating the official Hermes Desktop macOS artifact from the Nous Research Desktop page before any further install, launch, replacement, sign-in, permission grant, or external-service connection.

The official DMG verifies as a disk image, but the app bundle inside the verified artifact appears to be a setup/bootstrap bundle:

- bundle identifier: `com.nousresearch.hermes.setup`
- version: `0.0.1`
- executable: `Hermes-Setup`

Both the mounted official artifact app and the existing `/Applications/Hermes.app` show the same setup/bootstrap metadata and the same fail-closed signing pattern:

- strict `codesign --verify --deep --strict` fails with `invalid signature`
- `spctl` returns an internal Code Signing subsystem error

We need clarification on whether this is expected release behavior, whether there is a second final Desktop app created by bootstrap, and what trusted macOS Desktop release channel/checksum/signing path should be used.

## Local Environment

| Field | Value |
| --- | --- |
| macOS | `26.5.1` |
| macOS build | `25F80` |
| Architecture | `arm64` |
| Hermes CLI | `Hermes Agent v0.15.2 (2026.5.29.2)` |
| Hermes CLI project path | `/Users/michaelrinebold/.hermes/hermes-agent` |
| Python used by Hermes CLI | `3.11.14` |

Hermes CLI and the local model adapter path are working and should remain untouched while Desktop artifact integrity is clarified.

## Artifact Details

| Field | Value |
| --- | --- |
| Official Desktop page | `https://hermes-agent.nousresearch.com/desktop` |
| Download URL used | `https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05` |
| Local artifact path | `/Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg` |
| File size | `6752854` bytes |
| SHA-256 | `b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5` |
| `hdiutil verify` | passed; final CRC32 `$9DB5F445` |
| Mounted app path during verification | `/private/tmp/hermes-desktop-official-mount/Hermes.app` |
| Mounted bundle identifier | `com.nousresearch.hermes.setup` |
| Mounted bundle version | `0.0.1` |
| Mounted executable | `Hermes-Setup` |
| Mounted strict codesign | failed: `invalid signature (code or signature have been modified)` for `arm64` |
| Mounted `spctl --assess --type execute` | internal Code Signing subsystem error |
| Installed app comparison | `/Applications/Hermes.app` matches the setup/bootstrap metadata and signing failure pattern |

## Verification Evidence

### SHA-256

```text
b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5  /Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg
```

### File Size

```text
6752854 bytes
```

### `hdiutil verify`

```text
verified   CRC32 $9DB5F445
hdiutil: verify: checksum of "/Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg" is VALID
```

### Info.plist Metadata

From `/Applications/Hermes.app/Contents/Info.plist`, matching the mounted official artifact metadata captured during DESKTOP-9:

```text
CFBundleName = Hermes
CFBundleIdentifier = com.nousresearch.hermes.setup
CFBundleVersion = 0.0.1
CFBundleShortVersionString = 0.0.1
CFBundleExecutable = Hermes-Setup
CFBundlePackageType = APPL
LSMinimumSystemVersion = 11.0
```

### `codesign --display --verbose=4 /Applications/Hermes.app`

```text
Executable=/Applications/Hermes.app/Contents/MacOS/Hermes-Setup
Identifier=com.nousresearch.hermes.setup
Format=app bundle with Mach-O thin (arm64)
Authority=(unavailable)
Notarization Ticket=stapled
TeamIdentifier=T2F6S8MF7C
Runtime Version=15.5.0
Info.plist=not bound
```

### `codesign --verify --deep --strict --verbose=4 /Applications/Hermes.app`

```text
/Applications/Hermes.app: invalid signature (code or signature have been modified)
In architecture: arm64
```

### `spctl --assess --type execute --verbose=4 /Applications/Hermes.app`

```text
/Applications/Hermes.app: internal error in Code Signing subsystem
```

### Extended Attributes

```text
com.apple.macl:
com.apple.provenance:
```

No `com.apple.quarantine` marker was observed in the inspected installed app or downloaded artifact.

## Exact Questions For Nous Research

1. Is `Hermes-Setup.dmg` intended to contain only a setup/bootstrap app that installs or creates a second final Hermes Desktop app?
2. Is bundle identifier `com.nousresearch.hermes.setup` expected for the current macOS Desktop artifact?
3. Is version `0.0.1` expected for the Desktop app inside the current macOS artifact?
4. Is executable name `Hermes-Setup` expected for the installed/runnable Desktop app?
5. Is strict `codesign --verify --deep --strict` failure expected for this artifact on current macOS on Apple Silicon?
6. Is the `spctl` internal Code Signing subsystem error expected or known for this build?
7. Is there a notarized macOS Desktop artifact whose app bundle passes strict code-signature verification and Gatekeeper assessment?
8. Does Nous Research publish a SHA-256 checksum, detached signature, release note, or signing metadata for Hermes Desktop macOS artifacts?
9. Is there a stable release channel or GitHub release source for Hermes Desktop separate from the live Desktop page download?
10. If a first-run bootstrap step creates a final app bundle, what path, bundle identifier, version, executable name, and code-signature state should be expected afterward?
11. Should Hermes Desktop share `~/.hermes` with the Hermes CLI install?
12. Can Hermes Desktop be configured to use a localhost OpenAI-compatible endpoint without Nous Portal sign-in?

## Attachable Evidence List

Attach or paste these items if a support channel requests evidence:

- SHA-256 output for `Hermes-Setup.dmg`
- file size output for `Hermes-Setup.dmg`
- `hdiutil verify /Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg`
- `hdiutil imageinfo /Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg`
- mounted app `Info.plist` metadata
- installed app `Info.plist` metadata
- `codesign --display --verbose=4 /Applications/Hermes.app`
- `codesign --verify --deep --strict --verbose=4 /Applications/Hermes.app`
- `spctl --assess --type execute --verbose=4 /Applications/Hermes.app`
- mounted official artifact app comparison table from `docs/HERMES_DESKTOP_ARTIFACT_ESCALATION.md`

Do not attach credentials, Hermes CLI config, local `.env` files, logs containing secrets, or screenshots that expose private workspace data.

## Draft GitHub Issue

Do not send in DESKTOP-12.

```text
Title: macOS Hermes-Setup.dmg contains setup bundle with strict codesign failure on Apple Silicon

I am validating the official Hermes Desktop macOS artifact from:
https://hermes-agent.nousresearch.com/desktop

Download URL used:
https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05

Environment:
- macOS 26.5.1 build 25F80
- Apple Silicon / arm64
- Hermes CLI v0.15.2 (2026.5.29.2)

Artifact:
- File: Hermes-Setup.dmg
- Size: 6752854 bytes
- SHA-256: b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5
- hdiutil verify: passed

Mounted app metadata:
- Bundle identifier: com.nousresearch.hermes.setup
- Version: 0.0.1
- Executable: Hermes-Setup
- Team ID shown by codesign: T2F6S8MF7C
- Notarization ticket: stapled

Issue:
codesign --verify --deep --strict fails with:
"/Applications/Hermes.app: invalid signature (code or signature have been modified)"
"In architecture: arm64"

spctl --assess --type execute returns:
"/Applications/Hermes.app: internal error in Code Signing subsystem"

Can you clarify whether Hermes-Setup.dmg is intended to be a bootstrap installer that creates a second final Desktop app, whether com.nousresearch.hermes.setup version 0.0.1 is expected, and whether this strict codesign/spctl behavior is expected for the current macOS build?

I am also looking for the trusted Desktop release channel, published checksum/signature if available, expected final app bundle metadata, whether Desktop should share ~/.hermes with CLI, and whether Desktop can use a localhost OpenAI-compatible endpoint without Nous Portal sign-in.
```

## Draft Email

Do not send in DESKTOP-12.

```text
Subject: Hermes Desktop macOS artifact signature and release-channel clarification

Hello Nous Research team,

I am validating Hermes Desktop for macOS from the official Desktop page before launching or replacing anything locally.

The current macOS artifact I downloaded was:
https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05

Local environment:
- macOS 26.5.1 build 25F80
- Apple Silicon / arm64
- Hermes CLI v0.15.2 (2026.5.29.2)

Artifact details:
- Size: 6752854 bytes
- SHA-256: b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5
- hdiutil verify: passed
- App bundle: com.nousresearch.hermes.setup
- Version: 0.0.1
- Executable: Hermes-Setup

The app displays Team ID T2F6S8MF7C and a stapled notarization ticket, but strict codesign verification fails with "invalid signature (code or signature have been modified)" for arm64, and spctl returns an internal Code Signing subsystem error.

Can you clarify whether Hermes-Setup.dmg is intended to be a bootstrap installer that creates a second final Desktop app, whether the com.nousresearch.hermes.setup / 0.0.1 / Hermes-Setup metadata is expected, and whether this codesign/spctl behavior is known or expected?

I would also appreciate guidance on the trusted macOS Desktop release channel, any published checksums or detached signatures, the expected final app bundle metadata after bootstrap if applicable, whether Desktop should share ~/.hermes with the CLI, and whether Desktop can use a localhost OpenAI-compatible endpoint without Nous Portal sign-in.

Thanks.
```

## Draft Discord / Forum / Support Channel Message

Do not send in DESKTOP-12.

```text
I am validating the official Hermes Desktop macOS artifact before launching/replacing anything.

Source page: https://hermes-agent.nousresearch.com/desktop
Download URL: https://hermes-assets.nousresearch.com/Hermes-Setup.dmg?build=44c0c2d4ac05
macOS: 26.5.1 build 25F80, arm64
DMG SHA-256: b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5
hdiutil verify: passed

The app inside appears to be:
com.nousresearch.hermes.setup
version 0.0.1
executable Hermes-Setup

codesign display shows Team ID T2F6S8MF7C and a stapled notarization ticket, but strict codesign verify fails with "invalid signature (code or signature have been modified)" for arm64. spctl returns an internal Code Signing subsystem error.

Is this DMG expected to be a bootstrap installer that creates a second final Desktop app? Is this bundle metadata and strict codesign/spctl behavior expected? Is there a notarized/signature-clean macOS Desktop artifact, checksum/signature, or stable release channel? Also, should Desktop share ~/.hermes with CLI, and can it use a localhost OpenAI-compatible endpoint without portal sign-in?
```

## Current Decision

Hermes Desktop remains fail-closed until Nous Research clarifies the release channel, expected bootstrap behavior, and expected signature/Gatekeeper state, or until a separately approved local static-inspection phase confirms a trusted install path.
