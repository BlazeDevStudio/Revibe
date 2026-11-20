#!/usr/bin/env bash
# Runs as one shell process: android-emulator-runner otherwise executes
# each workflow script line independently, breaking multiline if/fi.
set -euo pipefail
adb install install-artifact/app-debug.apk
adb shell am start -W -n org.revibe.installcheck2/org.revibe.installprobe.MainActivity
sleep 3
adb shell ps | grep -F 'org.revibe.installcheck2'

API="$(adb shell getprop ro.build.version.sdk | tr -d '\r')"
if [ "$API" -ge 21 ]; then
    adb install instrument-artifact/app-debug-androidTest.apk
    RESULT="$(adb shell am instrument -w org.revibe.installcheck2.test/org.revibe.installprobe.InstallCallbackInstrumentation)"
    printf '%s\n' "$RESULT"
    printf '%s\n' "$RESULT" | grep -F 'INSTRUMENTATION_CODE: 0'
else
    echo "API19: package-install result callbacks need API21; independent app install/launch passed"
fi
