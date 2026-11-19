#!/usr/bin/env python3
"""Offline installation-compatibility preflight for original Messenger APKs.

This checks manifest minSdk, native ABI and legacy APK v1 signing presence;
it does *not* test install, launch, server acceptance, chat or encryption.
"""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from apk_static_audit import parse_manifest


def preflight(apk, api=19, abis=('armeabi-v7a',)):
    with ZipFile(apk) as z:
        paths=z.namelist()
        manifest=parse_manifest(z.read('AndroidManifest.xml'))
        sdk=manifest.get('sdk',{})
        min_api=sdk.get('minSdkVersion')
        if not isinstance(min_api,int):
            raise ValueError('Manifest has no usable integer minSdkVersion')
        archs=sorted({n.split('/')[1] for n in paths if n.startswith('lib/') and n.endswith('.so') and len(n.split('/'))==3})
        legacy_v1=any(n.upper().startswith('META-INF/') and n.upper().endswith(('.RSA','.DSA','.EC')) for n in paths)
        native_abi_match= not archs or bool(set(archs)&set(abis))
        min_api_match=api>=min_api
        v1_needed=api<24
        result={
          'apk_filename':apk.name,
          'package':manifest.get('manifest',{}).get('package'),
          'version':manifest.get('manifest',{}).get('versionName'),
          'manifest_min_sdk':min_api,
          'manifest_target_sdk':sdk.get('targetSdkVersion'),
          'device_api':api,
          'device_supported_abis':list(abis),
          'apk_native_abis':archs,
          'legacy_v1_signature_file_present':legacy_v1,
          'checks':{
            'api_minimum':min_api_match,
            'native_abi':native_abi_match,
            'legacy_signature_artifact_for_old_android':legacy_v1 or not v1_needed,
          },
          'preflight_passes': min_api_match and native_abi_match and (legacy_v1 or not v1_needed),
          'warnings':['A certificate entry being present does not cryptographically validate v1 signing.',
            'Passing static checks does not guarantee install, launch, authentication, encrypted chats or current-server compatibility.',
            'Never distribute altered Meta APKs as official Messenger.'],
        }
        return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('apks',nargs='+',type=Path)
    p.add_argument('--api',type=int,default=19)
    p.add_argument('--abis',default='armeabi-v7a',help='Comma-separated supported ABIs, e.g. armeabi-v7a,armeabi')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    if args.api<1 or args.api>100: p.error('Invalid Android API')
    abis=tuple(x.strip() for x in args.abis.split(',') if x.strip())
    if not abis: p.error('At least one device ABI required')
    d={'checks':[preflight(x,args.api,abis) for x in args.apks]}
    raw=json.dumps(d,indent=2)+'\n'
    if args.output:
        args.output.write_text(raw,encoding='utf-8');print('Saved',args.output)
    else:print(raw)

if __name__=='__main__':main()
