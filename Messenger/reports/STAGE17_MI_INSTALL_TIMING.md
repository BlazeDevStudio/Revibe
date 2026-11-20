# Stage 17 — Xiaomi installation result, timing does not diagnose root cause

User-reported field observation on 2026-11-20: original Messenger 410 ARM32/API19 APK gives **App not installed immediately**. Messenger 336 ARM64/API21 builds previously took longer and gave the same generic error. The side-by-side `org.revibe.orca01` ARM64 trial also failed. Multiple real installation rejections are reported; this is not a functional Messenger release.

## Reverified static distinctions

| APK | Byte size | Android API minimum | Native libraries | Identity/signature |
|---|---:|---:|---|---|
| Original Messenger410 | 44,136,716 | 19 | armeabi-v7a | com.facebook.orca, original Meta signer |
| Original Messenger336 | 60,954,119 | 21 | arm64-v8a | com.facebook.orca, original Meta signer |
| Stage15 side-by-side 336 | 62,416,612 | 21 | arm64-v8a | org.revibe.orca01, temporary Revibe signer |

Both original APKs have passed original JAR/v1 signature and ZIP integrity checks offline. The Android manifests are consistent with their stated API/ABI requirements. No live device-install or message-send verification exists.

## Interpretation

Different elapsed time until failure **does not prove** any specific ABI, SDK, signature, package conflict, or network issue. Those failures all occur before Messenger launches. Package size and different verification steps can also affect timing. Do not use the instant vs delayed distinction to invent a root cause.

The user's constraints are no complicated install, no ADB or computer commands. Avoid repeated identical/re-signed or renamed Meta APKs. The least intrusive information that could make the next artifact materially better is the Mi device model and its reported **Android OS version**, visible together in Settings → About phone (hide IMEI and serial identifiers). A 64-bit CPU is not proof of a 64-bit Android installation.

## Actions

1. Archive the two distinct field failures and ensure the next session reads this report.
2. Before another APK, verify the phone OS version/model, confirmed ABI support if possible, and free internal storage. Do not request sensitive identifiers.
3. If hardware facts are established, choose a valid API/ABI baseline and only build after a demonstrated package failure cause is available; if not, state what remains unverified.
4. No elderly-recipient distribution, passwords, or chats through experimental APKs until actual secure Messenger-to-Messenger messaging works.

Sources: Android PackageInstaller generic error string https://android.googlesource.com/platform/packages/apps/PackageInstaller/+/d9f8f57/res/values/strings.xml ; Xiaomi third-party app troubleshooting https://www.mi.com/global/support/faq/details/KA-07134/.
