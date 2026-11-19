# Revibe Messenger — Stage 11: Native API and runtime gate

**Research only. No Messenger service functionality restored.**

## Original APK evidence
A new read-only ELF analyzer examines Android notes in native libraries rather than trusting APK filenames.

| Original | Native .so files | Android API build notes |
|---|---:|---|
| Messenger 336 ARM64, API21 | 18 | all 18 API21 |
| Messenger 410 ARMv7, API19 | 23 | 22 API19; one unreadable |
| Messenger 588 ARM64, API28 | 14 | ten API28, one API23, three API21 |

The Messenger 336 manifest also specifies API21. That is the right native ARM64 Android 5/6 baseline, but native build notes cannot establish successful startup or service access.

Original SHA256: Messenger 336: 70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab; Messenger 410: 006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8; Messenger 588: 30ad524ac1c06efd75b5fd123efc89c4f61462a7eeb7b666c4f71cfd24de3aa7.

## Update warning investigation
The existing Stage 5 static resource scanner found five mandatory-update keyword matches inside Messenger 336's assets/strings/default.frsc, along with login, network, Google Play Services, and encryption categories. These are static textual indicators, not evidence of a live update gate or a viable workaround.

## Fixed test-runner defect
Stage 10's smoke test could launch any preexisting package named com.facebook.orca. Stage 11 refuses both install and launch on any preexisting Messenger because its identity has not been verified. Result: existing_messenger_identity_unverified_action_skipped. No installed app is changed or removed.

## Reproduce
Run python Messenger/engineering/elf_android_api_audit.py <original-APK> --output /tmp/elf_api.json and python -m unittest discover -s Messenger/engineering/tests -v. Only on an authorized disposable Android 5/6 ARM64 phone, run original_arm64_smoke.py against the original Meta-signed Messenger 336 with --install --ack-test-device --launch.

23 local Stage 11 regression tests passed. There is no ADB-connected device in this environment; installation, real login, two-way encrypted messaging, calls, notifications, and update-gate behavior remain unverified.

## Next gate
Test the original Meta-signed Messenger 336 on Android 5/6 hardware, recording only non-sensitive high-level failure categories. Repair a specific proven client defect rather than suppressing server-required upgrade notices. Never publish proprietary APKs, libraries, signing keys or private account data.
