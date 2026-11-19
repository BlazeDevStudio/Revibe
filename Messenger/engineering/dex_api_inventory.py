#!/usr/bin/env python3
"""Metadata-only DEX reference inventory for Android API compatibility research.

Parses DEX table structures, not instructions or any private account data.
A reference to an Android framework method does NOT prove that method is called
on KitKat or that it is unavailable on KitKat.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from zipfile import ZipFile

KEYWORDS = ('e2ee','labyrinth','signalprotocol','securestorage','secure_storage','keystore',
            'login','mqtt','graphql','omnistore','encryption')


def uleb(buf, offset):
    value = 0
    for shift in range(0, 35, 7):
        byte = buf[offset]
        offset += 1
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, offset
    raise ValueError('Bad ULEB128')


def dex_inventory(data):
    if len(data) < 112 or data[:4] != b'dex\n':
        raise ValueError('Not DEX')
    file_size, = struct.unpack_from('<I', data, 0x20)
    if file_size > len(data):
        raise ValueError('DEX header file_size exceeds actual length')
    string_count, string_off = struct.unpack_from('<II', data, 0x38)
    type_count, type_off = struct.unpack_from('<II', data, 0x40)
    method_count, method_off = struct.unpack_from('<II', data, 0x58)
    if string_count > 2_000_000 or method_count > 2_000_000:
        raise ValueError('Unreasonable table sizes')
    if string_off+string_count*4>len(data) or type_off+type_count*4>len(data) or method_off+method_count*8>len(data):
        raise ValueError('DEX tables out of range')
    strings=[]
    for i in range(string_count):
        offset, = struct.unpack_from('<I', data, string_off+i*4)
        _, offset=uleb(data, offset)
        end=data.find(b'\0',offset)
        if end == -1 or end-offset > 500_000:
            raise ValueError('Invalid DEX string terminator')
        strings.append(data[offset:end].decode('utf-8','replace'))
    types=[]
    for i in range(type_count):
        idx,=struct.unpack_from('<I',data,type_off+i*4)
        types.append(strings[idx])
    framework_methods=set()
    for i in range(method_count):
        c_idx, _p_idx, n_idx = struct.unpack_from('<HHI',data,method_off+i*8)
        if c_idx >= len(types) or n_idx >= len(strings):
            continue
        cls=types[c_idx]
        if cls.startswith('Landroid/'):
            framework_methods.add(cls+'->'+strings[n_idx])
    markers={k:sum(k in s.lower() for s in strings) for k in KEYWORDS}
    return {'dex_bytes':len(data),'dex_sha256':hashlib.sha256(data).hexdigest(),
            'version': data[4:7].decode('ascii','replace'),
            'strings':len(strings), 'types':len(types), 'method_refs':method_count,
            'framework_android_method_refs':len(framework_methods),
            'keyword_string_counts':markers,
            'framework_methods':framework_methods}


def inspect(path):
    totals=Counter()
    methods=set()
    per_dex=[]
    with ZipFile(path) as z:
        for n in sorted(z.namelist()):
            if n=='classes.dex' or (n.startswith('classes') and n.endswith('.dex')):
                d=dex_inventory(z.read(n))
                methods.update(d.pop('framework_methods'))
                totals.update(d['keyword_string_counts'])
                per_dex.append({'entry':n,**d})
    return {'file':path.name,'standard_dex_count':len(per_dex),'dex_files':per_dex,
            'keyword_total_in_standard_dex':dict(totals),
            'framework_methods':sorted(methods),
            'warning':'Superpacked .spo DEX is not included. References are not proof of runtime calls or required Android API levels.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('apks',nargs='+',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    arr=[inspect(p) for p in args.apks]
    if len(arr)>=2:
        base=set(arr[0]['framework_methods'])
        for other in arr[1:]:
            o=set(other['framework_methods'])
            other['new_android_framework_method_refs_vs_first']={'count':len(o-base),'sample':sorted(o-base)[:40]}
        arr[0]['comparison_baseline']=True
    for a in arr:
        a.pop('framework_methods')
    text=json.dumps(arr,indent=2)+'\n'
    if args.output:
        args.output.write_text(text,encoding='utf-8');print('Wrote '+str(args.output))
    else:print(text)

if __name__=='__main__':main()
