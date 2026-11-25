> Historical V21 snapshot (2026-11-21). Statements below about `Messenger/client/` being absent reflect that earlier date only. The independently authored **nonfunctional** V22 client foundation now exists; see [V23 current report](V23_RELEASE_INTEGRITY_AND_META_GATE.md) for the current acceptance gate. No functional Messenger release has been verified.

# V21 — verified feasibility, repository inventory, and release acceptance gate

Checked on 2026-11-21 against `main` 5ec2fbdc410a0e0c50b56cb3273914e64484753a, before this review branch. Do not mistake retrospective CI facts for tests on this branch.

## Product decision

**Canonical product: REVIBE MESSENGER CLIENT — BLOCKED.** There is no independently implemented consumer Messenger login/conversation client in this repository. `Messenger/install-probe/` is only an Android PackageInstaller diagnostic with a separate package identifier; it cannot authenticate to Meta, show conversations, or send messages. Preserve it as a tool rather than rename it.

## Executable source inventory

| Path | Executable? | What it is | Release status |
|---|---|---|---|
| `Messenger/install-probe/` | Java Android Gradle app | `org.revibe.installcheck2`, minSdk19, targetSdk35, no native `.so`, no INTERNET permission; `REQUEST_INSTALL_PACKAGES` for chosen local diagnostic APK | NON-MESSENGER; debug-signed CI diagnostic |
| `Messenger/engineering/*.py` | Python scripts | Static audits, signing research, package and device diagnostics requiring separately authorized APKs | research tooling, not an Android client |
| `Messenger/engineering/tests/` | Python tests | Offline source analyses | source tests only |
| `Messenger/reports/` | No (documents/data) | Historical stage-specific reports and metadata | archival evidence, not releases |
| `Messenger/engineering/archive/` | Archive binaries | Historical engineering material, not application release | preserved |
| `Messenger/client/` | Absent | No real client code to claim | BLOCKED |
| `Messenger/dist/` | Absent at review | No verified Messenger APKs, bundle, release cert or functional evidence | NOT RELEASED |

No proprietary Meta APK or native `.so` is tracked in the inspected Git tree. Historical source APKs, if independently held, must not be republished.

**Diagnostic build environment**: AGP 8.7.3; Gradle 8.9; Java 17; app ID `org.revibe.installcheck2`; Android minSdk19, targetSdk35. All supported emulator execution in reviewed run is x86 or x86_64 with no native libraries. Its debug signer is not a stable, protected production signing identity.

**Proven CI**:
- GitHub offline run [44776277527](https://github.com/BlazeDevStudio/Revibe/actions/runs/44776277527) passed at `e5222ae9...`, not at this review-branch head.
- Probe run [44760999284](https://github.com/BlazeDevStudio/Revibe/actions/runs/44760999284) passed all five jobs: build; API19 x86; API21 x86; API23 x86_64; API35 x86_64. These jobs verify an independent installer diagnostic and its synthetic callback instrumentation. They do **not** verify interactive phone file-picker/actual third-party installation or any Messenger functionality.
- Earlier Mi physical-device reports rejected historical APK variants with generic `App not installed`; no package-manager failure classification exists.

## Consumer Messenger and modern encryption feasibility

1. Meta's [Page conversations documentation](https://developers.facebook.com/docs/graph-api/reference/page/conversations) and [Messenger Platform quickstart](https://developers.facebook.com/docs/messenger-platform/getting-started/quick-start) require **Page access tokens** for Page-to-person chat. They are not a consumer-to-consumer inbox API or a supported Facebook personal login/third-party client session contract.
2. Meta describes [Messenger's personal E2EE](https://engineering.fb.com/2023/12/06/security/building-end-to-end-security-for-messenger/) and [key transparency](https://engineering.fb.com/2025/11/20/security/key-transparency-comes-to-messenger/). An official cryptography whitepaper is not by itself an approved production client access interface. Authentication, key provisioning, secure backups and real receipt/decryption must be tested end to end.
3. A **distinct EU/EEA interoperability channel** does exist for eligible third-party messaging service providers under the Digital Markets Act: [Meta's interoperability announcement](https://about.fb.com/news/2024/09/an-update-on-how-were-building-safe-and-secure-third-party-chats-for-users-in-europe/), [technical description](https://engineering.fb.com/2024/03/06/security/whatsapp-messenger-messaging-interoperability-eu/), [European Commission portal](https://digital-markets-act.ec.europa.eu/businesses-portal/messaging-interoperability_en). This is conditional, provider-to-provider interoperability for eligible European users and partners; it is **not** a general account sign-in API that allows an independently built Android 4.4 app to access any person's existing Messenger inbox. Eligibility, partner approval, specific endpoints and client compatibility have not been established for Revibe.
4. No authorized direct consumer inbox interface or active Meta partner entitlement has been verified here. The correct gate is **BLOCKED**, not impossible in all hypothetical future contexts and not an invitation to scrape tokens, defeat security, or impersonate the official app.

## Safe cleanup and CI guard

This branch makes no destructive moves: no old files, prior analyses, code or originals are deleted. `Messenger/STATUS.json` is updated with authoritative product/diagnostic separation. `Messenger/tools/release_gate.py` fails CI if somebody places `Revibe-Messenger-*.apk` or a Messenger release manifest in `Messenger/dist/` without satisfying the release contract. A blocked repository is allowed to pass **honesty checks**; a release claim cannot pass without files, signing, evidence references, and required platform observations.

This guard does not prove the external evidence is truthful and is **not** a substitute for actual authorized human-supervised Meta conversation tests. It must fail on a proposed release until those tests and an independently verifiable production package exist. Do not add mock chats or rebrand the diagnostic to satisfy CI.

## Next engineering decision

1. Establish eligible Meta personal Messenger consumer interoperability or approved EEA provider relationship with concrete technical specifications and permissions. No personal passwords or tokens in GitHub.
2. Once verified, implement independent, production-capable `Messenger/client/` from the existing Android build foundation, including login, E2EE receive/decrypt, bidirectional text, persistence/reconnect, notifications, logout, accessibility.
3. Validate independent signed artifacts and physical-install results for real OS/ABI combinations. Keep diagnostic APK downloads separate and labeled NON-MESSENGER.

**Release state: NO VERIFIED FUNCTIONAL MESSENGER RELEASE. No functional Messenger APK download is available.**
