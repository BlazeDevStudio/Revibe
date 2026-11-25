#!/usr/bin/env python3
"""Fail closed on misleading Revibe Messenger releases; NOT a Messenger client.

Normal CI: --check, succeeds when the product is explicitly blocked and no
Messenger-labelled APK is being shipped. If a candidate appears, --check
automatically performs the same strict gates as --release.

This checks *evidence presence*, package integrity, and APK signatures.
It cannot independently prove Meta authorization or real conversation/E2EE;
human verification of the referenced test records remains mandatory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BLOCKED = "NO VERIFIED FUNCTIONAL MESSENGER RELEASE"
VERIFIED = "VERIFIED FUNCTIONAL MESSENGER RELEASE"
PRODUCT_ID = "org.revibe.messenger"
ABIS = ("armeabi-v7a", "arm64-v8a", "x86")
REQUIRED_TESTS = (
    "authorized_personal_authentication",
    "bidirectional_meta_personal_text",
    "receive_and_decrypt_e2ee",
    "offline_retry_and_reconnect",
    "background_notifications",
    "session_revoke_and_logout",
)
# Distinct emulator/platform evidence cannot be silently represented as physical testing.
REQUIRED_MATRIX = (("armeabi-v7a", 19), ("arm64-v8a", 21), ("x86", 19))
REQUIRED_ANDROID_APIS = (19, 21, 23, 29, 35, 37)
APK_NAME = re.compile(r"Revibe-Messenger-(armeabi-v7a|arm64-v8a|x86|universal)\.apk\Z")



class GateError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise GateError(message)


def json_file(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GateError("Missing or invalid JSON: " + str(path)) from exc


def evidence_ok(value):
    return (isinstance(value, dict) and value.get("passed") is True
            and isinstance(value.get("evidence"), str)
            and value["evidence"].startswith(("https://", "http://"))
            and len(value["evidence"]) > 12)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sha256sums(dist, files):
    """The manifest must list exactly the released APKs, without aliases/paths."""
    location = dist / "SHA256SUMS.txt"
    require(location.is_file(), "Missing SHA256SUMS.txt")
    found = {}
    for line in location.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  (Revibe-Messenger-(?:armeabi-v7a|arm64-v8a|x86|universal)\.apk)", line)
        require(match is not None, "Malformed/noncanonical SHA256SUMS line")
        digest, name = match.groups()
        require(name not in found, "Duplicate checksum entry: " + name)
        found[name] = digest
    expected = {item["filename"]: str(item["sha256"]).lower() for item in files}
    require(found == expected, "SHA256SUMS must match exactly the release APK manifest")


def check_android_metadata(path, apk, signer):
    """Inspect *compiled* manifest, signatures and alignment; not declarative JSON."""
    aapt, apksigner, zipalign = (shutil.which(name)
                                 for name in ("aapt", "apksigner", "zipalign"))
    require(all((aapt, apksigner, zipalign)),
            "Android SDK aapt, apksigner and zipalign all required for release")
    args = [aapt, "dump", "badging", str(path)]
    result = subprocess.run(args, capture_output=True, text=True)
    require(result.returncode == 0, "aapt rejected compiled APK: " + path.name)
    badging = result.stdout
    package = re.search(r"^package: name='([^']+)'", badging, flags=re.MULTILINE)
    floor = re.search(r"^sdkVersion:'(\d+)'", badging, flags=re.MULTILINE)
    target = re.search(r"^targetSdkVersion:'(\d+)'", badging, flags=re.MULTILINE)
    require(package is not None and package.group(1) == PRODUCT_ID,
            "Compiled APK package ID is not the release product")
    require(floor is not None and int(floor.group(1)) == apk["min_sdk"],
            "Compiled APK minSdk differs from release claim")
    require(target is not None and int(target.group(1)) == apk["target_sdk"],
            "Compiled APK targetSdk differs from release claim")

    result = subprocess.run([zipalign, "-c", "-v", "4", str(path)],
                            capture_output=True, text=True)
    require(result.returncode == 0, "Unaligned APK: " + path.name)

    result = subprocess.run([apksigner, "verify", "--verbose", "--print-certs",
                             "--min-sdk-version", str(apk["min_sdk"]), str(path)],
                            capture_output=True, text=True)
    require(result.returncode == 0, "apksigner rejected: " + path.name)
    output = result.stdout
    require(re.search(r"Verified using v1 scheme \(JAR signing\): true", output),
            "Missing v1 signature for old Android support")
    require(re.search(r"Verified using v2 scheme \(APK Signature Scheme v2\): true", output),
            "Missing v2 signature for modern Android support")
    require(not re.search(r"certificate DN:.*Android Debug", output, re.IGNORECASE),
            "Debug certificate may not sign Messenger releases")
    certs = re.findall(r"certificate SHA-256 digest:\s*([0-9a-f:]+)", output,
                       flags=re.IGNORECASE)
    require(any(x.lower().replace(":", "") == signer.lower().replace(":", "")
                for x in certs), "Release signing certificate mismatch: " + path.name)


def verified_apk(path, apk, expected_abi, signer):
    require(path.is_file() and path.stat().st_size > 1024,
            "Missing/empty release APK: " + path.name)
    require(re.fullmatch(r"[a-fA-F0-9]{64}", str(apk.get("sha256", ""))),
            "Missing SHA-256 for " + path.name)
    require(sha256(path) == apk["sha256"].lower(), "APK hash mismatch: " + path.name)
    try:
        with zipfile.ZipFile(path) as archive:
            require(archive.testzip() is None, "Corrupt APK ZIP: " + path.name)
            names = archive.namelist()
            require("AndroidManifest.xml" in names and "classes.dex" in names,
                    "Missing manifest/DEX: " + path.name)
            present_abis = {p.split("/")[1] for p in names
                            if p.startswith("lib/") and p.endswith(".so") and len(p.split("/")) == 3}
            if expected_abi == "universal":
                require(not present_abis or set(ABIS).issubset(present_abis),
                        "Universal APK missing native ABI closure: " + path.name)
            elif present_abis:
                require(present_abis == {expected_abi},
                        "ABI-split includes incorrect native library architectures: " + path.name)
            else:
                raise GateError("DEX-only client must ship one universal APK, not ABI-labelled clones")
    except (OSError, zipfile.BadZipFile) as exc:
        raise GateError("Invalid APK: " + path.name) from exc

    check_android_metadata(path, apk, signer)


def check_release(root, status):
    require(status.get("release_status") == VERIFIED,
            "Messenger release still BLOCKED; do not publish diagnostic as Messenger")
    spec = json_file(root / "Messenger/dist/BUILD_MANIFEST.json")
    require(spec.get("product_kind") == "personal-meta-messenger",
            "Release must be PERSONAL Meta Messenger, not Page bot/installer")
    require(spec.get("application_id") == PRODUCT_ID, "Wrong app ID")
    require(re.fullmatch(r"[0-9a-f]{40}", str(spec.get("source_commit", ""))),
            "Missing exact source commit")
    signer = spec.get("signer_sha256", "")
    require(re.fullmatch(r"[0-9a-fA-F:]{64,95}", signer), "Missing release signer fingerprint")
    require(evidence_ok(spec.get("meta_authorization")),
            "Missing independently checkable personal Meta authorization evidence")
    tests = spec.get("functional_tests", {})
    require(isinstance(tests, dict), "Invalid functional evidence")
    for name in REQUIRED_TESTS:
        require(evidence_ok(tests.get(name)), "Missing live acceptance evidence: " + name)
    matrix = spec.get("platform_tests", [])
    require(isinstance(matrix, list), "Platform evidence must be a list")
    for abi, api in REQUIRED_MATRIX:
        require(any(isinstance(t, dict) and t.get("abi") == abi and t.get("api") == api
                    and t.get("environment") in ("physical", "emulator")
                    and evidence_ok(t) and t.get("install") is True
                    and t.get("launch") is True and t.get("restart") is True
                    for t in matrix), "Missing installed/launched/restarted platform proof: %s API%d" % (abi, api))
    for api in REQUIRED_ANDROID_APIS:
        require(any(isinstance(t, dict) and t.get("api") == api
                    and t.get("environment") in ("physical", "emulator")
                    and evidence_ok(t) and t.get("install") is True
                    and t.get("launch") is True and t.get("restart") is True
                    for t in matrix), "Missing Android version compatibility evidence: API%d" % api)
    files = spec.get("apks")
    require(isinstance(files, list) and files, "No released APK entries")
    types = [entry.get("abi") for entry in files if isinstance(entry, dict)]
    require(types == ["universal"] or set(types) == set(ABIS),
            "Supply one verified universal APK or all three real ABI splits")
    seen = set()
    for entry in files:
        abi = entry["abi"]
        name = entry.get("filename", "")
        require(name == "Revibe-Messenger-%s.apk" % abi,
                "Misleading/noncanonical release filename")
        require(name not in seen, "Duplicate release filename")
        seen.add(name)
        require(isinstance(entry.get("min_sdk"), int)
                and entry["min_sdk"] == (21 if abi == "arm64-v8a" else 19),
                "Release ABI claims unsupported Android SDK floor")
        require(isinstance(entry.get("target_sdk"), int) and entry["target_sdk"] >= 35,
                "Missing modern targetSdk for release")
        verified_apk(root / "Messenger/dist" / name, entry, abi, signer)
    check_sha256sums(root / "Messenger/dist", files)
    for name in ("SHA256SUMS.txt", "COMPATIBILITY_MATRIX.md", "TEST_REPORT.md"):
        require((root / "Messenger/dist" / name).is_file(),
                "Missing release record: " + name)


def check(root, release=False):
    status = json_file(root / "Messenger/STATUS.json")
    dist = root / "Messenger/dist"
    # ANY binary under dist must pass the full release gate. A noncanonical
    # filename, nested path or AAB cannot bypass an APK-only filename check.
    candidate = (dist / "BUILD_MANIFEST.json").exists() or any(
        p.is_file() for p in dist.rglob("*")
        if p.suffix.lower() in (".apk", ".aab", ".apks", ".xapk"))
    if release or candidate or status.get("release_status") == VERIFIED:
        check_release(root, status)
        return "Release structure, artifact signatures, and evidence references verified; live Meta testing still requires human audit"
    require(status.get("release_status") == BLOCKED,
            "Ambiguous release state: cannot mark blocked sources as shippable")
    product = status.get("product_release", {})
    require(product.get("state") == "BLOCKED_META_PERSONAL_INTEROPERABILITY",
            "Missing explicit personal Meta interoperability blocker")
    require(product.get("real_meta_personal_messaging_verified") is False,
            "Product status must not claim untested real messaging")
    require(product.get("installer_diagnostic_is_messenger") is False,
            "Installer probe must not masquerade as Messenger")
    return "BLOCKED: no Messenger-labelled release candidate; diagnostic remains distinct"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check state; fail if an unverified release appears")
    parser.add_argument("--release", action="store_true", help="Require fully evidenced release artifacts")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root for integration tests")
    args = parser.parse_args()
    try:
        message = check(args.root, release=args.release)
    except (GateError, KeyError, TypeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
