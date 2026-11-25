"""V23 release-integrity regression tests.

The Android SDK outputs below are synthetic unit fixtures ONLY; they must
never be used as real proof of an APK install, signature or Meta messaging.
"""
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Messenger.tools.release_gate import (
    BLOCKED, VERIFIED, GateError, REQUIRED_TESTS,
    check, check_android_metadata, check_release, check_sha256sums,
)


class V23ArtifactGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "Messenger").mkdir()
        self.dist = self.root / "Messenger" / "dist"
        self.dist.mkdir()
        self.certificate = "a" * 64
        self.declared = {"min_sdk": 19, "target_sdk": 35}
        self.badging = (
            "package: name='org.revibe.messenger' versionCode='1'\n"
            "sdkVersion:'19'\ntargetSdkVersion:'35'\n"
        )
        self.signature = (
            "Verified using v1 scheme (JAR signing): true\n"
            "Verified using v2 scheme (APK Signature Scheme v2): true\n"
            "Signer #1 certificate DN: CN=Revibe Release\n"
            "Signer #1 certificate SHA-256 digest: " + self.certificate + "\n"
        )

    def _tool_run(self, command, **_kwargs):
        executable = command[0]
        if executable.endswith("/aapt"):
            return SimpleNamespace(returncode=0, stdout=self.badging)
        if executable.endswith("/zipalign"):
            return SimpleNamespace(returncode=0, stdout="Verification successful")
        if executable.endswith("/apksigner"):
            return SimpleNamespace(returncode=0, stdout=self.signature)
        raise AssertionError("Unexpected SDK tool command: " + str(command))

    def _inspect(self):
        with patch("Messenger.tools.release_gate.shutil.which",
                   side_effect=lambda name: "/mock/" + name):
            with patch("Messenger.tools.release_gate.subprocess.run",
                       side_effect=self._tool_run):
                check_android_metadata(
                    self.dist / "Revibe-Messenger-universal.apk",
                    self.declared, self.certificate,
                )

    def test_compiled_manifest_and_release_signatures_can_pass_fixture(self):
        self._inspect()

    def test_reject_nonproduct_compiled_app_id(self):
        self.badging = self.badging.replace("org.revibe.messenger",
                                            "org.revibe.client.foundation")
        with self.assertRaisesRegex(GateError, "package ID"):
            self._inspect()

    def test_reject_compiled_min_sdk_mismatch(self):
        self.badging = self.badging.replace("sdkVersion:'19'", "sdkVersion:'21'")
        with self.assertRaisesRegex(GateError, "minSdk"):
            self._inspect()

    def test_reject_compiled_target_sdk_mismatch(self):
        self.badging = self.badging.replace("targetSdkVersion:'35'",
                                            "targetSdkVersion:'28'")
        with self.assertRaisesRegex(GateError, "targetSdk"):
            self._inspect()

    def test_reject_missing_v1_for_kitkat(self):
        self.signature = self.signature.replace(
            "v1 scheme (JAR signing): true", "v1 scheme (JAR signing): false"
        )
        with self.assertRaisesRegex(GateError, "v1 signature"):
            self._inspect()

    def test_reject_missing_v2_for_modern_android(self):
        self.signature = self.signature.replace(
            "v2 scheme (APK Signature Scheme v2): true",
            "v2 scheme (APK Signature Scheme v2): false",
        )
        with self.assertRaisesRegex(GateError, "v2 signature"):
            self._inspect()

    def test_reject_debug_certificate_even_with_matching_digest(self):
        self.signature = self.signature.replace(
            "CN=Revibe Release", "CN=Android Debug"
        )
        with self.assertRaisesRegex(GateError, "Debug certificate"):
            self._inspect()

    def test_reject_wrong_signer_digest(self):
        with self.assertRaisesRegex(GateError, "certificate mismatch"):
            self.certificate = "b" * 64
            self._inspect()

    def test_strict_checksum_manifest_matches_exact_release(self):
        item = {
            "filename": "Revibe-Messenger-universal.apk",
            "sha256": "f" * 64,
        }
        (self.dist / "SHA256SUMS.txt").write_text(
            "f" * 64 + "  Revibe-Messenger-universal.apk\n"
        )
        check_sha256sums(self.dist, [item])
        (self.dist / "SHA256SUMS.txt").write_text(
            "f" * 64 + "  Revibe-Messenger-universal.apk\n" +
            "0" * 64 + "  Revibe-Messenger-x86.apk\n"
        )
        with self.assertRaisesRegex(GateError, "match exactly"):
            check_sha256sums(self.dist, [item])

    def test_reject_malformed_checksum_path(self):
        (self.dist / "SHA256SUMS.txt").write_text(
            "a" * 64 + "  ../Revibe-Messenger-universal.apk\n"
        )
        with self.assertRaisesRegex(GateError, "noncanonical"):
            check_sha256sums(self.dist, [])

    def test_blocked_repo_rejects_disguised_nested_binary(self):
        (self.root / "Messenger/STATUS.json").write_text(json.dumps({
            "release_status": BLOCKED,
            "product_release": {
                "state": "BLOCKED_META_PERSONAL_INTEROPERABILITY",
                "real_meta_personal_messaging_verified": False,
                "installer_diagnostic_is_messenger": False,
            },
        }))
        nested = self.dist / "hidden"
        nested.mkdir()
        (nested / "copy.aab").write_bytes(b"no release")
        with self.assertRaisesRegex(GateError, "still BLOCKED"):
            check(self.root)

    def test_android_17_evidence_required_for_future_release(self):
        evidence = {"passed": True, "evidence": "https://github.com/org/repo/actions/runs/123"}
        matrix = [
            {"abi": abi, "api": api, "environment": "emulator",
             "passed": True, "evidence": evidence["evidence"],
             "install": True, "launch": True, "restart": True}
            for abi, api in (
                ("armeabi-v7a", 19), ("x86", 19), ("arm64-v8a", 21),
                ("x86", 23), ("x86", 29), ("x86", 35)
            )
        ]
        spec = {
            "product_kind": "personal-meta-messenger",
            "application_id": "org.revibe.messenger",
            "source_commit": "b" * 40,
            "signer_sha256": self.certificate,
            "meta_authorization": evidence,
            "functional_tests": {name: evidence for name in REQUIRED_TESTS},
            "platform_tests": matrix,
            "apks": [],
        }
        (self.dist / "BUILD_MANIFEST.json").write_text(json.dumps(spec))
        with self.assertRaisesRegex(GateError, "API37"):
            check_release(self.root, {"release_status": VERIFIED})


if __name__ == "__main__":
    unittest.main()
