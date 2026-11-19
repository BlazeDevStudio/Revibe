import io
import json
import lzma
import struct
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from inspect_superpack import parse_spo, xz_segments
from kitkat_device_probe import classify_logcat


def synthetic_spo():
    table = b'example-1.dex\0dex\0' + bytes(4) + struct.pack('<QQ', 123, 55)
    compressed=lzma.compress(b'dex\n035\0FAKE TEST HEADER',format=lzma.FORMAT_XZ)
    full_len = 0x28 + len(table) + len(compressed)
    header=struct.pack('<IIIIQ', 0x50C00100, 0x05ABAF01, 1, 1, full_len)
    header+=bytes(0x28-len(header))
    return header + table + compressed

class TestSpo(unittest.TestCase):
    def test_file_table(self):
        record=parse_spo(synthetic_spo())
        self.assertEqual(record['file_count'], 1)
        self.assertEqual(record['entries'][0]['name'], 'example-1.dex')
        self.assertEqual(record['entry_table_offset'], 0x28)
    def test_xz(self):
        seg=xz_segments(synthetic_spo())
        self.assertEqual(len(seg), 1)
        self.assertEqual(seg[0]['status'], 'valid_xz_stream')
        self.assertTrue(seg[0]['decoded_starts_with_dex_magic'])
    def test_bad_magic(self):
        with self.assertRaises(ValueError): parse_spo(b'bad')
    def test_redaction(self):
        raw='E/AndroidRuntime: FATAL EXCEPTION: User pass=private\nSSLHandshakeException user@email.com token=abcdef\n'
        parsed=classify_logcat(raw)
        self.assertEqual(parsed['error_categories']['android_runtime_crash'],1)
        self.assertEqual(parsed['error_categories']['tls_handshake_failure'],1)
        self.assertNotIn('private',json.dumps(parsed))
        self.assertNotIn('email',json.dumps(parsed))

if __name__=='__main__': unittest.main()
