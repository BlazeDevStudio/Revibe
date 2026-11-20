# Stage 15 — Lollipop ARM64 side-by-side installation trial

## What changed

The user reported a generic **"App not installed"** dialog on a Mi phone for earlier Revibe and original Meta Messenger APK candidates. Android's precise package-manager error code remains unknown. One plausible cause is package/signature/provider/permission collisions with an existing Messenger installation. This stage tests that hypothesis without deleting the installed app.

**User-supplied baseline:** original Meta-signed Messenger 336.0.0.13.142, native ARM64, API21+, SHA256 `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`.

**New research APK:** user-download-only `Revibe_Messenger_Lollipop_ARM64_SIDEBYSIDE_INSTALL_TRIAL.apk`, SHA256 `4eaf15fe989b62c51f86a5145d848f12fe63ccef581ee0d6c5ffd964b4a9b1ec`. It has new package ID `org.revibe.orca01`, 18 unique provider authorities, 6 unique custom permission names, and a temporary 2048-bit RSA/SHA256 JAR/v1 signing identity. The **eight original DEX files were retained without modification**. No Meta source code or APK bytes were uploaded to this repository.

## What was checked
- Original source SHA256 verified exactly
- Android binary XML remains structurally readable and byte length unchanged
- New package and all 18 provider authorities do not use the original `com.facebook.orca` package ID
- Repacked archive ZIP CRC passed; Java `jarsigner -verify` passed
- Native ABI remains `arm64-v8a` and original Android API21+ requirement remains
- Ten synthetic binary-XML regression tests passed locally, plus GitHub tests to check

## Critical limitations

The new APK is an **installation hypothesis test, not a restored Messenger**. It has **NOT** been installed on the Mi phone. Package-ID changes may disrupt app startup, interapp providers, authentication, Firebase, notifications, calling, or server-integrity checks. A valid APK/JAR signature is not Android hardware proof.

**Do not use personal accounts, messages, charity-recipient phones, or credentials with this modified and re-signed research APK.** It must never be represented as having working Meta login, default E2EE, messages, or removed server-side update requirements.

## Reproduce

Use the separately acquired, matching original APK plus Python 3 and JDK `keytool`/`jarsigner`:

```bash
python Messenger/engineering/build_side_by_side_lollipop.py \
  --source "/path/to/original-messenger-336-arm64.apk" \
  --output "/tmp/Revibe_SideBySide_Research.apk" \
  --report "/tmp/build.json"
python -m unittest discover -s Messenger/engineering/tests -v
```

Next gate: record whether the standalone package installs on a spare Android 5/6 ARM64 Mi phone. If it installs but does not launch, isolate package-ID startup assumptions. If it still fails to install, package conflict is not the only explanation, and APK/device installer evidence is needed. Live Meta interoperability and modern encryption remain separate unsolved blockers.
