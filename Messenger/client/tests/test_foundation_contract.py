"""Static foundation contract tests; real Android compile and emulator work in CI."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main"
A = "{http://schemas.android.com/apk/res/android}"


class FoundationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = (ROOT / "app/build.gradle").read_text()
        cls.manifest = ET.parse(APP / "AndroidManifest.xml").getroot()
        cls.activity = (APP / "java/org/revibe/foundation/MainActivity.java").read_text()
        cls.gate = (APP / "java/org/revibe/foundation/BackendGate.java").read_text()
        cls.settings = (APP / "java/org/revibe/foundation/AccessibilitySettings.java").read_text()
        cls.instrument = (ROOT / "app/src/androidTest/java/org/revibe/foundation/FoundationInstrumentation.java").read_text()
        cls.readme = (ROOT / "README.md").read_text()

    def test_api19_and_target35(self):
        self.assertRegex(self.build, r"\bminSdk 19\b")
        self.assertRegex(self.build, r"\btargetSdk 35\b")

    def test_non_release_distinct_id(self):
        self.assertIn("applicationId 'org.revibe.client.foundation'", self.build)
        self.assertNotIn("applicationId 'org.revibe.messenger'", self.build)
        self.assertNotIn("applicationId 'com.facebook.orca'", self.build)

    def test_no_sensitive_permissions(self):
        perms = [x.get(A + "name") for x in self.manifest if x.tag == "uses-permission"]
        self.assertEqual(perms, [])

    def test_backup_disabled(self):
        self.assertEqual(self.manifest.find("application").get(A + "allowBackup"), "false")

    def test_launcher_explicit(self):
        self.assertEqual(self.manifest.find("application/activity").get(A + "exported"), "true")

    def test_no_native_code(self):
        self.assertFalse(list(APP.rglob("*.so")))

    def test_no_fake_messaging_or_webview(self):
        self.assertNotRegex(self.activity, r"new\s+WebView\s*\(")
        self.assertNotIn("EditText", self.activity)
        self.assertNotIn("http://", self.activity)
        self.assertNotIn("https://", self.activity)
        self.assertIn("No messages can be delivered", self.activity)

    def test_blocking_backend_real(self):
        self.assertIn("return false", self.gate)
        self.assertIn("throw new UnsupportedOperationException", self.gate)
        self.assertIn("BLOCKED_META_PERSONAL_INTEROPERABILITY", self.gate)

    def test_accessible_readable_text(self):
        for size in ("26", "23", "20", "18"):
            self.assertRegex(self.activity, r"\b" + size + r",\s+Color\.")
        self.assertIn("setImportantForAccessibility", self.activity)
        self.assertIn("ScrollView", self.activity)

    def test_persistent_large_text_ui_is_real(self):
        self.assertIn('getSharedPreferences', self.settings)
        self.assertIn('edit.putBoolean(LARGE_TEXT, large)', self.settings)
        self.assertIn('AccessibilitySettings.setExtraLarge', self.activity)
        self.assertIn('button.setMinHeight(dp(56))', self.activity)
        self.assertIn('AccessibilitySettings.isExtraLarge', self.instrument)

    def test_instrumentation_denial_checks(self):
        self.assertIn("BackendGate.beginPersonalMessengerSession()", self.instrument)
        self.assertIn("PASS: ", self.instrument)
        self.assertIn("NO Meta messaging tested", self.instrument)

    def test_readme_truthtful(self):
        self.assertIn("NOT FUNCTIONAL MESSENGER", self.readme)
        self.assertIn("No authorized Meta path", self.readme)


if __name__ == "__main__":
    unittest.main()
