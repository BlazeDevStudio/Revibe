#!/usr/bin/env python3
"""Report declared native Superpack bridge symbols and ELF deps (read-only).

This is *not* a decoder; runtime functions must not be assumed interoperable.
Uses `readelf` if present for DT_NEEDED; basic ELF e_machine is read in Python.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
from zipfile import ZipFile

KEYWORDS=(b'init_superpack_archive',b'init_superpack_file',b'createSuperpackFileNative',
          b'readNative',b'appendNative',b'closeNative',b'getNameNative',
          b'com/facebook/superpack/SuperpackArchive',b'com/facebook/superpack/SuperpackFile',
          b'decompress_instructions_with_format',b'decompress_with_format')
ELF_MACHINES={3:'x86',40:'ARM',62:'x86-64',183:'AArch64'}


def inspect(path):
    arr=[]
    with ZipFile(path) as z:
        for name in sorted(n for n in z.namelist() if n.endswith('/libsuperpack-jni.so')):
            raw=z.read(name)
            if raw[:4]!=b'\x7fELF' or len(raw)<20:
                raise ValueError('Not ELF')
            machine=struct.unpack_from('<H',raw,18)[0] if raw[5]==1 else struct.unpack_from('>H',raw,18)[0]
            symbols=[s.decode() for s in KEYWORDS if s in raw]
            dep=[]
            if shutil.which('readelf'):
                # readelf consumes a temporary file to inspect dynamic dependencies.
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.so') as fp:
                    fp.write(raw);fp.flush()
                    c=subprocess.run(['readelf','-d',fp.name],capture_output=True,text=True,timeout=10,check=False)
                dep=re.findall(r'\(NEEDED\).*\[(.*?)\]',c.stdout)
            arr.append({'apk_elf_path':name, 'elf_bits':32 if raw[4]==1 else 64,
                        'native_machine':ELF_MACHINES.get(machine,str(machine)),
                        'bridge_symbol_strings':symbols,
                        'needed_libraries':dep})
    return {'apk':path.name,'superpack_libraries':arr,
       'warning':'Symbol presence and DT_NEEDED dependencies do not prove any decoder works on an ordinary Linux host. Android JNI/Bionic runtime is required.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('apks',nargs='+',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    obj=[inspect(x) for x in a.apks]
    raw=json.dumps(obj,indent=2)+'\n'
    if a.output:
        a.output.write_text(raw,encoding='utf-8');print('Saved',a.output)
    else:print(raw)
if __name__=='__main__':main()
