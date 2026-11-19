# Revibe Messenger — Android 5/6 on a 64-bit ARM phone

**Corrected compatibility direction:** use the Stage 6 Android 4.4/API19 `armeabi-v7a` research candidate on Android 5 (API21/22) or Android 6 (API23) **when the OS includes its 32-bit ARM runtime**.

Do **not** use the Stage 7 native `arm64-v8a` Messenger 588 research APK: its manifest requires Android 9 (API28).

## Candidate and verification

- Candidate: the original Stage 6 re-signed Messenger 410 research APK, **not** a newly ported native ARM64 build.
- Expected candidate SHA-256: `7e1a128728935ca3b9afd4079a7018b31c00b6215067514dfee8adc6ca5e66dd`.
- APK has only `armeabi-v7a` native shared libraries and retains source manifest/main DEX.
- Offline ZIP/JAR signature verified; device installation, login and messaging **not tested**.
- Two update-warning **text labels** were modified; no update gate, authentication or encrypted message protocol was fixed.

## Check whether the device accepts ARMv7 apps

With ADB on an authorized test device:

```sh
adb shell getprop ro.build.version.sdk
adb shell getprop ro.product.cpu.abilist
```

21 or 22 means Android 5.x; 23 means Android 6. If the ABI list includes `armeabi-v7a`, the 32-bit candidate meets basic OS/ABI requirements. `arm64-v8a` **alone** is not enough.

Run the read-only Revibe check:

```sh
python Messenger/engineering/android56_abi_check.py --apk /path/to/Revibe_Messenger_API19_ARMv7_RESEARCH_ONLY.apk
```

Without ADB, for a known device ABI list:

```sh
python Messenger/engineering/android56_abi_check.py --apk /path/to/Revibe_Messenger_API19_ARMv7_RESEARCH_ONLY.apk --sdk 23 --device-abis arm64-v8a,armeabi-v7a
```

## Testing warnings

- Use a disposable phone, not a charity recipient's device.
- The candidate package is `com.facebook.orca`, but it uses a **temporary research signing certificate**, not Meta's. It will conflict with the official installation. Removing the official app may remove local data.
- Never enter a real account password or collect private messages during initial smoke tests.
- APK installation alone proves nothing about Meta login, default end-to-end encryption, calls or notifications.
- Do **not** lower the Android 9 ARM64 APK's `minSdkVersion` and claim compatibility: API 28 native/framework dependencies may crash on Android 5/6.

## Next milestone

Test the pinned ARM32 candidate and original Meta-signed 410 separately on an Android 5/6 ARM64 **device with ARM32 runtime**; record redacted launch/error categories. Native ARM64/API21 porting remains a separate, unimplemented engineering task.
