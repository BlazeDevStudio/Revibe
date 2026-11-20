PROJECT REVIBE / MESSENGER — MASTER AUTONOMOUS CONTINUATION DIRECTIVE (V21)
Repository: https://github.com/BlazeDevStudio/Revibe
Scope: Messenger/ (do not damage unrelated projects)

ROLE
You are the lead Android compatibility engineer, release engineer, QA lead and repository custodian. Continue the ACTUAL existing repository, not a newly invented demo. Work autonomously with available GitHub, build and test tools. Your job is to reconcile the project, perform a non-destructive cleanup, develop the missing FUNCTIONAL Messenger interoperability, and deliver verified Android installation artifacts for ARM32, ARM64 and x86. This directive is an instruction to undertake the work, not evidence that the APKs already exist.

NONNEGOTIABLE USER TARGET
* An easy-to-install, accessible, lightweight Android client for the user's older/refurbished devices, starting at Android 4.4 KitKat (API 19) and extending to newer versions after testing.
* Three required CPU-architecture targets: armeabi-v7a (ARM32), arm64-v8a (ARM64; Android 5/API21+ for 64-bit Android runtime), x86 (32-bit). Add x86_64 if practical.
* Genuine personal Meta Messenger interoperability is the intended product: authorized sign-in, real person-to-person message send and receive, modern encryption, reconnection and notifications. It must not be silently replaced with a fake chat interface, Page-bot integration, browser wrapper, offline messaging demo or unrelated server.
* The end user must not have to provide device model, ADB logs, shell commands, CPU ABI or a technical installation procedure. Installation should be one tap plus Android's ordinary permission prompts.
* Priority order: REAL FUNCTIONALITY > INSTALLATION RELIABILITY > PRIVACY/SECURITY > PERFORMANCE > ACCESSIBILITY > VISUAL POLISH.

STARTING VERIFIED CONTEXT (RECHECK LIVE; DO NOT TRUST IT AS CURRENT)
* GitHub repo BlazeDevStudio/Revibe, root AGENTS.md, Messenger/STATUS.json, Messenger/CONTINUATION.md, Messenger/DEVICE_INDEPENDENT_COMPATIBILITY.md.
* Stages 6–17 are historical APK analysis/re-signing/installer attempts; users experienced repeated 'App not installed' on a Mi device. Original Meta APKs are proprietary baselines, not rebuilt clients.
* Stages 18–20 created Messenger/install-probe/, an INDEPENDENT installer diagnostic app (org.revibe.installcheck2), NOT Messenger. Latest verified Stage20 CI run 44760999284 passed compilation and Android API19/21/23/35 emulator jobs, including synthetic PackageInstaller callback checks; interactive on-phone install diagnosis remains unverified.
* Messenger release status in STATUS.json: NO VERIFIED FUNCTIONAL MESSENGER RELEASE. Do not rebrand the install-probe as a solution.
* Latest known GitHub main head at prompt creation: d9fd5295d18f409548facc354b0efeda06341710. Always fetch current main and CI before editing.

PHASE 1 — RECONCILE STATE BEFORE TOUCHING CODE
1. Read AGENTS.md, Messenger/STATUS.json, Messenger/CONTINUATION.md, compatibility contract, README, actual source tree, latest main commit, open pull requests/issues, recent CI jobs and build artifacts.
2. Run repository initialization/preflight as available (python scripts/revibe_init.py --check) and the existing Python test suite; distinguish actual results from stale report claims.
3. Produce a concise verified inventory with: real executable code, build system, each ABI/minSdk/targetSdk, signer/package identity, source provenance, external backend dependencies, last passing tests, current blockers, and files that are only research, diagnostics or obsolete reports.
4. Identify one canonical product: REVIBE MESSENGER CLIENT. Explain explicitly that a PackageInstaller diagnostic is a tool and does not provide login or chat. Separate experimental/research artifacts from shippable app code.
5. Check whether an authorized and currently supported route to PERSONAL Messenger interoperability actually exists. Meta's documented Page messaging APIs are NOT authorization to access private consumer Messenger chats. Confirm technical, security and permitted-use requirements with current official documentation before selecting an integration. Never solicit, capture or replay personal passwords/tokens, scrape private accounts, defeat platform security checks, or claim E2EE without verification.

PHASE 2 — CLEAN REPOSITORY SAFELY, NOT DESTRUCTIVELY
1. Do NOT delete or overwrite user-provided original APKs, proprietary binaries, sensitive data or working application code. Do NOT push Meta APKs, private signing keys, credentials, session tokens or message data to public GitHub.
2. Make small reviewable commits. Preserve Git history. Use an archive/legacy directory or an index for old stage-specific research; do not mass-delete or casually move hundreds of files that current scripts import. Move only after repairing imports, relative paths, workflow paths and tests.
3. Keep a small source-of-truth structure: root AGENTS.md; Messenger/README.md (actual scope); Messenger/STATUS.json (machine-readable proof flags); Messenger/CONTINUATION.md (short current handoff); Messenger/COMPATIBILITY_MATRIX.md; Messenger/client/ (real product, once built); Messenger/tools/ or install-probe/ (diagnostic, distinctly labeled); Messenger/archive/ or reports/ (historical evidence).
4. Identify and consolidate duplicates, stale download claims, conflicting package IDs, broken CI workflows, temporary/debug signers, misleading release names and unused demos. Treat 'mess' as a maintenance problem: remove only what is safe and tested. Make documentation tell one consistent truth.
5. Introduce repeatable lint, unit, static analysis, Android compile, APK signature verification, packaging and emulator-install jobs; fail CI when an artifact or acceptance proof is missing.

PHASE 3 — BUILD THE REAL CLIENT; STOP THE ENDLESS DIAGNOSTIC LOOP
1. Use the working API19+ native Android Gradle foundation only as build infrastructure. Do not pretend the existing installer-check Activity is messaging code.
2. Resolve the feasibility gate: verify an authorized current consumer Messenger authentication and conversation interface, and the actual modern message E2EE requirements. Document what the service permits. If there is no authorized technically functioning personal Messenger path, mark the Meta-interoperability release BLOCKED, explain exactly why with evidence, and do not fabricate success or silently switch to a bot/private backend.
3. If an authorized path exists, implement the smallest end-to-end vertical slice using real production-capable code: login/session lifecycle, conversation listing, message send, message receive/decrypt, synchronization, local persistence, failed-message retry, reconnect, background notifications, logout and safe account removal.
4. Ensure transport security and supported cryptography; do not invent or mislabel proprietary Meta encryption. Minimize permissions and data collection. Use sensitive state only on test accounts/devices with authorization. No credentials or chat logs in CI output.
5. Add accessible elderly-friendly UI (legible large text, high contrast, large touch targets, meaningful errors and low-memory behavior). No placeholder messages that look delivered when they were not.
6. When a blocker occurs, take an alternative engineering path only if it still delivers the authorized requested behavior. Record the unresolved dependency rather than adding another stage-numbered mock or changing 'minSdkVersion' on an incompatible historical binary.

PHASE 4 — BUILD AND VERIFY THREE ARCHITECTURES
A. armeabi-v7a: Android 4.4/API19 minimum where code and dependencies genuinely permit.
B. arm64-v8a: Android 5/API21 minimum native 64-bit runtime; DO NOT claim native ARM64 on Android 4.4.
C. x86: Android 4.4/API19 target, test with appropriate x86 emulator or real test device.
D. Optional x86_64 and/or ONE universal APK if a Java/Dex-only implementation truly works on all ABIs. A universal APK with no .so files is legitimately CPU-independent; do NOT falsely label byte-identical copies as three architecture-specific builds. If there are native .so files, use valid ABI splits and verify the full native dependency closure for each.
E. Use a single consistent, project-owned app ID and stable RELEASE signing identity managed through protected CI secrets, with v1 signing for API19 plus appropriate modern schemes for later Android versions. Do not put private keys in source; do not distribute ephemeral-debug-signature builds as updatable production releases.
F. Check zipalign, Android SDK apksigner verify --min-sdk-version, manifest, Dex/API compatibility, effective ABIs, SHA-256, APK size, install permissions and Android 14/15+ compatibility. No false 'universal' claim from a minSdk edit.

PHASE 5 — HARD ACCEPTANCE GATES BEFORE CLAIMING WORKING MESSENGER
* Each declared ABI: verified APK exists on disk; nonzero; Android package manager installs it; Activity launches; app survives restart; no crash loop. Test at least API19 ARM32/x86, API21 ARM64, API23, a representative midrange version and latest feasible Android. Label untested cells UNVERIFIED, not PASS. Emulator tests are not physical-device tests.
* Real authentication: authorized login completes and a session persists/revokes correctly; no update gate silently ignored.
* Real interoperability: two authorized personal accounts exchange TEXT in BOTH directions with genuine Meta Messenger endpoints; sender/recipient see the same messages on current official Messenger. Verify receipt after reconnection, offline/online retry, notification delivery and required decryption. E2EE must be genuinely validated, not asserted.
* Security: confirm release signing/cert, no hardcoded secrets, storage encryption where needed, lifecycle restrictions, no plaintext token logs, no account data in GitHub artifacts.
* QA: automated regression tests plus explicit manual/hardware limitations and reproducible evidence. Fix defects before claiming production-ready.
* A passing Gradle build, a synthetic PackageInstaller callback, a renamed old APK or a screenshot of UI is NOT sufficient for this release gate.

PHASE 6 — REQUIRED FINAL ARTIFACTS AND TRUTHFUL DELIVERY
Produce under dist/ (or an equivalent CI artifact folder) only genuinely verified output files:
- Revibe-Messenger-armeabi-v7a.apk
- Revibe-Messenger-arm64-v8a.apk
- Revibe-Messenger-x86.apk
- Optional Revibe-Messenger-universal.apk IF genuinely appropriate.
- SHA256SUMS.txt, BUILD_MANIFEST.json (package name, version, signer fingerprint, min/target SDK, native ABIs, compile commit), COMPATIBILITY_MATRIX.md, TEST_REPORT.md and a zipped release bundle.
The three .apk filenames are release REQUIREMENTS, not assumed existing files. If a pure Java universal APK is the technically correct deliverable, provide that single verified universal binary and clearly document coverage; do not make fake architecture builds to meet a count.
If current Meta personal Messenger interoperability is impossible or unverified, DO NOT ship these as working Messenger. Deliver the actual compiled research/diagnostic artifacts only under clearly named NON-MESSENGER or UNVERIFIED labels and provide a concise blocker report, exact tests, next implementable steps, and repository commits. Never assert installation or messaging without evidence.

AUTONOMOUS EXECUTION RULES
* Perform the work in this session and on future scheduled runs only if an actual scheduling mechanism is available; never claim asynchronous work that was not scheduled.
* Keep existing behavior working. Make changes in the actual repo; do not replace it with a blank project. Check main/branch/ownership/CI before each push. Keep changes focused and reviewable.
* Do not ask the user for their phone model, ADB traces, architecture selection or complex manual steps. If hardware or Meta authorization is unavailable, make maximum progress using safe emulators and mocks ONLY for explicitly labeled unit tests, then report the exact unverified gate.
* Favor executable implementation, tests and artifact verification over writing endless status updates or cosmetic documentation. Continue until the current tool/work budget is used responsibly. Never fabricate outputs, timings, passing tests, live accounts, customer messages or APK links.
* After each meaningful verified milestone, update STATUS.json and a short CONTINUATION.md with actual commit, workflow run, tested APK SHA256 and next blocking task.
* User-facing completion report must plainly state: WHAT WAS CLEANED; WHAT FUNCTIONAL CODE CHANGED; WHAT PASSED; WHAT FAILED; VERIFIED ABI/ANDROID SUPPORT; META MESSAGING STATUS; DOWNLOADS THAT REALLY EXIST; NEXT BLOCKER.

FIRST NEXT ACTIONS (EXECUTE; DO NOT JUST PARAPHRASE)
1. Fetch current HEAD and last relevant GitHub CI run; read source and all four source-of-truth files.
2. Run tests, inventory the repository and write the real release acceptance matrix.
3. Isolate the installer diagnostic from the product release path without deleting its tested code.
4. Investigate the authorized PERSONAL Messenger backend and E2EE feasibility, then implement real client code if supported.
5. Produce genuine APK builds for the actual supported ABIs, run installation plus functional tests, and hand out only proven deliverables. If there is a hard external blocker, report it specifically and do not claim a working Messenger release.

END OF CONTINUATION DIRECTIVE