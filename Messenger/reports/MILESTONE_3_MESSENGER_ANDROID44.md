# Messenger Android 4.4 — Engineering Milestone 3

**Date:** 20 November 2026  
**Project:** Elder-accessible refurbished Android 4.4 phone — restoring personal Messenger communication.  
**Baseline:** user-supplied Messenger 410 API19 ARMv7 (SHA-256 `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`).  
**Status:** verifiable static-research and diagnostics deliverables; **no modified Messenger APK built; no current Messenger login or messaging tested**.

## 1. Stage 3 result

Created a reproducible, one-command static analysis suite; measured DEX class-definition overlap; checked Superpack metadata cross-variant output identities; mapped the Superpack JNI native bridge for all three APKs; built an Android 4.4 offline install-compatibility preflight; improved optional logcat attribution to Messenger process PIDs; passed 13 unit tests. Original APKs were not altered. The deliverable contains **no original APKs or extracted Meta libraries**.

## 2. Class-definition comparison (real APK measurements)

| Supplied source | Standard DEX files examined | Identified class definitions | Scope caveat |
|---|---:|---:|---|
| v410.0.0.17.85 API19 ARM32 | 1 | 4,058 | Seven secondary DEX compressed in Superpack; result incomplete |
| v410.0.0.17.85 API21 x86 | 8 | 79,344 | Standard-DEX-only classes |
| v588.1.0.66.98 API28 ARM64 | 18 | 171,742 | Standard-DEX-only classes |

**62,651 class descriptor names** appear in both v410 x86 and v588 ARM64, out of 188,435 in the union; Jaccard overlap 0.332481. Descriptor identity is not implementation identity. The source APKs may include further content outside standard DEX. The KitKat's visible primary DEX overlaps v410 x86 at 3,733 classes but its seven Superpacked DEX files remain unexamined at class level.

Heuristic class-name marker counts in standard DEX only:

| Marker category | KitKat v410 primary DEX | v410 x86 | v588 ARM64 |
|---|---:|---:|---:|
| Names containing E2EE/end-to-end substrings | 1 | 13 | 353 |
| Names containing labyrinth | 0 | 0 | 1 |
| Names containing keystore/key_store | 0 | 0 | 6 |

**Interpretation:** these are simple substring matches in class *names*, not a proof of feature implementation. Renaming, obfuscation, custom native code, and Superpacked DEX files make absence particularly unreliable. No direct evidence yet that modern encrypted personal messages can be handled by KitKat.

## 3. New cross-variant output metadata finding

Meta's package metadata for v410 ARM API19 `longtail-1.dex` and v410 x86 API21 `longtail2.dex` declares the **same SHA-1**: `cb8db29f43b9fcf646df998023bfcb9855db3b54`.

This supports the hypothesis of one byte-identical intended decompressed longtail output across those two variants. It does **not** mean either `.spo` was fully decoded or that the entire APK is interchangeable. Stage 2 had already established that none of the **seven main secondary DEX** ordinal hashes matched the x86 standard DEX outputs.

## 4. Native Superpack loader discovery

The native Superpack JNI binary shipped in v410 API19 is **ELF32 ARM**; it depends on `liblog.so`, `libmemalign16.so`, and Android's `libc.so`. It advertises symbols/strings for `init_superpack_archive`, `init_superpack_file`, `createSuperpackFileNative`, `readNative`, `appendNative`, `closeNative`, `getNameNative`, and Java classes `SuperpackArchive` / `SuperpackFile`. The v410 x86 library uses a similar interface; the v588 ARM64 library uses a different ABI and does not expose the same `init_superpack_archive`/`init_superpack_file` strings.

**Implication:** an Android runtime capable of loading the exact v410 ARM native library, along with its JNI Java classes and bundled dependencies, is the credible path for full reconstruction. Running isolated XZ decompression on the host cannot recover all seven original DEX files. The supplied v588 ARM64 `.so` files cannot be loaded into a 32-bit KitKat process.

A native decoder was **not** executed, and no reconstructed DEX output is claimed. The Stage 3 ZIP deliberately excludes proprietary native library binaries.

## 5. Android 4.4 install compatibility preflight

For an API19 Android device with `armeabi-v7a` and `armeabi` support:

| APK | Manifest minSdk | Native ABI | APK contains v1 signature artifact | Preflight |
|---|---:|---|---|---|
| v410 ARM | 19 | armeabi-v7a | Yes | **PASS** |
| v410 x86 | 21 | x86 | Yes | **FAIL** (API and ABI) |
| v588 ARM64 | 28 | arm64-v8a | No | **FAIL** (API, ABI, old signature requirement) |

The preflight checks for a v1 certificate artifact but does **not** cryptographically validate v1 signing. Passing is **not** proof of installation, launch, login, or server compatibility. Prior Stage 1 APK v2 cryptographic integrity findings do not replace a KitKat v1 signature check.

## 6. Improved privacy-conscious device diagnostics

`messenger_log_sieve.py` can consume recent `adb logcat` in memory and emit only categorized errors for process IDs identified as `com.facebook.orca`. It does not emit raw logs, message text, credentials, tokens, contacts, or device IDs. If Messenger PID cannot be identified, it explicitly returns no attribution instead of guessing.

Logcat PID attribution is not perfect: delayed system-process errors and log buffers without a process anchor may be missed. Even an absence of errors cannot validate Messenger login/E2EE. The tool was tested against synthetic log fixtures; **no physical/emulated Android 4.4 device was connected**.

## 7. Exact reproducible commands

Host requires Python 3.8+; `readelf` is optional. Place all three original user-provided APKs together in a folder, then run from the unpacked Stage 3 archive:

```sh
python run_stage3.py --apk-dir "/path/to/three-apks" --output-dir results
python -m unittest discover -s tests -v
```

Only if a test device is present, owned or permitted, and Android Platform Tools/ADB are installed:

```sh
# Original, unmodified KitKat APK only (never log passwords or private chats):
python kitkat_device_probe.py --install "/path/to/v410_minAPI19_arm.apk" --launch --output launch_result.json
python messenger_log_sieve.py --adb --output messenger_error_categories.json
```

No user account credentials should be entered into the host scripts or logs. Testing accounts must be disposable and fully authorized.

## 8. Gate before attempting any patched Messenger

1. **On-device smoke test:** Does the original signed v410 ARM APK install and reach the first screen? If yes, record only non-sensitive outcomes.
2. **Login/update gate:** Does today's Meta backend accept an authentic authorized test account? If it rejects outdated clients, blind version spoofing or class substitution is not a reliable fix.
3. **Encryption:** Can an account with current default Messenger E2EE genuinely send, receive, restore and decrypt a test conversation? If not, do not distribute the client as functional.
4. **Patch minimal reproducible failure only:** If a local missing class/native dependency is identified and resolvable, build from that concrete evidence, retain a clear test provenance, and re-sign any changed APK; never misrepresent the result as official Meta software.

We have not crossed gates 1–3 yet. Thus **no working KitKat Messenger APK is represented in this milestone**.

## 9. Package contents and verification

`run_stage3.py`, `android44_apk_preflight.py`, `dex_class_matrix.py`, `cross_variant_spo.py`, `superpack_native_surface.py`, `messenger_log_sieve.py`, carry-over Stage 2 inspection/probe scripts, parsers and tests, and generated read-only JSON evidence. All 13 unit tests pass; the `run_stage3.py` end-to-end static pipeline successfully reproduced the supplied three APK analyses.

## External context, distinct from APK-derived measurements

- Meta: Superpack compresses DEX code using format-aware transformations: https://engineering.fb.com/2021/09/13/core-infra/superpack/
- Independent analysis of Messenger's distinct `libsuperpack-jni.so` API: https://clearbluejar.github.io/posts/desuperpacking-meta-superpacked-apks-with-github-actions/
- Meta's December 2023 default Messenger E2EE rollout: https://about.fb.com/news/2023/12/default-end-to-end-encryption-on-messenger/
- Meta on secure storage and multi-device encryption: https://engineering.fb.com/2023/12/06/security/building-end-to-end-security-for-messenger/
