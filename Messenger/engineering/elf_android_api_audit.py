#!/usr/bin/env python3
"""Inspect Android min-API notes in bundled native ELF libraries, without executing them.

An ELF .note.android.ident is a native build-version clue, NOT a runtime guarantee.
No APK bytes are altered or uploaded by this tool.
"""
import argparse
import json
import struct
import sys
import zipfile
from pathlib import Path

MAX_LIBRARY_BYTES = 128 * 1024 * 1024
MAX_LIBRARIES = 256


class InspectError(ValueError):
    pass


def _u32(blob, pos):
    return struct.unpack_from("<I", blob, pos)[0]


def _elf_sections(blob):
    if len(blob) < 52 or blob[:4] != b"\x7fELF" or blob[4] not in (1, 2) or blob[5] != 1:
        raise InspectError("requires little-endian ELF32 or ELF64")
    elf64 = blob[4] == 2
    if elf64 and len(blob) < 64:
        raise InspectError("truncated ELF64 header")
    if elf64:
        shoff = struct.unpack_from("<Q", blob, 40)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 58)
    else:
        shoff = struct.unpack_from("<I", blob, 32)[0]
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 46)
    required_entry_size = 64 if elf64 else 40
    if not shoff or shentsize < required_entry_size or not shnum or shnum > 4096 or shstrndx >= shnum:
        raise InspectError("missing or unsupported ELF section index")
    if shoff + shentsize * shnum > len(blob):
        raise InspectError("ELF section table out of bounds")
    entries = []
    for i in range(shnum):
        start = shoff + i * shentsize
        if elf64:
            name_off, typ, _flags, _addr, off, size = struct.unpack_from("<IIQQQQ", blob, start)
        else:
            name_off, typ, _flags, _addr, off, size = struct.unpack_from("<IIIIII", blob, start)
        # SHT_NOBITS (.bss) occupies memory at runtime, not file bytes.
        if typ != 8 and (off > len(blob) or size > len(blob) - off):
            raise InspectError("ELF section extends beyond file")
        entries.append((name_off, typ, off, 0 if typ == 8 else size))
    _n, _t, off, size = entries[shstrndx]
    strings = blob[off:off + size]
    for name_off, typ, off, size in entries:
        if name_off >= len(strings):
            continue
        end = strings.find(b"\0", name_off)
        if end == -1:
            continue
        yield (strings[name_off:end], typ, blob[off:off + size])


def android_elf_note_api(blob):
    """Extract min native Android API from .note.android.ident, or None."""
    for sec_name, sec_type, sec in _elf_sections(blob):
        if sec_name != b".note.android.ident" or sec_type != 7:
            continue
        cur = 0
        while cur + 12 <= len(sec):
            namesz, descsz, typ = struct.unpack_from("<III", sec, cur)
            cur += 12
            nameend = cur + namesz
            descstart = cur + ((namesz + 3) & ~3)
            descend = descstart + descsz
            if nameend > len(sec) or descend > len(sec):
                raise InspectError("truncated Android ELF note")
            name = sec[cur:nameend].rstrip(b"\x00")
            if name == b"Android" and typ == 1 and descsz >= 4:
                api = _u32(sec, descstart)
                if 1 <= api <= 100:
                    return api
                raise InspectError("unreasonable native API level")
            cur = descstart + ((descsz + 3) & ~3)
    return None


def inspect_apk(path):
    result = []
    with zipfile.ZipFile(path) as apk:
        libs = [n for n in apk.namelist()
                if n.startswith("lib/") and n.endswith(".so") and n.count("/") == 2]
        if len(libs) > MAX_LIBRARIES:
            raise InspectError("too many native libraries")
        for name in sorted(libs):
            item = apk.getinfo(name)
            if item.file_size > MAX_LIBRARY_BYTES:
                raise InspectError("oversized native library")
            data = apk.read(name)
            try:
                api = android_elf_note_api(data)
                status = "android_note_found" if api is not None else "android_note_absent"
            except InspectError:
                api = None
                status = "elf_format_or_note_unreadable"
            result.append({"abi": name.split("/")[1],
                           "library": name.split("/")[-1],
                           "android_ndk_min_api_note": api,
                           "status": status})
    levels = sorted({item["android_ndk_min_api_note"] for item in result
                     if item["android_ndk_min_api_note"] is not None})
    return {"native_library_count": len(result), "observed_native_min_api_levels": levels,
            "libraries": result,
            "device_install_verified": False,
            "server_login_verified": False,
            "limitation": "native ELF build notes are not an end-to-end Android runtime or Messenger compatibility test"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path, help="locally available, authorized APK")
    parser.add_argument("--output", type=Path, help="optional JSON output")
    args = parser.parse_args()
    try:
        result = inspect_apk(args.apk)
    except (OSError, zipfile.BadZipFile, InspectError) as exc:
        parser.error(str(exc))
    value = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(value, encoding="utf-8")
    print(value, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
