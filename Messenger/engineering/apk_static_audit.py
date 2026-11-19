#!/usr/bin/env python3
"""Read-only static APK inventory, including binary AndroidManifest.xml and DEX headers.
No execution, patching, network, or extraction of private account information.
"""
import os, sys, zipfile, hashlib, json, struct, collections, re, datetime, glob
from pathlib import Path

U16=lambda b,o:struct.unpack_from('<H',b,o)[0]
U32=lambda b,o:struct.unpack_from('<I',b,o)[0]

def _ulen8(data,pos):
    a=data[pos];pos+=1
    if a&128: a=((a&127)<<8)|data[pos];pos+=1
    return a,pos

def _ulen16(data,pos):
    a=U16(data,pos); pos+=2
    if a&0x8000: a=((a&0x7fff)<<16)|U16(data,pos);pos+=2
    return a,pos

def parse_manifest(data):
    if len(data)<8 or U16(data,0)!=3: return {'error':'not Android binary XML'}
    pool=[];out=[];p=8
    while p+8 <= len(data):
        typ,hs,size=struct.unpack_from('<HHI',data,p)
        if size<hs or size<8 or p+size>len(data):break
        if typ==1:
            n=U32(data,p+8);flags=U32(data,p+16);start=U32(data,p+20)
            for i in range(n):
                at=p+start+U32(data,p+hs+4*i)
                if flags&0x100:
                    _,at=_ulen8(data,at)
                    length,at=_ulen8(data,at)
                    pool.append(data[at:at+length].decode('utf8','replace'))
                else:
                    length,at=_ulen16(data,at)
                    pool.append(data[at:at+length*2].decode('utf-16le','replace'))
        if typ==0x0102 and pool:
            off=p+16
            nameidx=U32(data,off+4);attrstart=U16(data,off+8);attrsize=U16(data,off+10);count=U16(data,off+12)
            name=pool[nameidx] if nameidx<len(pool) else f'UNKNOWN:{nameidx}'
            attrs={}
            for i in range(min(count,500)):
                aa=off+attrstart+i*attrsize
                if aa+20>p+size:break
                nsid,nid,raw=struct.unpack_from('<III',data,aa)
                dtype=data[aa+15];v=U32(data,aa+16)
                k=pool[nid] if nid<len(pool) else f'UNK:{nid}'
                if raw!=0xffffffff and raw<len(pool): val=pool[raw]
                elif dtype==3 and v<len(pool): val=pool[v]
                elif dtype==0x12: val=bool(v)
                elif dtype in [0x10,0x11]:val=v
                else:val=f'0x{v:08x}(type {dtype})'
                attrs[k]=val
            out.append({'tag':name,'attrs':attrs})
        p+=size
    interesting=[x for x in out if x['tag'] in ('manifest','uses-sdk','application','uses-permission','uses-permission-sdk-23','uses-feature','activity','service','receiver','provider')]
    outinfo={'elements':len(out),'sdk':{},'manifest':{},'application':{},'permissions':[], 'features':[], 'components':collections.Counter()}
    for x in interesting:
        tag=x['tag']; a=x['attrs']
        if tag=='manifest': outinfo['manifest']=a
        elif tag=='uses-sdk':outinfo['sdk']=a
        elif tag=='application':outinfo['application']=a
        elif tag.startswith('uses-permission'):outinfo['permissions'].append(a.get('name'))
        elif tag=='uses-feature':outinfo['features'].append(a)
        else:outinfo['components'][tag]+=1
    outinfo['components']=dict(outinfo['components'])
    return outinfo


def audit(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while part:=f.read(1024*1024):h.update(part)
    ret={'filename':Path(path).name,'sha256':h.hexdigest(),'size_bytes':os.path.getsize(path)}
    with zipfile.ZipFile(path,'r') as z:
        infos=z.infolist(); files=[f.filename for f in infos]
        ret['zip_entries']=len(files)
        ret['compressed_bytes']=sum(x.compress_size for x in infos)
        ret['uncompressed_bytes']=sum(x.file_size for x in infos)
        try: ret['manifest']=parse_manifest(z.read('AndroidManifest.xml'))
        except Exception as e:ret['manifest']={'error':str(e)}
        ret['dex']={}
        for name in sorted(n for n in files if re.fullmatch('classes(\d*)\.dex',n)):
            with z.open(name) as f:head=f.read(112)
            ret['dex'][name]={'size_bytes':z.getinfo(name).file_size,'dex_version':head[:8].decode('latin1','replace').strip('\0'), 'string_ids':U32(head,56),'type_ids':U32(head,64),'method_ids':U32(head,88),'class_defs':U32(head,96)}
        so=[x for x in infos if x.filename.startswith('lib/') and x.filename.endswith('.so')]
        ret['lib_arches']={}
        for arch in sorted(set(x.filename.split('/')[1] for x in so)):
            s=[x for x in so if x.filename.split('/')[1]==arch]
            ret['lib_arches'][arch]={'count':len(s),'bytes':sum(x.file_size for x in s),'names':sorted(x.filename.split('/')[-1] for x in s)}
        ret['cert_files']=[x for x in files if re.search(r'META-INF/.*\.(RSA|DSA|EC)$',x,re.I)]
        ret['asset_groups']=dict(collections.Counter(x.split('/')[0] for x in files).most_common(15))
        ret['suspicious_zip_names']=[x for x in files if '..' in Path(x).parts]
    return ret

if __name__=='__main__':
    paths=glob.glob('/mnt/data/*.apk')
    all_data=[audit(p) for p in sorted(paths)]
    with open('/mnt/data/messenger_apk_static_audit.json','w') as f:json.dump(all_data,f,indent=2,default=list)
    for a in all_data:
        m=a['manifest'];print('\n'+a['filename'])
        print('size',round(a['size_bytes']/1048576,1),'MiB','sha256',a['sha256'])
        print('manifest',m.get('manifest'));print('sdk',m.get('sdk'))
        print('application',m.get('application'))
        print('permissions',len(m.get('permissions',[])),m.get('permissions',[])[:30]);print('components',m.get('components'))
        print('DEX',len(a['dex']),sum(x['size_bytes'] for x in a['dex'].values())//1024,'KiB', 'classes',sum(x['class_defs'] for x in a['dex'].values()))
        print('LIBS',[(k,v['count'],round(v['bytes']/1048576,2)) for k,v in a['lib_arches'].items()])
        print('CERT',a['cert_files'])
