#!/usr/bin/env python3
"""Compare original archive locator hashes across APK variants, without unpacking code.

A matching locator SHA-1 for a declared output is evidence that Meta
metadata expects matching decompressed bytes. It does NOT authenticate the
original metadata or prove a working decoder.
"""
import argparse
import json
from pathlib import Path
import re
from zipfile import ZipFile

RE = re.compile(r'^([^\s]+\.dex)\s+([a-f0-9]{40})\s+(\S+)', re.M)
CATEGORIES = ('secondary-program-dex-jars', 'effects', 'longtail')


def locators(path):
    found = {}
    with ZipFile(path) as z:
        for cat in CATEGORIES:
            name = f'assets/{cat}/metadata.txt'
            if name not in z.namelist():
                continue
            data = z.read(name).decode('utf-8', 'replace')
            found[cat] = [{'output':name, 'sha1':sha1, 'locator':loc}
                          for name, sha1, loc in RE.findall(data)]
    return found


def report(apks):
    allitems = [locators(p) for p in apks]
    common = []
    for i, a in enumerate(allitems):
        for j in range(i+1, len(allitems)):
            b = allitems[j]
            for group in CATEGORIES:
                for x in a.get(group, []):
                    for y in b.get(group, []):
                        if x['sha1'] == y['sha1']:
                            common.append({'left_apk_index':i, 'right_apk_index':j,
                                'category':group, 'left_output':x['output'],
                                'right_output':y['output'], 'matching_declared_sha1':x['sha1']})
    return {'apks':[{'filename':p.name, 'locators':ls} for p,ls in zip(apks,allitems)],
            'cross_variant_matching_declared_hashes': common,
            'interpretation': 'Hashes are declared in APK package metadata. Identical values indicate expected content identity, not proof of actually extracted identical code.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('apks', nargs='+', type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    result=report(a.apks)
    s=json.dumps(result,indent=2)+'\n'
    if a.output:
        a.output.write_text(s,encoding='utf-8');print('Saved',a.output)
    else:print(s)

if __name__=='__main__':main()
