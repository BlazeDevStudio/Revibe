"""Synthetic ELF fixtures: no Meta binaries or hardware required."""
import io
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from elf_android_api_audit import InspectError, android_elf_note_api, inspect_apk


def fixture(api=21, valid=True, elf_class=2):
    sections = b"\x00.shstrtab\x00.note.android.ident\x00"
    note = struct.pack("<III", 8, 4, 1) + b"Android\0" + struct.pack("<I", api)
    blob = bytearray(512)
    blob[:6] = b"\x7fELF" + bytes([elf_class, 1])
    # Header at 256, names at 64, note at 128.
    if elf_class == 2:
        struct.pack_into("<Q", blob, 40, 256)
        struct.pack_into("<HHH", blob, 58, 64, 3, 1)
    else:
        struct.pack_into("<I", blob, 32, 256)
        struct.pack_into("<HHH", blob, 46, 40, 3, 1)
    blob[64:64+len(sections)] = sections
    blob[128:128+len(note)] = note
    if elf_class == 2:
        struct.pack_into("<IIQQQQ", blob, 256+64, 1, 3, 0, 0, 64, len(sections))
        struct.pack_into("<IIQQQQ", blob, 256+128, 11, 7, 0, 0, 128, len(note))
    else:
        struct.pack_into("<IIIIII", blob, 256+40, 1, 3, 0, 0, 64, len(sections))
        struct.pack_into("<IIIIII", blob, 256+80, 11, 7, 0, 0, 128, len(note))
    if not valid:
        blob[4] = 1
    return bytes(blob)


class ElfAuditTests(unittest.TestCase):
    def test_api21_note(self):
        self.assertEqual(android_elf_note_api(fixture(21)), 21)

    def test_api19_note(self):
        self.assertEqual(android_elf_note_api(fixture(19)), 19)

    def test_api28_note(self):
        self.assertEqual(android_elf_note_api(fixture(28)), 28)

    def test_elf32_api19(self):
        self.assertEqual(android_elf_note_api(fixture(19, elf_class=1)), 19)

    def test_bad_class_rejected(self):
        with self.assertRaises(InspectError):
            android_elf_note_api(fixture(valid=False))

    def test_malformed_note_or_elf_detected(self):
        with self.assertRaises(InspectError):
            android_elf_note_api(b"\x00"*70)

    def test_zipped_apk_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fixture.apk"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("lib/arm64-v8a/libtest.so", fixture())
                z.writestr("classes.dex", b"fixture")
            report = inspect_apk(p)
            self.assertEqual(report["native_library_count"], 1)
            self.assertEqual(report["observed_native_min_api_levels"], [21])
            self.assertFalse(report["server_login_verified"])

    def test_no_native_libraries(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fixture.apk"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("classes.dex", b"fixture")
            self.assertEqual(inspect_apk(p)["observed_native_min_api_levels"], [])


if __name__ == "__main__":
    unittest.main()
