# REVIBE — Autonomous Engineer Initialization

This file is the **authoritative entrypoint** for AI coding agents continuing work in `BlazeDevStudio/Revibe`. Read it before code changes, then run `python scripts/revibe_init.py --check` from the repository root. Read `Messenger/CONTINUATION.md`, `Messenger/STATUS.json`, and the current project README. Inspect the actual GitHub branch/commit and current tool outputs before making claims.

## Mission
Revibe is an independent, AI-assisted compatibility and accessibility project giving older apps and refurbished devices a useful second life. First priority: **functional, secure, straightforward messaging for elderly recipients on Android 4.4/API 19 where technically feasible**. Do not mistake a wrapper, an installable APK, or a suppressed warning for a functioning Messenger client.

## Messenger nonnegotiable priorities
1. Preserve source APKs (never overwrite). **Never upload or commit proprietary Meta APKs, embedded native libraries, third-party signing keys, credentials, chat content or account tokens.** Publish only our independently written tooling and non-sensitive findings.
2. Work incrementally in `Messenger/`, without destructive rewrites. Each next run must check repository branch, code, tests, release status, and the last documented blockers.
3. Target Android 4.4 through Android 10, plus `armeabi-v7a`, `arm64-v8a`, and `x86` *eventually*, but only mark a particular combination supported after real-device validation. The first candidate is **API19 ARMv7 ONLY**.
4. Keep privacy/accessibility central: elderly users need a safe, low-friction experience; no browser detours or disguised server errors.
5. Never claim Meta login, encrypted messages, notifications, or voice calls work without a live test. Do not misrepresent Meta encryption or bypass genuine server-side requirements.
6. Client-side update/deprecation prompts may be investigated, but changing a local string is NOT removing an update gate and cannot restore backend functionality.
7. Re-signing an APK changes its signing identity. Warn about install conflicts, test on disposable devices, and don't collect passwords, personal accounts, serial IDs, or chat contents.
8. Run tests and prove artifact presence; report exact test numbers and limitations. Disclose failures and blockers, don't substitute fake binaries or placeholder apps.
9. Preserve prior progress, write a concise status update to `Messenger/STATUS.json` and `Messenger/CONTINUATION.md` after each milestone, and push only relevant tested sources.

## Immediately upon continuation
- Inspect repository state before making claims, including latest `main` and GitHub Actions.
- Run `python scripts/revibe_init.py --check` (tests need Python 3.8+; APK signing needs Java `keytool` and `jarsigner`; optional device tests need Android `adb`).
- Understand experimental Stage 6 APK: rebuilt from user-supplied original with two *string changes only*, v1 signed with temporary test key; **not a Messenger compatibility fix**. No public binary is committed.
- Prioritize actual observed Android 4.4 runtime behavior: install, launch, login/update gate origin, encryption send+receive. Only then pursue targeted code compatibility changes and additional ABIs.
- The next chat can start with: **"Continue Revibe from GitHub. Read AGENTS.md and run scripts/revibe_init.py --check, then work on Messenger's latest verified blocker. Do not restart or invent successful tests."**

## Stage 7 extension (2026-11-20)

Continue ARM64/API28 research only after checking `Messenger/STATUS.json`, `Messenger/CONTINUATION.md`, `Messenger/engineering/README_STAGE7.md`, and the latest main commit. An ARM64 research package was derived from the user's original Messenger 588; it is v1+experimental-v2 signed and **requires Android 9+, not KitKat**. A separate Lite research track (`com.facebook.mlite`) has been opened; Messenger Lite was discontinued in September 2023. These are research leads only. Prioritize real device diagnostics, authentic encrypted messaging, compatibility, and privacy. Do not publish proprietary Meta APKs or pretend the update gate is fixed.


## Stage 10 checkpoint (2026-11-20)
- Verified original Messenger 336 API21 ARM64 binary available to the researcher; SHA256 `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`. This **is not** a restored Messenger release.
- On next continuation, use `Messenger/reports/STAGE10_NATIVE_ARM64_336.md` and `Messenger/engineering/original_arm64_smoke.py` to classify real Android 5/6 runtime failures before modifying APKs. Do not commit third-party binaries.

## Stage 14 continuation checkpoint
- First hardware feedback is `App not installed` for supplied research APKs. See `Messenger/reports/STAGE14_LOLLIPOP_INSTALL_DIAGNOSIS.md`; do not invent root causes.
- Run the corrected `Messenger/engineering/install_failure_probe.py` on one authorized spare Android 5/6 phone. Its filtered package check now distinguishes missing `com.facebook.orca` from package-manager errors. It refuses to overwrite existing Messenger or test a wrong APK hash.
- The original Messenger 336 ARM64/API21 remains the **unchanged** baseline; do not resubmit a relabeled, identical APK as a code fix.
- No live messaging or deprecation-warning removal is verified. Obtain exact install rejection, then test startup, then authentication/E2EE. Never publish Meta APKs in this public repo.

## Stage 15 test checkpoint
- New app-ID-isolated experimental Android 5 ARM64 package created from user-supplied original Messenger336; see `Messenger/reports/STAGE15_SIDE_BY_SIDE_LOLLIPOP.md`.
- User needs simple APK tap-to-install. Do not demand ADB or a computer for the first step.
- Standalone package name `org.revibe.orca01` tries to avoid original Messenger installation collisions, but no real-device install/launch or current Meta service compatibility is verified. Signer is Revibe ephemeral, not Meta, and app code is unmodified. **Never represent this as a functional Messenger revival.**
- Before another modification, distinguish: installed, crashes on launch, or still not installed. Protect existing Messenger data and do not collect private credentials.

## Stage 16 checkpoint — respect no-computer installation
- User's Mi phone still shows `App not installed` for the side-by-side `org.revibe.orca01` package. No exact Android installer code is known. Avoid claiming that changing the app ID fixed anything.
- Verifiably prepared a **different original** Meta-signed Messenger 410 API19 ARMv7 APK for one-tap testing (SHA256 `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`) as conditional fallback if the Android OS supports ARM32. This is NOT a repaired application. Source `Messenger/engineering/prepare_original_abi_candidate.py`; 13 local tests.
- Read `Messenger/reports/STAGE16_MI_INSTALL_FALLBACK.md`; do not demand ADB or complex phone steps. Preserve truthful separation between **package verification**, **actual device installation**, and **real server messaging**.

## Product-scope correction — device-independent KitKat onward (2026-11-20)
- **Do not request a phone model, ADB, or manual ABI selection from the user.** The user explicitly requires one-tap functionality from Android 4.4/API19 onward. The product must handle OS/ABI differences without imposing a device-specific diagnosis on end users.
- Read `Messenger/DEVICE_INDEPENDENT_COMPATIBILITY.md` and use it as the current release acceptance contract. One universal APK is preferred; fallback automatic packaging may be needed. The minimum API is a target, not proof of compatibility on newer Android.
- Existing Messenger APK variants repeatedly failed install on a Mi phone; **no new fixed installer is available yet**. Stop relabeling originals and claiming repaired compatibility. Actual independent code/build and representative OS/ABI installation + full messaging tests are required.

## Stage 18: GitHub Android build / independent install probe
- Read `Messenger/reports/STAGE18_CLEAN_INSTALL_PROBE.md`. Real native Android source in `Messenger/install-probe/`, compiled with AGP 8.7.3 and API35, minSdk19/targetSdk35, no native libraries and no permissions. GitHub build `44684505264` passed, with signed APK and archive verification.
- **This is a diagnostic installer, NOT Messenger or a messaging demo.** Do not confuse an install probe with requested secure Meta-to-Meta messaging. The separate app must not gather personal data, contact Meta, or ask for a password.
- Check latest `.github/workflows/revibe-install-probe.yml` API19/23/35 emulator matrix and its actual conclusions; do not make unsupported install claims. Continue toward consistent APK signing, genuine API19+ platform support, and viable authorized secure messaging interoperability.

## Stage 18 verified platform gate
- **Real CI evidence:** `Revibe independent API19+ installation probe` workflow run `44684869636` passed APK signature/zipalign and emulator install+launch on API19 (KitKat), API23 (Android 6), API35 (Android 15). Artifact SHA256 `5945cd715fdf414639d140341b5073eca00d2d30fa1f591dcba80f10ae3947d5`.
- The probe is independent Android code, **not** a Messenger implementation. No Meta auth/chat functionality exists. Do not call this a finished revival or distribute it as one. Keep original Meta APKs outside repo.
- On continuation: use this working API19+ build/CI foundation, then implement verified **actual** messaging functionality only through authorized service interfaces; track separate login, E2EE, message exchange, background notifications and accessible UI milestones.

## Stage 19 — portable Android installer error checker
- Continue from `Messenger/install-probe` and `Messenger/reports/STAGE19_INSTALLER_ERROR_DIAGNOSIS.md`. New independent diagnostic package ID `org.revibe.installcheck` uses `PackageInstaller.Session` on API21+ to capture install errors locally without ADB. Android 4.4 still supported for app install/launch.
- New APK SHA256 `1a83b5cfa52c426540d03a4449df2fe8fa708aa7c90d7bc5dcc3a7cf0fa6bc02`, 16,753 bytes, GitHub run `44751936662`. Track emulator and actual interactive flow separately; don't infer user device results from CI.
- Never require phone model/serial/ADB. Preserve existing Messenger installations; never use personal passwords, access Meta servers without authorization, or claim this diagnostic is Messenger.

## Stage 20 continuation
- Source `Messenger/install-probe/` added a sanitized **Copy result** UI and native Android instrumentation for PackageInstaller callback categories. Updated diagnostic ID `org.revibe.installcheck2` avoids a debug-signer conflict with Stage19; no private release signing key exists yet.
- See `Messenger/reports/STAGE20_CALLBACK_VERIFICATION.md`. Emulator workflow executes a Bash script `scripts/emulator_verify.sh` so its if/fi conditional is not broken by `android-emulator-runner` running each workflow line separately.
- Do not call synthetic callback assertions a real APK installation error test. Collect actual user-selected file approval and final callback only through user authorization. No Facebook login, end-to-end encryption or chat is present. Continue prioritizing supported personal Meta Messenger interoperability and genuine device-independent Android 4.4+ compatibility.

## Stage 20 security / CI handoff
- Never authorize an install from package name alone. Stage20 uses `AllowedApks.matches(package,sha256)` against four pinned, audited APK digests; reject changed files before calling `PackageInstaller.Session`.
- The Android API21 custom instrumentation reports `PASS: N on-emulator assertions` via stream, not always `INSTRUMENTATION_CODE: 0`. The CI script was fixed to check its explicit PASS marker; inspect latest rerun, and don't conflate a test harness failure with app logic failure.
- Latest compiled diagnostic source: run `44760714269`, APK SHA256 `9ca9132eea21fdc2221527c6dbfc46c3d3d63b0aba15d6697a4ea975b4d114a5`. Still not Messenger; no Meta chat service interoperability.

## V21 master continuation directive (2026-11-21)
For continuation of the user's actual goal, **start by reading `Messenger/MASTER_CONTINUATION_V21.md`** along with this file and current repository state. Reconcile and safely clean historical research, keep the installer diagnostic distinct from the product, pursue authorized real personal Messenger interoperability, and require verified ARM32, ARM64 and x86 artifacts with separate install/launch and real messaging evidence. Never relabel a diagnostic, historic APK or simulated chat as a working Messenger release.
