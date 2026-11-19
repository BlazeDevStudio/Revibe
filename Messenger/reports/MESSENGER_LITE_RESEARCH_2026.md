# Messenger Lite — historical compatibility research (2026-11-20)

## Why Revibe should examine it
Messenger Lite (`com.facebook.mlite`) was introduced by Meta in October 2016 for older and lower-powered Android phones and slower networks. This matches Revibe's accessibility and device-reuse mission.

## Confirmed shutdown
Meta discontinued Messenger Lite on Android in September 2023 (reported shutdown date September 18, 2023). Meta told TechCrunch users would be directed to Messenger or Facebook Lite beginning August 21, 2023. Server-side discontinuation means changing local warning strings does not restore account messaging.

## Version leads requiring APK-level verification
- Archived Messenger Lite `338.0.0.3.102`, package `com.facebook.mlite`, is listed by APKMirror and Uptodown with Android 4.0.3+/API15 compatible ARMv7 variants. Independently verify actual `AndroidManifest.xml`, architecture, package signature, and integrity if a legally sourced original is acquired.
- A historical `320.0.0.4.108` edition is sometimes discussed by former users as an earlier functional build; this is anecdotal and NOT a recommendation or verified 2026 compatibility claim.

## Engineering opportunity
1. Compare `com.facebook.mlite` against the API19 `com.facebook.orca` baseline on install size, DEX count, native dependencies, Android framework requirements, resource/UI and message transport characteristics.
2. Learn from reduced UI complexity, limited data usage, and memory-conscious design. Avoid copying proprietary code into the public Revibe repository.
3. Establish whether `mlite` uses a transport/authentication model that can participate in modern Meta-authenticated encrypted conversations; do not infer interoperability from the archived minSdk level.
4. Treat restoration of real Messenger-to-Messenger messaging as the acceptance gate; offline local UI alone is inadequate.

## Current known blockers
- No Messenger Lite APK has yet been supplied and statically inspected in this project.
- Meta discontinued the service; successful APK installation alone is not evidence that it can send/receive messages.
- No evidence that a 2023 Lite client fully supports the modern Messenger E2EE system or server login requirements.
- No proof Meta discontinued Messenger Lite to prioritize revenue; that motive is not established by the sources below.

## References
- Meta launch (2016): https://about.fb.com/news/2016/10/empowering-the-world-to-stay-connected-introducing-messenger-lite/
- Meta video chat expansion (2018): https://about.fb.com/news/2018/03/introducing-video-chat-in-messenger-lite/
- TechCrunch August 24 2023: https://techcrunch.com/2023/08/24/meta-is-shutting-down-messenger-lite-for-android-in-september/
- APKMirror archived Messenger Lite versions: https://www.apkmirror.com/apk/meta-platforms-inc/messenger-lite/
- Google Play Facebook Lite messaging description: https://play.google.com/store/apps/details?id=com.facebook.lite
- Android 64-bit ABI guidance: https://developer.android.com/google/play/requirements/64-bit
