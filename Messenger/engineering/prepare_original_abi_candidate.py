#!/usr/bin/env python3
"""Prepare byte-identical, original Meta-signed ARM32/ARM64 install candidates.
Never edits APK code, signing identity or underlying server compatibility.
No Meta binaries/keys should be committed to public Revibe git.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

CANDIDATES = {
    "arm32-api19": {
        "version": "410.0.0.17.85",
        "sha256": "006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8",
        "minimum_api": 19,
        "native_abi": "armeabi-v7a",
        "signature_block": "META-INF/IMPORTED.RSA",
    },
    "arm64-api21": {
        "version": "336.0.0.13.142",
        "sha256": "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab",
        "minimum_api": 21,
        "native_abi": "arm64-v8a",
        "signature_block": "META-INF/FACEBOOK.RSA",
    },
}

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def choose(api, device_abis):
    """OS-supported ABIs, not the processor's marketed bitness."""
    return [variant for variant, entry in CANDIDATES.items()
            if api >= entry["minimum_api"] and entry["native_abi"] in device_abis]

def verify(path, variant, require_java=True):
    if variant not in CANDIDATES:
        raise ValueError("Unknown candidate")
    entry = CANDIDATES[variant]
    if not path.is_file() or digest(path) != entry["sha256"]:
        raise ValueError("Unexpected original APK SHA256")
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Bad ZIP member")
        names = set(archive.namelist())
        required = {"AndroidManifest.xml", "classes.dex", entry["signature_block"]}
        if not required <= names:
            raise ValueError("Missing original signing/app structure")
        abis = {n.split("/")[1] for n in names
                if n.startswith("lib/") and n.endswith(".so")}
        if abis != {entry["native_abi"]}:
            raise ValueError("Wrong APK native ABI")
    if require_java:
        try:
            r = subprocess.run(["jarsigner", "-verify", str(path)],
                               capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as err:
            raise RuntimeError("Java jarsigner unavailable") from err
        if r.returncode or "jar verified" not in r.stdout.lower():
            raise ValueError("Original APK v1 signature verification failed")
    return {
        "variant": variant, "version": entry["version"],
        "minimum_android_api": entry["minimum_api"],
        "native_abi": entry["native_abi"],
        "original_sha256": entry["sha256"],
        "source_unchanged": True,
        "jar_v1_verified": require_java,
        "physical_install_verified": False,
        "meta_login_verified": False,
        "e2ee_verified": False
    }

def prepare(source, output, variant):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError("Never overwrite existing source or output")
    report = verify(source, variant)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(source, "rb") as f, open(output, "xb") as o:
            shutil.copyfileobj(f, o, length=1024 * 1024)
        if digest(output) != CANDIDATES[variant]["sha256"]:
            raise ValueError("Prepared bytes differ from original")
    except Exception:
        output.unlink(missing_ok=True)
        raise
    report["output_filename"] = output.name
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--variant", required=True, choices=sorted(CANDIDATES))
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    try:
        report = prepare(args.source, args.output, args.variant)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        p.error(str(exc))
    payload = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")

if __name__ == "__main__":
    main()
