# V23 — Android release integrity and personal Messenger feasibility (2026-11-25)

## Decision

**NO VERIFIED FUNCTIONAL PERSONAL MESSENGER RELEASE.** The existing `Messenger/client/` is independently authored Android Java source with a deliberately blocked transport. The debug APK's successful installation is not an authentication, message-receipt or end-to-end encryption test. `Messenger/install-probe/` remains a separate diagnostic; neither is a consumer Meta Messenger client.

## Current official integration evidence

- [Meta Messenger Platform quick start](https://developers.facebook.com/docs/messenger-platform/getting-started/quick-start) and [Page conversations Graph API](https://developers.facebook.com/docs/graph-api/reference/page/conversations/) document **Page access tokens** and Page-to-person conversations, not authorized personal-account inbox access.
- [Meta's interoperability technical article](https://engineering.fb.com/2024/03/06/security/whatsapp-messenger-messaging-interoperability-eu/) describes the Digital Markets Act (DMA) model for **eligible third-party messaging service providers** with technical and security requirements. It does not grant a generic old-Android Facebook account sign-in API.
- [European Commission DMA interoperability portal](https://digital-markets-act.ec.europa.eu/businesses-portal/messaging-interoperability_en) describes the EU framework. This is a separate provider-to-provider route for eligible European users, not established for Revibe or a general global consumer client.
- [Meta 2025 WhatsApp third-party-chats announcement](https://about.fb.com/news/2025/11/messaging-interoperability-whatsapp-enables-third-party-chats-for-users-in-europe/) confirms practical interop development on WhatsApp. Do not infer that Revibe has Messenger partner credentials, interfaces or approval.
- [Official Android 17 platform announcement](https://android-developers.googleblog.com/2026/06/Android-17.html) identifies Android 17 as **API 37**. The SDK package uses a minor platform identifier (for example `android-37.0`), unlike earlier SDK packages.

No authorized personal Messenger authentication/transport specification, Meta partner entitlement or live two-account E2EE test exists in this repository. Avoid requesting passwords, tokens, device identifiers or customer chat logs. Do not substitute Page bots, scraped private sessions or proprietary APK re-signing.

## Concrete software change: stronger release qualification

Prior `Messenger/tools/release_gate.py` depended on manifest JSON and presence of a signature; it did not compare that JSON with the actual APK's package name, minSdk or targetSdk. It also did not require ZIP alignment, v1+v2 signatures, or a complete SHA256SUMS manifest. V23 now:

1. Examines the **actual compiled APK** with Android SDK `aapt dump badging`; rejects a wrong package ID, SDK floor or target.
2. Checks `zipalign -c` and `apksigner verify --min-sdk-version`, requiring v1 for old Android and v2 for modern Android, rejecting Android Debug and mismatched/multiple signer certificates.
3. Validates exact SHA256SUMS against the manifest and rejects hidden/noncanonical/nested binary artifacts under `Messenger/dist/` when a release is claimed or while it is blocked.
4. Requires truthful distinct ABI+Android platform install/launch/restart evidence, including API19, API21, API23, API29, API35, and **API37** before a future release claim. Distinguishes `environment: emulator` from `physical`. These evidence URLs still require independent manual authenticity review.
5. Rejects an ARM64 APK claiming Android 4.4, prevents ABI-labelled DEX-only duplicates, and retains the existing physical binary hash checks. **The release gate is not evidence of Meta service access.**

The release gate also rejects insecure HTTP evidence URLs. Unit fixtures mocking SDK output are synthetics **for negative tests only**, not purported APKs. No Meta APK, credentials or signing secrets were introduced.

## Android 17 validation

Existing verified V22 foundation emulator matrix: API19/x86, API21/x86, API23/x86_64, API35/x86_64; it says nothing about Meta messaging or ARM hardware. V23 adds a separate Android 17/API37 emulator target. The first attempt [45620971131](https://github.com/BlazeDevStudio/Revibe/actions/runs/45620971131) failed SDK setup because the runner requested `platforms;android-37` rather than `android-37.0`. That failure is a **test environment/configuration failure, not an app test pass or crash**. Check the follow-up [45621293805](https://github.com/BlazeDevStudio/Revibe/actions/runs/45621293805) before changing the Android 17 acceptance cell to PASS. This exploratory API37.0 foundation matrix entry is non-blocking to prevent a CI environment fault from obscuring the already-proven older emulator matrix; the actual future Messenger release gate continues to require API37 evidence.

## Current stop/go criteria

Do not change `Messenger/STATUS.json` to a functional release until a supported personal Meta integration exists, there is explicit permitted-use evidence, full E2EE is implemented and tested on real accounts, and all promised Android/ABI install and launch tests pass with a non-debug release signer. A passing release-integrity check, by itself, does not authorize use of Meta's service.

**V23 changes no network transport or chat behavior; real consumer Messenger messaging remains BLOCKED.**
