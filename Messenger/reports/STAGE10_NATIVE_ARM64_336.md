# Stage 10 — genuine Android 5 ARM64 Messenger 336 acquired and verified

## Verified source and reproducible static check

The user supplied an unmodified historical Messenger 336 Android APK. **Never publish the APK or its proprietary libraries in this public repository.**

- Original filename: `com.facebook.orca_336.0.0.13.142-297217556_minAPI21(arm64-v8a)(nodpi)_apkmirror.com.apk`
- SHA-256: `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`
- Size: 60,954,119 bytes; ZIP entries: 14,874
- Manifest: `com.facebook.orca`, version `336.0.0.13.142`, versionCode `297217556`; **minimum Android API21**, target API30.
- Native libraries: **18** in `lib/arm64-v8a/`, with ELF 64-bit headers; no other native ABIs were found.
- Readable `classes*.dex`: **8**, total `72,979` class definitions. Compare with Messenger 410 x86 (8, 79,344 class definitions) and Messenger 588 arm64 (18, 171,774). These are static counts, not portable source-code metrics.
- APK CRC passed. `jarsigner -verify` passed, and its v1 signing certificate SHA-256 matches the known original Meta signing certificate. Full Android SDK `apksigner` verification was **not** available.
- `native_arm64_gate.py` returned `static_platform_gate_passed=true` for Android 5/API21 with `arm64-v8a`; repeat with `--device-api 23` for Android 6.

## Engineering decision

**Test the original Meta-signed package first.** It is a genuine native ARM64 Android 5/6 candidate. Changing strings or re-signing the APK would add signing identity issues without restoring current server communication. Android 4.4 ARMv7 uses the separate Messenger 410 baseline; do not say this ARM64/API21 file runs on KitKat.

The DEX content contains `e2ee` and `endtoend` references but absence of `labyrinth` strings in the inspected DEX, unlike newer variants. This is a static clue only: it does not establish encryption capability or absence of another implementation.

## Reproduce

```sh
python Messenger/engineering/native_arm64_gate.py /path/to/original336.apk --device-api 21 --device-abis arm64-v8a --verify-signature --verify-meta-cert
python Messenger/engineering/original_arm64_smoke.py --apk /path/to/original336.apk --output /tmp/preflight.json
# On an authorized disposable Android 5/6 phone with ADB:
python Messenger/engineering/original_arm64_smoke.py --apk /path/to/original336.apk --install --ack-test-device --launch --output /tmp/smoke.json
```

The ADB runner refuses to replace existing Messenger, records only selected categories, and collects **no device identifiers, credentials, logcat, messages, or screenshots**. It does not test login or encrypted messages. Observe update/deprecation screens manually and use only non-sensitive observations. Never expose personal accounts on abandoned old Android security stacks.

## Unverified / required next steps

1. Install and launch on a real Android 5 or 6 64-bit test phone; report only redacted failure categories.
2. Check client-side version banner vs server rejection; identify exact failure without assuming message-prompt suppression solves it.
3. Verify an authorized synthetic test account can log in, exchange encrypted messages, reconnect and receive notifications. No such test has been completed.
4. Only patch a verified compatibility defect with justified tests. Do not publish an APK as restored Messenger based solely on install or package integrity.
