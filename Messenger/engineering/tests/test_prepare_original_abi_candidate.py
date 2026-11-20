"""Offline tests: no Meta APK files or Android devices required."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_original_abi_candidate as m

class OriginalCandidateTests(unittest.TestCase):
    def test_32_on_android5(self):
        self.assertEqual(m.choose(21, ["armeabi-v7a"]), ["arm32-api19"])
    def test_64_on_android5(self):
        self.assertEqual(m.choose(21, ["arm64-v8a"]), ["arm64-api21"])
    def test_both_on_android5(self):
        self.assertEqual(m.choose(21, ["arm64-v8a", "armeabi-v7a"]),
                         ["arm32-api19", "arm64-api21"])
    def test_32_on_kitkat(self):
        self.assertEqual(m.choose(19, ["armeabi-v7a"]), ["arm32-api19"])
    def test_64_on_kitkat_disallowed(self):
        self.assertEqual(m.choose(19, ["arm64-v8a"]), [])
    def test_older_unsupported(self):
        self.assertEqual(m.choose(18, ["armeabi-v7a"]), [])
    def test_x86_not_claimed(self):
        self.assertEqual(m.choose(23, ["x86"]), [])
    def test_unknown_label_fails(self):
        with self.assertRaises(ValueError):
            m.verify(Path("missing.apk"), "bad")
    def test_wrong_hash_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"fake.apk"
            p.write_bytes(b"junk")
            with self.assertRaises(ValueError):
                m.verify(p, "arm32-api19")
    def test_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"source.apk"
            p.write_bytes(b"fixture")
            with self.assertRaises(ValueError):
                m.prepare(p, p, "arm32-api19")
    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"source.apk"
            q = Path(td)/"target.apk"
            p.write_bytes(b"source"); q.write_bytes(b"preserve")
            with self.assertRaises(ValueError):
                m.prepare(p, q, "arm32-api19")
            self.assertEqual(q.read_bytes(), b"preserve")
    def test_mocked_copy_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"source.apk"; p.write_bytes(b"test source")
            q = Path(td)/"new.apk"
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            entry = {**m.CANDIDATES["arm32-api19"], "sha256": sha}
            with patch.dict(m.CANDIDATES, {"arm32-api19": entry}), \
                 patch.object(m, "verify", return_value={"verified": True}):
                result = m.prepare(p, q, "arm32-api19")
            self.assertEqual(p.read_bytes(), q.read_bytes())
            self.assertTrue(result["verified"])
    def test_missing_structure_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"source.apk"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("unrelated", "content")
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            entry = {**m.CANDIDATES["arm32-api19"], "sha256": sha}
            with patch.dict(m.CANDIDATES, {"arm32-api19": entry}):
                with self.assertRaisesRegex(ValueError, "Missing original"):
                    m.verify(p, "arm32-api19", False)

if __name__ == "__main__":
    unittest.main()
