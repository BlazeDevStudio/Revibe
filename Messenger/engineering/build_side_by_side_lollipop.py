#!/usr/bin/env python3
"""Repackage a pinned, user-supplied original Messenger 336 APK to isolate app ID.

Research-only! This addresses only Android package-name, content-provider and
custom permission collisions. It does NOT fix Meta authentication, encrypted
messaging, obsolete-version policies, or possible startup faults. No accounts.

Avoids an Android SDK dependency by rewriting *equal-length* UTF-16 strings in
Android binary XML's existing string pool and signing the APK with JDK tools.
The original APK and app DEX files are never modified.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path

PINNED_SHA256 = '70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab'
PACKAGE_OLD = 'com.facebook.orca'
PACKAGE_NEW = 'org.revibe.orca01'  # 17 characters exactly, unlike the official package
SKIP_NAMES = {'META-INF/MANIFEST.MF','META-INF/FACEBOOK.SF','META-INF/FACEBOOK.RSA'}


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def strings_and_elements(data):
    u16=lambda x:struct.unpack_from('<H',data,x)[0]
    u32=lambda x:struct.unpack_from('<I',data,x)[0]
    if len(data)<8 or u16(0)!=3 or u32(4)!=len(data):
        raise ValueError('not valid Android binary XML file')
    chunks=[]; cursor=8
    while cursor<len(data):
        if cursor+8>len(data): raise ValueError('truncated chunk')
        t,h,s=u16(cursor),u16(cursor+2),u32(cursor+4)
        if s<8 or h> s or cursor+s>len(data):raise ValueError('invalid chunk')
        chunks.append((cursor,t,h,s));cursor+=s
    pools=[c for c in chunks if c[1]==1]
    if len(pools)!=1:raise ValueError('expected one string pool')
    pool=pools[0][0]; count=u32(pool+8);flags=u32(pool+16)
    if flags&0x100:raise ValueError('UTF-8 pool unsupported for fixed-width edits')
    start=u32(pool+20)
    values=[];payloads=[]
    for n in range(count):
        off=pool+start+u32(pool+28+n*4)
        v=u16(off);prefix=2;size=v
        if v&0x8000:size=((v&0x7fff)<<16)|u16(off+2);prefix=4
        begin=off+prefix
        end=begin+2*size
        if end>len(data):raise ValueError('string out of bounds')
        values.append(data[begin:end].decode('utf-16le'))
        payloads.append((begin,end))
    elements=[]
    for pos,t,h,s in chunks:
        if t!=0x102:continue
        nameidx=u32(pos+20)
        if nameidx>=count:raise ValueError('out of range element name')
        name=values[nameidx];offset=pos+16+u16(pos+24); item=u16(pos+26);n=u16(pos+28)
        attrs={}
        for i in range(n):
            x=offset+i*item
            key_idx=u32(x+4);raw=u32(x+8);typ=data[x+15];typed=u32(x+16)
            if key_idx>=count:continue
            idx=raw if raw<count else (typed if typ==3 and typed<count else None)
            if idx is not None: attrs[values[key_idx]]=(idx,values[idx])
        elements.append((name,attrs))
    return values,payloads,elements


def unique_fixed_length(prefix,old,index):
    name=f'{prefix}{index}.'
    if len(name)>len(old):
        raise ValueError('old string too short to map to unique authority')
    return name+'x'*(len(old)-len(name))


def patch_manifest(data):
    strings,payloads,elements=strings_and_elements(data)
    replaces={}
    root=[a for n,a in elements if n=='manifest']
    if len(root)!=1 or root[0].get('package',(None,None))[1]!=PACKAGE_OLD:
        raise ValueError('unexpected original package')
    pkg_index=root[0]['package'][0]
    replaces[pkg_index]=PACKAGE_NEW
    provider_count=0;permission_count=0
    # All provider authorities must be isolated: otherwise an existing official
    # Messenger might prevent installation for duplicate authorities.
    for name,attrs in elements:
        if name=='provider' and 'authorities' in attrs:
            idx,old=attrs['authorities']
            if ';' in old:raise ValueError('unexpected multi-authority provider')
            provider_count+=1
            replaces[idx]=unique_fixed_length('org.revibe.orca01.p',old,provider_count)
        if name=='permission' and 'name' in attrs:
            idx,old=attrs['name']
            permission_count+=1
            replaces[idx]=unique_fixed_length('org.revibe.orca01.m',old,permission_count)
    # If those permission-name indices are reused in <uses-permission> and
    # component permission attributes, they change together automatically.
    new=bytearray(data)
    for idx,val in replaces.items():
        start,end=payloads[idx];old=strings[idx]
        if len(val.encode('utf-16le'))!=end-start:raise ValueError(f'string size changed: {old}')
        new[start:end]=val.encode('utf-16le')
    after,_,elems2=strings_and_elements(new)
    if next(a['package'][1] for n,a in elems2 if n=='manifest') != PACKAGE_NEW:
        raise ValueError('package patch unsuccessful')
    assert all(a['authorities'][1].startswith('org.revibe.orca01.p') for n,a in elems2 if n=='provider' and 'authorities' in a)
    return bytes(new),{'provider_authorities_rewritten':provider_count,'custom_permissions_rewritten':permission_count,'root_package_rewritten':True}


def make_unsigned(original,output):
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(output,'w',allowZip64=True) as dst:
        for info in src.infolist():
            if info.filename.upper() in SKIP_NAMES:continue
            if info.filename.endswith('/'):
                continue
            raw=src.read(info)
            if info.filename=='AndroidManifest.xml':
                raw,mod=patch_manifest(raw)
            zi=zipfile.ZipInfo(info.filename,date_time=info.date_time)
            zi.compress_type=info.compress_type
            zi.external_attr=info.external_attr
            zi.create_system=info.create_system
            zi.flag_bits=info.flag_bits & ~0x8
            # Force predictable alignment for STORED entry data (resources.arsc and libs).
            if zi.compress_type==zipfile.ZIP_STORED:
                offset=dst.fp.tell()
                base=offset+30+len(zi.filename.encode('utf-8'))
                pad=(-base-4)%4
                if pad: zi.extra=struct.pack('<HH',0xfffe,pad)+b'\x00'*pad
            dst.writestr(zi,raw)
    return mod


def run(original,output):
    if sha256(original)!=PINNED_SHA256:raise ValueError('wrong source APK SHA256')
    if original.resolve()==output.resolve():raise ValueError('never overwrite source APK')
    if shutil.which('keytool') is None or shutil.which('jarsigner') is None:
        raise RuntimeError('Java JDK keytool and jarsigner are required')
    with tempfile.TemporaryDirectory(prefix='revibe_side_by_side_') as d:
        unsigned=Path(d)/'unsigned.apk';keystore=Path(d)/'test.p12'; tmp=Path(d)/'signed.apk'
        changes=make_unsigned(original,unsigned)
        password=os.urandom(16).hex()
        subprocess.run(['keytool','-genkeypair','-alias','revibe','-keystore',str(keystore),'-storetype','PKCS12','-storepass',password,'-keypass',password,'-keyalg','RSA','-keysize','2048','-validity','30','-dname','CN=Revibe Installation Research, O=Test only, C=PH','-noprompt'],capture_output=True,text=True,check=True,timeout=30)
        subprocess.run(['jarsigner','-keystore',str(keystore),'-storetype','PKCS12','-storepass',password,'-keypass',password,'-sigalg','SHA256withRSA','-digestalg','SHA-256','-signedjar',str(tmp),str(unsigned),'revibe'],capture_output=True,text=True,check=True,timeout=180)
        verify=subprocess.run(['jarsigner','-verify','-strict',str(tmp)],capture_output=True,text=True,timeout=180)
        # -strict returns 4 for expected self-signed research certificate; ordinary verification returns zero.
        verify2=subprocess.run(['jarsigner','-verify',str(tmp)],capture_output=True,text=True,timeout=180)
        if verify2.returncode!=0 or 'jar verified' not in verify2.stdout.lower():
            raise RuntimeError('jarsigner failed archive verification')
        with zipfile.ZipFile(original) as o,zipfile.ZipFile(tmp) as z:
            if z.testzip() is not None:raise ValueError('APK ZIP integrity failure')
            assert z.read('classes.dex')==o.read('classes.dex'), 'App code unexpectedly modified'
            new,_,els=strings_and_elements(z.read('AndroidManifest.xml'))
            assert next(a['package'][1] for n,a in els if n=='manifest')==PACKAGE_NEW
            abis={n.split('/')[1] for n in z.namelist() if n.startswith('lib/') and n.endswith('.so')}
            assert abis=={'arm64-v8a'},abis
            count=sum(1 for n in z.namelist() if n.startswith('classes') and n.endswith('.dex'))
        output.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(tmp,output)
    return {'source_sha256':PINNED_SHA256,'output_sha256':sha256(output),'name':'Revibe Messenger 336 Lollipop installer-isolation trial','package':PACKAGE_NEW,'android_min_api':21,'native_abi':'arm64-v8a','original_code_modified':False,'temporary_test_signer':True,'on_device_install_tested':False,'actual_messenger_communication_verified':False,'caveat':'Changes package identity, custom permissions and provider authorities only; Meta service and login compatibility not established. Do not enter personal credentials.', 'dex_count':count,**changes}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    report=run(a.source,a.output)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()