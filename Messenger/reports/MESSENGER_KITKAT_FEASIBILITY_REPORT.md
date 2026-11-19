# Messenger Android 4.4 reverse-engineering / feasibility audit

**Date:** 2026-11-20 (Philippines)  
**Goal:** Determine whether supplied Messenger builds can be used as the basis of a reliable, very simple client for Android 4.4 / API 19, particularly person-to-person messaging for a device-reuse charity.

## Bottom line

**The v410 ARMv7 build declares Android 4.4 compatibility in its package manifest.** The supplied APK's manifest declares `minSdkVersion=19` and includes 32-bit ARM native libraries. Its APK Signature Scheme v2 cryptographic signature and full-file content digest both verify against a Facebook Corporation signing certificate. **This does not establish that installation or launch will succeed on every Android 4.4 device, or that Meta's backend still accepts authentication or supports present-day encrypted messages from that version.**

A direct merger of the newer v588 APK into v410 is **not technically credible as a shortcut**. v588 requires API 28 and contains 64-bit ARM native code and vastly more Android framework dependencies. Modifying either APK requires a new signing key, so it will no longer retain Meta's verified signature identity. Modern personal-chat cryptography and server-side compatibility still have to work; changing the APK version or its minimum SDK cannot provide that.

**Current result: no functional patched/merged APK was produced or claimed.** The deliverable is a verified static inventory, integrity check, symbol scan, and a realistic engineering test path.

## Audited APKs

| Build | Minimum SDK (confirmed in manifest) | Target SDK | ABI (from APK `lib/`) | Size | ZIP entries | DEX layout |
|---|---:|---:|---|---:|---:|---|
| Messenger 410.0.0.17.85, variant 312007848 (Drive) | 19 (Android 4.4) | 33 | `armeabi-v7a` | 42.1 MiB | 8,361 | 1 root DEX plus 10.92 MiB Meta Superpack DEX payload |
| Messenger 410.0.0.17.85, variant 312007866 (upload) | 21 (Android 5.0) | 33 | `x86` | 74.7 MiB | 16,624 | 8 root DEX files plus a small Superpack payload |
| Messenger 588.1.0.66.98, variant 347617515 (upload) | 28 (Android 9.0) | 37 | `arm64-v8a` | 174.1 MiB | 24,890 | 18 root DEX files |

These are distinct APK variants. **Do not install the x86 build as the KitKat ARM client**, and do not assume a 64-bit-only native library can be copied into an Android 4.4 32-bit process.

## Integrity results

The independently implemented APK Signature Scheme v2 check validated:

1. Embedded signed-data cryptographic signature (RSA/PKCS1v1.5/SHA-256, scheme algorithm 0x0103).
2. SHA-256 content digest over signed APK sections, including the central directory and corrected EOCD.
3. The certificate extracted from the signed data.

**All three APKs passed.** Their signer is `CN=Facebook Corporation,OU=Facebook,O=Facebook Mobile,L=Palo Alto,ST=CA,C=US`, with signing certificate SHA-256:

`e3f9e1e0cf99d0e56a055ba65e241b3399f7cea524326b0cdd6ec1327ed0fdc1`

This is an integrity verification against the certificate embedded in the files, **not an external chain-of-trust or malware-analysis verdict**. Apps have not been executed.

Whole-file SHA-256 checksums:

| Build | SHA-256 |
|---|---|
| v410 API 19 ARMv7 | `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8` |
| v410 API 21 x86 | `6f22a9cf3172bcdc3e0c7b87ef77c1d56c5476cb378322b8087a953e1469cf88` |
| v588 API 28 ARM64 | `30ad524ac1c06efd75b5fd123efc89c4f61462a7eeb7b666c4f71cfd24de3aa7` |

## Interesting internal evidence

- All three APK manifests use the original application package `com.facebook.orca`.
- Both v410 variants have the same 75 declared permission names and the same component-count profile: 403 activities, 112 services, 21 providers, 75 receivers.
- The v410 API 19 APK contains a 10.92 MiB `assets/secondary-program-dex-jars/store-0.dex.spo` binary; this is Meta's packed code payload. A decompiler that reads only `classes.dex` would omit much of the implementation.
- The v410 API 19's root `classes.dex` contains **symbol-string references** to `E2EE` and `LABYRINTH` (including `LABYRINTH_INFRA_RESTORE_BACKUP`). These are indications that the old build was prepared for some encryption/backup infrastructure; **they do not prove that current E2EE messages can be read or sent**.
- v588 contains more E2EE/Labyrinth/secure-storage symbol references in its larger root DEX collection and declares an additional set of permissions associated with later Android releases. Those raw symbol counts are **not a like-for-like functional comparison** because v410 stores much of its code in Superpack.
- The old v410 native folder contains 23 `armeabi-v7a` .so files, and the new v588 contains 14 `arm64-v8a` .so files. Several new v588 libraries have no directly corresponding name in the old APK.
- The base dex files use format `dex\n035`, but that alone does not resolve runtime API dependencies or loader compatibility.

## Why naive amalgamation won't work

1. **Code and native ABI:** Android 4.4 commonly uses 32-bit Dalvik, while the newer package targets API 28+ and its bundled native libraries target 64-bit ARM. A straight copy of DEX/native code is not an Android 4.4 port.
2. **Meta package signing:** Changes invalidate the original signatures. A re-signed APK is no longer Meta-signed. Package-to-package trusted interactions and server checks may break; those checks cannot be inferred from static analysis alone.
3. **Modern encrypted messaging:** Meta moved personal Messenger chats to default end-to-end encryption beginning in December 2023. Encryption interoperability is a protocol and key-management issue, not just a new user interface.
4. **Backend behavior is unknown:** There is no evidence from the static package audit that any build can log in, fetch conversations, synchronize encryption keys, or exchange messages with current production Messenger services.
5. **Official third-party Messenger platform APIs:** The available developer API is not a general personal-account-to-personal-account messaging replacement; it generally operates with Pages/business integrations.

Relevant Meta references:
- https://engineering.fb.com/2023/12/06/security/building-end-to-end-security-for-messenger/
- https://about.fb.com/news/2024/03/end-to-end-encryption-on-messenger-explained/
- https://developers.facebook.com/docs/messenger-platform/getting-started/quick-start

## Proposed engineering stages (priority order)

### Stage 1: isolate why the real v410 KitKat build fails (not yet tested)

On a consented test account and physical Android 4.4 device, assess each separately:
- APK installation and launch.
- TLS/certificate/network handshake without disabling certificate validation.
- Standard sign-in and session renewal.
- Account upgrade/version-gating messages (distinguish backend rejection from local exception).
- Opening existing conversations, E2EE secure-storage key recovery, sending/receiving one-to-one text.
- Restart, notification delivery, battery/memory use.

Collect **redacted** runtime exceptions and network error codes; never export passwords, access tokens, encryption keys, contact lists, or message text. No live test was performed in this audit.

### Stage 2: only investigate changes supported by test evidence

- If startup is a local runtime failure: focus on the actual crashing class / missing Android API and backport minimal isolated code with strict safety and licensing review.
- If the server blocks old clients: do not claim that patching a version number is enough. Establish whether a legitimate supported integration exists before spending time on app-level modifications.
- If E2EE key recovery fails: do not disable encryption, imitate an untrusted endpoint, or expose keys to an intermediary. A correct, auditable cryptographic implementation is mandatory.

### Stage 3: senior-friendly distribution

Only after end-to-end successful testing, provide a **large-button native launcher** and a signed, distributable installer with repeatable installation procedures. No credentials hard-coded in a common APK; per-recipient account provisioning and privacy protections required. Maintain supported calling/SMS fallback for emergency and routine communication.

## Current test-status matrix

| Requirement | Status |
|---|---|
| Read provided APK bytes | **PASS** (3/3) |
| Enumerate Drive folder | **PASS** (1 APK) |
| Parse binary AndroidManifest.xml | **PASS** |
| Verify APK v2 package signatures and data digests | **PASS** (3/3) |
| Identify compressed old DEX payload | **PASS** |
| Inspect unpacked Superpack secondary DEX code | **NOT DONE** |
| Install/launch on Android 4.4 device | **NOT TESTED** |
| Live personal-account login | **NOT TESTED** |
| Current personal-message delivery and E2EE sync | **NOT TESTED** |
| Working modified/backported Messenger APK | **NOT BUILT** |

## Files in this audit package

- `messenger_apk_static_audit.json`: structured manifests, permissions, library names, DEX headers, hashes.
- `messenger_dex_symbols.json`: exact symbol-string scan of *standard* DEX files only.
- `messenger_apk_integrity.json`: v2 certificate/signature/content-digest validation output.
- `apk_static_audit.py`: repeatable read-only APK inventory.
- `dex_symbol_scout.py`: repeatable read-only DEX keyword scan.
- `verify_apk_v2.py`: repeatable APK v2 verification.

No proprietary APK binaries are redistributed in this audit package.
