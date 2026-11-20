# Installation failure: Android 5/6 ARM64

**Field report, 2026-11-20:** The user's Android installer displayed **“App not installed”** for supplied research APKs. No package-manager error code was recorded. This is a real hardware failure report; the cause is **unconfirmed**.

## Do not confuse packages
- Revibe Messenger 410 ARMv7 uses a *different signer* from Meta, retains `com.facebook.orca` and works only if the OS supports 32-bit ARM. A signature collision with installed Messenger is possible.
- Revibe Messenger 588 ARM64 requires Android 9/API28, and will not install on Android 5/6.
- **Original Meta-signed Messenger 336 ARM64/API21** is the correct first installation diagnostic for Android 5/6 ARM64. Its SHA-256 is `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`. It is NOT a revived Messenger client.

## Safely identify the package-manager failure

Use a computer with Android platform-tools (ADB) and Python 3, and an authorized spare Android 5/6 phone with USB debugging enabled. Keep real accounts and personal chats off test devices. Do not uninstall an existing Messenger installation merely for this test.

From the Revibe repository root:

```bash
python Messenger/engineering/install_failure_probe.py
```

This first command is **read-only**. It checks Android API level, the availability of the ARM64 runtime, and whether Messenger is already installed. It never prints a serial number or reads accounts.

If there is NO installed Messenger and you have a separate original Meta-signed Messenger 336 APK:

```bash
python Messenger/engineering/install_failure_probe.py --apk "/path/to/Messenger336-arm64.apk" --install --ack-test-device --output install_result.json
```

The tool refuses to install a wrong-hash APK, refuses to overwrite an existing `com.facebook.orca`, and avoids gathering logcat, message text, or credentials. Only generic installation status is recorded.

### Typical diagnosis by code

| Package manager result | Meaning |
|---|---|
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Existing `com.facebook.orca` signed by a different key |
| `INSTALL_FAILED_VERSION_DOWNGRADE` | Older APK collides with a newer installation |
| `INSTALL_FAILED_NO_MATCHING_ABIS` | Device lacks needed ABI support |
| `INSTALL_FAILED_OLDER_SDK` | APK requires a newer OS |
| `INSTALL_FAILED_INSUFFICIENT_STORAGE` | Storage unavailable |
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | Signature/package parsing problem |
| `INSTALL_FAILED_INVALID_APK` | Malformed or rejected APK |
| `UNCLASSIFIED_INSTALL_FAILURE` | ADB did not expose a recognized error code |

**Do not** force an update, downgrade, or uninstall with personal data present. For a standalone “App not installed” message on the handset, the next step is to capture the precise `INSTALL_FAILED_*` code through ADB. A screenshot of the generic message does not identify the cause.

## After installation

An install and visible launch do not establish Meta server authorization, default end-to-end encryption compatibility, notifications or actual message delivery. Debug those separately and do not distribute experimental packages as working Messenger.

## Xiaomi / Mi hardware field screenshot (2026-11-20)

A user-supplied Mi-device screenshot shows the Android package installer saying **“App not installed”** beside Messenger's icon and name. It contains **no Android package-manager error code**, version number, APK checksum or installed-package state. This observation cannot distinguish signer collision, downgrade, ABI mismatch, SDK restriction, storage exhaustion, source policy or archive invalidity.

Xiaomi-specific checks, without removing application data:

1. Open Settings → Apps / Manage apps and search for Messenger; check whether an original app or clone exists. Xiaomi supports **Dual apps** and sometimes **Second space**: https://www.mi.com/global/support/article/KA-12531/. Clearing Dual apps can delete clone data, so **do not reset Dual apps or uninstall apps simply to test**.
2. Under Settings → About phone, record the Android version and MIUI version (not IMEI or serial number). For the Messenger336 ARM64 baseline, Android API21+ and `arm64-v8a` OS ABI support are mandatory.
3. On a computer with platform-tools and an authorized spare phone, run `adb shell getprop ro.build.version.sdk`, `adb shell getprop ro.product.cpu.abilist`, and `adb shell pm list packages com.facebook.orca`. Then use the repository's safe installer probe with the exact pinned original Meta-signed 336 APK to obtain only the `INSTALL_FAILED_*` category.
4. Do not disable Xiaomi security controls, force downgrades, or delete cloned/second-space data to make the APK appear installable. Capture the true error first.

**Status:** first-hand UI failure confirmed on an unspecified Mi phone; root cause and underlying package not confirmed. No new Messenger client fix or on-device install success is demonstrated by this screenshot.
