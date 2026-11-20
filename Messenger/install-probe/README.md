# Revibe Install Check — Stage 20

**Not Messenger. Not a messaging client.** Independent Android app for a safe installation diagnostic, without ADB or a PC.

- Android 4.4+ (minSdk 19), targets Android 15/API35; no native libraries, so ARM32, ARM64, and x86 use the same APK.
- Own Stage 20 package ID `org.revibe.installcheck2`, separate from Stage 19 (`org.revibe.installcheck`) and Stage 18 (`org.revibe.installprobe`) so their ephemeral debug signatures do not cause an upgrade conflict.
- Android 5+ users can voluntarily select an existing `com.facebook.orca` or `org.revibe.orca01` APK, and Android's official PackageInstaller handles the request.
- If the selected package is already installed, this app REFUSES to overwrite it. This protects existing accounts and app data.
- On Android 8+ installation-source permission requires explicit user approval in Settings; no security protections are bypassed.
- Only generic installer statuses are shown, e.g., conflict, invalid package, incompatible device, storage or blocked installation. **Copy result** copies only that locally stored sanitized category for easy sharing. No raw logs, credentials, chats, contacts, account identifiers, analytics or network access.
- Selected APK is temporarily copied to app-private cache (up to 250 MiB) and then deleted. No Meta binary is published in this GitHub repository.
- On Android 4.4 the tool only verifies that Revibe installs/opens and shows OS information; session-level installer diagnostics require Android 5+.

## Security
`REQUEST_INSTALL_PACKAGES` is declared solely for explicitly user-selected local diagnostics; the APK has **no INTERNET permission**. The status receiver is non-exported and uses an explicit mutable PendingIntent on newer Android. A successful install of this tool does not establish working Messenger login or encrypted messaging.

## Reproducible build
GitHub Actions workflow `.github/workflows/revibe-install-probe.yml` compiles, signs and verifies the APK, then tests launching on Android emulators. Source regression tests are in `tests/`. Stage 20 adds a native Android instrumentation runner `InstallCallbackInstrumentation` which exercises the result receiver with synthetic statuses on API21+ emulators; it does not install an actual third-party APK or test the file-picker UI.

## Important limitation
Meta's public Messenger Platform is based on Facebook Page access tokens. It does not establish consumer personal Messenger-to-Messenger chat interoperability for an unauthorized third-party client. This diagnostic is **not** a revived Messenger.
## Build identity and installation limitations
Stage 20 uses a new app ID because GitHub Actions debug keys are temporary. For a long-term updatable Revibe release, provision a stable private signing key as a protected secret; never commit it to a public Git repository. The emulator receiver tests do **not** verify user-selection and approval through an actual phone installer. The real Mi installation failure remains undiagnosed, and this utility is not a working Messenger.


## Stage 20 verification safeguard
An APK's package name by itself is **not** proof of its provenance. The Stage 20 file picker now computes a SHA-256 digest while copying the selected APK and permits the installation diagnostic only if both the package name AND SHA-256 match an independently audited artifact: original Messenger 336 ARM64, original Messenger 410 ARM32, the Stage 6 ARM32 research version, or the Stage 15 separated-package ARM64 research version. Any other APK is rejected **before** an installation session is created. The hashes are not secrets, and no file data or paths are uploaded. This cannot guarantee modern Messenger messaging and does not fix an incompatible OS.
