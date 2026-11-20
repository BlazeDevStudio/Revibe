"""Android 5-compatible, read-only installed-package tri-state tests."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import package_state_probe as s

class PackageStateProbeTests(unittest.TestCase):
    def test_exact_package_found(self):
        self.assertIs(s.parse_package_list("package:com.facebook.orca\n"), True)

    def test_uninstalled_is_empty_output_with_zero_exit(self):
        self.assertIs(s.parse_package_list("", "", 0), False)

    def test_no_substring_false_positive(self):
        self.assertIs(s.parse_package_list("package:com.facebook.orca.fake\n"), False)

    def test_other_package_not_messenger(self):
        self.assertIs(s.parse_package_list("package:com.example.other\n"), False)

    def test_multiple_eligible_package_lines(self):
        self.assertIs(s.parse_package_list("package:com.other\npackage:com.facebook.orca\n"), True)

    def test_nonzero_exit_is_not_absence(self):
        self.assertIsNone(s.parse_package_list("", "Failure", 1))

    def test_error_stdout_is_not_absence(self):
        self.assertIsNone(s.parse_package_list("Error: Could not access Package Manager", "", 0))

    def test_stderr_on_success_is_inconclusive(self):
        self.assertIsNone(s.parse_package_list("", "warning", 0))

    def test_unexpected_stdout_is_inconclusive(self):
        self.assertIsNone(s.parse_package_list("Android shell version 1", "", 0))

    def test_custom_package_exact_match(self):
        self.assertTrue(s.parse_package_list("package:com.facebook.mlite", "", 0, "com.facebook.mlite"))

    def test_uses_old_android_package_manager_syntax(self):
        seen = []
        def fake(*args):
            seen.append(args)
            return SimpleNamespace(stdout="", stderr="", returncode=0)
        self.assertIs(s.installed_package("adb", fake), False)
        self.assertEqual(seen, [("adb", "shell", "pm", "list", "packages", "com.facebook.orca")])

    def test_no_adb_is_unknown(self):
        self.assertIsNone(s.installed_package("adb", lambda *args: None))

if __name__ == "__main__":
    unittest.main()
