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