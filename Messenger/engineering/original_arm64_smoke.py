#!/usr/bin/env python3
"""Privacy-conscious Android 5/6 native ARM64 ORIGINAL Messenger 336 test.

Read-only device preflight by default. Installation is opt-in, and never
replaces/uninstalls an existing package. Does not collect logcat, UI snapshots,
account identifiers, credentials or conversations. A launched process does NOT
establish Meta server compatibility.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

PACKAGE = "com.facebook.orca"
PINNED_SHA256 = "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab"
PROPS = {"ro.build.version.sdk", "ro.product.cpu.abilist", "ro.product.cpu.abi", "ro.product.cpu.abi2"}
SCREENS = {"not_checked", "login_screen", "update_required", "app_closed", "other", "working_ui_unverified"}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute(*args, timeout=40):
    """Only fixed commands and local APK path; never shell-interpolate inputs."""
    try:
        return subprocess.run(["adb", *args], capture_output=True, text=True,
                              errors="replace", timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None


def adb_device_count():
    r = execute("devices")
    if r is None or r.returncode:
        return -1
    return sum(len(parts) >= 2 and parts[1] == "device"
               for line in r.stdout.splitlines()[1:]
               if (parts := line.split()))


def property_value(name):
    if name not in PROPS:
        raise ValueError("Disallowed device property")
    r = execute("shell", "getprop", name)
    return r.stdout.strip() if r is not None and not r.returncode else ""


def device_info():
    sdk = property_value("ro.build.version.sdk")
    if not sdk.isdigit():
        return None
    csv = property_value("ro.product.cpu.abilist")
    if not csv:
        csv = ",".join(x for x in
                       (property_value("ro.product.cpu.abi"), property_value("ro.product.cpu.abi2")) if x)
    abis = [x.strip() for x in csv.split(",") if x.strip()]
    return {"android_api": int(sdk), "supported_abis": abis}


def package_installed():
    r = execute("shell", "pm", "path", PACKAGE)
    return bool(r and r.returncode == 0 and "package:" in r.stdout)


def process_observed():
    r = execute("shell", "pidof", PACKAGE)
    if r and r.returncode == 0 and any(x.isdecimal() for x in r.stdout.split()):
        return True
    r = execute("shell", "ps")
    return bool(r and r.returncode == 0 and any(
        cols and (cols[-1] == PACKAGE or cols[-1].startswith(PACKAGE + ":"))
        for line in r.stdout.splitlines()[1:] if (cols := line.split())))


def classify_device(api, abis):
    if api < 21 or "arm64-v8a" not in abis:
        return "unsupported_android_or_abi"
    if api > 29:
        return "outside_requested_android5_to10_test_range"
    return "device_platform_eligible"


def run(apk, install=False, launch=False, ack=False, observed_screen="not_checked", sleep_fn=time.sleep):
    if observed_screen not in SCREENS:
        raise ValueError("Unknown screen observation category")
    if install and not ack:
        raise ValueError("--install requires --ack-test-device (spare device only)")
    if not apk.is_file() or sha256_file(apk) != PINNED_SHA256:
        raise ValueError("APK must match verified original Messenger 336 ARM64 SHA256")
    report = {
        "original_apk_sha256": PINNED_SHA256,
        "privacy": "no identifiers, logcat, account credentials or message content captured",
        "source_original_meta_signature_preserved": True,
        "installed_package_identity_verified": False,
        "install_attempted": False,
        "install_succeeded": False,
        "launch_attempted": False,
        "process_observed": False,
        "messenger_login_verified": False,
        "encrypted_message_exchange_verified": False,
        "observed_screen_manual_category": observed_screen,
    }
    if adb_device_count() != 1:
        report["status"] = "requires_exactly_one_authorized_adb_device"
        return report
    device = device_info()
    if not device:
        report["status"] = "device_android_version_unavailable"
        return report
    report["device_android_api"] = device["android_api"]
    # No device serial, manufacturer, model, phone number or account identifiers.
    report["device_abi_arm64_supported"] = "arm64-v8a" in device["supported_abis"]
    report["status"] = classify_device(device["android_api"], device["supported_abis"])
    if report["status"] != "device_platform_eligible":
        return report
    report["package_preexisting"] = package_installed()
    if (install or launch) and report["package_preexisting"]:
        report["status"] = "existing_messenger_identity_unverified_action_skipped"
        return report
    if install:
        report["install_attempted"] = True
        r = execute("install", str(apk), timeout=180)
        if not r or r.returncode != 0:
            result = ((r.stdout or "") + (r.stderr or "")) if r else ""
            code = re.search(r"INSTALL_FAILED_[A-Z0-9_]+", result)
            report["status"] = "install_failed"
            report["install_error_code"] = code.group() if code else "unknown_install_error"
            return report
        report["install_succeeded"] = True
        report["status"] = "installed_not_authenticated"
    if launch:
        if not (report["install_succeeded"] or report["package_preexisting"]):
            report["status"] = "package_not_installed_launch_skipped"
            return report
        report["launch_attempted"] = True
        r = execute("shell", "monkey", "-p", PACKAGE,
                    "-c", "android.intent.category.LAUNCHER", "1")
        report["launch_command_accepted"] = bool(r and r.returncode == 0)
        if report["launch_command_accepted"]:
            sleep_fn(2)
            report["process_observed"] = process_observed()
            report["status"] = ("process_seen_not_authenticated" if report["process_observed"]
                                else "process_not_observed")
        else:
            report["status"] = "launch_failed"
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apk", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--install", action="store_true")
    p.add_argument("--ack-test-device", action="store_true")
    p.add_argument("--launch", action="store_true")
    p.add_argument("--observed-screen", choices=sorted(SCREENS), default="not_checked")
    args = p.parse_args()
    try:
        report = run(args.apk, args.install, args.launch, args.ack_test_device,
                     args.observed_screen)
    except (OSError, ValueError) as ex:
        p.error(str(ex))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in {
        "device_platform_eligible", "installed_not_authenticated", "process_seen_not_authenticated",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
