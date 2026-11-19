#!/usr/bin/env python3
"""Compare metadata-declared ARM Superpack DEX with unpacked x86 DEX by ordinal.

An ordinal and size resemblance is not proof of byte-for-byte equivalence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile


def compare(arm_kitkat, x86):
    with ZipFile(arm_kitkat) as a, ZipFile(x86) as b:
        manifest=a.read('assets/secondary-program-dex-jars/metadata.txt').decode('utf-8')
        arm=[(m.group(1),m.group(2)) for m in re.finditer(r'^(secondary-\d+\.dex) ([0-9a-f]{40})',manifest,re.M)]
        results=[]
        for n,(arm_name,arm_sha) in enumerate(arm,2):
            x86_name=f'classes{n}.dex'
            raw=b.read(x86_name)
            x86_sha=hashlib.sha1(raw).hexdigest()
            results.append({'kitkat_file':arm_name, 'kitkat_manifest_sha1':arm_sha,
                            'x86_file':x86_name,'x86_size':len(raw),'x86_sha1':x86_sha,
                            'binary_identical_by_sha1':x86_sha==arm_sha})
    return {'android44_apk':arm_kitkat.name,'android50_x86_apk':x86.name,
            'results':results,
            'sha1_match_count':sum(r['binary_identical_by_sha1'] for r in results),
            'caution':'Different SHA1s mean x86 DEX cannot be substituted as-is for ARM packed DEX. Class-level overlap not measured.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('kitkat',type=Path)
    p.add_argument('x86',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    s=json.dumps(compare(a.kitkat,a.x86),indent=2)+'\n'
    if a.output: a.output.write_text(s);print('Wrote '+str(a.output))
    else:print(s)
