# Revibe Messenger — continuation handoff (Stage 7)

**Always start:** read root `AGENTS.md`, run `python scripts/revibe_init.py --check`, inspect GitHub latest main, `Messenger/STATUS.json`, and current APK/report status. Preserve previous work, never invent a successful login or build.

## Target
Restore real Messenger-to-Messenger messaging for elderly users on refurbished Android 4.4 KitKat where technically possible, eventually supporting Android 4.4–10 and ARMv7/ARM64/x86. Privacy, low resource requirements and reliable communications take priority over package appearance.

## Exact artifacts to date
- Stage6: API19 `armeabi-v7a` research APK from Messenger 410; only two English resource strings changed; v1 signed with temporary test key; NOT live tested.
- Stage7: API28 `arm64-v8a` research APK from Messenger 588; only one English resource string changed, v1 and experimental APK v2 self-signed; local ZIP CRC and v2 digest verification passed; no Android SDK apksigner cross-check or device test. *Does not install on Android 4.4–8.1.* Re-signing may break Meta login and conflicts with official installed Messenger.
- Stage7 Messenger Lite study: archived Lite `com.facebook.mlite` 338 for Android 4.0.3+ may be a useful lightweight architecture/UI baseline. Lite was discontinued in September 2023 and no Lite APK has been inspected here yet. No assertion of working current server messaging.

## Next verification gates
1. Cross-verify the Stage7 signed APK with official Android SDK `apksigner` and ADB on **disposable** devices, avoiding real accounts and private data.
2. Determine exact original vs re-signed install/start behavior; diagnose signing-related self-checks, local update prompts, network rejection and E2EE capabilities separately.
3. Obtain a legally sourced Messenger Lite v338 APK and inspect its manifest, native ABI, dependency tree, size, and client UI; compare with Messenger 410 and 588, not just filenames. Do not publish proprietary bytes.
4. Only ship a Messenger revival after authenticated two-way encrypted personal messages, reconnection and notifications work under authorization. Do not suppress meaningful warnings merely to hide service failure.
5. Maintain tests, status, ABI matrix and handoff; do not re-create a demo or false compatibility claim.

## Source commands
```sh
python -m unittest discover -s Messenger/engineering/tests -v
python Messenger/engineering/build_arm64_research.py --original /path/to/your/Messenger588-arm64.apk --output /tmp/Revibe_ARM64_RESEARCH.apk --report /tmp/stage7.json
```

Third-party APKs must remain off GitHub. No signed APK is distributed by the public repository.

## Stage 8 correction: Android 5 and 6 on a 64-bit CPU

- Use the **ARMv7/API19 Stage 6 research APK** on Android 5 or 6 only if the device OS lists `armeabi-v7a` among supported ABIs.
- Never label the Messenger 588 ARM64/API28 package compatible with Android 5 or 6; changing `minSdkVersion` is not a valid fix.
- ABI checker: `python Messenger/engineering/android56_abi_check.py --apk /path/to/ARM32-research.apk` (read-only, requires ADB unless manual API/ABI flags supplied).
- The test download is the **same binary** as the Stage 6 candidate, SHA-256 `7e1a128728935ca3b9afd4079a7018b31c00b6215067514dfee8adc6ca5e66dd`.
- No real hardware install, login, end-to-end messaging, deprecation-gate repair or native ARM64/API21 port is established.
- See `Messenger/ANDROID_5_6_ARM64_COMPATIBILITY.md` and continue toward a real, safely observed device error.


## Stage 9: genuinely native Android 5/6 ARM64 baseline
- Read `Messenger/NATIVE_ARM64_ANDROID5_BASELINE.md` and `Messenger/reports/STAGE9_NATIVE_ARM64_FINDINGS.md`.
- APKMirror archived original Messenger 336.0.0.13.142, versionCode 297217556, single APK for arm64-v8a/nodpi/Android 5.0 API21+.
- **We have not obtained or executed the 336 APK**. Do not mistake an archive listing for verified client compatibility or a new APK deliverable.
- Run the read-only `Messenger/engineering/native_arm64_gate.py` with --verify-signature --verify-meta-cert once the authentic original file is available.
- Fourteen new offline unit tests pass locally; the known ARMv7, x86, and API28 ARM64 source APKs all fail the API21 native ARM64 gate as expected.
- Next decisive gate: obtain and validate exact APK bytes; test on spare authorized Android 5/6 ARM64 hardware; classify auth/version/E2EE blockers before any patch.
- Never commit Meta APKs, keys, personal-account data or chat contents. A package that installs is not a functioning Messenger revival.


## Stage 10 — verified ORIGINAL ARM64 Android 5/6 baseline
- User supplied Messenger 336.0.0.13.142 API21 ARM64. SHA256 `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`.
- APK manifest, ARM64 ELF libraries, ZIP CRC, Meta certificate identity and JAR/v1 cryptographic signature verified offline. Static Android 5/API21 and Android 6/API23 gates pass.
- This is an **original Meta-signed APK**, NOT a modified/revived Messenger. Use it for first device test; don't re-sign just to remove an update warning.
- New privacy-preserving runner: `python Messenger/engineering/original_arm64_smoke.py --apk /path/to/original336.apk --output /tmp/preflight.json`; optional authorized spare-device install requires `--install --ack-test-device --launch`. It never overwrites an existing package or logs private data.
- 14 new runner unit tests passed locally; previous Stage 9's 14 tests also passed. No ADB device connected, no live login/E2EE or notification test. See `Messenger/reports/STAGE10_NATIVE_ARM64_336.md`.

## Stage 11 — Verified ARM64 native notes / safer device smoke test
- Re-read this repository's root AGENTS.md and run scripts/revibe_init.py --check before doing work.
- The original Meta-signed Messenger 336 ARM64/API21 has 18 native libraries. Each carries a native Android API21 ELF note. This is a static platform confirmation, **not** a restored Messenger login or runtime test.
- New source: Messenger/engineering/elf_android_api_audit.py. Its eight offline tests run through the existing test discovery workflow.
- Diagnostic safety fix: original_arm64_smoke.py now refuses **both** install and launch if com.facebook.orca already exists because the installed variant's signature/version are not verified. New regression test covers this case.
- Stage 11 subset: 23 local unit tests passed; no ADB/hardware tests, login, messages, notifications, update-gate bypass or modified new Messenger APK.
- The old APK includes mandatory-update keyword matches; their mere presence cannot establish a client-side or server-side block.
- NEXT GATE: first authorized Android 5/6 device install/launch and non-sensitive failure-category observation, followed only by a targeted proven compatibility repair. Keep third-party APKs off GitHub.

## Stage 12 follow-up — first real install failure (2026-11-20)
- User reports `App not installed` for Revibe research APKs, without the exact package-manager failure code. Do NOT declare a root cause from generic installer text.
- The public repo includes `Messenger/INSTALL_FAILURE_DIAGNOSIS.md` and read-only-by-default `Messenger/engineering/install_failure_probe.py`.
- Run without arguments to collect only API level, ARM64 ABI availability, and whether `com.facebook.orca` already exists (no serials/chat data). An opt-in install test requires the pinned original Meta-signed Messenger336 APK plus `--install --ack-test-device`; it refuses to overwrite a pre-existing package.
- New offline tests: `Messenger/engineering/tests/test_install_failure_probe.py`; check GitHub CI completion before claiming passing results.
- Next blocker: obtain Android's actual `INSTALL_FAILED_*` or `INSTALL_PARSE_FAILED_*` rejection code from an authorized spare device. Compare original Meta-signed 336 vs any re-signed APK only AFTER documenting the exact cause. No revived Messenger release exists.

## Stage 13 — Lollipop 64-bit test package (2026-11-20)
- Prepared **byte-identical** original Meta-signed Messenger 336 `arm64-v8a` Android API21 test download. Verified pinned SHA256 `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`; it is NOT a modified Messenger or functional revival.
- New reproducible source: `Messenger/engineering/prepare_lollipop_test.py`; source/target hash, ZIP CRC, native ABI, original JAR/v1 signing required, no source edit or output overwrite. Six new offline unit tests passed locally in Stage 13.
- Documents `Messenger/LOLLIPOP_ARM64_INSTALL_TRIAL.md` and `Messenger/reports/lollipop_arm64_test_manifest.json`.
- Test on authorized disposable Android 5.0/5.1 native ARM64 OS, not merely a 64-bit CPU with 32-bit OS. Do not uninstall existing Messenger with important data. Do not ask recipients to use experimental APKs.
- **No device install or modern Messenger messages verified.** The user's earlier “App not installed” report still lacks an exact Android `INSTALL_FAILED_*` category. That must be captured before patching code or resigning anything.

## Stage 14 — Android 5/6 Lollipop installation diagnosis (2026-11-20)
- Reverified original Meta-signed Messenger336 ARM64/API21 bytes; Stage13 test APK remains byte-identical and is NOT a newly revived Messenger.
- Fixed `Messenger/engineering/install_failure_probe.py`: replaces `pm path` (which can return a nonzero code when a package is merely absent on older Android versions) with exact filtered `pm list packages`, distinguishing present/absent/unknown. New `package_state_probe.py` and tests cover edge cases and avoid exporting installed-app lists.
- Stage14 report: `Messenger/reports/STAGE14_LOLLIPOP_INSTALL_DIAGNOSIS.md`.
- Offline tests in local Stage14 sample: 51 passed. Confirm CI for latest GitHub HEAD before claiming remote green.
- **Still no physical-device install result or repaired login/E2EE protocol.** Next run should prioritize an exact `INSTALL_FAILED_*` code with the safe, opt-in probe on authorized spare hardware. Do not infer a cause from the generic UI prompt.

## Stage 15 — one-tap native ARM64 Lollipop installation experiment
- User explicitly cannot perform complicated installation/ADB. Honor simple tap-to-install testing. Never require commands as prerequisite for trying the APK.
- Built new **side-by-side experimental APK** from supplied Messenger336 original with package `org.revibe.orca01`, rewriting 18 provider authorities and 6 declared custom permissions to avoid collisions; DEX files unchanged. SHA256 `4eaf15fe989b62c51f86a5145d848f12fe63ccef581ee0d6c5ffd964b4a9b1ec`.
- Builder and synthetic tests: `Messenger/engineering/build_side_by_side_lollipop.py`, `Messenger/engineering/tests/test_side_by_side_lollipop.py`; report: `Messenger/reports/STAGE15_SIDE_BY_SIDE_LOLLIPOP.md`. The original Meta APK and re-signed outputs must NOT be committed to public GitHub.
- Offline checks passed, but **hardware installation, startup, Meta login, E2EE and notifications are NOT demonstrated**. Changing package/signature could make the app crash or be rejected by Meta. Do not request or collect real passwords.
- This is a narrow collision-isolation hypothesis, not a repaired Messenger release. Next step is the user's installation/launch outcome, then a targeted fix.

## Stage 16 — Mi installer still rejects side-by-side ARM64 (2026-11-20)
- Actual field result: the user reports `App not installed` for the Stage15 `org.revibe.orca01` install trial on Mi. This falsifies changing package ID as a sufficient fix.
- Alternative no-ADB path: an **unchanged Meta-signed original** Messenger 410 ARMv7/API19 APK, checksum `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`, signature fingerprint `e3f9e1e0cf99d0e56a055ba65e241b3399f7cea524326b0cdd6ec1327ed0fdc1`. It is smaller and supports 32-bit Android OS images that may run on marketed 64-bit CPUs. Prior Stage6 ARM32 Revibe APK was **modified/re-signed**; this original is a distinct test. No live install guarantee.
- New source and tests: `Messenger/engineering/prepare_original_abi_candidate.py` and `Messenger/engineering/tests/test_prepare_original_abi_candidate.py` (13 local tests). Report: `Messenger/reports/STAGE16_MI_INSTALL_FALLBACK.md`.
- The original ARM64/API21 Messenger336 remains valid only on OS images with `arm64-v8a`. Do not infer device OS ABI from CPU marketing.
- NEVER claim that original 410 or 336 restores Meta login, E2EE, messages or deprecation compatibility. Do not publish proprietary APK files/keys. Next investigate field install/launch with simple, non-invasive user feedback; avoid ADB requirement.

## Stage 17 — Xiaomi original ARM32 fails immediately; ARM64 takes longer (2026-11-20)
- Firsthand user feedback: the original Meta-signed Messenger410 ARMv7/API19 trial immediately says **App not installed**. Previously tested original and separate-package ARM64/API21 APKs take longer, then say **App not installed**.
- Treat *time to failure* as non-diagnostic: file sizes, verification paths and OEM installer behavior vary. Do not assert ARM32 is unsupported or ARM64 is supported based on this observation alone.
- Static manifests verified: source Messenger410 is API19 + armeabi-v7a, 44,136,716 bytes; Messenger336 is API21 + arm64-v8a, 60,954,119 bytes; side-by-side 336 remains API21/ARM64 with changed installer identity and signer. No known mandatory hardware feature other than OpenGL ES 2.0.
- Under no circumstances claim a successful install, login, update-gate bypass or E2EE; the UI failure occurs before app launch. The user does not want ADB or complicated installation.
- Next low-friction evidence: ask only for a screenshot of **Settings > About phone** showing model and Android version; do not request IMEI/serial. Before creating any further APK, establish actual Android OS and ABI policy. Official Android package installer uses generic **App not installed** text for different underlying failures.

## Device-independent scope directive — KitKat onward
The user explicitly declines phone-specific details. Do not ask for Mi model, screen info, ADB or commands again as a prerequisite. Product goal is **one-tap Android 4.4/API19 and up**, with ARMv7, ARM64, x86 support and modern Android forward-compatibility verified separately. Prefer a single universal APK; if not feasible, ensure ABI-specific delivery is selected automatically. Read `Messenger/DEVICE_INDEPENDENT_COMPATIBILITY.md`. Avoid more renamed/re-signed historical APK trial downloads without a demonstrated package-compatibility repair. No real functioning Messenger restored yet. Tests across Android versions and actual Meta E2EE service are required, not merely `minSdk=19`.

## Stage 18 — Actual Android source and APK compilation (2026-11-20)
- Read `Messenger/reports/STAGE18_CLEAN_INSTALL_PROBE.md`. Independently implemented `Messenger/install-probe/`: NO Meta code, native libraries, network, permissions or user data.
- True Android Gradle compiled and signed diagnostic APK, `org.revibe.installprobe`, `minSdk19`, `targetSdk35`. GitHub Actions successful build https://github.com/BlazeDevStudio/Revibe/actions/runs/44684505264, 9 source tests passed, SDK apksigner for API19 and ZIP alignment passed; compiled APK SHA256 `3fd07a210318ae7f69541d5ae61ccb685ef2a4250ba4defdc02a3ced72122ec5`, 10,042 bytes.
- GitHub workflow now includes API19/API23/API35 emulator install+launch matrix; **inspect actual run results before claiming hardware/emulator success**.
- The probe is an installability diagnostic only; no Facebook login/chat. Never describe it as a Messenger revival or suggest users enter credentials.
- Next: resolve any emulator installation or startup failures. If APK works, use the reproducible API19+ app/build pipeline as a foundation for independent app features; real Meta interoperability requires authorized supported APIs and demonstrated E2EE.
- Do not request phone model/ADB from user; product is device-independent and one-tap.

## Stage 18 completed verification: emulator matrix green (2026-11-20)
- GitHub Actions run https://github.com/BlazeDevStudio/Revibe/actions/runs/44684869636 **PASS**. The independently authored install probe installed and launched in Android **4.4/API19**, **6/API23** and **15/API35** emulator instances. CI verified signed APK from API19, ZIP alignment, target35, and source tests.
- The exact CI artifact used by all three emulator jobs was downloaded: 10,044 bytes, SHA-256 `5945cd715fdf414639d140341b5073eca00d2d30fa1f591dcba80f10ae3947d5`. It is a diagnostic, **not Messenger**. It has no native code or network access and cannot send messages.
- Do not call this phone-specific installation or live Messenger compatibility. It proves the *independent build pipeline* can produce an APK installable and launchable in three representative Android emulators.
- Next work: move beyond package renames and build actual independent client functionality, but be honest that Meta server authorization and E2EE compatibility may require support by Meta. Continue maintaining API19+ cross-platform release gates; never claim restored secure Messenger without end-to-end tests.
