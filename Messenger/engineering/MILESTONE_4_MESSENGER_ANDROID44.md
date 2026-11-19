# Messenger Android 4.4 — Stage 4 Engineering Milestone

**Date:** 2026-11-20

## Scope

Continued from previous validated Stage 3. Verified the exact original KitKat APK's v1/JAR content signature using a real Java `jarsigner -verify` run. Added a single-command offline/optional device diagnostics gateway with a pinned original SHA-256 allowlist, process observation, and privacy-redacted Android logcat attribution. Retained the previous Superpack/DEX analysis and unit tests.

## Directly verified results

- The original Messenger v410 API19 ARMv7 APK has SHA-256 `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`.
- Its binary manifest declares `minSdkVersion=19` and native `armeabi-v7a` code and its ZIP includes v1 signature artifacts.
- `jarsigner -verify` completed with exit status 0 and the explicit `jar verified.` marker. Java warns of a self-signed signing certificate, a 1024-bit RSA key, and nonstandard `JarFile` versus `JarInputStream` entry statuses; therefore the result must **not** be characterized as a valid PKIX chain, modern signing strength or source provenance.
- The target APK passes offline KitKat/ARM compatibility gates. Neither its current server acceptance nor E2EE messaging have been tested.
- 19 offline automated unit tests passed (13 Stage 3 carry-over plus 6 Stage 4 tests), including mocked ADB response redaction and refusal of multiple devices / unrecognized v1 status strings.
- No Android SDK emulator, `adb`, or connected Android device is available in the current execution environment. **No installed application, Messenger login, send/receive, or call test was performed.**

## New deliverables

- `stage4_kitkat_gate.py`: verifies SHA-256 identity, KitKat API/ABI, and true v1 signed contents. With explicit device flags and an authorized ADB device, optionally installs/launches the **original** APK, observes Messenger process and summarizes error categories only. It refuses changed APK hashes and incompatible device targets.
- `tests/test_stage4.py`: synthetic device and v1 signature tests.
- `STAGE4_STATIC_GATE_RESULT.json`: generated from the original KitKat APK; includes explicit `device_test_completed=false`, `modern_login_verified=false`, and `encrypted_chat_send_receive_verified=false`.
- `MANUAL_ACCEPTANCE_TEMPLATE.json`: privacy-conscious functional check gates with all statuses `NOT_TESTED`.
- `README_STAGE4.md`: usage, safeguards, and interpretation.
- Previous Stage 3 static inspection tools, to retain continuity.

## Priority technical decision

The original APK is intact and has the right KitKat architecture; making another repackaged binary without first proving a working backend session would be speculative. A **live, authorized Android 4.4 baseline test** is the release-blocking next step. Possible outcomes:

- The original works: optimize the actual UI/launcher workflow without modifying Messenger binaries unnecessarily.
- Login/update blocked: determine whether this is enforced by Meta's backend or local client code; don't infer bypass feasibility from a UI prompt alone.
- Login succeeds but chats fail: examine *redacted* error categories and current E2EE compatibility. Don't claim restoration by disabling encryption or shipping unaudited cryptographic code.
- Installation/launch fails locally: diagnose that specific class, native loader, TLS, or package error before any patch attempt.

**Build outcome:** this stage provides tested diagnostics, **not a modified or working Messenger APK**. The original APKs remain unchanged.
