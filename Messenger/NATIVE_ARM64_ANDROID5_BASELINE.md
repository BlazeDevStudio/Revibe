# Native ARM64 Messenger baseline for Android 5/6

## Authenticated historical lead (NOT tested on a device)

APKMirror lists genuine Meta Messenger **336.0.0.13.142**, versionCode **297217556**, as a single APK for **arm64-v8a**, **nodpi**, **Android 5.0+ (API21)**. Advertised size: 60,954,119 bytes; target API 30.

Exact original archive page:
https://www.apkmirror.com/apk/facebook-2/messenger/messenger-336-0-0-13-142-release/facebook-messenger-text-and-video-chat-for-free-336-0-0-13-142-8-android-apk-download/

**We have not obtained this APK's bytes yet.** The archive listing is not proof of 2026 Meta server compatibility, installation, login, encrypted messaging or notifications.

### Why this matters

The earlier native ARM64 Messenger 588 requires Android 9 (minAPI28) and is not suitable for Android 5/6. The earlier Messenger 410 for API19 is ARMv7 and can only run on a 64-bit CPU if the phone's OS includes ARM32 support. Messenger 336 is a plausible *native ARM64* API21 baseline without falsifying a manifest.

### Verify the archive binary (once independently acquired)

Keep original proprietary APKs outside the public repository. Run:

    python Messenger/engineering/native_arm64_gate.py /path/to/Messenger336_ARM64_API21.apk --device-api 21 --device-abis arm64-v8a --verify-signature --verify-meta-cert

Repeat with `--device-api 23` for Android 6. The checker requires Python 3, existing `apk_static_audit.py`, Java `jarsigner` for signature integrity and optional `cryptography` for original Meta signer identity. Published Meta SHA256 certificate fingerprint: `e3f9e1e0cf99d0e56a055ba65e241b3399f7cea524326b0cdd6ec1327ed0fdc1`.

A passing static gate is NOT a working Messenger restoration. Never mistake hiding an update message for restoring server support. Use a disposable authorized test device with no private account data; investigate observed login and E2EE errors before patching.

### Next engineering milestone

Acquire the authentic API21 ARM64 APK, verify its manifest/ABI and signing identity, then compare code structure with versions 410/588. Test installation and launch on real Android 5/6 hardware before changing code. Do not commit Meta binaries.