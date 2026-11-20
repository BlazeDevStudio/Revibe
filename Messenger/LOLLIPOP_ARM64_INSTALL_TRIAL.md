# Stage 13: Lollipop ARM64 installation trial

**This is not a revived Messenger.** The test APK is a byte-identical copy of the user-supplied, original Meta-signed Messenger 336.0.0.13.142, versionCode 297217556, package com.facebook.orca, minimum Android 5.0/API21 and native arm64-v8a architecture.

Pinned SHA256: 70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab

## Verified offline
- Original and output SHA256 match exactly.
- APK ZIP CRC, main manifest and classes.dex present.
- ARM64 native libraries present; Java jarsigner accepts the original v1 signature.
- Existing Stage 9 native gate reports min API21 and 18 ARM64 libraries.
- Six new preparation-tool tests passed locally.

## Not verified
No real Android 5 installation, startup, Meta login, encryption or message delivery test has passed. Update/deprecation notices have not been removed or fixed. The user's generic “App not installed” report remains unclassified. No proprietary APK is checked into the public repository.

## Build a trustworthy unchanged install test
Use your separately acquired original Meta-signed APK and a JDK with jarsigner:

    python Messenger/engineering/prepare_lollipop_test.py --source /path/to/Messenger336.apk --output /tmp/Revibe_Lollipop_ARM64_INSTALL_TEST_Original_MetaSigned.apk --report /tmp/lollipop_report.json

This tool refuses unknown hashes and existing output paths. It never edits or re-signs the original.

## What to test
Use an authorized spare Lollipop phone (Android 5.0/5.1, API21/22). OS support must include arm64-v8a. Before installing, check Settings > Apps > Messenger for a pre-existing com.facebook.orca package; do not uninstall important apps or data. If installation again fails, use:

    python Messenger/engineering/install_failure_probe.py

Then, only when the phone has no existing Messenger installation and contains no personal data, use:

    python Messenger/engineering/install_failure_probe.py --apk /path/to/Messenger336.apk --install --ack-test-device --output install_result.json

The diagnostic records only a generic INSTALL_FAILED_* category. Identify the actual install failure before producing another re-signed APK. A successful installation is not evidence of functional messaging.
