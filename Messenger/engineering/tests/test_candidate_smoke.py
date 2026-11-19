"""Stage 6 no-touch tests for research APK ADB smoke wrapper."""
import importlib.util
from pathlib import Path
from unittest import mock
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / "candidate_smoke.py"
spec = importlib.util.spec_from_file_location("trial_smoke", SOURCE)
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)

class CandidateSafety(unittest.TestCase):
    def test_cannot_install_without_acknowledgement(self):
        with self.assertRaises(ValueError):
            trial.smoke(Path("/nonexistent.apk"), install=True, ack=False)

    def test_no_connected_device_means_no_install_commands(self):
        with tempfile.TemporaryDirectory() as td:
            apk = Path(td) / "test.apk"
            with zipfile.ZipFile(apk, "w") as z:
                z.writestr("AndroidManifest.xml", b"test")
            with mock.patch.object(trial, "connected_count", return_value=0), mock.patch.object(trial, "adb") as adb:
                response = trial.smoke(apk, install=True, ack=True)
                self.assertEqual(response["status"], "requires_one_authorized_adb_device")
                adb.assert_not_called()

if __name__ == "__main__":
    unittest.main()
