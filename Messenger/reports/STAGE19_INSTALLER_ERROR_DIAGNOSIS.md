# Revibe Stage 19: on-phone package-install result diagnosis

**This tool is NOT Messenger and cannot send or receive any Meta messages.** It is an independently authored Android utility for discovering why a previously downloaded historical Messenger APK fails to install.

## Built result
- Android application ID `org.revibe.installcheck`, distinct from Stage18's debug-signed app.
- Android `minSdk=19`, `targetSdk=35`, zero native libraries (one universal APK across common CPU architectures).
- GitHub build and verification: https://github.com/BlazeDevStudio/Revibe/actions/runs/44751936662
- APK size **16,753 bytes**, SHA256 `1a83b5cfa52c426540d03a4449df2fe8fa708aa7c90d7bc5dcc3a7cf0fa6bc02`.
- ZIP CRC and Java JAR signature verified in local analysis; Android SDK `apksigner verify --min-sdk-version 19`, zipalign, manifest SDK checks and 15 source safety tests passed in GitHub.
- Source: `Messenger/install-probe/app/src/main/java/org/revibe/installprobe/`.
- Android emulator installation/launch matrix: API19, 21, 23, 35; CI job result is separately checked.

## What the Android 5+ interface does
1. The user taps **Choose an APK to test**. This starts Android's own file picker; it never searches private files automatically.
2. The app reads the user-chosen local APK into a size-limited temporary private file, parses the package name and rejects anything other than `com.facebook.orca` or `org.revibe.orca01`.
3. It checks if that package is already installed and refuses to overwrite it, protecting existing data.
4. Only if not installed and the user explicitly selected the APK, it opens an Android `PackageInstaller.Session` and lets Android request user approval.
5. The installed-package result receiver shows a generic safe category such as `STATUS_FAILURE_INCOMPATIBLE`, conflict, invalid, storage, blocked, or a sanitized `INSTALL_FAILED_*` code if the OS supplies one. It does not transmit raw logs or account data.

On API19/Android 4.4, this app can install and launch, but session status is not available; it explains that limitation in the UI.

## Security and limitations
- No INTERNET, contacts, storage, SMS, microphone or account permissions.
- The only declared permission is `android.permission.REQUEST_INSTALL_PACKAGES`, used for user-initiated installer session requests on newer Android versions; user approval is required.
- The status receiver is non-exported. The temporary APK copy is deleted after submission. Only result categories are stored locally.
- CI compilation and app launch are not proof that the **interactive file-picker/session approval callbacks** work on every OEM phone. That workflow remains **unverified on the user's phone**.
- The tool cannot repair installation requirements, Meta login, mandatory update policy or E2EE messaging. Never deliver it as revived Messenger.

## Meta API limitation
Meta's official Messenger Platform documentation describes Page access tokens and Page-to-person chats; that is different from access to a private consumer's Messenger inbox. See https://developers.facebook.com/docs/messenger-platform/getting-started/quick-start and https://developers.facebook.com/docs/graph-api/reference/page/conversations/. Real Meta-to-Meta communication from Revibe remains unverified.

Next steps: verify interactive package-install diagnostics on representative API21 and modern Android devices, obtain the exact safe error category, and pursue only proven compatibility repairs; separately determine a viable authorized personal Messenger messaging mechanism.
