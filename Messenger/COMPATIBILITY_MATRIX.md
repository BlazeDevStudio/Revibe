# Revibe Messenger — evidence-separated compatibility matrix

## V23 Android 17 expansion (2026-11-25)

Android 17 is **API 37**. The V23 release gate requires independently evidenced Android 17 compatibility, not merely targetSdk35. The first API37 foundation job failed because the CI runner looked for `platforms;android-37` instead of `android-37.0`. This is a CI configuration failure, not evidence of app incompatibility. Follow-up (exploratory, non-blocking for the nonfunctional foundation, but required to pass for any actual Messenger release): [workflow 45621293805](https://github.com/BlazeDevStudio/Revibe/actions/runs/45621293805) (verify completion before claiming Android 17 PASS). ARM32/ARM64 hardware and actual Meta authentication/E2EE remain unverified.

V23 release-integrity unit suite [45621187131](https://github.com/BlazeDevStudio/Revibe/actions/runs/45621187131) passed 175 source/contract tests; latest [45621785540](https://github.com/BlazeDevStudio/Revibe/actions/runs/45621785540) passed 176 after HTTPS evidence validation; none substitute for hardware or real Messenger tests.


## V22 independent native foundation (NOT FUNCTIONAL MESSENGER)

New independent source is in `Messenger/client/`, package `org.revibe.client.foundation` (separate from real product ID and installer diagnostic), minSdk19/targetSdk35, Java/DEX-only with **no `.so` libraries**, no network permission, and a fail-closed Meta session. Its native status screen has persistent large/standard text controls. **This is not a Messenger client capable of authentication, conversation listing or messages.**

- [Build workflow 44911221467](https://github.com/BlazeDevStudio/Revibe/actions/runs/44911221467): 12 source-contract tests PASS, real Android Gradle compilation and debug APK metadata/signature/zipalign verification PASS.
- Compiled APK SHA-256 `f7b0c704e74281f500541aa817cbd3f2b56ae3eeb7f56c84eb3412bb93c7c85e`; 11,294 bytes, package `org.revibe.client.foundation`.
- API19 x86, API21 x86, API23 x86_64 and API35 x86_64: **PASS** on emulator install/launch/restart and 13 on-device foundation-only assertions per job, run [44911221467](https://github.com/BlazeDevStudio/Revibe/actions/runs/44911221467). These assert disabled Meta sessions and persisted large text, NOT Messenger communications.
- ARM32 and ARM64 emulator/physical hardware: **UNVERIFIED**. Personal Meta login, real bidirectional communication and E2EE: **NOT IMPLEMENTED**.
- This debug-only foundation cannot be renamed to `Revibe-Messenger-universal.apk`, nor does architecture-neutral DEX prove real service compatibility.


Reconciled 2026-11-21. **The product is BLOCKED; no row below claims a functioning personal Messenger release.** Architectural goals and Meta interoperability are separate from installing the independent diagnostic.

## Actual diagnostic emulator evidence (NON-MESSENGER)

Source: GitHub run [44760999284](https://github.com/BlazeDevStudio/Revibe/actions/runs/44760999284), completed successfully. All declared emulator jobs passed; results are **not** physical ARM device tests.

| Android | Runtime ABI of emulator | Independent `org.revibe.installcheck2` | Actual interactive install of selected Meta APK | Personal Messenger login, send/receive, E2EE |
|---|---|---|---|---|
| API 19 / Android 4.4 | x86 | PASS (install/launch) | UNVERIFIED (PackageInstaller sessions unavailable below API21) | NOT IMPLEMENTED |
| API 21 / Android 5 | x86 | PASS (install/launch, synthetic callback) | UNVERIFIED | NOT IMPLEMENTED |
| API 23 / Android 6 | x86_64 | PASS (install/launch, synthetic callback) | UNVERIFIED | NOT IMPLEMENTED |
| API 35 / Android 15 | x86_64 | PASS (install/launch, synthetic callback) | UNVERIFIED | NOT IMPLEMENTED |
| API 19 ARM32 | armeabi-v7a | UNVERIFIED | UNVERIFIED | NOT IMPLEMENTED |
| API 21 ARM64 | arm64-v8a | UNVERIFIED | UNVERIFIED | NOT IMPLEMENTED |

The diagnostic contains no `.so` files, so its compiled DEX-only package is architecture-independent in principle, but no ARM emulator or physical install was verified in this run. This does not verify the proprietary Meta APK variants.

## Required Messenger product gate (not yet met)

| Product acceptance requirement | ARM32 (API19+) | ARM64 (API21+) | x86 (API19+) |
|---|---|---|---|
| Independent Messenger client compiled | MISSING | MISSING | MISSING |
| Stable release certificate, v1 plus modern signing | MISSING | MISSING | MISSING |
| APK installed/launched/restarted | UNVERIFIED | UNVERIFIED | UNVERIFIED |
| Authorized personal Messenger login | BLOCKED | BLOCKED | BLOCKED |
| Bidirectional Meta-to-Meta text | BLOCKED | BLOCKED | BLOCKED |
| Genuine E2EE receive/decrypt and identity verification | BLOCKED | BLOCKED | BLOCKED |
| Offline retry/reconnect and push notification | UNIMPLEMENTED | UNIMPLEMENTED | UNIMPLEMENTED |
| User-friendly one-tap actual hardware installation | UNVERIFIED | UNVERIFIED | UNVERIFIED |

ARM64 native runtime requires Android API21+; Android 4.4 can run ARM32 code on compatible hardware, not a native `arm64-v8a` executable. Real `x86` support is a distinct test from x86_64. A universal no-native-library APK, if later engineered, may be a proper single artifact instead of three byte-identical misleading ABI names.

## Enforced release preconditions

`python3 Messenger/tools/release_gate.py --check` passes **only as a blocked-source integrity check** while no Messenger-labeled release exists. Any Messenger-named APK/manifest triggers the strict --release checks. The gate requires actual binaries, valid APK ZIPs, SHA-256, Android SDK signing verification with expected signer fingerprint, verified Meta/functional test references, install/launch/restart evidence for API19 ARM32/x86 and API21 ARM64, and a truthful release status. Human audit still has to authenticate external test proof; CI cannot prove Meta messaging merely from JSON flags.
