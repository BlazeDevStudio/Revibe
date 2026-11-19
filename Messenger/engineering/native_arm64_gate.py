#!/usr/bin/env python3
"""Read-only verification of native ARM64 Messenger APK eligibility on Android 5/6."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import BadZipFile, ZipFile
from apk_static_audit import parse_manifest

EXPECTED_PACKAGE = "com.facebook.orca"
HISTORICAL_CANDIDATE = "336.0.0.13.142"
HISTORICAL_VERSION_CODE = 297217556
EXPECTED_ABI = "arm64-v8a"
META_CERT_SHA256 = "e3f9e1e0cf99d0e56a055ba65e241b3399f7cea524326b0cdd6ec1327ed0fdc1"

def _hash_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()

def inspect_meta_certificate(apk):
    """Compare legacy signer identity; does not verify content integrity."""
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.serialization import pkcs7
    except ImportError as exc:
        raise RuntimeError("Install cryptography to verify the original Meta signer") from exc
    with ZipFile(apk) as z:
        blocks = [n for n in z.namelist() if n.upper().startswith("META-INF/")
                  and n.upper().endswith((".RSA", ".DSA", ".EC"))]
        cert_hashes = set()
        for block in blocks:
            cert_hashes.update(cert.fingerprint(hashes.SHA256()).hex()
                               for cert in pkcs7.load_der_pkcs7_certificates(z.read(block)))
    return META_CERT_SHA256 in cert_hashes

def analyze(apk, device_api=21, device_abis=("arm64-v8a",), check_crc=True,
            check_signing=False, check_meta_cert=False):
    """Evaluate installation prerequisites only. No account/network interaction."""
    apk = Path(apk)
    if device_api < 1 or device_api > 100:
        raise ValueError("Unsupported Android API argument")
    if not device_abis:
        raise ValueError("At least one device ABI is required")
    with ZipFile(apk) as z:
        names = z.namelist()
        if len(names) > 50000:
            raise ValueError("Unreasonably large APK file table")
        if "AndroidManifest.xml" not in names:
            raise ValueError("Not a standalone Android APK: missing manifest")
        if z.getinfo("AndroidManifest.xml").file_size > 4 * 1048576:
            raise ValueError("Manifest exceeds inspection limit")
        parsed = parse_manifest(z.read("AndroidManifest.xml"))
        attrs, sdk = parsed.get("manifest", {}), parsed.get("sdk", {})
        min_sdk = sdk.get("minSdkVersion")
        if not isinstance(min_sdk, int):
            raise ValueError("Manifest minimum Android API could not be decoded")
        package = attrs.get("package")
        version = attrs.get("versionName")
        code = attrs.get("versionCode")
        lib_paths = [n for n in names if re.fullmatch(r"lib/[^/]+/[^/]+\.so", n)]
        abis = sorted({n.split("/")[1] for n in lib_paths})
        arm64_paths = [n for n in lib_paths if n.split("/")[1] == EXPECTED_ABI]
        invalid = []
        for item in arm64_paths:
            with z.open(item) as stream:
                header = stream.read(5)
            if len(header) != 5 or header[:4] != b"\x7fELF" or header[4] != 2:
                invalid.append(item)
        v1_entry = any(n.upper().startswith("META-INF/")
                       and n.upper().endswith((".RSA", ".DSA", ".EC")) for n in names)
        if check_crc:
            bad = z.testzip()
            if bad is not None:
                raise ValueError("APK ZIP CRC failed")
    checks = {
        "messenger_package": package == EXPECTED_PACKAGE,
        "android_minimum": min_sdk <= device_api,
        "native_arm64_present": len(arm64_paths) > 0,
        "native_arm64_elf_valid": len(arm64_paths) > 0 and not invalid,
        "device_supports_arm64": EXPECTED_ABI in device_abis,
        "legacy_apk_v1_signature_artifact": v1_entry,
    }
    certificate = "not_performed"
    if check_meta_cert:
        certificate = ("matches_known_meta_certificate" if inspect_meta_certificate(apk)
                       else "not_meta_signed")
        checks["known_original_meta_certificate"] = certificate == "matches_known_meta_certificate"
    signing = "not_performed"
    if check_signing:
        try:
            r = subprocess.run(["jarsigner", "-verify", str(apk)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=90, check=False)
            signing = "jar_v1_verified" if r.returncode == 0 else "jar_v1_failed"
        except (OSError, subprocess.TimeoutExpired):
            signing = "verification_tool_failed"
        checks["legacy_signature_cryptographically_verified"] = signing == "jar_v1_verified"
    return {
        "apk_filename": apk.name, "apk_sha256": _hash_file(apk),
        "package_name": package, "version_name": version, "version_code": code,
        "manifest_min_android_api": min_sdk,
        "manifest_target_android_api": sdk.get("targetSdkVersion"),
        "native_abis": abis, "arm64_native_libraries": len(arm64_paths),
        "device_api": device_api, "device_abis": list(device_abis),
        "known_2021_arm64_api21_baseline_metadata_match":
            (version == HISTORICAL_CANDIDATE and code == HISTORICAL_VERSION_CODE
             and min_sdk == 21 and abis == [EXPECTED_ABI]),
        "checks": checks, "static_platform_gate_passed": all(checks.values()),
        "signer_verification": signing, "meta_certificate_check": certificate,
        "warnings": [
            "Passing static checks does not prove installation or launch.",
            "Meta login, modern encrypted messaging, notifications and calls remain unverified.",
            "A v1 signature file is not cryptographic verification; use --verify-signature.",
            "Original signer identity and signed-content integrity are different checks."
        ]
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("apk", type=Path)
    p.add_argument("--device-api", type=int, default=21, help="21/22 Android 5; 23 Android 6")
    p.add_argument("--device-abis", default="arm64-v8a")
    p.add_argument("--verify-signature", action="store_true")
    p.add_argument("--verify-meta-cert", action="store_true")
    p.add_argument("--skip-crc", action="store_true")
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    abis = tuple(x.strip() for x in a.device_abis.split(",") if x.strip())
    try:
        data = analyze(a.apk, a.device_api, abis, check_crc=not a.skip_crc,
                       check_signing=a.verify_signature, check_meta_cert=a.verify_meta_cert)
    except (BadZipFile, OSError, ValueError, RuntimeError, KeyError) as exc:
        p.error(str(exc))
    body = json.dumps(data, indent=2) + "\n"
    if a.output:
        a.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0 if data["static_platform_gate_passed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
