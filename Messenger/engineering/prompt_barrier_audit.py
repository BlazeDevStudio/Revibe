#!/usr/bin/env python3
"""Read-only Revibe prompt-barrier inspector, for Android 4.4+ devices.

This tool finds *evidence of strings* in locally supplied APK resources and,
optionally, classifies the currently visible Android UI via authorized ADB.
It does not patch an APK, remove warnings, bypass login, or claim server support.
The UI's original text and XML never get written to local disk.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

PKG = 'com.facebook.orca'
REMOTE = '/data/local/tmp/revibe_messenger_ui_audit.xml'
MAX_XML = 2 * 1024 * 1024

# Curated patterns and labels; only labels/counts, not discovered text, are saved.
PATTERNS = {
    'mandatory_app_update': (
        r'required to update|must update|update (?:the app|messenger) to continue|'
        r'version is outdated|(?:this|your) version (?:is )?no longer supported|'
        r'no longer (?:be able to )?use this version',
    ),
    'unsupported_android_or_device': (
        r'android (?:version )?(?:is )?(?:not supported|unsupported|too old)|'
        r'(?:device|operating system) (?:is )?(?:not supported|incompatible)|'
        r'(?:not compatible|incompatible) with (?:your|this) device',
    ),
    'google_play_services': (
        r'google play services.{0,85}(?:update|required|not supported)|'
        r'(?:update|required).{0,85}google play services',
    ),
    'optional_app_update': (
        r'update available|new version (?:is )?available|update now|app updates',
    ),
    'login_or_session': (r'log in|sign in|session (?:has )?expired|enter your password',),
    'network_problem': (
        r'no internet connection|check your (?:internet|connection)|'
        r'couldn.t connect|network unavailable',
    ),
    'encryption_problem': (
        r'end.to.end encrypt|cannot decrypt|unable to decrypt',
    ),
}
REGEX = {name: re.compile('|'.join(parts), re.I) for name, parts in PATTERNS.items()}


def classify_texts(texts):
    counts = Counter()
    for value in texts:
        if not value or not isinstance(value, str):
            continue
        # One hit/category per individual field, to avoid duplicated counting.
        for name, expression in REGEX.items():
            if expression.search(value):
                counts[name] += 1
    # Do not persist the strings (account names, prompts and passwords may occur).
    return dict(sorted(counts.items()))


def classify_xml(xml_text):
    if len(xml_text.encode('utf-8', 'replace')) > MAX_XML:
        raise ValueError('UI hierarchy exceeds safety size limit')
    root = ET.fromstring(xml_text)
    values = []
    for node in root.iter('node'):
        values.extend((node.get('text', ''), node.get('content-desc', '')))
    return {
        'status': 'classified',
        'visible_ui_categories': classify_texts(values),
        'nodes_examined': sum(1 for _ in root.iter('node')),
        'original_ui_text_saved': False,
        'interpretation': 'Observed visible client UI only; origin and server enforcement not determined.',
    }


def scan_apk(apk):
    apk = Path(apk)
    if not apk.is_file():
        raise FileNotFoundError('APK not found')
    h = hashlib.sha256()
    with apk.open('rb') as f:
        for chunk in iter(lambda: f.read(2**20), b''):
            h.update(chunk)
    scans = {}
    with zipfile.ZipFile(apk) as z:
        candidates = ('assets/strings/default.frsc', 'resources.arsc')
        for entry in candidates:
            if entry not in z.namelist():
                scans[entry] = {'status': 'absent'}
                continue
            item = z.getinfo(entry)
            if item.file_size > 16 * 1024 * 1024:
                scans[entry] = {'status': 'skipped_oversize'}
                continue
            blob = z.read(entry)
            # FRSC typically stores short UTF-8 null-terminated text pieces;
            # Android resources may also contain UTF-16. False negatives are possible.
            ascii_segments = [p.decode('utf-8', 'replace') for p in blob.split(b'\x00')
                              if len(p) >= 7 and any(65 <= b <= 122 for b in p)]
            utf16_segments = [p.decode('utf-16le', 'replace') for p in blob.split(b'\x00\x00')
                              if len(p) > 12 and len(p) % 2 == 0]
            scans[entry] = {
                'status': 'scanned',
                'category_hits': classify_texts(ascii_segments + utf16_segments),
                'extraction_note': 'Pattern scan, not a complete Android/FRSC resource parser; false positives/negatives possible.',
            }
    return {
        'apk_sha256': h.hexdigest(),
        'apk_basename': apk.name,
        'resources': scans,
        'original_apk_modified': False,
        'runtime_or_server_compatibility_tested': False,
    }


def adb_call(args, timeout=25, run=subprocess.run):
    return run(['adb', *args], capture_output=True, text=True,
               errors='replace', timeout=timeout, check=False)


def inspect_live_ui(run=subprocess.run):
    def call(*args, timeout=25):
        return adb_call(list(args), timeout=timeout, run=run)

    devices = call('devices')
    if devices.returncode != 0:
        return {'status': 'adb_unavailable'}
    ready = [line.split()[0] for line in devices.stdout.splitlines()[1:]
             if len(line.split()) >= 2 and line.split()[1] == 'device']
    if len(ready) != 1:
        return {'status': 'requires_exactly_one_authorized_device', 'device_count': len(ready)}
    pkg = call('shell', 'pm', 'path', PKG)
    if pkg.returncode != 0 or 'package:' not in pkg.stdout:
        return {'status': 'messenger_not_installed'}
    try:
        result = call('shell', 'uiautomator', 'dump', REMOTE, timeout=45)
        if result.returncode != 0 or 'dumped to' not in (result.stdout + result.stderr).lower():
            return {'status': 'ui_dump_unavailable'}
        xml_result = call('shell', 'cat', REMOTE, timeout=20)
        if xml_result.returncode != 0:
            return {'status': 'ui_read_unavailable'}
        try:
            return classify_xml(xml_result.stdout)
        except (ET.ParseError, ValueError):
            return {'status': 'ui_xml_invalid_or_oversize'}
    finally:
        # Unconditional cleanup of the fixed device-side temporary file.
        call('shell', 'rm', '-f', REMOTE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path, help='APK for offline *read-only* prompt inventory')
    parser.add_argument('--inspect-ui', action='store_true',
                        help='Read current screen through ADB, classify and discard raw UI XML')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not (args.apk or args.inspect_ui):
        parser.error('Choose --apk and/or --inspect-ui')
    report = {'project': 'Revibe Messenger', 'phase': 'Stage 5 — Update Barrier Classification',
              'not_a_functionality_test': True}
    if args.apk:
        report['offline_apk'] = scan_apk(args.apk)
    if args.inspect_ui:
        report['live_ui'] = inspect_live_ui()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Wrote non-sensitive category report:', args.output)


if __name__ == '__main__':
    main()
