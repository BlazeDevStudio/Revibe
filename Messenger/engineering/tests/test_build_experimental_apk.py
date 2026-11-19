"""Stage 6 resource-only experiment safety checks."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1] / "build_experimental_apk.py"
spec = importlib.util.spec_from_file_location("trial_builder", SOURCE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class Stage6Packaging(unittest.TestCase):
    def test_equal_resource_lengths_and_same_formatter(self):
        raw = b"/".join(builder.PATCHES.keys())
        result, evidence = builder.patch_resources(raw)
        self.assertEqual(len(raw), len(result))
        self.assertEqual(sum(evidence.values()), 2)
        self.assertEqual(result.count(b"%1$s"), 2)

    def test_missing_old_strings_fails_closed(self):
        with self.assertRaises(ValueError):
            builder.patch_resources(b"not relevant")

    def test_duplicate_old_strings_fails_closed(self):
        raw = b"/".join(list(builder.PATCHES.keys()) + [next(iter(builder.PATCHES))])
        with self.assertRaises(ValueError):
            builder.patch_resources(raw)

    def test_repackager_drops_invalid_signatures(self):
        with tempfile.TemporaryDirectory() as td:
            original = Path(td) / "original.apk"
            patched = Path(td) / "new.apk"
            with zipfile.ZipFile(original, "w") as archive:
                archive.writestr(builder.RESOURCE, b"/".join(builder.PATCHES.keys()))
                archive.writestr("META-INF/IMPORTED.SF", b"old signature")
                archive.writestr("META-INF/IMPORTED.RSA", b"old signature")
                archive.writestr("assets/normal.txt", b"keep")
            counts = builder.repack_original(original, patched)
            with zipfile.ZipFile(patched) as archive:
                self.assertEqual(sum(counts.values()), 2)
                self.assertNotIn("META-INF/IMPORTED.SF", archive.namelist())
                self.assertIn("assets/normal.txt", archive.namelist())

    def test_repackager_does_not_overwrite_original(self):
        with tempfile.TemporaryDirectory() as td:
            original = Path(td) / "original.apk"
            original.write_bytes(b"sample")
            with self.assertRaises(ValueError):
                builder.repack_original(original, original)

if __name__ == "__main__":
    unittest.main()
