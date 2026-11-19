# Messenger for Android 4.4 — Stage 4 Validation Toolkit

**This is not a modified Messenger APK and does not restore Meta server compatibility.** It is a runnable, privacy-conscious test for the user's original, unmodified Messenger 410 API19 ARMv7 APK. It verifies its SHA-256 identity, KitKat minimum SDK, native architecture, and APK v1/JAR integrity. Optionally, using ADB, it can install the original package and observe launch/process health. It does not prove login or messaging by itself.

## Requirements

- Python 3.8+ and (for signature checks) Java JDK `jarsigner`
- For device testing, Android Platform Tools `adb` and one authorized Android 4.4 test phone connected by USB; `adb` is *not* required for offline/static checks
- Your original Messenger 410 Android 4.4 ARMv7 APK, provided separately — this ZIP deliberately contains NO Meta APKs or proprietary `.so` binaries
- No root access is required and no credentials are requested by any script

## Offline quick start

Put the unmodified original APK next to these scripts or reference its absolute path:

```sh
python -m unittest discover -s tests -v
python stage4_kitkat_gate.py "/path/to/com.facebook.orca_410.0.0.17.85-312007848_minAPI19(armeabi-v7a)(160,120dpi)_apkmirror.com.apk" --output offline_result.json
```

Expected for the exact supplied APK: `is_known_original_kitkat_apk=true`, `kitkat_arm_preflight.preflight_passes=true`, `apk_v1_signature_integrity.status=verified_v1_integrity`, and `device_test_completed=false`. The Metro/Meta signature is self-signed, and strict trust-path verification is not expected to pass. Java `jarsigner -verify` checks APK v1 signed content integrity, not store provenance or backend acceptance.

## Optional real Android 4.4 smoke test

This command **installs/reinstalls and launches** the original signed APK on your connected Android device; run it only on a device you own or have authorization to test. Take account backup precautions. It never installs a patched APK.

```sh
python stage4_kitkat_gate.py "/path/to/unmodified-minAPI19-ARM.apk" \
  --adb-device --install-original --launch --output device_result.json
```

The tool refuses to run device actions if the APK's SHA-256 differs from the known original. It also refuses incompatible SDK / ABI targets. `launch_command=sent` simply means the intent was sent, while `app_process_observed_after_launch=true` indicates an observed process; neither proves the app UI loaded, login works, or messages send. In the event of a crash, the report includes Messenger-attributed error **categories** only. Account names, message text, tokens, serial IDs, and raw logs are not saved.

If the app is already installed and no installation is desired, omit `--install-original`. If you only want device info without launching, omit `--launch`.

## Test accounts / release gate

Use a disposable, authorized account on a controlled device; never enter credentials into the diagnostic CLI. Open the app normally and record **only status categories** in `MANUAL_ACCEPTANCE_TEMPLATE.json`:

1. `install`: did the original signed APK install on Android 4.4?
2. `launch_ui`: does a human see a usable screen (not just a process)?
3. `login`: can the authorized test account log in without an update block?
4. `e2ee_send`: can it send a modern encrypted personal message?
5. `e2ee_receive`: can it receive and decrypt the reply?
6. `resume`: does it still work after reboot/reconnect?
7. `family_call`: can it make and receive real voice calls (optional, not a substitute for text chat)?

All are **NOT_TESTED** until measured. Do not submit personal data with the test results. No child or vulnerable recipient should be issued a phone based only on successful static checks.

## Limitations

- Original application was built for KitKat and is installable in principle. Its current Meta authentication and default end-to-end encrypted chat compatibility remain unknown.
- Re-signing or repackaging the APK changes package signing identity, invalidates the official signature, and may prevent package updates or backend authentication.
- Meta's Superpack code still requires an effective format-aware decoder; running XZ in isolation does not reconstruct DEX.
- The phone's Android 4.4 operating system has serious age-related security limitations. Use a controlled test account and avoid sensitive personal information.

This toolkit supports evaluation of the exact APK supplied by the user; it makes no claim to be a Meta-endorsed product.
