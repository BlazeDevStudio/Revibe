# Stage 7 — ARM64 candidate and Messenger Lite investigation

The ARM64 candidate is a **research-only** modified Messenger 588 APK, not a revived service. Source APK: user's legally obtained Messenger 588.1.0.66.98 `arm64-v8a`, minimum Android 9 (API28), target API37, SHA256 pinned in `build_arm64_research.py`.

## Build (optional, user-provided original APK)
Requires Python 3.8+, `cryptography`, JDK `keytool` and `jarsigner`.

```sh
python Messenger/engineering/build_arm64_research.py \
  --original '/path/to/original-Messenger-588-ARM64-API28.apk' \
  --output '/tmp/Revibe_Messenger_ARM64_API28_RESEARCH_ONLY.apk' \
  --report '/tmp/stage7_arm64_candidate.json'
```

The builder preserves the manifest and app code; modifies one fixed-length English resource string (`Update Messenger` -> `Revibe test app `), re-signs using an ephemeral test certificate (APK v1 and experimental v2), checks ZIP integrity, native ABI, and local v2 cryptographic content digest. It does not modify authentication, encryption, server APIs, or the actual version/update restriction. The replaced text might not appear in the running app. This is **not** a production signing pipeline; verify with Google Android SDK `apksigner` before device install or distribution.

The app retains `com.facebook.orca`, which conflicts with Meta-signed Messenger. Uninstalling original Messenger can remove local app data. Test only on disposable, owned/authorized devices without any meaningful accounts or messages, and never deploy to vulnerable charity recipients.

## API/ABI reality
- Existing Stage6 ARMv7 research candidate: minimum API19, 32-bit only, may run on ARM64 phones if OS supports 32-bit app processes.
- Stage7 ARM64 research candidate: minimum API28 and target API37; **not compatible with Android 4.4 through Android 8.x**. No API19 ARM64 binary exists in this project.
- Neither is verified to log in or exchange encrypted messages. No release claim.

## Tests
```sh
python -m unittest discover -s Messenger/engineering/tests -v
```
The new unit tests use a synthetic ZIP fixture, not proprietary app code. See `Messenger/reports/MESSENGER_LITE_RESEARCH_2026.md` for Lite leads and remaining analysis questions.
