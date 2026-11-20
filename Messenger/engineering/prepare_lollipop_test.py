#!/usr/bin/env python3
"""Prepare a byte-identical original Meta-signed Messenger 336 trial APK.
Requires Python >=3.8, Java JDK jarsigner. Never changes APK code or signing.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

SOURCE_SHA256 = '70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab'
VERSION = '336.0.0.13.142'
API = 21
ABI = 'arm64-v8a'

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def verify_original(path):
    path = Path(path)
    if not path.is_file() or sha256_file(path) != SOURCE_SHA256:
        raise ValueError('Wrong APK: original Messenger 336 ARM64 fingerprint required')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('Corrupted ZIP member')
        names = set(z.namelist())
        if not {'AndroidManifest.xml', 'classes.dex', 'META-INF/FACEBOOK.RSA', 'META-INF/FACEBOOK.SF'} <= names:
            raise ValueError('Unexpected APK structure')
        abis = {name.split('/')[1] for name in names if name.startswith('lib/') and name.endswith('.so')}
        if abis != {ABI}:
            raise ValueError('Unexpected native architecture')
    try:
        result = subprocess.run(['jarsigner', '-verify', str(path)],
                                capture_output=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as ex:
        raise RuntimeError('Java jarsigner unavailable or timed out') from ex
    if result.returncode != 0:
        raise ValueError('Original APK signature did not verify')
    return {'version': VERSION, 'minimum_android_api': API,
            'native_abi': ABI, 'sha256': SOURCE_SHA256,
            'zip_crc': 'pass', 'original_v1_signature': 'verified'}

def prepare(source, output):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('Source and output must differ')
    evidence = verify_original(source)
    if output.exists():
        raise ValueError('Output already exists; refusing to overwrite')
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(source, 'rb') as original, open(output, 'xb') as prepared:
            shutil.copyfileobj(original, prepared, length=1024 * 1024)
        if sha256_file(output) != SOURCE_SHA256:
            raise ValueError('Output differs from signed original')
    except Exception:
        if output.exists():
            output.unlink()
        raise
    evidence.update({
        'test_artifact': output.name,
        'unchanged_original_meta_signed_apk': True,
        'modified_app_code': False,
        'update_gate_removed': False,
        'installation_on_physical_device_verified': False,
        'real_messenger_login_verified': False,
        'encrypted_message_delivery_verified': False,
        'warning': 'APK installs only if OS/ABI, package signature conflicts, storage and other device rules permit it.'
    })
    return evidence

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    try:
        result = prepare(args.source, args.output)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        ap.error(str(exc))
    payload = json.dumps(result, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding='utf-8')
    print(payload, end='')

if __name__ == '__main__':
    main()
