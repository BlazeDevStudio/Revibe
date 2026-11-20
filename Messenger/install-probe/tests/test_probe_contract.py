"""Static pre-build safety tests for independent Revibe install probe."""
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


class ProbeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gradle = (ROOT / "app/build.gradle").read_text()
        cls.manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
        cls.java = (ROOT / "app/src/main/java/org/revibe/installprobe/MainActivity.java").read_text()

    def test_min_sdk_19(self):
        self.assertRegex(self.gradle, r"\bminSdk\s+19\b")

    def test_target_sdk_35_or_higher(self):
        target = re.search(r"\btargetSdk\s+(\d+)\b", self.gradle)
        self.assertIsNotNone(target)
        self.assertGreaterEqual(int(target.group(1)), 35)

    def test_distinct_package_identity(self):
        self.assertIn("applicationId 'org.revibe.installprobe'", self.gradle)
        self.assertNotIn("com.facebook.orca", self.gradle)

    def test_no_sensitive_permissions(self):
        permissions = [x.get(ANDROID + "name", "") for x in self.manifest
                       if x.tag == "uses-permission"]
        self.assertEqual(permissions, [])

    def test_launcher_activity_and_export_flag(self):
        app = self.manifest.find("application")
        self.assertEqual(app.find("activity").get(ANDROID + "exported"), "true")
        self.assertEqual(app.get(ANDROID + "allowBackup"), "false")

    def test_no_native_libraries(self):
        self.assertFalse(list((ROOT / "app/src/main").rglob("*.so")))

    def test_no_external_network_dependencies(self):
        for banned in ("HttpURLConnection", "Socket(", "getAccounts(", "READ_SMS",
                       "ACCESS_FINE_LOCATION", "WebView(", "FacebookSdk"):
            self.assertNotIn(banned, self.java)

    def test_explicit_disclaimer(self):
        self.assertIn("does not log into Facebook", self.java)
        self.assertIn("not a Messenger", (ROOT / "README.md").read_text())

    def test_api21_guard_for_supported_abis(self):
        self.assertIn("Build.VERSION.SDK_INT >= 21", self.java)
        self.assertIn("Build.SUPPORTED_ABIS", self.java)

if __name__ == "__main__":
    unittest.main()
