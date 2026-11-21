# Revibe Android client foundation — NOT FUNCTIONAL MESSENGER

This is an independently authored **Android native app foundation**, separate from the existing `Messenger/install-probe/` diagnostic and all historical Meta APKs. The customer requirement is real personal Messenger interoperability; this module does **not** satisfy that requirement and must not be distributed as a Messenger replacement.

## What exists
- Real Android Java source and AGP/Gradle build, with `minSdk 19`, `targetSdk 35`.
- No `.so` native binaries: the build is DEX-based and architecture-independent in principle.
- Own debug-only package `org.revibe.client.foundation`. The planned production ID `org.revibe.messenger` is deliberately not used.
- Large high-contrast native text, ScrollView for small older screens, meaningful screen reader content. Real on-device persisted large/standard text control with 56dp touch targets and no personal data.
- No INTERNET permission, credentials, contacts, tracking, WebView, chat placeholders, locally forged messages or unrelated backend.
- A fail-closed `BackendGate` that rejects session startup. Enabling it by flipping a constant would NOT constitute a feature.

## Build only for engineering evaluation

`cd Messenger/client && gradle :app:assembleDebug :app:assembleDebugAndroidTest --no-daemon`

The separate foundation CI workflow builds and tests under emulators; internal artifact names explicitly include **NOT-FUNCTIONAL-MESSENGER**. Do not publish under `Revibe-Messenger-*.apk` names or label its installation as proof of Meta login/chat.

## No authorized Meta path

Meta Messenger Platform documented Page access tokens are Page-to-customer APIs, not personal Facebook inbox access. A separate European third-party interoperability partner pathway may exist subject to provider eligibility, Meta onboarding and verified cryptographic requirements. No such approval, session contract or two-way E2EE is established for Revibe. See `../reports/V21_FEASIBILITY_AND_RELEASE_GATE.md`.

## Next product work

Do not add a fake chat UI or password input while the service contract is blocked. First verify an eligible, supported personal interoperability agreement and production endpoints. Then implement actual authentication, crypto and messaging with validated tests under a new review. Physical ARM32/ARM64 tests and stable release signing are still outstanding.
