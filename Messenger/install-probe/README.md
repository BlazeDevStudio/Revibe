# Revibe native installation probe

**Not Messenger. Not a messenger clone.** This is a separate, tiny, independently authored Android APK used only to separate Android-package-install failures from issues caused by historic proprietary Meta APKs.

- Application ID: `org.revibe.installprobe` (never `com.facebook.orca`)
- Minimum Android API: **19** (KitKat 4.4)
- Target API: **35** (supports Android 15's minimum target-SDK install rule)
- Native dependencies: **none**; Android runtimes select platform Java/Dex automatically
- Permissions: **none** (no INTERNET, storage, contacts, logs, or accounts)
- On-device UI: a large-text installation success screen with Android API and supported OS ABIs shown locally. Never transmits information.
- No Facebook/Meta code or binary resources.

## Why this is useful

The Mi phone rejected multiple signed historical Messenger APKs, including an original ARM32 build and a modified ARM64 side-by-side build. The exact Android package-manager error remains unavailable. If an independent Android 4.4+ package installs, the operating system's general sideload pathway functions; failures in Meta APKs may involve incompatible manifest/signatures/ABI or OEM rules. **Installation of this probe does NOT prove anything about Messenger login, encryption, updates, or messaging.**

## Build (on GitHub Actions)

See `.github/workflows/revibe-install-probe.yml`. That workflow produces a signed **debug** APK, checks ZIP alignment, `apksigner` verification back to API19, and manifest API range, and uploads the APK as a workflow artifact. Debug keys are ephemeral per runner; reinstallations from other runs may require removal of this *diagnostic-only* app. Do not use it for messaging or collect user passwords.

Local building requires Android SDK 35 and Gradle 8.9:

```sh
cd Messenger/install-probe
gradle :app:assembleDebug
```

Do not publish this diagnostic APK as a working Revibe Messenger release. The broader Revibe Messenger application remains an unverified feasibility project.
