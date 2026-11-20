"""Offline tests for Revibe's Android 5/6 safe installation diagnostics."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import install_failure_probe as f


class InstallFailureProbeTests(unittest.TestCase):
    def test_error_code_is_redacted(self):
        error = "Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE: path=/secret/phone]"
        self.assertEqual(f.installation_failure_code("", error),
                         "INSTALL_FAILED_UPDATE_INCOMPATIBLE")
        self.assertNotIn("secret", f.installation_failure_code("", error))

    def test_parse_failed_code(self):
        self.assertEqual(
            f.installation_failure_code("INSTALL_PARSE_FAILED_NO_CERTIFICATES", ""),
            "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
        )

    def test_unknown_returns_category_only(self):
        self.assertEqual(f.installation_failure_code("path=/private/account", ""),
                         "UNCLASSIFIED_INSTALL_FAILURE")

    def test_install_requires_ack(self):
        with self.assertRaises(ValueError):
            f.probe(apk=Path("sample.apk"), install=True)

    def test_install_requires_apk(self):
        with self.assertRaises(ValueError):
            f.probe(install=True, acknowledge=True)

    def test_wrong_property_rejected(self):
        with self.assertRaises(ValueError):
            f.getprop("adb", "ro.serialno")

    def test_no_adb_device(self):
        with patch.object(f, "device_count", return_value=0):
            self.assertEqual(f.probe()["status"],
                             "requires_exactly_one_authorized_adb_device")

    def base(self):
        return patch.multiple(
            f, device_count=lambda adb: 1,
            getprop=lambda adb, key: {
                "ro.build.version.sdk": "23",
                "ro.product.cpu.abilist": "arm64-v8a,armeabi-v7a",
            }[key],
            installed_package=lambda adb: False,
        )

    def test_read_only(self):
        with self.base(), patch.object(f, "command") as cmd:
            r = f.probe()
            self.assertEqual(r["status"], "read_only_preflight_completed")
            self.assertTrue(r["native_arm64_supported"])
            cmd.assert_not_called()

    def test_existing_package_blocks_install(self):
        with self.base(), patch.object(f, "installed_package", return_value=True), \
             patch.object(f, "command") as cmd:
            r = f.probe(apk=Path("not-read.apk"), install=True, acknowledge=True)
            self.assertEqual(r["status"], "existing_messenger_preserved_install_skipped")
            cmd.assert_not_called()

    def test_wrong_source_hash_blocks_install(self):
        with self.base(), patch.object(Path, "is_file", return_value=True), \
             patch.object(f, "apk_matches_original", return_value=False), \
             patch.object(f, "command") as cmd:
            r = f.probe(apk=Path("wrong.apk"), install=True, acknowledge=True)
            self.assertEqual(r["status"], "source_apk_sha256_not_verified")
            cmd.assert_not_called()

    def test_install_failure_code_redacted(self):
        fake = SimpleNamespace(
            returncode=1, stdout="", stderr="Failure [INSTALL_FAILED_NO_MATCHING_ABIS] SECRET"
        )
        with self.base(), patch.object(Path, "is_file", return_value=True), \
             patch.object(f, "apk_matches_original", return_value=True), \
             patch.object(f, "command", return_value=fake):
            r = f.probe(apk=Path("original.apk"), install=True, acknowledge=True)
            self.assertEqual(r["install_error_code"], "INSTALL_FAILED_NO_MATCHING_ABIS")
            self.assertNotIn("SECRET", str(r))

    def test_success_does_not_claim_messaging(self):
        fake = SimpleNamespace(returncode=0, stdout="Success", stderr="")
        with self.base(), patch.object(Path, "is_file", return_value=True), \
             patch.object(f, "apk_matches_original", return_value=True), \
             patch.object(f, "command", return_value=fake):
            r = f.probe(apk=Path("original.apk"), install=True, acknowledge=True)
            self.assertTrue(r["install_succeeded"])
            self.assertFalse(r["live_messaging_verified"])

    def test_android9_cannot_install_to_android6_target(self):
        with self.base(), patch.object(f, "getprop", side_effect=lambda adb, k:
                {"ro.build.version.sdk": "28", "ro.product.cpu.abilist": "arm64-v8a"}[k]), \
             patch.object(f, "command") as cmd:
            r = f.probe(apk=Path("original.apk"), install=True, acknowledge=True)
            self.assertEqual(r["status"], "platform_does_not_match_original_336_test_target")
            cmd.assert_not_called()


    def test_android5_absent_package_does_not_block_probe(self):
        fake = SimpleNamespace(returncode=0, stdout="", stderr="")
        with patch.object(f, "command", return_value=fake) as c:
            self.assertIs(f.installed_package("adb"), False)
            c.assert_called_once_with("adb", "shell", "pm", "list", "packages", "com.facebook.orca")

    def test_android5_existing_exact_package_is_detected(self):
        fake = SimpleNamespace(returncode=0, stdout="package:com.facebook.orca\n", stderr="")
        with patch.object(f, "command", return_value=fake):
            self.assertIs(f.installed_package("adb"), True)

    def test_android5_package_manager_error_is_not_absence(self):
        fake = SimpleNamespace(returncode=1, stdout="", stderr="Error: Could not access Package Manager")
        with patch.object(f, "command", return_value=fake):
            self.assertIsNone(f.installed_package("adb"))


if __name__ == "__main__":
    unittest.main()
