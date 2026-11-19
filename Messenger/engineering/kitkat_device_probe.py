#!/usr/bin/env python3
"""Privacy-conscious Android 4.4 / Messenger local device diagnostic.

Requires ADB installed and USB debugging authorized on a phone. Does not
upload anything, alter encryption, record messages, or save raw logcat lines.
Only use on devices and test accounts you are authorized to inspect.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

PACKAGE = 'com.facebook.orca'

SIGNATURES = [
    ('android_runtime_crash', r'FATAL EXCEPTION'),
    ('missing_android_class', r'NoClassDefFoundError|ClassNotFoundException'),
    ('missing_android_method', r'NoSuchMethodError'),
    ('dex_verifier', r'VerifyError|DexOpt|DexFile.*exception'),
    ('native_library', r'UnsatisfiedLinkError|dlopen failed'),
    ('security_exception', r'SecurityException'),
    ('tls_handshake_failure', r'SSLHandshakeException|CertPathValidatorException|CERTIFICATE_VERIFY_FAILED'),
    ('network_resolution_failure', r'UnknownHostException|EAI_NODATA'),
    ('network_connection_failure', r'ConnectException|SocketTimeoutException'),
    ('process_anr', r'ANR in com\.facebook\.orca'),
]
COMPILED = [(name, re.compile(pattern, re.I)) for name, pattern in SIGNATURES]


def classify_logcat(text):
    """Return error classes/counts ONLY; do not echo or store logs."""
    counts = Counter()
    lines = text.splitlines()
    for line in lines:
        for name, pattern in COMPILED:
            if pattern.search(line):
                counts[name] += 1
    return {'scope':'device-wide error indicators; not attributed specifically to Messenger', 'lines_examined': len(lines), 'error_categories': dict(counts)}


def run_adb(*args, timeout=40):
    cmd = ['adb', *args]
    result = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def getprop(property_name):
    rc, out, err = run_adb('shell', 'getprop', property_name)
    return out.strip() if rc == 0 else 'unavailable'


def safe_device_check():
    rc, out, err = run_adb('devices')
    devices = [l.split()[0] for l in out.splitlines()[1:] if l.endswith('\tdevice')]
    if rc or len(devices) != 1:
        raise RuntimeError('Requires exactly one authorized ADB device; found '+str(len(devices)))
    return hashlib.sha256(devices[0].encode()).hexdigest()[:12]


def probe(install_apk=None, launch=False, read_logcat=False):
    if not shutil.which('adb'):
        raise RuntimeError('ADB is not installed or missing from PATH')
    anonymized_id = safe_device_check()
    report = {'captured_utc': datetime.now(timezone.utc).isoformat(),
              'device_id_hash_prefix': anonymized_id,
              'android_version': getprop('ro.build.version.release'),
              'api_level': getprop('ro.build.version.sdk'),
              'primary_cpu_abi': getprop('ro.product.cpu.abi'),
              'supported_cpu_abi_list': getprop('ro.product.cpu.abilist'),
              'package': PACKAGE}
    rc, out, err = run_adb('shell', 'pm', 'path', PACKAGE)
    report['messenger_package_installed'] = rc == 0 and 'package:' in out
    if install_apk is not None:
        if not install_apk.is_file() or install_apk.suffix.lower() != '.apk':
            raise ValueError('The --install path must exist and end in .apk')
        # Never include stderr: install errors occasionally contain file paths or IDs.
        rc, out, err = run_adb('install', '-r', str(install_apk), timeout=120)
        match = re.search(r'INSTALL_FAILED_[A-Z_]+', out + err)
        report['install'] = ('succeeded' if rc == 0 and 'Success' in out else (match.group(0) if match else 'failed_unknown'))
    if launch:
        rc, out, err = run_adb('shell','monkey','-p',PACKAGE,'-c','android.intent.category.LAUNCHER','1')
        report['launcher_invocation'] = 'command_sent' if rc == 0 else 'command_failed'
    if read_logcat:
        rc, out, err = run_adb('logcat', '-d', '-v', 'brief', timeout=45)
        report['logcat_classification'] = classify_logcat(out[-8_000_000:]) if rc == 0 else {'error':'logcat_failed'}
    report['privacy'] = 'No raw logs, messages, contacts, credentials or tokens saved; device identifier hashed.'
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--install', type=Path, metavar='APK', help='Opt-in install/reinstall Messenger')
    p.add_argument('--launch', action='store_true', help='Opt-in launch Messenger')
    p.add_argument('--classify-logcat', action='store_true', help='Extract error labels only; discard raw logs')
    p.add_argument('--output', type=Path, default=Path('kitkat_device_report.json'))
    a=p.parse_args()
    result=probe(a.install,a.launch,a.classify_logcat)
    a.output.write_text(json.dumps(result,indent=2)+'\n', encoding='utf-8')
    print('Wrote '+str(a.output))

if __name__=='__main__':
    main()
