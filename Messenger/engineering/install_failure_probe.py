#!/usr/bin/env python3
"""Revibe Messenger 336: privacy-preserving Android 5/6 installation diagnosis.

Read-only by default. Does not collect identifiers, chat data, or raw logcat.
An install attempt requires an explicit flag, a verified original APK, and a
spare authorized device with no existing Messenger package.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PACKAGE = "com.facebook.orca"
ORIGINAL_336_SHA256 = "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab"
ERROR_PATTERN = re.compile(
    r"\b(INSTALL_(?:FAILED|PARSE_FAILED|CANCELED)_[A-Z0-9_]+)\b"
)
PROPERTIES = ("ro.build.version.sdk", "ro.product.cpu.abilist",
              "ro.product.cpu.abi", "ro.product.cpu.abi2")


def installation_failure_code(stdout, stderr):
    """Extract only the package-manager status, never raw diagnostics."""
    match = ERROR_PATTERN.search((stdout or "") + "\n" + (stderr or ""))
    return match.group(1) if match else "UNCLASSIFIED_INSTALL_FAILURE"


def explain(code):
    prefixes = {
        "INSTALL_FAILED_UPDATE_INCOMPATIBLE":
            "Existing app was signed by a different certificate.",
        "INSTALL_FAILED_VERSION_DOWNGRADE":
            "A newer version is present; do not force a downgrade.",
        "INSTALL_FAILED_NO_MATCHING_ABIS":
            "No matching CPU architecture is supported.",
        "INSTALL_FAILED_OLDER_SDK":
            "APK requires a newer Android release.",
        "INSTALL_FAILED_INSUFFICIENT_STORAGE":
            "Not enough available internal storage.",
        "INSTALL_FAILED_ALREADY_EXISTS":
            "Package already installed.",
        "INSTALL_PARSE_FAILED_NO_CERTIFICATES":
            "Package signature could not be validated.",
        "INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES":
            "Package signing certificates are inconsistent.",
        "INSTALL_FAILED_INVALID_APK":
            "Android rejected the APK structure.",
    }
    return prefixes.get(code, "Installer returned an unclassified error; inspect locally.")


def command(adb, *arguments, timeout=25):
    """Call adb without a shell and never echo captured raw output."""
    try:
        return subprocess.run(
            [adb, *arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors="replace", timeout=timeout, check=False
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None


def device_count(adb):
    p = command(adb, "devices")
    if p is None or p.returncode:
        return None
    return sum(len(parts) >= 2 and parts[1] == "device"
               for line in p.stdout.splitlines()[1:]
               if (parts := line.split()))


def getprop(adb, name):
    if name not in PROPERTIES:
        raise ValueError("Not an allowed non-sensitive device property")
    p = command(adb, "shell", "getprop", name)
    return p.stdout.strip() if p is not None and p.returncode == 0 else ""


def installed_package(adb):
    p = command(adb, "shell", "pm", "path", PACKAGE)
    if p is None or p.returncode != 0:
        return None
    return "package:" in p.stdout


def apk_matches_original(apk):
    digest = hashlib.sha256()
    with open(apk, "rb") as handle:
        for piece in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(piece)
    return digest.hexdigest() == ORIGINAL_336_SHA256


def probe(apk=None, install=False, acknowledge=False, adb="adb"):
    if install and not acknowledge:
        raise ValueError("--install requires --ack-test-device")
    if install and apk is None:
        raise ValueError("--install requires --apk pointing to original Messenger 336")
    result = {
        "project": "Revibe Messenger",
        "purpose": "diagnose_installation_only",
        "original_apk_version": "336.0.0.13.142",
        "privacy": "only generic SDK, ABI match and package-manager error category",
        "install_attempted": False,
        "install_succeeded": False,
        "live_messaging_verified": False,
    }
    count = device_count(adb)
    if count != 1:
        result["status"] = "requires_exactly_one_authorized_adb_device"
        return result
    sdk_value = getprop(adb, "ro.build.version.sdk")
    csv = getprop(adb, "ro.product.cpu.abilist")
    if not csv:
        csv = ",".join(filter(None, (
            getprop(adb, "ro.product.cpu.abi"),
            getprop(adb, "ro.product.cpu.abi2"),
        )))
    if not sdk_value.isdigit() or not csv:
        result["status"] = "unable_to_read_android_api_or_abis"
        return result
    sdk = int(sdk_value)
    result["android_api"] = sdk
    result["native_arm64_supported"] = "arm64-v8a" in csv.split(",")
    result["android5_6_arm64_platform_eligible"] = (
        21 <= sdk <= 23 and result["native_arm64_supported"]
    )
    previous = installed_package(adb)
    result["messenger_package_present"] = previous
    if previous is None:
        result["status"] = "unable_to_verify_installed_package"
        return result
    if not install:
        result["status"] = "read_only_preflight_completed"
        return result
    if not result["android5_6_arm64_platform_eligible"]:
        result["status"] = "platform_does_not_match_original_336_test_target"
        return result
    if previous:
        result["status"] = "existing_messenger_preserved_install_skipped"
        return result
    try:
        if not apk.is_file() or not apk_matches_original(apk):
            result["status"] = "source_apk_sha256_not_verified"
            return result
    except OSError:
        result["status"] = "source_apk_missing_or_unreadable"
        return result
    result["install_attempted"] = True
    p = command(adb, "install", str(apk), timeout=180)
    if p is not None and p.returncode == 0 and re.search(
        r"\bSuccess\b", p.stdout or ""
    ):
        result["install_succeeded"] = True
        result["status"] = "installed_but_messaging_unverified"
        return result
    code = installation_failure_code(p.stdout, p.stderr) if p else "UNCLASSIFIED_INSTALL_FAILURE"
    result["install_error_code"] = code
    result["install_error_explanation"] = explain(code)
    result["status"] = "install_rejected"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--install", action="store_true",
                        help="Opt-in install on spare device only; never overwrites another Messenger")
    parser.add_argument("--ack-test-device", action="store_true")
    parser.add_argument("--output", type=Path, help="Optional redacted JSON result")
    args = parser.parse_args()
    try:
        result = probe(apk=args.apk, install=args.install,
                       acknowledge=args.ack_test_device, adb=args.adb)
    except ValueError as ex:
        parser.error(str(ex))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] in (
        "read_only_preflight_completed", "installed_but_messaging_unverified"
    ) else 2


if __name__ == "__main__":
    raise SystemExit(main())
