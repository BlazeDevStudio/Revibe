import io
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dex_class_matrix import DEX_NAME, dex_classes
from android44_apk_preflight import preflight
from cross_variant_spo import locators
from superpack_native_surface import ELF_MACHINES


def make_dex():
    # Tiny synthetic table test, not executable or a functional Android APK.
    desc=b'Lcom/facebook/endtoend/Synthetic;'
    size=256
    buf=bytearray(size)
    buf[:8]=b'dex\n035\0'
    struct.pack_into('<II',buf,0x20,size,112)
    struct.pack_into('<II',buf,0x38,1,0x80)
    struct.pack_into('<II',buf,0x40,1,0x84)
    struct.pack_into('<II',buf,0x60,1,0x88)
    struct.pack_into('<I',buf,0x80,0xb0)
    struct.pack_into('<I',buf,0x84,0)
    struct.pack_into('<I',buf,0x88,0)
    buf[0xb0]=len(desc)
    buf[0xb1:0xb1+len(desc)]=desc
    return bytes(buf)


class TestStage3(unittest.TestCase):
    def test_multidex_filename_includes_ten_plus(self):
        self.assertTrue(DEX_NAME.fullmatch('classes.dex'))
        self.assertTrue(DEX_NAME.fullmatch('classes8.dex'))
        self.assertTrue(DEX_NAME.fullmatch('classes10.dex'))
        self.assertTrue(DEX_NAME.fullmatch('classes18.dex'))
        self.assertFalse(DEX_NAME.fullmatch('classes1.dex'))

    def test_minimal_dex_class_parser(self):
        self.assertEqual(dex_classes(make_dex()),{'Lcom/facebook/endtoend/Synthetic;'})

    def test_dex_rejects_bad_class_index(self):
        data=bytearray(make_dex())
        struct.pack_into('<I',data,0x88,5)
        with self.assertRaises(ValueError):
            dex_classes(bytes(data))

    def test_preflight_rejects_new_android(self):
        with tempfile.TemporaryDirectory() as td:
            apk=Path(td)/'sample.apk'
            with ZipFile(apk,'w') as z:
                z.writestr('AndroidManifest.xml',b'binary-xml-mock')
                z.writestr('lib/armeabi-v7a/libexample.so',b'x')
                z.writestr('META-INF/SIGNED.RSA',b'fixture')
            with patch('android44_apk_preflight.parse_manifest',return_value={
                    'sdk':{'minSdkVersion':28,'targetSdkVersion':35},
                    'manifest':{'package':'com.example.fake','versionName':'1'}}):
                r=preflight(apk,19,('armeabi-v7a',))
            self.assertFalse(r['preflight_passes'])
            self.assertFalse(r['checks']['api_minimum'])

    def test_preflight_rejects_wrong_native_arch(self):
        with tempfile.TemporaryDirectory() as td:
            apk=Path(td)/'sample.apk'
            with ZipFile(apk,'w') as z:
                z.writestr('AndroidManifest.xml',b'binary-xml-mock')
                z.writestr('lib/x86/libexample.so',b'x')
                z.writestr('META-INF/SIGNED.RSA',b'fixture')
            with patch('android44_apk_preflight.parse_manifest',return_value={
                    'sdk':{'minSdkVersion':19,'targetSdkVersion':33},
                    'manifest':{'package':'com.example.fake','versionName':'1'}}):
                r=preflight(apk,19,('armeabi-v7a',))
            self.assertFalse(r['preflight_passes'])
            self.assertFalse(r['checks']['native_abi'])

    def test_parses_metadata_and_sha(self):
        with tempfile.TemporaryDirectory() as td:
            apk=Path(td)/'sample.apk'
            sha='a'*40
            with ZipFile(apk,'w') as z:
                z.writestr('assets/longtail/metadata.txt',
                           f'.superpack_files 1\nlongtail-1.dex {sha} store.Canary\n')
            l=locators(apk)
            self.assertEqual(l['longtail'][0]['sha1'],sha)

    def test_elf_machine_dictionary(self):
        self.assertEqual(ELF_MACHINES[40],'ARM')
        self.assertEqual(ELF_MACHINES[183],'AArch64')

if __name__=='__main__': unittest.main()

class TestLogSieve(unittest.TestCase):
    def test_only_app_pid_is_counted_and_raw_text_not_exposed(self):
        from messenger_log_sieve import summarize
        log='''11-20 08:01:02.000  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main
11-20 08:01:02.001  1234  1234 E AndroidRuntime: Process: com.facebook.orca, PID: 1234
11-20 08:01:02.002  1234  1234 E AndroidRuntime: java.lang.NoClassDefFoundError token=SECRET_PRIVATE
11-20 08:01:02.003   999   999 E AndroidRuntime: SSLHandshakeException unrelated
'''
        result=summarize(log)
        self.assertEqual(result['app_pid_error_counts']['java_crash'],1)
        self.assertEqual(result['app_pid_error_counts']['android_class_missing'],1)
        self.assertNotIn('tls_certificate_failure',result['app_pid_error_counts'])
        import json
        self.assertNotIn('SECRET_PRIVATE',json.dumps(result))

    def test_no_attribution_when_unknown_process(self):
        from messenger_log_sieve import summarize
        x=summarize('11-20 08:01:02.000  1234  1234 E AndroidRuntime: FATAL EXCEPTION: main')
        self.assertEqual(x['identified_messenger_pids'],0)
        self.assertFalse(x['app_pid_error_counts'])
