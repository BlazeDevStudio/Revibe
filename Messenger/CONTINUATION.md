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
