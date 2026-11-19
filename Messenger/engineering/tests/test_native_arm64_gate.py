"""Synthetic tests for the native Android 5 ARM64 APK gate; no proprietary code."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import BadZipFile, ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import native_arm64_gate as gate

def fake_manifest(min_sdk=21, package="com.facebook.orca", version="336.0.0.13.142",
                  code=297217556):
    return {"manifest": {"package": package, "versionName": version,
                         "versionCode": code},
            "sdk": {"minSdkVersion": min_sdk, "targetSdkVersion": 30}}

class NativeArm64Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.apk = Path(self.temp.name) / "candidate.apk"

    def tearDown(self):
        self.temp.cleanup()

    def write_apk(self, header=b"\x7fELF\x02", abi="arm64-v8a", v1=True):
        with ZipFile(self.apk, "w") as z:
            z.writestr("AndroidManifest.xml", b"test manifest fixture")
            z.writestr(f"lib/{abi}/libexample.so", header + b"test-only bytes")
            if v1:
                z.writestr("META-INF/CERT.RSA", b"not a real signature")

    def result(self, manifest=None, **kwargs):
        with patch.object(gate, "parse_manifest", return_value=manifest or fake_manifest()):
            return gate.analyze(self.apk, **kwargs)

    def test_api21_pass(self):
        self.write_apk()
        result = self.result()
        self.assertTrue(result["static_platform_gate_passed"])
        self.assertTrue(result["known_2021_arm64_api21_baseline_metadata_match"])

    def test_api23_pass(self):
        self.write_apk()
        self.assertTrue(self.result(device_api=23)["static_platform_gate_passed"])

    def test_api28_requirement_rejected(self):
        self.write_apk()
        self.assertFalse(self.result(fake_manifest(min_sdk=28))["static_platform_gate_passed"])

    def test_arm32_rejected(self):
        self.write_apk(header=b"\x7fELF\x01", abi="armeabi-v7a")
        self.assertFalse(self.result()["static_platform_gate_passed"])

    def test_wrong_package_rejected(self):
        self.write_apk()
        self.assertFalse(self.result(fake_manifest(package="example.other"))["static_platform_gate_passed"])

    def test_wrong_elf_class_rejected(self):
        self.write_apk(header=b"\x7fELF\x01")
        self.assertFalse(self.result()["checks"]["native_arm64_elf_valid"])

    def test_missing_v1_signature_rejected(self):
        self.write_apk(v1=False)
        self.assertFalse(self.result()["static_platform_gate_passed"])

    def test_missing_manifest_rejected(self):
        with ZipFile(self.apk, "w") as z:
            z.writestr("example.txt", "test")
        with self.assertRaisesRegex(ValueError, "missing manifest"):
            self.result()

    def test_crc_corruption_detected(self):
        self.write_apk()
        data = self.apk.read_bytes()
        at = data.index(b"test manifest fixture")
        self.apk.write_bytes(data[:at] + b"X" + data[at + 1:])
        with self.assertRaises((ValueError, BadZipFile)):
            self.result()

    def test_unknown_version_not_historic_candidate(self):
        self.write_apk()
        result = self.result(fake_manifest(version="other"))
        self.assertTrue(result["static_platform_gate_passed"])
        self.assertFalse(result["known_2021_arm64_api21_baseline_metadata_match"])

    def test_device_without_arm64_rejected(self):
        self.write_apk()
        self.assertFalse(self.result(device_abis=("armeabi-v7a",))["static_platform_gate_passed"])

    def test_invalid_device_api_rejected(self):
        self.write_apk()
        with self.assertRaises(ValueError):
            self.result(device_api=-1)

    def test_nonmeta_certificate_rejected(self):
        self.write_apk()
        with patch.object(gate, "inspect_meta_certificate", return_value=False):
            self.assertFalse(self.result(check_meta_cert=True)["static_platform_gate_passed"])

    def test_meta_certificate_recognized(self):
        self.write_apk()
        with patch.object(gate, "inspect_meta_certificate", return_value=True):
            self.assertTrue(self.result(check_meta_cert=True)["static_platform_gate_passed"])

if __name__ == "__main__":
    unittest.main()
