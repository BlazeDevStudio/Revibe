# Stage 20 — On-emulator install-callback verification and simpler error sharing

**This remains an independent diagnostic app, NOT a Messenger client.** It does not log into Facebook, send or decrypt messages, or implement a Meta-compatible protocol.

## Changes compared with Stage 19

- Stage 19's install-check app had only compilation and launch evidence. Stage 20 introduces an Android **instrumentation runner** which executes in actual API21+ emulator app context and invokes the same `InstallResultReceiver` with deliberately synthesized installation callbacks.
- The regression runner checks incompatible, signature conflict, blocked, insufficient storage, pending-user-action-without-intent, and success categories. It confirms a literal `INSTALL_FAILED_NO_MATCHING_ABIS` code is preserved while secret-looking text and paths are not saved or exposed. It verifies the diagnostic has no INTERNET permission.
- The app now has a **Copy result** button that only copies the locally stored *sanitized error category*. No file paths, account credentials or message text are copied.
- The Android application ID changed from `org.revibe.installcheck` to **`org.revibe.installcheck2`** to avoid an immediate signature collision with the Stage 19 debug-signed APK on a phone. Stage 19 uses GitHub's ephemeral debug signer; Stage 20 is not an in-place upgrade. A future production release must use an owned, stable, securely stored signing key; do not publish that private key.
- The GitHub workflow builds both normal and androidTest APKs, runs the diagnostics on emulators Android 5.0/API21, Android 6/API23 and Android 15/API35, and preserves basic app install/launch testing for Android 4.4/API19.

## Acceptance evidence and limitations

A successful instrumentation job establishes that the receiver and its sanitizer handle simulated callbacks on the specified Android emulator. It **does not** prove the Android file picker, package installer approval UI or final failure code from an actual historical Messenger APK on the user's Mi phone.

The full path (file picker → user-selected file → session → user-approved installation → callback) remains separate, unverified acceptance testing. App install/launch plus callback fixture tests cannot be presented as working Messenger.

## User workflow

Install this **diagnostic-only** APK by tapping the download. On Android 5+, tap **Choose an APK to test**, select a previously downloaded Messenger test APK, and approve Android's dialog if presented. The result appears on screen; tap **Copy result** to share just the safe error category. Android 4.4 supports basic install/launch but not API21 PackageInstaller session callbacks. No computer, ADB or device-model identification is requested.

Do not reset existing Messenger profiles, uninstall real chat apps, give account passwords, or bypass Android's installation authorization.

## Remaining product blocker

The primary Revibe goal is functional personal Meta Messenger interoperability from Android 4.4 upward. That is not established by the public Facebook Page messaging API or historical Meta APKs; availability of a supported user-facing API plus modern authentication, encrypted send/receive, reconnect and notifications must be independently verified. No finished Revibe Messenger release exists.
