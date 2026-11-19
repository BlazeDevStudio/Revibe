#!/usr/bin/env python3
"""Create an Android 4.4 ARMv7 signed *research trial* from the user's own APK.

Only two English update-related messages are changed to research labels.
No version gate, login code, E2EE logic or other app functionality is fixed.
Does not include/redistribute Meta APKs or Meta signing certificates.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile

ORIGINAL_SHA256 = "006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8"
RESOURCE = "assets/strings/default.frsc"
PATCHES = {
    b"Your %1$s version is outdated": b"Research %1$s test build only",
    b"You are required to update. Get the new version of %1$s.":
        b"Revibe test only: %1$s login or chats might not work.   ",
}
SIGNATURE = re.compile(r"^META-INF/(?:MANIFEST\.MF|[^/]+\.(?:RSA|DSA|EC|SF))$", re.I)

def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def patch_resources(raw):
    modified = raw
    results = {}
    for old, new in PATCHES.items():
        if len(old) != len(new):
            raise ValueError("FRSC resource lengths must remain identical")
        count = modified.count(old)
        if count != 1:
            raise ValueError("Expected unique prompt resource; found " + str(count))
        modified = modified.replace(old, new, 1)
        results[old.decode("ascii")] = count
    assert len(modified) == len(raw)
    return modified, results

def repack_original(original, dest):
    original, dest = Path(original), Path(dest)
    if original.resolve() == dest.resolve():
        raise ValueError("Original APK must not be overwritten")
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(dest, "w", allowZip64=True) as dst:
        if src.testzip() is not None:
            raise ValueError("Corrupt original APK")
        if RESOURCE not in src.namelist():
            raise ValueError("Missing expected FRSC resource")
        results = None
        for entry in src.infolist():
            if SIGNATURE.match(entry.filename):
                continue
            data = src.read(entry)
            if entry.filename == RESOURCE:
                data, results = patch_resources(data)
            dst.writestr(entry, data)
    return results

def invoke(args, timeout=300):
    try:
        p = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("Missing or timed-out build tool: " + str(args[0])) from exc
    if p.returncode:
        raise RuntimeError("{} failed ({}): {}".format(args[0], p.returncode, (p.stderr or p.stdout)[-300:]))
    return p

def build(original, output, report):
    original, output, report = Path(original), Path(output), Path(report)
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unknown source APK SHA-256; expected exact API19 ARMv7 source")
    for executable in ("keytool", "jarsigner"):
        if not shutil.which(executable):
            raise RuntimeError("Required JDK tool unavailable: " + executable)
    if output.exists():
        raise FileExistsError("Refusing to overwrite an existing output")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="revibe-kitkat-") as tmp:
        tmp = Path(tmp)
        unsigned = tmp / "unsigned.apk"
        keyfile = tmp / "research-only.p12"
        replacements = repack_original(original, unsigned)
        password = "temporary-revibe-research-2026"
        invoke(["keytool", "-genkeypair", "-keystore", str(keyfile),
                "-storetype", "PKCS12", "-alias", "revibe-research",
                "-keyalg", "RSA", "-keysize", "3072", "-validity", "30",
                "-dname", "CN=Revibe Temporary Research Build, O=Independent Testing",
                "-storepass", password, "-keypass", password, "-noprompt"], 45)
        invoke(["jarsigner", "-keystore", str(keyfile),
                "-storepass", password, "-keypass", password,
                "-sigalg", "SHA256withRSA", "-digestalg", "SHA-256",
                "-signedjar", str(output), str(unsigned), "revibe-research"], 300)
    v = invoke(["jarsigner", "-verify", str(output)], 300)
    verified = bool(re.search(r"(?im)^jar verified\.$", v.stdout + "\n" + v.stderr))
    if not verified:
        raise RuntimeError("v1/JAR signature verification marker missing")
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:
            raise RuntimeError("Signed APK CRC failed")
        resources = z.read(RESOURCE)
        for old, new in PATCHES.items():
            if new not in resources or old in resources:
                raise RuntimeError("Experimental prompt replacement missing")
    result = {
        "artifact": output.name,
        "source_sha256": ORIGINAL_SHA256,
        "output_sha256": digest(output),
        "output_bytes": output.stat().st_size,
        "changed_resource": RESOURCE,
        "text_replacements": sum(replacements.values()),
        "signature_v1_verified": True,
        "zip_crc_verified": True,
        "android44_armv7_install_tested": False,
        "messenger_login_tested": False,
        "encrypted_messages_tested": False,
        "update_gate_removed": False,
        "warning": "NOT a restored Messenger app. This build modifies only two strings. Do not distribute to charity recipients."
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.original, args.output, args.report), indent=2))

if __name__ == "__main__":
    main()
