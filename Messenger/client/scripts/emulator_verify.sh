#!/usr/bin/env bash
# Run as one process for android-emulator-runner; no real Meta traffic attempted.
set -euo pipefail
adb install foundation/app-debug.apk
adb shell am start -W -n org.revibe.client.foundation/org.revibe.foundation.MainActivity
sleep 3
adb shell ps | grep -F 'org.revibe.client.foundation'
adb install instrumentation/app-debug-androidTest.apk
RESULT="$(adb shell am instrument -w org.revibe.client.foundation.test/org.revibe.foundation.FoundationInstrumentation)"
printf '%s\n' "$RESULT"
printf '%s\n' "$RESULT" | grep -F 'PASS: 9 on-emulator foundation assertions'
adb shell am force-stop org.revibe.client.foundation
adb shell am start -W -n org.revibe.client.foundation/org.revibe.foundation.MainActivity
adb shell ps | grep -F 'org.revibe.client.foundation'
echo "PASS: foundation-only app restarted; no Meta login or messaging tested"
