"""Regression tests for the release firewall; no Meta accounts or APK binaries."""
import json
from pathlib import Path
import tempfile
import unittest

from Messenger.tools.release_gate import BLOCKED, GateError, check


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "Messenger").mkdir()
        self.status = {
            "release_status": BLOCKED,
            "product_release": {
                "state": "BLOCKED_META_PERSONAL_INTEROPERABILITY",
                "real_meta_personal_messaging_verified": False,
                "installer_diagnostic_is_messenger": False,
            },
        }
        self.write_status()

    def write_status(self):
        (self.root / "Messenger/STATUS.json").write_text(json.dumps(self.status))

    def test_blocked_repository_is_truthtfully_green_not_a_messenger_release(self):
        self.assertIn("BLOCKED", check(self.root))

    def test_explicit_release_request_fails_closed(self):
        with self.assertRaisesRegex(GateError, "still BLOCKED"):
            check(self.root, release=True)

    def test_stray_messenger_apk_triggers_strict_gate(self):
        dist = self.root / "Messenger/dist"
        dist.mkdir()
        (dist / "Revibe-Messenger-arm64-v8a.apk").write_bytes(b"not an apk")
        with self.assertRaisesRegex(GateError, "still BLOCKED"):
            check(self.root)

    def test_manifest_triggers_strict_gate_even_without_apk(self):
        dist = self.root / "Messenger/dist"
        dist.mkdir()
        (dist / "BUILD_MANIFEST.json").write_text("{}")
        with self.assertRaisesRegex(GateError, "still BLOCKED"):
            check(self.root)

    def test_inconsistent_product_flags_fail(self):
        self.status["product_release"]["installer_diagnostic_is_messenger"] = True
        self.write_status()
        with self.assertRaisesRegex(GateError, "must not masquerade"):
            check(self.root)

    def test_missing_messenger_blocker_fails(self):
        self.status["product_release"]["state"] = "READY"
        self.write_status()
        with self.assertRaisesRegex(GateError, "blocker"):
            check(self.root)

    def test_claim_of_release_without_artifacts_is_rejected(self):
        self.status["release_status"] = "VERIFIED FUNCTIONAL MESSENGER RELEASE"
        self.write_status()
        with self.assertRaisesRegex(GateError, "Missing or invalid JSON"):
            check(self.root)


if __name__ == "__main__":
    unittest.main()
