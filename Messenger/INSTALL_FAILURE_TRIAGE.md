# Revibe Messenger — installation failure triage

## Field report (2026-11-20)
The user tried supplied Revibe APKs and Android displayed 'App not installed'. Exact candidate, OS API, supported ABIs, and package-manager failure code are unknown. This is an actual field report of failed installation, but not a confirmed diagnosis. Offline ZIP and signature checks do NOT establish on-device installability.

## Candidate differences
- Modified Messenger 410 ARMv7: API19 min, armeabi-v7a only, changed signing certificate, package com.facebook.orca.
- Modified Messenger 588 ARM64: API28 min (Android 9), unsuitable for Android 5/6, changed signing certificate, same package.
- Original Meta-signed Messenger 336 ARM64: API21 min (Android 5), native arm64-v8a. Use as the first controlled comparison, but its login and modern encryption are unverified.

## Read-only checks on an authorized spare device
adb shell getprop ro.build.version.sdk
adb shell getprop ro.product.cpu.abilist
adb shell pm path com.facebook.orca

If there is no installed Messenger package, record the exact result of:
adb install /path/to/original-Messenger336-ARM64-API21.apk

Do not uninstall, downgrade or overwrite an existing official app containing important data just to test. Save only the INSTALL_FAILED_* code; do not collect messages, credentials or device identifiers.

Common outcomes: INSTALL_FAILED_UPDATE_INCOMPATIBLE (signer mismatch); INSTALL_FAILED_VERSION_DOWNGRADE (newer app present); INSTALL_FAILED_NO_MATCHING_ABIS (ABI mismatch); INSTALL_FAILED_OLDER_SDK (Android too old); INSTALL_FAILED_INSUFFICIENT_STORAGE (space); INSTALL_PARSE_FAILED_NO_CERTIFICATES or INSTALL_FAILED_INVALID_APK (packaging/signature). INSTALL_FAILED_ALREADY_EXISTS means the package is already installed.

Priority: diagnose the exact package-manager rejection BEFORE any new APK patch, update text suppression, authentication claims or rollout to charity recipients.
