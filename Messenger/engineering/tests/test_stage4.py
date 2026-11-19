import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stage4_kitkat_gate import (parse_devices, parse_ps_pids, device_smoke,
                                  verify_v1_with_jarsigner, ORIGINAL_SHA256)
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess


class FakeAdb:
    def __init__(self, good=True):
        self.calls=[]
        self.good=good
    def prop(self, name):
        return {'ro.build.version.sdk':'19','ro.product.cpu.abi':'armeabi-v7a',
                'ro.product.cpu.abi2':'armeabi','ro.product.cpu.abilist':''}.get(name,'')
    def run(self, *args, **kw):
        self.calls.append(args)
        key=' '.join(args)
        text=''
        if key=='devices': text='List of devices attached\nredacted-device\tdevice\n'
        if key=='shell pm path com.facebook.orca':text='package:/data/app/com.facebook.orca.apk\n'
        if key=='shell ps':text='USER PID PPID VSIZE RSS WCHAN PC NAME\nu0_a123 171 1 1000 1000 ffff ffff com.facebook.orca\n'
        if key.startswith('install'):text='Success\n'
        if key.startswith('shell monkey'):text='Events injected: 1\n'
        if key.startswith('logcat'):text='11-20 04:50:01.012 171 172 E AndroidRuntime: FATAL EXCEPTION: main\n'
        return CompletedProcess(args,0,text,'')


class TestStage4(unittest.TestCase):
    def test_detect_device_lines(self):
        self.assertEqual(parse_devices('List of devices attached\nSERIAL\tunauthorized\nSIM\tdevice\n'), ['SIM'])
    def test_no_probing_serial_if_two_devices(self):
        class Many(FakeAdb):
            def run(self,*args,**kw):
                if args==('devices',): return CompletedProcess(args,0,'List of devices attached\na\tdevice\nb\tdevice\n','')
                raise AssertionError('Should not be called')
        with self.assertRaisesRegex(RuntimeError,'exactly one'):
            device_smoke(Many(),Path('unused.apk'), False,False)
    def test_kitkat_ps_parser(self):
        ps='USER PID PPID VSIZE RSS WCHAN PC NAME\nu0_a12 519 1 1000 20 a b com.facebook.orca\nu0_a12 520 1 1000 20 a b com.facebook.orca:push\nu0_a12 101 1 1000 20 a b com.facebook.katana\n'
        self.assertEqual(parse_ps_pids(ps),[519,520])
    def test_no_synthetic_verification(self):
        def fake(*args, **kw):return CompletedProcess(args,0,'no proof present','')
        with patch('stage4_kitkat_gate.shutil.which',return_value='/usr/bin/jarsigner'):
            x=verify_v1_with_jarsigner(Path('test.apk'),fake)
        self.assertEqual(x['status'],'verification_failed')
    def test_signed_selfsigned_but_valid(self):
        def fake(*args, **kw):return CompletedProcess(args,0,'jar verified.\nThis jar contains entries whose signer certificate is self-signed.','')
        with patch('stage4_kitkat_gate.shutil.which',return_value='/usr/bin/jarsigner'):
            x=verify_v1_with_jarsigner(Path('test.apk'),fake)
        self.assertEqual(x['status'],'verified_v1_integrity')
        self.assertFalse(x['certificate_trust_established'])
    @patch('stage4_kitkat_gate.preflight', return_value={'preflight_passes':True})
    @patch('stage4_kitkat_gate.time.sleep',return_value=None)
    def test_live_summary_redacts_log_entries(self,*mocks):
        report=device_smoke(FakeAdb(), Path('user.apk'), True,True,0)
        self.assertEqual(report['install_result'],'succeeded')
        self.assertTrue(report['app_process_observed_after_launch'])
        s=str(report)
        self.assertNotIn('redacted-device',s)
        self.assertNotIn('FATAL EXCEPTION',s)
        self.assertFalse('modern_login_verified' in report)
        self.assertIn('redacted_app_logcat', report)

if __name__=='__main__':unittest.main()
