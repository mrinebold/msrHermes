# Hermes Desktop Governed Install

Phase: 7A
Status: fail-closed; Desktop not launched or reinstalled

## Purpose

This document records the governed Hermes Desktop installation and validation decision for Phase 7A.

Phase 7A does not bypass Gatekeeper, remove quarantine, override invalid signatures, grant macOS privacy permissions, sign in, connect Google/Supabase/GitHub/Home Assistant/Helio/Agent Bus, use credentials, or launch Desktop when verification fails.

## Artifact

Official artifact path:

```text
/Users/michaelrinebold/Downloads/hermes-desktop-official/Hermes-Setup.dmg
```

SHA-256:

```text
b61e047efe3059faf1c55fec3252e661f2d2a993a7a3eebf5cc6a9aa5c1790f5
```

File size:

```text
6752854 bytes
```

`hdiutil verify` result:

```text
VALID
```

## Installed App

Installed app path:

```text
/Applications/Hermes.app
```

Installed app metadata:

```text
CFBundleIdentifier=com.nousresearch.hermes.setup
CFBundleName=Hermes
CFBundleShortVersionString=0.0.1
CFBundleVersion=0.0.1
CFBundleExecutable=Hermes-Setup
```

Installed app size:

```text
12M
```

Installed app strict codesign:

```text
failed: invalid signature (code or signature have been modified)
```

Installed app Gatekeeper assessment:

```text
failed: internal error in Code Signing subsystem
```

## Mounted Artifact App

Mounted app path:

```text
/private/tmp/hermes-phase7a-dmg/Hermes.app
```

Mounted app metadata:

```text
CFBundleIdentifier=com.nousresearch.hermes.setup
CFBundleName=Hermes
CFBundleShortVersionString=0.0.1
CFBundleVersion=0.0.1
CFBundleExecutable=Hermes-Setup
```

Mounted app size:

```text
12M
```

Mounted app strict codesign:

```text
failed: invalid signature (code or signature have been modified)
```

Mounted app Gatekeeper assessment:

```text
failed: internal error in Code Signing subsystem
```

## Decision

Desktop install/update decision:

```text
do not install or replace
```

Desktop launch decision:

```text
do not launch
```

Reason:

```text
The official artifact verifies as a DMG, but the contained app is the same setup/bootstrap bundle pattern already installed and fails strict codesign and Gatekeeper assessment. Phase 7A must not bypass Gatekeeper, remove quarantine, override signatures, or launch a failed app.
```

## Governance Status

- Gatekeeper bypass: none
- quarantine removal: none
- signature override: none
- privacy permissions granted: none
- Desktop launch: none
- Desktop sign-in: none
- credentials added: none
- integrations connected: none
- Desktop final state: installed setup/bootstrap app present, not running, fail-closed

## Next Step

Request official release-channel clarification from Nous Research or obtain a notarized Desktop artifact with a valid strict signature before any Desktop install, replacement, or launch retry.
