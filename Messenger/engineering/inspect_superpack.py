#!/usr/bin/env python3
"""Read-only inventory of Meta Superpack .spo DEX archives in an APK.

Works on ordinary Python 3 without Android SDK. Enumerates archive metadata and
independently XZ-compressed streams only. It does NOT reconstruct full DEX files.
"""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import re
import struct
from zipfile import ZipFile

MAGIC = 0x50C00100
XZ_MAGIC = b'\xfd7zXZ\x00'
HEADER_CANDIDATES = (0x28, 0x38)
MAX_FILES = 256
MAX_XZ_SCAN = 256
MAX_DECODED_SEGMENT = 32 * 1024 * 1024


def read_cstr(buf, off, max_len=100):
    end = buf.find(b'\0', off, min(len(buf), off + max_len + 1))
    if end < 0:
        raise ValueError(f'Unterminated string at 0x{off:x}')
    return buf[off:end].decode('ascii'), end + 1


def read_file_table(data, off, count):
    entries = []
    last_fmt = ''
    for idx in range(count):
        name, off = read_cstr(data, off)
        fmt, off = read_cstr(data, off, 8)
        fmt = fmt or last_fmt
        last_fmt = fmt
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', name) or fmt not in ('dex', 'so', 'raw', 'blob'):
            raise ValueError(f'Invalid entry at {idx}: name={name!r} type={fmt!r}')
        if off + 20 > len(data):
            raise ValueError('Truncated file table')
        # This Messenger .spo variant stores four zero bytes after the format
        # string before its 64-bit size/checksum fields.
        if data[off:off+4] != b'\0\0\0\0':
            raise ValueError('Unexpected flags in Messenger .spo file entry')
        off += 4
        uncompressed_size, checksum = struct.unpack_from('<QQ', data, off)
        off += 16
        if uncompressed_size > (1 << 31):
            raise ValueError('Implausibly large output')
        entries.append({'name': name, 'format': fmt,
                        'declared_uncompressed_size': uncompressed_size,
                        'archive_checksum64': f'{checksum:016x}'})
    return entries, off


def parse_spo(data):
    if len(data) < 0x50 or struct.unpack_from('<I', data)[0] != MAGIC:
        raise ValueError('Not a recognized .spo archive')
    version, stream_count, file_count = struct.unpack_from('<III', data, 4)
    declared_size, = struct.unpack_from('<Q', data, 0x10)
    if not 0 < file_count <= MAX_FILES:
        raise ValueError(f'Unexpected file_count: {file_count}')
    if declared_size != len(data):
        raise ValueError(f'Archive-size mismatch: {declared_size} != {len(data)}')
    candidates = []
    for start in HEADER_CANDIDATES:
        try:
            entries, end = read_file_table(data, start, file_count)
            candidates.append((start, end, entries))
        except (ValueError, UnicodeError):
            pass
    if not candidates:
        raise ValueError('Could not locate a valid .spo file table')
    start, end, entries = candidates[0]
    return {'magic': f'{MAGIC:08x}', 'version_hex': f'{version:08x}',
            'stream_count_header': stream_count, 'file_count': file_count,
            'archive_bytes': len(data), 'entry_table_offset': start,
            'entry_table_end': end, 'entries': entries}


def xz_segments(data, max_scan=MAX_XZ_SCAN):
    results = []
    index = 0
    while len(results) < max_scan:
        off = data.find(XZ_MAGIC, index)
        if off < 0:
            break
        index = off + 6
        item = {'offset': off}
        try:
            dec = lzma.LZMADecompressor(format=lzma.FORMAT_XZ)
            # Extraction is deliberately bounded: a corrupt archive must not
            # trigger huge allocations or an output of proprietary app code.
            output = dec.decompress(data[off:], max_length=MAX_DECODED_SEGMENT)
            if not dec.eof:
                item['status'] = 'exceeds_bound_or_incomplete'
                item['decoded_bytes_lower_bound'] = len(output)
            else:
                item['status'] = 'valid_xz_stream'
                item['decoded_bytes'] = len(output)
                item['compressed_bytes'] = len(data) - off - len(dec.unused_data)
                item['decoded_starts_with_dex_magic'] = output.startswith(b'dex\n')
                # No raw decompressed bytes included in output.
        except lzma.LZMAError:
            item['status'] = 'not_independent_xz_stream'
        results.append(item)
    return results


def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inspect_apk(path, scan_xz=True):
    reports = []
    with ZipFile(path) as z:
        paths = sorted(n for n in z.namelist() if n.endswith('.dex.spo'))
        for name in paths:
            data = z.read(name)
            result = {'archive_path': name, 'sha256': hashlib.sha256(data).hexdigest()}
            result.update(parse_spo(data))
            metadata_path = name.rsplit('/', 1)[0] + '/metadata.txt'
            if metadata_path in z.namelist():
                metadata = z.read(metadata_path).decode('utf-8', 'replace')
                locators = re.findall(r'(?m)^([^\s.][^\s]*)\s+[0-9a-f]{40}\s+', metadata)
                result['metadata_locator_names'] = locators
                result['locator_names_match'] = set(locators) == {e['name'] for e in result['entries']}
            if scan_xz:
                xs = xz_segments(data)
                result['xz_independent_stream_count'] = sum(x['status'] == 'valid_xz_stream' for x in xs)
                result['xz_magic_count_scanned'] = len(xs)
                result['xz_begins_with_dex_header'] = sum(bool(x.get('decoded_starts_with_dex_magic')) for x in xs)
                result['xz_decoded_segment_total_bytes'] = sum(x.get('decoded_bytes', 0) for x in xs)
                # To keep report compact, retain first five successful streams.
                result['xz_sample'] = [x for x in xs if x['status'] == 'valid_xz_stream'][:5]
            reports.append(result)
    return {'apk_name': path.name, 'apk_sha256': sha256_file(path),
            'archives': reports,
            'limitations': 'XZ block recognition is not Superpack DEX reconstruction; decoded payloads are never exported.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('apk', type=Path)
    p.add_argument('--no-xz', action='store_true', help='Quick metadata only')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    report = inspect_apk(args.apk, not args.no_xz)
    raw = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(raw + '\n', encoding='utf-8')
        print(f'Wrote {args.output}')
    else:
        print(raw)

if __name__ == '__main__':
    main()
