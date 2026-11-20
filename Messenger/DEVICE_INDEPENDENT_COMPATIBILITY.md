# Revibe Messenger — device-independent compatibility contract

## User requirement (2026-11-20)

Build a **one-tap-installable application** usable from **Android 4.4 KitKat (API 19) upward** across supported Android phone generations, without requiring the end user to know their phone model, OS ABI, or run ADB. A single universal APK is the preferred deliverable. If its size or platform limitations make that impractical, use automatically selected verified ABI-specific variants without making the user diagnose architectures.

This is a **product target, NOT completed compatibility**.

## Platform rules

- Establish `minSdkVersion=19` only for a codebase actually using APIs available on API19, with guarded higher-API calls. Do **not** lower an Android 9 APK's manifest and call it a port.
- Target Android 4.4 through current supported releases, with acceptance tests at every major platform generation. Platform forward-compatibility is not guaranteed by minSdk alone.
- Include complete native libraries for `armeabi-v7a`, `arm64-v8a`, and `x86` when using a universal APK, and optionally `x86_64` for completeness. Never mix native libraries from unrelated proprietary Messenger releases into one unsigned/re-signed archive and claim interoperability.
- Ensure the package remains consistent for installation/updates: unique app ID if independent, consistent **owned** release signing key, valid v1 signatures for KitKat and appropriate modern APK signatures, permissions, manifest authorities, resources and ZIP/native alignment.
- Validate Android background restrictions, notification permissions, package install rules, scoped storage, transport/TLS, and native memory page-size constraints where applicable.
- **Every test dimension has separate evidence:** archive validity, actual device installation, UI launch, authentication, encrypted send/receive, notifications, reconnection and accessibility. Never claim success from static tests alone.
- For real Meta-to-Meta messaging, confirm server and E2EE interoperability. Historical Meta APK repackaging, a UI mock, browser wrapper, relabeled original or hidden update prompt is not a complete restoration.
- Respect user preference: no requesting individual phone model, Android properties, ADB or complex installation steps as an ordinary prerequisite. Use generic compatibility lab/emulator/device matrix, platform-specific CI, and reproducible test artifacts instead; do not invent run results when no lab is available.
- Test packages with narrow hypotheses. Stop repeated variations that lack demonstrated repair, and do not offer another APK as 'fixed' solely because it passes offline signing checks.

## Acceptance matrix

Minimum gates to claim *any* Android release: valid signing + OS/ABI installation + visible UI launch on a representative device. To claim *Messenger restoration*: actual authorized login + modern end-to-end encrypted send AND receive + background notifications + reconnect + accessibility, on each declared supported platform. Mark unsupported or unverified targets explicitly.

## Current evidence

Multiple source and repackaged Messenger APKs have been rejected with "App not installed" on one Mi phone. Timing differences do not reveal the cause. The available Android 4.4 ARM32/Android 5 ARM64 original Meta APKs are historical baselines, **not finished Revibe releases**. No real server interoperability, no universal signed build, and no cross-version hardware test are demonstrated.
