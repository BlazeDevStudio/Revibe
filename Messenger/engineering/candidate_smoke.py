#!/usr/bin/env python3
"""Privacy-conscious ADB smoke test for a RESEARCH-only Messenger APK.

Device actions occur only with one authorized connected Android device.
Never captures or persists credentials, chat content, raw logs or device IDs.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time
import zipfile

PKG = "com.facebook.orca"

def adb(*args, timeout=30):
    try:
        return subprocess.run(["adb", *args], capture_output=True, text=True,
                              errors="replace", timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None

def connected_count():
    p = adb("devices")
    if p is None or p.returncode:
        return 0
    return len([line for line in p.stdout.splitlines()[1:]
                if len(line.split()) >= 2 and line.split()[1] == "device"])

def prop(name):
    p = adb("shell", "getprop", name)
    return p.stdout.strip() if p is not None and p.returncode == 0 else ""

def running():
    p = adb("shell", "ps")
    return p is not None and p.returncode == 0 and any(
        line.split() and (line.split()[-1] == PKG or line.split()[-1].startswith(PKG + ":"))
        for line in p.stdout.splitlines()[1:])

def smoke(apk, install=False, ack=False, launch=False):
    apk = Path(apk)
    if install and not ack:
        raise ValueError("Use --ack-test-device before installation; never use a recipient's phone")
    if not apk.is_file():
        raise FileNotFoundError(apk)
    with zipfile.ZipFile(apk) as archive:
        if archive.testzip() is not None or "AndroidManifest.xml" not in archive.namelist():
            raise ValueError("Invalid APK ZIP")
    if connected_count() != 1:
        return {"status": "requires_one_authorized_adb_device",
                "installed": False, "messenger_communication_tested": False}
    sdk = prop("ro.build.version.sdk")
    abi1 = prop("ro.product.cpu.abi")
    abi2 = prop("ro.product.cpu.abi2")
    abis = set([abi1, abi2] + prop("ro.product.cpu.abilist").split(","))
    if not sdk.isdecimal() or int(sdk) < 19 or "armeabi-v7a" not in abis:
        return {"status": "incompatible_api_or_abi", "installed": False}
    result = {"status": "preflight_passed", "android_api": int(sdk),
              "abi": abi1, "installed": False, "launch_command_sent": False,
              "process_observed": False, "messenger_communication_tested": False}
    if install:
        installed = adb("install", str(apk), timeout=180)
        if installed is None or installed.returncode:
            err = "" if installed is None else installed.stdout + installed.stderr
            m = re.search(r"INSTALL_FAILED_[A-Z_]+", err)
            result["status"] = "install_failure"
            result["install_failure_category"] = m.group(0) if m else "unknown"
            return result
        result.update(status="installed_not_functionally_verified", installed=True)
    if launch:
        launched = adb("shell", "monkey", "-p", PKG, "-c",
                       "android.intent.category.LAUNCHER", "1")
        result["launch_command_sent"] = launched is not None and launched.returncode == 0
        if result["launch_command_sent"]:
            time.sleep(3)
            result["process_observed"] = running()
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apk", type=Path, required=True)
    p.add_argument("--install", action="store_true")
    p.add_argument("--ack-test-device", action="store_true")
    p.add_argument("--launch", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = smoke(args.apk, args.install, args.ack_test_device, args.launch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
