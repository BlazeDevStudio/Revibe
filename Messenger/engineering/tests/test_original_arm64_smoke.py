"""No real adb/device/APK required. Fake device and source checks only."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import original_arm64_smoke as s

class OriginalArm64SmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'orig.apk'
        self.path.write_bytes(b'fixture')
        self.hash = patch.object(s, 'sha256_file', return_value=s.PINNED_SHA256)
        self.hash.start()
        self.count = patch.object(s, 'adb_device_count', return_value=1)
        self.count.start()
        self.device = patch.object(s, 'device_info', return_value={
            'android_api':21, 'supported_abis':['arm64-v8a','armeabi-v7a']})
        self.device.start()
        self.installed = patch.object(s, 'package_installed', return_value=False)
        self.installed.start()

    def tearDown(self):
        self.hash.stop(); self.count.stop(); self.device.stop(); self.installed.stop()
        self.tmp.cleanup()

    def test_api21_native_arm64_eligible(self):
        r=s.run(self.path)
        self.assertEqual(r['status'],'device_platform_eligible')
        self.assertFalse(r['messenger_login_verified'])

    def test_android6_eligible(self):
        self.assertEqual(s.classify_device(23,['arm64-v8a']),'device_platform_eligible')

    def test_android4_rejected(self):
        self.assertEqual(s.classify_device(19,['arm64-v8a']),'unsupported_android_or_abi')

    def test_arm32_only_rejected(self):
        self.assertEqual(s.classify_device(23,['armeabi-v7a']),'unsupported_android_or_abi')

    def test_wrong_hash_refused(self):
        with patch.object(s,'sha256_file',return_value='wrong'):
            with self.assertRaises(ValueError):s.run(self.path)

    def test_install_requires_ack(self):
        with self.assertRaises(ValueError):s.run(self.path,install=True)

    def test_do_not_overwrite_preexisting(self):
        with patch.object(s,'package_installed',return_value=True), patch.object(s,'execute') as command:
            r=s.run(self.path,install=True,ack=True)
            self.assertEqual(r['status'],'existing_messenger_not_overwritten')
            command.assert_not_called()

    def test_install_success_still_unverified(self):
        with patch.object(s,'execute',return_value=SimpleNamespace(returncode=0,stdout='Success',stderr='')) as c:
            r=s.run(self.path,install=True,ack=True)
            self.assertEqual(r['status'],'installed_not_authenticated')
            self.assertFalse(r['encrypted_message_exchange_verified'])
            c.assert_called_once()

    def test_install_failure_redacted(self):
        result=SimpleNamespace(returncode=1,stdout='',stderr='Failure [INSTALL_FAILED_OLDER_SDK] token=secret')
        with patch.object(s,'execute',return_value=result):
            r=s.run(self.path,install=True,ack=True)
            self.assertEqual(r['install_error_code'],'INSTALL_FAILED_OLDER_SDK')
            self.assertNotIn('secret',str(r))

    def test_launch_without_install_skipped(self):
        with patch.object(s,'execute') as c:
            r=s.run(self.path,launch=True)
            self.assertEqual(r['status'],'package_not_installed_launch_skipped')
            c.assert_not_called()

    def test_launch_process_not_equal_server_login(self):
        with patch.object(s,'execute',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')),\
             patch.object(s,'process_observed',return_value=True):
            r=s.run(self.path,install=True,launch=True,ack=True,sleep_fn=lambda x:None)
            self.assertTrue(r['process_observed'])
            self.assertFalse(r['messenger_login_verified'])

    def test_reject_arbitrary_observation(self):
        with self.assertRaises(ValueError):s.run(self.path,observed_screen='contact:person')

    def test_no_connected_device(self):
        with patch.object(s,'adb_device_count',return_value=0):
            self.assertEqual(s.run(self.path)['status'],'requires_exactly_one_authorized_adb_device')

    def test_wrong_sdk_property_blocked(self):
        with self.assertRaises(ValueError):s.property_value('ro.serialno')

if __name__=='__main__':unittest.main()
