#!/usr/bin/env python3
"""Read-only device OS/ABI check for Revibe's pinned API19 ARMv7 research APK.
This checks basic install eligibility, NOT functioning Messenger or real install.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from zipfile import ZipFile

PINNED_SHA256 = "7e1a128728935ca3b9afd4079a7018b31c00b6215067514dfee8adc6ca5e66dd"

def classify(sdk, device_abis, apk_abis):
    matches = sorted(set(device_abis).intersection(apk_abis))
    compatible = sdk >= 19 and bool(matches)
    return {
        "android_api_level": sdk,
        "device_supported_abis": device_abis,
        "apk_native_abis": sorted(apk_abis),
        "matching_abis": matches,
        "basic_install_eligible": compatible,
        "physical_install_verified": False,
        "messenger_login_verified": False,
        "e2ee_messaging_verified": False
    }

def getprop(name, adb="adb"):
    if name not in ("ro.build.version.sdk","ro.product.cpu.abilist","ro.product.cpu.abi","ro.product.cpu.abi2"):
        raise ValueError("Unexpected Android property")
    p = subprocess.run([adb,"shell","getprop",name],capture_output=True,text=True,timeout=15)
    if p.returncode:
        raise RuntimeError("ADB failed; check connection and device authorization")
    return p.stdout.strip()

def inspect(apk, sdk, abi_csv):
    h = hashlib.sha256()
    with open(apk, "rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    if h.hexdigest() != PINNED_SHA256:
        raise ValueError("Unexpected APK hash; minimum-SDK assumptions do not apply")
    with ZipFile(apk) as z:
        if z.testzip() is not None:
            raise ValueError("APK ZIP CRC failed")
        native = {name.split("/")[1] for name in z.namelist()
                  if name.startswith("lib/") and name.endswith(".so") and len(name.split("/"))==3}
    if native != {"armeabi-v7a"}:
        raise ValueError("Unexpected APK native ABIs")
    return classify(sdk, [x.strip() for x in abi_csv.split(",") if x.strip()], native)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apk", type=Path, required=True)
    p.add_argument("--sdk", type=int, default=None, help="21=Android 5, 23=Android 6")
    p.add_argument("--device-abis", default=None, help="Comma-separated supported ABIs, instead of ADB")
    p.add_argument("--adb", default="adb")
    args = p.parse_args()
    if (args.sdk is None) != (args.device_abis is None):
        p.error("--sdk and --device-abis must be supplied together")
    try:
        sdk = args.sdk if args.sdk is not None else int(getprop("ro.build.version.sdk",args.adb))
        abis = args.device_abis if args.device_abis is not None else getprop("ro.product.cpu.abilist",args.adb)
        if not abis:
            abis = ",".join(x for x in [getprop("ro.product.cpu.abi",args.adb),
                                         getprop("ro.product.cpu.abi2",args.adb)] if x)
        result = inspect(args.apk, sdk, abis)
    except (ValueError, OSError, RuntimeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["basic_install_eligible"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
