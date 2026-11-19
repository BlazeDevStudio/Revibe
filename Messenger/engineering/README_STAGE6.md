# Stage 6 — experimental Android 4.4 ARMv7 APK

A genuine, self-signed **research APK** can now be built from the owner's separate, legally acquired Messenger 410 API19 ARMv7 original. This is **not a working Messenger revival**. It only replaces two English obsolete update strings with trial labels. Its code, encryption, login, server interactions and update gate are not patched.

## Requirements
Python 3.8+, Java JDK `keytool` and `jarsigner`; optionally Android SDK platform-tools `adb` for a disposable device.

## Build from local original
```bash
python Messenger/engineering/build_experimental_apk.py --original /path/to/original-API19-ARMv7.apk --output /tmp/Revibe_Research.apk --report /tmp/stage6_build.json
```

The source APK SHA-256 is pinned to prevent accidentally modifying the wrong binary. The original is never overwritten. A temporary signing key is generated, then discarded. A subsequent build cannot upgrade the first without uninstalling it. The package name is still `com.facebook.orca`, so it conflicts with official Meta Messenger and cannot replace that installation via an upgrade.

## Optional device smoke test
**Only on a spare phone you own or are authorized to test, without real account data.** This is an active installation; back up important information and uninstall the official package first.

```bash
python Messenger/engineering/candidate_smoke.py --apk /tmp/Revibe_Research.apk --install --ack-test-device --launch --output /tmp/stage6_smoke.json
```

Only install and process status categories are saved, not phone IDs, messages or login credentials. A successful installation, signed archive, or process is **not** evidence that modern Messenger works. Real-device compatibility, authentication and end-to-end encrypted send/receive remain unverified.

## Why the GitHub repo has no APK
Third-party Meta code/binaries, proprietary native libraries, certificates, and signing keys are intentionally excluded from the public Revibe repository. Only our build and inspection tools are published.

## Next milestone
Observe the exact failure on a spare Android 4.4 phone. Only then attempt a minimal, defensible compatibility repair rather than removing genuine warnings.
