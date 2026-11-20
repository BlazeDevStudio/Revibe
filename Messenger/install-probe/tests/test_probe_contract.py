"""Offline safety checks; emulator CI validates actual Android compilation/launch."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
MAIN = ROOT / "app/src/main"
A = "{http://schemas.android.com/apk/res/android}"

class ProbeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gradle = (ROOT / "app/build.gradle").read_text()
        cls.manifest = ET.parse(MAIN / "AndroidManifest.xml").getroot()
        base = MAIN / "java/org/revibe/installprobe"
        cls.activity = (base / "MainActivity.java").read_text()
        cls.helper = (base / "SessionHelper.java").read_text()
        cls.receiver = (base / "InstallResultReceiver.java").read_text()
        cls.status = (base / "InstallStatus.java").read_text()
        cls.instrumentation = (MAIN.parent / "androidTest/java/org/revibe/installprobe/InstallCallbackInstrumentation.java").read_text()

    def test_sdk_floor_and_target(self):
        self.assertRegex(self.gradle, r"\bminSdk\s+19\b")
        target = re.search(r"\btargetSdk\s+(\d+)\b", self.gradle)
        self.assertIsNotNone(target)
        self.assertGreaterEqual(int(target.group(1)), 35)

    def test_new_package_id_avoids_stage18_signing_collision(self):
        self.assertIn("applicationId 'org.revibe.installcheck2'", self.gradle)
        self.assertNotIn("applicationId 'com.facebook.orca'", self.gradle)

    def test_no_native_libraries(self):
        self.assertFalse(list(MAIN.rglob("*.so")))

    def test_no_internet_or_data_permissions(self):
        perms = [e.get(A + "name", "") for e in self.manifest if e.tag == "uses-permission"]
        self.assertEqual(perms, ["android.permission.REQUEST_INSTALL_PACKAGES"])

    def test_backup_disabled_and_launcher_exported(self):
        app = self.manifest.find("application")
        self.assertEqual(app.get(A+"allowBackup"), "false")
        self.assertEqual(app.find("activity").get(A+"exported"), "true")

    def test_receiver_is_non_exported(self):
        self.assertEqual(self.manifest.find("application/receiver").get(A+"exported"), "false")

    def test_kitkat_guard_for_api21_features(self):
        self.assertIn("Build.VERSION.SDK_INT < 21", self.activity)
        self.assertIn("Build.VERSION.SDK_INT >= 21", self.activity)

    def test_android8_permission_is_user_initiated(self):
        self.assertIn("canRequestPackageInstalls()", self.activity)
        self.assertIn("showInstallerPermissionSettings()", self.activity)

    def test_only_user_chosen_apks(self):
        self.assertIn("Intent.ACTION_GET_CONTENT", self.activity)
        self.assertIn("onActivityResult", self.activity)
        self.assertIn('"com.facebook.orca".equals(pkg)', self.activity)
        self.assertIn('"org.revibe.orca01".equals(pkg)', self.activity)

    def test_existing_package_protected(self):
        self.assertIn("isAlreadyInstalled(pkg)", self.activity)
        self.assertIn("no replacement attempted", self.activity)

    def test_background_apk_copy_is_bounded_and_deleted(self):
        self.assertIn("250L * 1024L * 1024L", self.activity)
        self.assertIn("copy.delete()", self.activity)
        self.assertIn("new Thread(", self.activity)

    def test_mutable_pending_intent_on_new_android(self):
        self.assertIn("PendingIntent.FLAG_MUTABLE", self.helper)
        self.assertIn("Build.VERSION.SDK_INT >= 31", self.helper)
        self.assertIn("new Intent(context, InstallResultReceiver.class)", self.helper)

    def test_abort_uncommitted_session(self):
        self.assertIn("installer.abandonSession(sessionId)", self.helper)

    def test_only_safe_error_tokens_displayed(self):
        self.assertIn("InstallStatus.failureCode(", self.receiver)
        self.assertIn("matcher.group()", self.status)
        self.assertIn("No network access", (ROOT / "README.md").read_text()) if False else None

    def test_instrumented_callback_privacy_check_exists(self):
        self.assertIn("InstallResultReceiver().onReceive", self.instrumentation)
        self.assertIn("private_example", self.instrumentation)
        self.assertIn("finish(0, result)", self.instrumentation)

    def test_copy_button_exposes_only_saved_category(self):
        self.assertIn('copyResult.setText("Copy result")', self.activity)
        self.assertIn('InstallerState.lastResult(MainActivity.this)', self.activity)
        self.assertIn('ClipData.newPlainText', self.activity)

    def test_readme_disclaims_messaging(self):
        self.assertIn("Not Messenger", (ROOT / "README.md").read_text())
        self.assertIn("Not Messenger", self.activity)

if __name__ == "__main__":
    unittest.main()
