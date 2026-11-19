# Stage 6 — actual build result

A locally modified 44,548,271-byte APK was produced from the separately provided original Messenger 410 API19 ARMv7 package. SHA-256 of original: `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`.

The experiment only replaced two strings in `assets/strings/default.frsc`. Existing Meta signatures were invalidated, and the APK was re-signed with a disposable research key. ZIP CRC, Java JAR/v1 signature verification, and API19 ARMv7 static preflight passed. Those tests do not establish Android package-manager acceptance or correct app execution.

The candidate is intentionally not uploaded to this public repository. No device install/launch, Meta login, version-gate elimination, modern end-to-end encrypted personal-chat send/receive, notifications, or voice calls were verified. Three ABI builds and Android 10 compatibility remain future goals.

See `Messenger/STATUS.json` and `Messenger/engineering/README_STAGE6.md` for next actions and safety rules.
