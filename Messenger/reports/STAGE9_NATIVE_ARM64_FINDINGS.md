# Stage 9 — genuine native Android 5/6 ARM64 baseline discovery

Archived original Meta Messenger 336.0.0.13.142 (version code 297217556) has a distinct arm64-v8a/nodpi single-APK variant with Android 5.0 API21 minimum. Details and archive link: ../NATIVE_ARM64_ANDROID5_BASELINE.md.

**This version's APK bytes have not been retrieved, audited, built or live tested.** An archive listing does not mean live Messenger service works.

Added native_arm64_gate.py with static checks for manifest SDK, package, native ELF class, ABI, ZIP CRC, APK v1 signing artifacts, optional original Meta certificate fingerprint verification and jarsigner verification. The checker is read-only.

14 new synthetic unit tests passed locally. Three authentic source APKs were also inspected: original Messenger 410 ARMv7/API19, Messenger 410 x86/API21 and Messenger 588 ARM64/API28; none passes a native ARM64/API21 check. The genuine 410 ARMv7 original passes v1 verification and matches the archived Meta signing certificate; the modified Stage 6 research APK does not have the Meta signer identity.

Unresolved: obtain exact original Messenger 336 ARM64 API21 APK; validate binary, test install/start on Android 5/6, and diagnose Meta authentication/update requirements and E2EE. No working Messenger APK has been produced in this stage.