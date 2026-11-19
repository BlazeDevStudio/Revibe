# Revibe / Messenger

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
