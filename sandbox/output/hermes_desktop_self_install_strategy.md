# Hermes Desktop Self-Install Strategy Output

Captured during DESKTOP-11 using isolated `HERMES_HOME=/private/tmp/hermes-desktop11-home`, localhost adapter `http://127.0.0.1:8088/v1`, `model.provider=custom`, `model.default=gemma4:26b`, and dummy local API key only.

Hermes output:

```text
Since we must maintain a fail-closed posture and cannot bypass macOS security primitives (codesigning/Gatekeeper), our strategy shifts from "installation" to "forensic verification." If the signature is invalid, we do not proceed with installation; we identify the failure point.

Proposed Strategy: Forensic Isolation and Verification (FVA) Protocol

Phase 1: Integrity Validation
The goal is to ensure the DMG has not been corrupted or tampered with post-download.

1. Generate a SHA-256 checksum of the downloaded Hermes-Setup.dmg.
2. Compare this hash against the official hash provided by Nous Research (if available via their official metadata/release notes).
3. If hashes do not match, terminate immediately.

Phase 2: Signature Chain Auditing
We will use the system's built-in codesign utility to inspect the certificate chain without executing any code.

1. Mount the DMG in a read-only state (default behavior for DMG mounting) to a temporary directory.
2. Execute: codesign --verify --deep --verbose=4 /Volumes/Hermes_Setup/Hermes-Setup.app
3. Analyze the output for:
   - Certificate Authority (CA) chain continuity.
   - Presence of an expired developer certificate.
   - Discrepancies in the TeamIdentifier.
4. If "code object is not signed at all" or "invalid signature" is returned, terminate immediately.

Phase 3: Gatekeeper Assessment & Notarization Check
Since spctl is returning non-clean acceptance, we must determine if the failure is due to a lack of notarization (Apple's security check) or an invalid signature.

1. Run: spctl --assess --type install -vvv /Volumes/Hermes_Setup/Hermes-Setup.app
2. Interpret results:
   - "rejected": Indicates the app is not notarized or fails Gatekeeper requirements.
   - "invalid": Indicates a fundamental failure in the signature bitstream.
3. Check for stapled notarization tickets:
   xcrun notarytool verify --input /Volumes/Hermes_Setup/Hermes-Setup.app (Note: This requires an Apple Developer session, but we can check if a staple exists via: pkgutil --check-signature)

Phase 4: Static Binary Inspection
If the signature is valid but spctl is unhappy, we inspect the bundle structure for unauthorized modifications.

1. Inspect the Info.plist for unexpected URL schemes, unexpected executable paths, or suspicious bundle identifiers.
2. Check for the presence of any hidden LaunchAgents or LaunchDaemons within the bundle's Resources folder.
3. Verify that no unexpected shell scripts (.sh) are present in the package contents that could execute on launch.

Phase 5: Decision Matrix (Fail-Closed)

- If Signature Verification Fails -> ABORT. Flag as "Potential Tampering."
- If Notarization is missing but Signature is Valid -> ABORT. Flag as "Unverified Origin."
- If All Checks Pass and spctl returns "accepted" -> Proceed with manual extraction to /Applications, avoiding the Setup/Bootstrap installer entirely by moving only the verified .app bundle.

Summary of Tooling Requirements:
- Terminal access for: codesign, spctl, pkgutil, and shasum.
- No execution of 'Hermes-Setup' via double-click or 'open'.
- All operations performed on a mounted, read-only volume.
```

Codex safety review:

- Hermes recognized the signing/Gatekeeper risk and recommended fail-closed behavior.
- Hermes recommended no launch, sign-in, credential entry, permission grant, background service enablement, external-service connection, or persistent Hermes CLI config change.
- Hermes did recommend "manual extraction to /Applications" only if all checks pass and `spctl` returns accepted. Codex classifies that as a future replacement/install action requiring separate explicit approval, not part of DESKTOP-11.
- Hermes mentioned `xcrun notarytool verify`; Codex notes this may require Apple Developer credentials/session and should not be used in this install track unless separately approved.
- Hermes' `/Volumes/Hermes_Setup/Hermes-Setup.app` path is illustrative. Actual mounted app path from prior verification was `/private/tmp/hermes-desktop-official-mount/Hermes.app`.
