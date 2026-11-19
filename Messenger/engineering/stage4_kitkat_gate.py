#!/usr/bin/env python3
"""Stage 4: original-APK integrity, KitKat applicability and OPTIONAL ADB smoke test.

Tests only a user-supplied, unmodified Messenger 410 API19 ARMv7 APK by
pinned SHA-256. Never captures credentials, conversations, or raw logcat.
No root, binary rewriting, interception, or encryption bypass.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

from android44_apk_preflight import preflight
from messenger_log_sieve import summarize

ORIGINAL_SHA256 = '006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8'
PKG = 'com.facebook.orca'


def digest_file(path):
    hash_obj = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def parse_devices(adb_output):
    entries = []
    for line in adb_output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == 'device':
            entries.append(parts[0])
    return entries


def parse_ps_pids(stdout):
    # KitKat ps commonly has USER PID PPID VSIZE RSS WCHAN PC NAME.
    # Android O uses a different layout; PID must be read via the header.
    lines = stdout.splitlines()
    if not lines:
        return []
    header = lines[0].split()
    try:
        pid_idx = header.index('PID')
    except ValueError:
        return []
    found = []
    for line in lines[1:]:
        fields = line.split()
        if len(fields) <= pid_idx:
            continue
        if fields[-1] == PKG or fields[-1].startswith(PKG + ':'):
            pid = fields[pid_idx]
            if pid.isdecimal():
                found.append(int(pid))
    return sorted(set(found))


def verify_v1_with_jarsigner(apk, invoke=subprocess.run):
    """Verify APK v1 signer digests (does not establish signer trust).

    jarsigner's *non-strict* mode is deliberate: Meta's app certificate is
    self-signed, so strict PKIX checks misleadingly reject it. Check return
    code AND the explicit verification marker. Never echo tool output.
    """
    if not shutil.which('jarsigner'):
        return {'status': 'not_tested', 'reason': 'Java jarsigner unavailable'}
    try:
        proc = invoke(['jarsigner', '-verify', str(apk)], capture_output=True,
                      text=True, timeout=120, check=False, errors='replace')
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'not_tested', 'reason': type(exc).__name__}
    outcome = (proc.stdout or '') + '\n' + (proc.stderr or '')
    verified = proc.returncode == 0 and bool(re.search(r'(?im)^jar verified\.$', outcome))
    return {
        'status': 'verified_v1_integrity' if verified else 'verification_failed',
        'signed_contents_verified': verified,
        'self_signed_certificate_warning': 'self-signed' in outcome.lower(),
        'certificate_trust_established': False,
        'weak_signing_key_warning': ('keysize' in outcome.lower() or 'key size' in outcome.lower()),
        'explanation': 'JAR/v1 integrity only; not APK v2 verification, store provenance, or proof of server functionality.'
    }


class Adb:
    def __init__(self, command='adb'):
        self.command = command

    def run(self, *arguments, timeout=30):
        return subprocess.run([self.command, *arguments], capture_output=True,
                              text=True, errors='replace', check=False, timeout=timeout)

    def prop(self, name):
        result = self.run('shell', 'getprop', name)
        return result.stdout.strip() if result.returncode == 0 else ''


def device_smoke(adb, apk, install, launch, observe_seconds=4):
    """Only system facts and grouped error counts; no raw device identifiers."""
    devs = adb.run('devices')
    if devs.returncode != 0:
        raise RuntimeError('ADB devices failed (no device actions performed)')
    connected = parse_devices(devs.stdout)
    if len(connected) != 1:
        raise RuntimeError('Expected exactly one authorized ADB device; found ' + str(len(connected)))
    sdk = adb.prop('ro.build.version.sdk')
    abi = adb.prop('ro.product.cpu.abi')
    abi2 = adb.prop('ro.product.cpu.abi2')
    supported = [x for x in (abi, abi2) if x]
    abi_list = adb.prop('ro.product.cpu.abilist')
    if abi_list:
        supported.extend(x.strip() for x in abi_list.split(',') if x.strip())
    supported = sorted(set(supported))
    try:
        sdk_num = int(sdk)
    except ValueError:
        raise RuntimeError('Device API level is not available; no changes made')
    device_gate = preflight(apk, sdk_num, tuple(supported))
    report = {
        'one_authorized_device': True,
        'android_sdk': sdk_num,
        'device_abis': supported,
        'device_install_preflight_passes': device_gate['preflight_passes'],
        'actions_requested': {'install_original': bool(install), 'launch': bool(launch)},
    }
    if (install or launch) and not device_gate['preflight_passes']:
        report['action_outcome'] = 'not_run_due_to_incompatible_device'
        return report
    pkg = adb.run('shell', 'pm', 'path', PKG)
    report['package_installed_before'] = pkg.returncode == 0 and 'package:' in pkg.stdout
    if install:
        outcome = adb.run('install', '-r', str(apk), timeout=180)
        raw = (outcome.stdout or '') + (outcome.stderr or '')
        fail = re.search(r'INSTALL_FAILED_[A-Z_]+', raw)
        report['install_result'] = ('succeeded' if outcome.returncode == 0 and
                                    'Success' in outcome.stdout else (fail.group() if fail else 'failed_unknown'))
        if report['install_result'] != 'succeeded':
            report['launch_result'] = 'not_attempted_after_install_failure'
            return report
    if launch:
        before = adb.run('shell', 'ps')
        pids_before = parse_ps_pids(before.stdout) if before.returncode == 0 else []
        result = adb.run('shell', 'monkey', '-p', PKG, '-c', 'android.intent.category.LAUNCHER', '1')
        report['launch_command'] = 'sent' if result.returncode == 0 else 'failed'
        if observe_seconds:
            time.sleep(observe_seconds)
        after = adb.run('shell', 'ps')
        pids_after = parse_ps_pids(after.stdout) if after.returncode == 0 else []
        report['app_process_observed_after_launch'] = bool(pids_after)
        report['process_observation'] = ('observed' if pids_after else 'not_observed')
        report['process_preexisting'] = bool(pids_before)
        # Android 4.4 supports -d and -v threadtime. Keep raw bytes in memory.
        logs = adb.run('logcat', '-d', '-v', 'threadtime', '-t', '10000', timeout=50)
        report['redacted_app_logcat'] = (summarize(logs.stdout) if logs.returncode == 0
                                         else {'status':'unavailable'})
        report['launch_and_process_are_not_login_proof'] = True
    report['sensitive_data_policy'] = 'No account details, message text, original logs, or device serial stored'
    return report


def build_report(apk, adb_device=False, install=False, launch=False, observe_seconds=4, adb=None):
    if not apk.is_file():
        raise FileNotFoundError('APK not found')
    sha = digest_file(apk)
    known = sha == ORIGINAL_SHA256
    report = {
        'project': 'Messenger 410 Android 4.4 compatibility',
        'phase': 'Stage 4 — original APK runtime gate',
        'captured_utc': datetime.now(timezone.utc).isoformat(),
        'apk_sha256': sha,
        'is_known_original_kitkat_apk': known,
        'device_test_completed': False,
        'modern_login_verified': False,
        'encrypted_chat_send_receive_verified': False,
    }
    if not known:
        report['error'] = 'SHA-256 differs from the exact previously audited original: no device actions allowed'
        return report
    report['kitkat_arm_preflight'] = preflight(apk, 19, ('armeabi-v7a','armeabi'))
    report['apk_v1_signature_integrity'] = verify_v1_with_jarsigner(apk)
    if adb_device:
        if not report['kitkat_arm_preflight']['preflight_passes']:
            report['error'] = 'Static preflight failed; device actions refused'
        else:
            report['device'] = device_smoke(adb or Adb(), apk, install, launch, observe_seconds)
            report['device_test_completed'] = bool(launch)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('apk', type=Path, help='Original Messenger 410 minAPI19 ARMv7 APK only')
    p.add_argument('--adb-device', action='store_true', help='Opt into reading an authorized USB connected test device')
    p.add_argument('--install-original', action='store_true', help='Explicitly install/reinstall original APK')
    p.add_argument('--launch', action='store_true', help='Explicitly launch Messenger and inspect process')
    p.add_argument('--observe-seconds', type=int, default=4)
    p.add_argument('--output', type=Path, default=Path('stage4_original_apk_gate.json'))
    a = p.parse_args()
    if (a.install_original or a.launch) and not a.adb_device:
        p.error('--install-original/--launch require --adb-device')
    if not 0 <= a.observe_seconds <= 30:
        p.error('--observe-seconds must be 0–30')
    report = build_report(a.apk, a.adb_device, a.install_original, a.launch, a.observe_seconds)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Wrote redacted report:', a.output)
    if 'error' in report:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
