# Native ARM64 Android 5/6 baseline — Stage 10

The user-provided Messenger 336.0.0.13.142 APK (API21+, arm64-v8a) has now been acquired and cryptographically verified offline. **No updated Messenger APK was created.** The original Meta-signed APK is the preferred initial trial on Android 5/6 ARM64 because re-signing or editing it introduces additional compatibility risk.

The new `engineering/original_arm64_smoke.py` provides read-only ADB preflight by default. Installation is optional and requires `--install --ack-test-device`, and never overwrites an existing package. It logs no private or device-identifying data. See `reports/STAGE10_NATIVE_ARM64_336.md` for reproducible commands, signed APK hash, and remaining blockers.
