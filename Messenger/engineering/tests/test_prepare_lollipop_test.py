"""Offline preparation tool tests. No Meta APK or phone needed."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_lollipop_test as m

class PrepareLollipopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / 'original.apk'
        self.dst = Path(self.tmp.name) / 'trial.apk'
        self.src.write_bytes(b'fixture original payload')

    def tearDown(self):
        self.tmp.cleanup()

    def test_refuses_wrong_hash(self):
        with self.assertRaisesRegex(ValueError, 'Wrong APK'):
            m.verify_original(self.src)

    def test_refuses_self_overwrite(self):
        with self.assertRaisesRegex(ValueError, 'must differ'):
            m.prepare(self.src, self.src)

    def test_does_not_overwrite_existing_file(self):
        self.dst.write_bytes(b'existing important data')
        with patch.object(m, 'verify_original', return_value={}):
            with self.assertRaisesRegex(ValueError, 'already exists'):
                m.prepare(self.src, self.dst)
        self.assertEqual(self.dst.read_bytes(), b'existing important data')

    def test_copies_byte_identical_and_no_fake_claim(self):
        with patch.object(m, 'verify_original', return_value={}):
            with patch.object(m, 'sha256_file', return_value=m.SOURCE_SHA256):
                report = m.prepare(self.src, self.dst)
        self.assertEqual(self.src.read_bytes(), self.dst.read_bytes())
        self.assertFalse(report['real_messenger_login_verified'])
        self.assertFalse(report['update_gate_removed'])

    def test_corrupt_output_is_removed(self):
        with patch.object(m, 'verify_original', return_value={}):
            with patch.object(m, 'sha256_file', return_value='wrong'):
                with self.assertRaisesRegex(ValueError, 'differs'):
                    m.prepare(self.src, self.dst)
        self.assertFalse(self.dst.exists())

    def test_output_does_not_modify_original(self):
        original = self.src.read_bytes()
        with patch.object(m, 'verify_original', return_value={}):
            with patch.object(m, 'sha256_file', return_value=m.SOURCE_SHA256):
                m.prepare(self.src, self.dst)
        self.assertEqual(self.src.read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
