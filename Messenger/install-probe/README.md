# Revibe Install Check — Stage 19

**Not Messenger. Not a messaging client.** Independent Android app for a safe installation diagnostic, without ADB or a PC.

- Android 4.4+ (minSdk 19), targets Android 15/API35; no native libraries, so ARM32, ARM64, and x86 use the same APK.
- Own package ID `org.revibe.installcheck`, different from Stage18 (`org.revibe.installprobe`) to avoid an upgrade signing collision.
- Android 5+ users can voluntarily select an existing `com.facebook.orca` or `org.revibe.orca01` APK, and Android's official PackageInstaller handles the request.
- If the selected package is already installed, this app REFUSES to overwrite it. This protects existing accounts and app data.
- On Android 8+ installation-source permission requires explicit user approval in Settings; no security protections are bypassed.
- Only generic installer statuses are shown, e.g., conflict, invalid package, incompatible device, storage or blocked installation. No raw logs, credentials, chats, contacts, account identifiers, analytics or network access.
- Selected APK is temporarily copied to app-private cache (up to 250 MiB) and then deleted. No Meta binary is published in this GitHub repository.
- On Android 4.4 the tool only verifies that Revibe installs/opens and shows OS information; session-level installer diagnostics require Android 5+.

## Security
`REQUEST_INSTALL_PACKAGES` is declared solely for explicitly user-selected local diagnostics; the APK has **no INTERNET permission**. The status receiver is non-exported and uses an explicit mutable PendingIntent on newer Android. A successful install of this tool does not establish working Messenger login or encrypted messaging.

## Reproducible build
GitHub Actions workflow `.github/workflows/revibe-install-probe.yml` compiles, signs and verifies the APK, then tests launching on Android emulators. Source regression tests are in `tests/`.

## Important limitation
Meta's public Messenger Platform is based on Facebook Page access tokens. It does not establish consumer personal Messenger-to-Messenger chat interoperability for an unauthorized third-party client. This diagnostic is **not** a revived Messenger.