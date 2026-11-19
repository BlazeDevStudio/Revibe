#!/usr/bin/env python3
"""Read-only DEX class-definition comparison for the three user-supplied APKs.

Only classes present in standard classes*.dex are measurable. Superpacked
payloads are excluded. No app execution, APK modification, accounts, or network.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
from zipfile import ZipFile

DEX_NAME = re.compile(r'^classes(?:[2-9]|[1-9][0-9]+)?\.dex$')
MARKERS = {
    'e2ee': ('e2ee', 'endtoend', 'end_to_end', 'e2e_'),
    'labyrinth': ('labyrinth',),
    'secure_storage': ('securestorage', 'secure_storage', 'keychain', 'key_store'),
    'signal_protocol': ('signalprotocol', 'signal_protocol', 'libsignal'),
    'keystore': ('keystore', 'key_store'),
    'login_auth': ('auth', 'login', 'oauth', 'account'),
    'messaging': ('messaging', 'message', 'thread'),
    'transport': ('mqtt', 'graphql', 'omnistore', 'thrift'),
}


def dex_classes(data):
    if len(data) < 112 or data[:4] != b'dex\n':
        raise ValueError('Invalid DEX file header')
    file_size = struct.unpack_from('<I', data, 0x20)[0]
    header_size = struct.unpack_from('<I', data, 0x24)[0]
    if file_size != len(data) or header_size != 112:
        raise ValueError('Inconsistent DEX header or size')
    string_count, string_off = struct.unpack_from('<II', data, 0x38)
    type_count, type_off = struct.unpack_from('<II', data, 0x40)
    class_count, class_off = struct.unpack_from('<II', data, 0x60)
    if string_count > 2_000_000 or type_count > 2_000_000 or class_count > 1_000_000:
        raise ValueError('Unreasonable DEX table size')
    if (string_off + 4 * string_count > len(data) or
            type_off + 4 * type_count > len(data) or
            class_off + 32 * class_count > len(data)):
        raise ValueError('DEX tables extend beyond end of file')

    def uleb(off):
        v = 0
        for i in range(5):
            if off >= len(data):
                raise ValueError('Truncated ULEB')
            b = data[off]
            off += 1
            v |= (b & 0x7f) << (i * 7)
            if b < 128:
                return v, off
        raise ValueError('ULEB too long')

    strings = []
    for i in range(string_count):
        at = struct.unpack_from('<I', data, string_off + i * 4)[0]
        if at >= len(data):
            raise ValueError('Bad string offset')
        _, at = uleb(at)
        # DEX modified UTF-8: class descriptors contain ASCII only, so UTF-8
        # replacement parsing is sufficient for this *symbol* inventory.
        end = data.find(b'\0', at)
        if end < 0 or end - at > 1_000_000:
            raise ValueError('Bad DEX string terminator')
        strings.append(data[at:end].decode('utf-8', 'replace'))

    types = []
    for i in range(type_count):
        sidx = struct.unpack_from('<I', data, type_off + 4 * i)[0]
        if sidx >= len(strings):
            raise ValueError('Bad type string index')
        types.append(strings[sidx])
    result = set()
    for i in range(class_count):
        cidx = struct.unpack_from('<I', data, class_off + 32 * i)[0]
        if cidx >= len(types):
            raise ValueError('Bad class definition index')
        sym = types[cidx]
        if not sym.startswith('L') or not sym.endswith(';'):
            raise ValueError('Bad class descriptor')
        result.add(sym)
    return result


def summarize(path):
    names = set()
    files = []
    by_prefix = Counter()
    with ZipFile(path) as z:
        for entry in sorted(n for n in z.namelist() if DEX_NAME.match(n)):
            data = z.read(entry)
            classes = dex_classes(data)
            files.append({'entry': entry, 'class_defs': len(classes),
                          'sha256': hashlib.sha256(data).hexdigest()})
            names.update(classes)
    for n in names:
        parts = n[1:-1].split('/')
        if len(parts) >= 3:
            p = '/'.join(parts[:3])
        elif len(parts) == 2:
            p = '/'.join(parts[:2])
        else:
            p = parts[0]
        by_prefix[p] += 1
    cats = {}
    for label, values in MARKERS.items():
        found = sorted(n for n in names if any(v in n.lower() for v in values))
        cats[label] = {'matching_class_defs': len(found), 'sample': found[:8]}
    return {
        'apk_name': path.name,
        'standard_dex_count': len(files),
        'standard_dex_files': files,
        'defined_class_count': len(names),
        'top_namespace_prefixes': by_prefix.most_common(15),
        'markers': cats,
    }, names


def report(paths):
    results = []
    allnames = []
    for path in paths:
        s, names = summarize(path)
        results.append(s)
        allnames.append(names)
    comparisons = []
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            common = allnames[i] & allnames[j]
            union = allnames[i] | allnames[j]
            comparisons.append({'left_index': i, 'right_index': j,
                'common_defined_class_names': len(common),
                'union_defined_class_names': len(union),
                'jaccard': round(len(common) / len(union), 6) if union else 0,
                'caution': 'Class-name overlap measures symbol identity only, not behavioral compatibility; incomplete for Superpacked APKs.'})
    return {'source_apks': results, 'comparisons': comparisons,
      'limits': 'Read only standard classes*.dex. KitKat seven secondary Superpacked DEX files are NOT decompressed; class counts are therefore severely incomplete for that APK. Matching keyword names do NOT establish working E2EE or login.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('apks', type=Path, nargs='+')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    obj = report(args.apks)
    s = json.dumps(obj, indent=2) + '\n'
    if args.output:
        args.output.write_text(s, encoding='utf-8')
        print('Saved', args.output)
    else:
        print(s)

if __name__ == '__main__':
    main()
