# Stage 5 — Update-Barrier Classification

**Status: diagnostic utility only. Not a patched Messenger APK.**

`prompt_barrier_audit.py` compares curated update/deprecation patterns in a **user-provided** APK with a redacted classification of the current on-device Messenger screen (optional). It does not change app code, log in, read messages, bypass server enforcement, or prove working modern chats.

## Offline analysis

```sh
python prompt_barrier_audit.py --apk "/path/to/your/original.apk" --output report.json
python -m unittest discover -s tests -v
```

The offline report contains a SHA-256 identifier and the **number of resource string segments matching each category**. The scanner covers only `assets/strings/default.frsc` and `resources.arsc`, so it may overcount fragments or miss messages elsewhere. Matching bundled text does **not** prove it is shown, nor identify a server-side trigger.

## Optional read-only Android device screen check

On one authorized device with Android Platform Tools installed, open the Messenger screen you want to examine; then:

```sh
python prompt_barrier_audit.py --inspect-ui --output ui_report.json
```

The tool requires exactly one authorized ADB device and an installed `com.facebook.orca` package. It uses Android's `uiautomator dump` command to inspect the visible UI hierarchy **in memory**, writes only coarse category counts, and deletes its temporary device-side XML. No credentials, message contents, account names, device serials, or raw UI text are saved by this tool. A device command may fail on customized ROMs; a failure is reported as unavailable.

**Don't run a screen capture over sensitive conversations.** Even though the tool saves no raw text, the OS's UI hierarchy can contain private content while in memory. Run on a controlled test account if possible.

## Interpreting results

- `mandatory_app_update`: update-related text appears on screen; it may come from local logic or backend response.
- `unsupported_android_or_device`: compatibility language appears; it doesn't establish whether the OS check can safely be bypassed.
- `google_play_services`: potential GMS dependency; may require separate device investigation.
- `optional_app_update`: advisory language; need not be blocking.
- No matches means **no matching text visible at capture time**, not a successful login.
- The current screen check is an observation, **not** authentication or encrypted send/receive testing.

This project does not remove legitimate security or service-compatibility warnings without restoring the underlying functionality.
