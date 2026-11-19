# Revibe Messenger — continuation handoff

**Start here on each future engineering run:** read ../AGENTS.md; run `python scripts/revibe_init.py --check`; check main HEAD, existing code, previous reports and current status. Never restart blindly.

## Mission
Revive useful real Messenger-to-Messenger communication on refurbished Android 4.4 (API 19) devices, ideally covering Android 4.4–10 and ARMv7, ARM64 and x86 eventually. Reliability, accessibility, privacy and actual communication matter more than packaging or bypassing warnings.

## Current verified state (Stage 6)
* Three source Messenger APKs studied; genuine KitKat Messenger 410 API19 ARMv7 variant is our first baseline.
* Earlier Stages 1–5 provide cryptographic checks, APK/DEX/Superpack analysis, an Android 4.4 preflight and update-prompt inventory.
* Experimental Stage 6 rebuild: repackage the user's original KitKat APK, change **only two UI warning strings**, then sign with temporary research v1 key. New candidate ZIP integrity, v1 signature and basic API19 ARMv7 static compatibility were verified locally.
* **No Meta encryption, version-gate logic or login functionality was changed or restored.** An altered client will not update an existing Meta-signed installation and could fail any app signature checks.
* No physical Android device or authenticated Messenger test was available. No working Messenger variant has been established.

## Rebuild and test (only controlled disposable devices)
Provide your separately acquired original Messenger 410 API19 ARMv7 APK matching the pinned SHA256. Java JDK with keytool and jarsigner required.
```sh
python Messenger/engineering/build_experimental_apk.py --original /path/to/original-API19-ARMv7.apk --output /tmp/Revibe_Research.apk --report /tmp/research_build.json
python Messenger/engineering/candidate_smoke.py --apk /tmp/Revibe_Research.apk --install --ack-test-device --launch --output /tmp/adb_result.json
```
The second command requires ADB and **one owned/authorized disposable phone**. Backup/uninstall the conflicting official package before an experiment. Never use a charity recipient's account/device.

## Priorities for the next session
1. Confirm the original or research APK **installs and launches** on an actual API19 ARMv7 device.
2. Record redacted error categories for actual Meta login and client-side update screen, without saving credentials, chats, or account IDs.
3. Distinguish local update prompt from server-required version change and missing E2EE support. Merely hiding a prompt does not restore messaging.
4. Only after a failure is demonstrated, make a minimal targeted repair with repeatable tests. Recheck signer integrity and affected device compatibility.
5. Publish legitimate scripts, reports and docs under Messenger; **do not commit Meta APKs, proprietary libraries, credentials, or signing keys**.

**Reminder:** three ABI variants and Android 4.4–10 compatibility remain goals, not tested deliverables. Stage 6 is a research-only APK, not a distribution release.
