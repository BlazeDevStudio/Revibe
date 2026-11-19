#!/usr/bin/env python3
"""Build a v1+v2 signed ARM64 research candidate from supplied Messenger 588/API28 APK.

Research-only label change; not a Messenger API, login or update-gate repair.
No Meta binaries or keys are included in this source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile
from apk_v2_sign import sign_v2

PIN_SHA256='30ad524ac1c06efd75b5fd123efc89c4f61462a7eeb7b666c4f71cfd24de3aa7'
RESOURCE='assets/strings/default.frsc'
OLD=b'Update Messenger'
NEW=b'Revibe test app '
SIGNED_FILES = re.compile(r'^META-INF/(?:MANIFEST\.MF|[^/]+\.(?:RSA|DSA|EC|SF))$', re.I)

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):h.update(chunk)
    return h.hexdigest()

def run(argv, timeout=600):
    done=subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    if done.returncode:
        raise RuntimeError(f'{argv[0]} failed: {(done.stderr or done.stdout)[-1200:]}')
    return done

def build(src, out, report):
    if src.resolve()==out.resolve() or out.exists():
        raise ValueError('Refusing to overwrite source or existing artifact')
    if sha256(src)!=PIN_SHA256:
        raise ValueError('Original Messenger 588 hash mismatch')
    if len(OLD)!=len(NEW):
        raise ValueError('Resource patch length changed')
    for cmd in ['keytool','jarsigner']:
        if not shutil.which(cmd):raise RuntimeError('Missing JDK '+cmd)
    out.parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(prefix='revibe-arm64-') as td:
        td=Path(td)
        unsigned=td/'unsigned.apk'
        v1=td/'v1.apk'
        key=td/'temp.p12'
        with zipfile.ZipFile(src) as original, zipfile.ZipFile(unsigned,'w',allowZip64=True) as target:
            if original.testzip() is not None:raise ValueError('corrupt original')
            if RESOURCE not in original.namelist():raise ValueError('missing expected resource')
            for info in original.infolist():
                if SIGNED_FILES.match(info.filename):continue
                payload=original.read(info)
                if info.filename==RESOURCE:
                    if payload.count(OLD)<1:raise ValueError('no expected English prompt')
                    payload=payload.replace(OLD,NEW,1)
                target.writestr(info,payload)
        password='revibe-nonprod-arm64-test-key'
        run(['keytool','-genkeypair','-storetype','PKCS12','-keystore',str(key),'-alias','revibe-arm64',
             '-keyalg','RSA','-keysize','3072','-validity','30','-dname','CN=Revibe Test Candidate, O=Independent Research',
             '-storepass',password,'-keypass',password,'-noprompt'],120)
        run(['jarsigner','-keystore',str(key),'-storepass',password,'-keypass',password,'-sigalg','SHA256withRSA',
             '-digestalg','SHA-256','-signedjar',str(v1),str(unsigned),'revibe-arm64'],600)
        v1_text=run(['jarsigner','-verify',str(v1)],600).stdout
        if not re.search(r'^jar verified\.$',v1_text,re.M):raise RuntimeError('v1 signature verification failed')
        verify=sign_v2(v1,out,key,password.encode())
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise RuntimeError('bad CRC')
        if NEW not in z.read(RESOURCE):raise RuntimeError('missing research label')
        native={n.split('/')[1] for n in z.namelist() if n.startswith('lib/') and n.endswith('.so')}
        if native!={'arm64-v8a'}:raise RuntimeError(f'unexpected ABIs: {native}')
        if z.read('AndroidManifest.xml')!=zipfile.ZipFile(src).read('AndroidManifest.xml'):
            raise RuntimeError('manifest changed unexpectedly')
    report_data={
        'original_version':'Messenger 588.1.0.66.98', 'original_sha256':PIN_SHA256,
        'output_file':out.name,'output_sha256':sha256(out),'output_size_bytes':out.stat().st_size,
        'package':'com.facebook.orca', 'abi':'arm64-v8a','minSdkVersion':28,'targetSdkVersion':37,
        'modified':'one English string in assets/strings/default.frsc: Update Messenger -> Revibe test app ',
        'app_code_changed':False,'update_gate_fixed':False,'meta_login_verified':False,
        'e2ee_messaging_verified':False, 'device_install_verified':False,
        'v1_jarsigner':'verified','v2_integrity':verify,'zip_crc':'passed',
        'release_status':'RESEARCH ONLY — DO NOT DISTRIBUTE TO CHARITY RECIPIENTS',
        'limitations':'ARM64 v588 requires Android 9+, not Android 4.4. Meta certificate is lost on re-signing; self-check and server login may fail.'
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(report_data,indent=2)+'\n',encoding='utf-8')
    return report_data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--report',required=True,type=Path)
    args=ap.parse_args()
    print(json.dumps(build(args.original,args.output,args.report),indent=2))

if __name__=='__main__':main()
