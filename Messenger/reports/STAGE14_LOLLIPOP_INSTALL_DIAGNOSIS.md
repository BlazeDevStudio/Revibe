# Revibe Messenger Stage 14 — Lollipop 64-bit install blocker

**Release status:** NOT READY. The Android 5/6 user reported a generic **App not installed** error. No ADB failure code was supplied; no Android 5 test device was connected during this stage.

## Original APK, independently reverified

The original Messenger 336.0.0.13.142 ARM64/API21 binary and Stage 13 test copy have identical SHA256: `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`.
The binary manifest declares `minSdkVersion=21`, `targetSdkVersion=30`, native `arm64-v8a`, and a requirement for OpenGL ES 2.0. Camera, telephony, NFC and location are *not* required features. All 18 native libraries belong to ARM64. ZIP integrity, original Meta signer identity and JAR/v1 signature verification passed offline.

**These checks are not proof of on-device installability or Messenger server compatibility.**

## Actual code fix

Prior to Stage 14, `install_failure_probe.py` attempted to detect an installed `com.facebook.orca` using `adb shell pm path`. Some older Android package managers exit nonzero when an app is absent, so that call could report an inconclusive state and prevent the opt-in test install.

Stage 14 uses filtered `adb shell pm list packages com.facebook.orca`, parses exact package names and distinguishes:
- **present** — exact package found;
- **absent** — valid successful command with no matching package;
- **unknown** — shell, permission or package-manager error.

No full package list or private data is saved. Existing installations are still protected from overwrite. Unit tests cover empty, exact, substring and erroneous output, plus the integration case.

## Real hardware test (only on a spare phone)

Read-only probe from a clone of Revibe:
```sh
python Messenger/engineering/install_failure_probe.py
```

Optional installation on a spare Android 5/5.1 ARM64 device with no preexisting Messenger package, using **the unchanged original Meta-signed APK**:
```sh
python Messenger/engineering/install_failure_probe.py --apk '/path/to/original-messenger336-arm64.apk' --install --ack-test-device --output install_result.json
```

The script refuses an unexpected APK SHA256, a missing ARM64 runtime, or a preexisting Messenger installation. It outputs only the error category, such as `INSTALL_FAILED_UPDATE_INCOMPATIBLE`, `INSTALL_FAILED_NO_MATCHING_ABIS`, or `INSTALL_PARSE_FAILED_NO_CERTIFICATES`. **Do not uninstall existing apps with valuable data or enter private accounts for this test.**

## Remaining gates
1. Confirm exact `INSTALL_FAILED_*` or `INSTALL_PARSE_FAILED_*` result from the phone; diagnose and repair the *observed* cause.
2. Confirm actual launch on Android 5/6 hardware.
3. Determine whether Meta will authenticate an original old client. Only then investigate update prompt, mandatory version policies, and modern encrypted messaging.
4. Never advertise a re-signed or merely renamed original APK as a working restored Messenger. Do not publish proprietary Meta binaries or keys on GitHub.
