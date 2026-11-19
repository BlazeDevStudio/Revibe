#!/usr/bin/env python3
"""One-command, read-only Messenger KitKat Stage 3 repeatable static audit.

Requires all three user-owned APKs in --apk-dir; never changes the APKs.
"""
import argparse
import hashlib
import json
from pathlib import Path
from android44_apk_preflight import preflight
from cross_variant_spo import report as metadata_report
from dex_class_matrix import report as class_report
from superpack_native_surface import inspect as native_inspect


def select_inputs(folder):
    apks = sorted(folder.glob('*.apk'))
    groups = [
      [x for x in apks if '410.0.0.17.85' in x.name and 'minAPI19' in x.name],
      [x for x in apks if '410.0.0.17.85' in x.name and 'minAPI21' in x.name],
      [x for x in apks if '588.1.0.66.98' in x.name and 'minAPI28' in x.name],
    ]
    if any(len(x)!=1 for x in groups):
        raise ValueError('Need exactly one each: v410 API19, v410 API21, v588 API28')
    return [x[0] for x in groups]


def hashes(paths):
    d={}
    for p in paths:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(4*1024*1024),b''):
                h.update(b)
        d[p.name]=h.hexdigest()
    return d


def execute(folder, out):
    paths=select_inputs(folder)
    out.mkdir(parents=True,exist_ok=True)
    reports={
      'dex_class_comparison.json':class_report(paths),
      'metadata_cross_variant.json':metadata_report(paths),
      'android44_preflight_results.json':{'checks':[preflight(p,19,('armeabi-v7a','armeabi')) for p in paths]},
      'superpack_native_bridges.json':[native_inspect(p) for p in paths],
    }
    for name, obj in reports.items():
        (out/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    summary={'input_sha256':hashes(paths),
      'standard_dex_classes':[a['defined_class_count'] for a in reports['dex_class_comparison.json']['source_apks']],
      'kitkat_preflight_pass':[x['preflight_passes'] for x in reports['android44_preflight_results.json']['checks']],
      'tests':'Only static analysis performed. No login, messaging, or device execution tested.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apk-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,default=Path('stage3_static_results'))
    a=p.parse_args()
    s=execute(a.apk_dir,a.output_dir)
    print('Saved 5 JSON result files to',a.output_dir)
    print('Preflight compatibility:', s['kitkat_preflight_pass'])

if __name__=='__main__':main()
