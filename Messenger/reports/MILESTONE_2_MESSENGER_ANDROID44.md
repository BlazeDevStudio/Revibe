# Messenger Android 4.4 — Engineering Milestone 2

**Date:** 20 November 2026 (Asia/Manila)  
**Objective:** Inspect Meta's Superpack secondary DEX arrangement, use the two v410 variants for a technically defensible comparison, and deliver a privacy-conscious local test harness.  
**Inputs:** Three user-supplied Messenger APKs; original files were not changed.

## Result

**Completed:** Validated the archive-level layout of the KitKat build; recovered the *file table* for all nine packed DEX payloads in three `.spo` archives; successfully decoded independent XZ-encoded blocks as a partial inspection step; compared the two v410 variants by DEX hash; compared readable framework-method references in the API 21 and API 28 variants; built and unit-tested a read-only inspection tool and optional Android device probe.

**Not completed:** Reconstructing full runnable DEX files from Superpack, backporting the API 28 client, or proving present-day Messenger personal account login/E2EE delivery. **No modified/working Messenger APK exists yet.**

## New finding 1 — actual Superpack contents

The v410.0.0.17.85 Android 4.4/ARM32 APK has three `.spo` DEX archives. The primary one reports **seven secondary DEX outputs**:

| Archive entry | Expected unpacked bytes |
|---|---:|
| `secondary-1.dex` | 7,481,688 |
| `secondary-2.dex` | 5,760,200 |
| `secondary-3.dex` | 9,891,896 |
| `secondary-4.dex` | 9,300,892 |
| `secondary-5.dex` | 9,310,792 |
| `secondary-6.dex` | 8,606,192 |
| `secondary-7.dex` | 7,611,604 |

It also contains `effects-1.dex` (16,476 bytes) and `longtail-1.dex` (320 bytes). Their filenames are consistent with all three corresponding `metadata.txt` locator lists.

All three archives use Superpack magic `0x50c00100` and an observed per-entry layout of NUL-terminated filename/format, four zero bytes, and two 64-bit fields. This parser is **specific to this observed version**, not a complete Superpack decoder.

**Partial decompression evidence:**

| Packed archive | Valid individual XZ streams identified and decoded | Streams beginning with DEX magic |
|---|---:|---:|
| Main secondary DEX | 79 | 1 |
| Effects | 46 | 1 |
| Longtail | 15 | 1 |

Total decoded independent streams: **140**. These decode to *fragments or intermediate tables*, not nine reconstructed DEX files. The 19,361,468 decoded main-archive bytes are **not** the total size of the seven complete expected DEX files. Superpack uses additional metadata/transforms; simple concatenation would be incorrect. The inspector intentionally exports only sizes and indicators, never proprietary bytecode.

## New finding 2 — the v410 x86 APK is a reference, not a replacement

The v410 x86/API21 variant contains eight visible standard DEX files, corresponding in *number* to the KitKat version's one base DEX plus seven packed secondary DEX files. However, a comparison of each `classes2.dex` through `classes8.dex` with the KitKat `metadata.txt` SHA-1 values for `secondary-1.dex` through `secondary-7.dex` found **zero matching hashes (0/7)**.

Consequences:

- The x86 DEX files can help locate concepts and likely v410 code structure for research.
- They are **not byte-identical substitutes**, and matching ordinals do not prove class-level equivalence.
- Copying the x86 DEX into the ARM KitKat APK would change signature, resources and potentially ABI/API dependencies; this is not a valid repair.

## New finding 3 — why the API 28 build is not a drop-in patch

The standard-DEX reference scan found **2,374 Android framework class/method name references** in v588 that were not present in all eight visible v410 x86 DEX files. Examples include `android.adservices.measurement.MeasurementManager` references and methods on newer Android animation classes.

**Interpretation limit:** These are symbolic references, not confirmed runtime calls or individually verified API-level requirements. Some may be behind Android version checks or come from unrelated libraries. The count is a prioritization aid, **not a count of 2,374 required backports**.

The 64-bit-only native libraries in the supplied v588 cannot run inside the old 32-bit KitKat process. A credible port requires 32-bit compatible native implementation plus a supported login, transport and end-to-end encryption integration.

## New deliverable — local Android 4.4 probe

`kitkat_device_probe.py` is a **host-side** script. It uses `adb`, requires exactly one authorized connected Android device, and can inventory the OS/API/CPU and report whether `com.facebook.orca` is installed. Optional flags can install or launch the original user-supplied APK and classify error names in the current `logcat` buffer. The script **does not export raw logs, credentials, message text, contact lists, or encryption keys**. It reports device-wide error indicators only, not a proven Messenger root cause. No network proxying, bypass of TLS checks, password collection, or protocol imitation is implemented.

Suggested permitted test sequence on a volunteer-owned device with a disposable test account:

1. `python kitkat_device_probe.py --output before.json`
2. `python kitkat_device_probe.py --install "<path-to-original-API19-APK>" --launch --output launch.json`
3. Observe whether Messenger displays an update gate or a login screen. If a test account is used, keep credentials on the device. Do not share raw logs/screenshots showing personal information.
4. `python kitkat_device_probe.py --classify-logcat --output error_categories.json`
5. Decide next action from observed *on-device* behavior, not the existence of old crypto symbol strings.

The test script has not been run on a physical Android 4.4 device in this environment, since no ADB-connected device or emulator is available here.

## Decision gates for future backport work

- **Installation/startup fails with missing framework classes or native libraries:** investigate the specific local stack failure; a minimal compatibility patch might be achievable, but must be verified on-device.
- **Login server requires upgrading or rejects the old client:** the block is not solved by changing APK version constants or blindly merging DEX files. Evaluate Meta's legitimate supported interfaces before attempting distribution.
- **Encrypted chats cannot sync or decrypt:** shipping an app without correct E2EE interoperability would fail the charity goal. Do not disable E2EE, weaken TLS, forward decrypted personal messages through untrusted relays, or store credentials in the distributed APK.
- **All core test steps pass on the unmodified v410 KitKat APK:** optimize the elderly-facing launcher and onboarding *without altering Messenger*, preserving the original package signature.

## Engineering status matrix

| Verification | Status |
|---|---|
| Source APKs preserved | PASS |
| Packed archive header and all nine entry names parsed | PASS |
| Metadata filename/locator cross-check | PASS (3/3) |
| Independent XZ streams recognized and decoded | PASS (140 valid segments) |
| Full secondary DEX reconstruction | NOT DONE |
| v410 ARM-vs-x86 byte identity comparison | PASS (0/7 match) |
| Framework symbol reference scan v410 x86 vs v588 | PASS (static references only) |
| Inspector and local probe unit tests | PASS (4 tests) |
| APK install/launch on Android 4.4 | NOT TESTED |
| Messenger personal-account login, messaging, E2EE | NOT TESTED |
| Modified, working Messenger for KitKat | NOT BUILT |

## External technical context

- Meta engineering describes Superpack as a compressor for executable code such as DEX: <https://engineering.fb.com/2021/09/13/android/superpack/>
- Facebook's SoLoader details loader integrations: <https://github.com/facebook/SoLoader>
- Meta introduced default Messenger personal-chat E2EE in December 2023: <https://about.fb.com/news/2023/12/default-end-to-end-encryption-on-messenger/>
- Independent investigation confirms Messenger uses a specialized `libsuperpack-jni.so` and a DEX-oriented Superpack layout: <https://clearbluejar.github.io/posts/desuperpacking-meta-superpacked-apks-with-github-actions/>

**Note:** The static inventory and numeric comparisons above come from the actual three APKs supplied for this project. The linked material is used only to explain the wider Superpack/E2EE context.
