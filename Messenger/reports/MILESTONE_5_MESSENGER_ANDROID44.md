# Stage 5 — Update Prompt Evidence & Runtime Classification

**Date:** 2026-11-20

## New direct evidence

The exact original Android 4.4 Messenger 410 ARMv7 APK has bundled client strings describing mandatory updates, an outdated app version, and Google Play Services updates. The two Messenger 410 build variants (ARM API 19 and x86 API 21) produce identical resource-pattern category counts in the inspected files, though their other package content differs. Messenger 588 ARM64 also contains update/deprecation-related strings.

### Offline resource-pattern counts

The scanner matches text fragments from `assets/strings/default.frsc` and `resources.arsc`. Values are matching segments, **not** runtime warning frequency or evidence of backend enforcement.

| APK | FRSC mandatory-update matches | FRSC Play Services matches | ARSC device/Android unsupported matches |
|---|---:|---:|---:|
| Messenger 410, API 19, ARMv7 | 5 | 4 | 3 |
| Messenger 410, API 21, x86 | 5 | 4 | 3 |
| Messenger 588, API 28, ARM64 | 2 | 5 | 4 |

Original SHA-256 identities: API19 ARMv7 `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`; API21 x86 `6f22a9cf3172bcdc3e0c7b87ef77c1d56c5476cb378322b8087a953e1469cf88`; API28 ARM64 `30ad524ac1c06efd75b5fd123efc89c4f61462a7eeb7b666c4f71cfd24de3aa7`.

## Implementation

Added `engineering/prompt_barrier_audit.py` and eight unit tests. The tool classifies locally bundled strings and optionally a connected authorized phone's visible XML hierarchy into coarse error categories. Device-side temporary XML is removed; no raw text or device serial appears in the stored report.

**Tests:** Stage 5: 8/8 passed offline. Existing Stage 4 toolkit: 19/19 passed independently. 27 offline tests in total. No connected Android phone or live Meta account in this execution environment.

## What we cannot conclude

An embedded update string can be displayed because of a local condition, remote response, or both. Replacing the string or hiding a dialog cannot restore rejected login, unsupported TLS, missing cryptographic operations, or server-enforced deprecation. Modern default end-to-end-encrypted Messenger communication remains **unverified**.

No patched Messenger APK or three-ABI release was built.

## Next engineering gate

On an authorized Android 4.4 ARMv7 test phone: run Stage 4's original APK install/launch smoke test, then Stage 5's **read-only UI barrier check** while the actual update dialog is visible. Record the error category, not user credentials or private chats. Only after a demonstrated failure should any compatible client-side repair be implemented and tested for genuine encrypted send/receive.
