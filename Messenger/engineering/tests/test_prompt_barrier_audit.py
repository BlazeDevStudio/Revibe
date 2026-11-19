import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile
from subprocess import CompletedProcess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prompt_barrier_audit import classify_texts, classify_xml, scan_apk, inspect_live_ui, REMOTE


class FakeAdb:
    def __init__(self, ui_text='Your Messenger version is outdated'):
        self.calls = []
        self.ui_text = ui_text
    def __call__(self, args, **kwargs):
        self.calls.append(tuple(args))
        action = ' '.join(args[1:])
        if action == 'devices':
            s = 'List of devices attached\nSECRET_SERIAL\tdevice\n'
        elif action.startswith('shell pm path'):
            s = 'package:/data/app/com.facebook.orca.apk\n'
        elif action.startswith('shell uiautomator dump'):
            s = 'UI hierarchy dumped to: ' + REMOTE
        elif action.startswith('shell cat'):
            s = f'<hierarchy><node text="{self.ui_text}" content-desc="" /></hierarchy>'
        else:
            s = ''
        return CompletedProcess(args, 0, s, '')

class TestPromptBarrierAudit(unittest.TestCase):
    def test_hard_update_distinct_from_optional(self):
        c = classify_texts(['You are required to update', 'App updates', 'Profile updated'])
        self.assertEqual(c.get('mandatory_app_update'), 1)
        self.assertEqual(c.get('optional_app_update'), 1)

    def test_unsupported_os_and_play_services(self):
        c = classify_texts(['This device is not supported', 'Google Play services update required'])
        self.assertEqual(c.get('unsupported_android_or_device'), 1)
        self.assertEqual(c.get('google_play_services'), 1)

    def test_ui_classification_never_contains_raw_account_text(self):
        x = classify_xml('<hierarchy><node text="Your Messenger version is outdated" />'
                         '<node text="secret@example.com" /></hierarchy>')
        self.assertEqual(x['visible_ui_categories']['mandatory_app_update'], 1)
        self.assertNotIn('secret@example.com', json.dumps(x))
        self.assertFalse(x['original_ui_text_saved'])

    def test_malformed_or_oversize_xml(self):
        with self.assertRaises(Exception): classify_xml('<hierarchy')
        with self.assertRaises(ValueError): classify_xml('A' * (2*1024*1024+1))

    def test_static_apk_scanner_reports_categories_not_strings(self):
        with tempfile.TemporaryDirectory() as td:
            apk = Path(td) / 'synthetic.apk'
            with ZipFile(apk,'w') as z:
                z.writestr('assets/strings/default.frsc', b'\x00Your Messenger version is outdated\x00Update now\x00')
            x = scan_apk(apk)
        hits = x['resources']['assets/strings/default.frsc']['category_hits']
        self.assertEqual(hits['mandatory_app_update'], 1)
        self.assertEqual(hits['optional_app_update'], 1)
        self.assertNotIn('Your Messenger version', json.dumps(x))
        self.assertFalse(x['runtime_or_server_compatibility_tested'])

    def test_adb_cleans_device_file_and_redacts_serial(self):
        fake = FakeAdb()
        x = inspect_live_ui(run=fake)
        self.assertEqual(x['visible_ui_categories']['mandatory_app_update'], 1)
        self.assertEqual(fake.calls[-1], ('adb','shell','rm','-f',REMOTE))
        self.assertNotIn('SECRET_SERIAL', json.dumps(x))

    def test_two_devices_cannot_be_inspected(self):
        def many(args, **kw):
            return CompletedProcess(args, 0, 'List of devices attached\nONE\tdevice\nTWO\tdevice\n', '')
        x = inspect_live_ui(run=many)
        self.assertEqual(x['status'], 'requires_exactly_one_authorized_device')
        self.assertEqual(x['device_count'],2)

    def test_known_user_data_not_kept(self):
        x = classify_texts(['Dear User Jane, message from Paula: secret',
                            'Session expired. Sign in again'])
        self.assertEqual(x['login_or_session'],1)
        self.assertNotIn('Jane',str(x))

if __name__ == '__main__':
    unittest.main()
