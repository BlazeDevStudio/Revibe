# Revibe / Messenger

## V22 Android foundation (NOT a functional Messenger app)

Independent native Android source now lives at [`client/`](client/), separately from [`install-probe/`](install-probe/). It has a blocked-service screen, working offline persistent large-text controls, a fail-closed `BackendGate`, `minSdk19`, `targetSdk35`, no INTERNET permission and no native libraries. The debug-only package is `org.revibe.client.foundation`, **not** the reserved production ID. [V22 CI run](https://github.com/BlazeDevStudio/Revibe/actions/runs/44911221467) has passed independent Android compilation and API19 signature/manifest checks, with 12 source tests; the separate emulator matrix must be checked for its final result.

This remains **NOT FUNCTIONAL MESSENGER** and must never be distributed as a replacement for personal Meta Messenger. No login, conversation list, end-to-end encryption, message send/receive, notification transport, or Meta partner authorization is implemented.


## Current V21 product decision (2026-11-21)

**No verified functional personal Meta Messenger client has been built or released.** The canonical product is REVIBE MESSENGER CLIENT. Meta's Page messaging APIs are not consumer Messenger inbox access; the EU/EEA third-party interoperability program requires separate eligibility and does not establish general personal Facebook login for Revibe. Real authentication, two-way message exchange and E2EE are BLOCKED until a supported, authorized integration is established.

`install-probe/` is an independent, debug-signed **NON-MESSENGER** Android installer diagnostic. Its x86/x86_64 emulator test run [44760999284](https://github.com/BlazeDevStudio/Revibe/actions/runs/44760999284) passed API19/21/23/35 install/launch and synthetic callback checks. This is not proof of ARM hardware installation or consumer chats. The diagnostic is not eligible for Messenger release naming.

Canonical evidence: [V21 feasibility report](reports/V21_FEASIBILITY_AND_RELEASE_GATE.md), [compatibility matrix](COMPATIBILITY_MATRIX.md), machine-readable [release state](STATUS.json), [release integrity gate](tools/release_gate.py). Test `python3 Messenger/tools/release_gate.py --check` at the repository root. No proprietary APK or credentials should be added to GitHub.


## Mission
Explore reviving Messenger for refurbished devices used by older adults, with a large-text, simple, reliable interface.

## Planned compatibility (NOT VERIFIED)
- Android 4.4 / API 19 through Android 10 / API 29.
- Potential ARMv7 (`armeabi-v7a`), ARM64 (`arm64-v8a`) and x86 (`x86`) distributions.
- Builds will only be advertised for OS/ABI combinations actually tested.

## Update and deprecation prompts
Investigate client-side notices only where they can be corrected without hiding a real service failure.
Backend-required upgrades, authentication, and end-to-end encryption must be handled through genuinely compatible communication.
No bypass of server policy is claimed.

## Current status
- Three source APKs audited (KitKat ARMv7 Messenger 410; Android 5 x86 Messenger 410; Android 9 ARM64 Messenger 588).
- Original API 19 ARMv7 build validated offline for manifest and v1 content signature.
- Static analysis tools and device diagnostic runner are included in `engineering/`.
- Complete Superpack reconstruction remains outstanding.
- Real login, end-to-end encrypted send/receive, notifications, and calls are NOT TESTED.
- **No modified APK, 3-ABI release, or proven deprecation-warning fix exists yet.**

## Working with the code
See `engineering/README_STAGE4.md`. Run `python -m unittest discover -s engineering/tests -v` and provide your own legally obtained APK separately when using the tools.

## Safeguards
No credentials, tokens, message text, or private conversation logs should be committed. Do not distribute proprietary Meta APKs or bundled native libraries from this repository.

## Stage 5: update/deprecation barrier diagnostics

The [Stage 5 toolkit](engineering/README_STAGE5.md) inventories warning-related APK resources and can classify the warning displayed on an authorized Android test device without retaining messages or credentials. [Stage 5 findings](reports/MILESTONE_5_MESSENGER_ANDROID44.md) include three original APK inventories. **It does not fix server enforcement or create an APK.**

Offline tests: 27 passing locally as of 2026-11-20; GitHub Actions tests run without APK binaries. No device or real-account test has been conducted here.

## Updated device-independent requirement (2026-11-20)
The end-user goal is one-tap installation from **Android 4.4/API19 upward**, without identifying a specific phone model. Prefer one universal APK supporting ARMv7, ARM64 and x86; expand support to later Android releases through actual OS/ABI acceptance tests. This supersedes the earlier Android 10-only *planning* ceiling, **but does not imply wider support is proven**. See [the compatibility contract](DEVICE_INDEPENDENT_COMPATIBILITY.md). Repeated APK install failures remain unresolved. No universal functional Messenger binary has been produced.
