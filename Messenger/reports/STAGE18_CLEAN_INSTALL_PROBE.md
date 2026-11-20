# Stage 18 — Independent, genuinely compiled Android 4.4+ installation probe

**IMPORTANT: This APK IS NOT Messenger.** It contains no Meta code, login, backend access, chat UI, messages, accounts, or private data collection. It is solely a clean Android APK build/installer smoke test in response to repeated `App not installed` results for historic Messenger packages.

## Working engineering deliverable

New independently authored Android Gradle module: `Messenger/install-probe/`.

- Android application ID: `org.revibe.installprobe`
- `minSdkVersion=19` (Android 4.4), `targetSdkVersion=35`.
- No native libraries, so one APK does not require ARM32/ARM64/x86-specific APK variants.
- No permissions, no INTERNET, no Meta APK content or libraries.
- Uses Android platform Java/Activity APIs available on API19; `Build.SUPPORTED_ABIS` is called only if API >= 21.
- Displays locally: installation success, OS API, supported OS ABIs and clear disclaimer. No data sent anywhere.
- Built with Android Gradle Plugin 8.7.3, Gradle 8.9, Android SDK 35 in GitHub Actions.

## Verified evidence

GitHub Actions successful build: https://github.com/BlazeDevStudio/Revibe/actions/runs/44684505264

- Nine static source and manifest safety tests passed.
- Build `:app:assembleDebug` passed.
- Android SDK `apksigner verify --min-sdk-version 19` passed.
- Android SDK ZIP alignment check passed.
- Binary manifest reports SDK minimum 19 and target SDK 35.
- GitHub Actions artifact `Revibe-API19-Installation-Probe-NOT-MESSENGER` (id 14605522671).
- Downloaded ZIP CRC and extracted APK ZIP CRC passed in the engineering container.
- Extracted APK size 10,042 bytes; SHA-256 `3fd07a210318ae7f69541d5ae61ccb685ef2a4250ba4defdc02a3ced72122ec5`.
- Local `jarsigner -verify` reported `jar verified`; self-signed debug certificate is expected for a diagnostic APK.

**Emulator installation and launch PASSED on API19, API23 and API35.** CI: https://github.com/BlazeDevStudio/Revibe/actions/runs/44684869636 — all four jobs (build plus three emulator smoke runs) completed successfully. Each emulator ran `adb install`, `am start -W`, and process presence verification. These are virtual Android devices, not the user's Mi phone. Successful install/launch of the independent diagnostic does NOT demonstrate Messenger login, modern encryption, notifications or phone-wide compatibility.

Exact binary from the emulator-verified workflow artifact: **10,044 bytes**, SHA-256 `5945cd715fdf414639d140341b5073eca00d2d30fa1f591dcba80f10ae3947d5`. ZIP archive and APK CRC passed; Java JAR/v1 signature reported verified locally; Android SDK `apksigner` API19 and zipalign tests passed in CI.

## What a test means

If the probe installs on a spare phone, then an independent, low-permission Revibe app can be installed by that phone's package manager. This rules out a blanket prohibition on installing third-party APKs but DOES NOT identify exactly why old Meta binaries fail.

If the probe still fails with `App not installed`, the phone's app installer/download policy, storage or packaging rules need further investigation—without asking the user to run ADB or identify their phone model.

## Delivery and safeguards

The diagnostic APK may be shared separately in the current conversation for simple tap-to-install testing, **explicitly not as a revived Messenger**. GitHub public repository contains our own source and workflow, not Meta proprietary binaries, accounts, chat data, or signing keys.

Android 15 blocks installation of apps targeting SDK below 24 by default; targeting 35 avoids this particular restriction. See https://developer.android.com/about/versions/15/behavior-changes-all

## Next Messenger milestone

Develop and validate a genuinely installable, securely signed, API19+ independent messaging codebase. Real Messenger-to-Messenger interoperability requires an authorized supported Meta interface with encrypted messaging semantics. Historical Meta APK repackaging cannot itself guarantee server compatibility. **No working Revibe Messenger release exists yet.**
