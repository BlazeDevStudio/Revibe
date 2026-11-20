"""Offline synthetic Android binary XML tests; no Meta APK or credentials required."""
import sys
import unittest
from pathlib import Path
import struct
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_side_by_side_lollipop as b


def fixture(package=b.PACKAGE_OLD, provider='com.facebook.orca.messages',
            permission='com.facebook.orca.provider.ACCESS'):
    strings = ['manifest', 'package', package, 'provider', 'authorities', provider,
               'permission', 'name', permission, 'activity',
               'com.facebook.orca.threadview.ThreadViewActivity']
    data=b''; offsets=[]
    for text in strings:
        offsets.append(len(data))
        data += struct.pack('<H',len(text)) + text.encode('utf-16le') + b'\x00\x00'
    count=len(strings); start=28+count*4
    pool=struct.pack('<HHI',1,28,start+len(data))+struct.pack('<IIIII',count,0,0,start,0)
    pool+=struct.pack('<'+'I'*count,*offsets)+data
    def element(name,attributes):
        vals=b''
        for key,value in attributes:
            ki=strings.index(key); vi=strings.index(value)
            vals+=struct.pack('<IIIHBBI',0xffffffff,ki,vi,8,0,3,vi)
        extension=struct.pack('<IIHHHHHH',0xffffffff,strings.index(name),20,20,len(attributes),0,0,0)
        body=struct.pack('<II',0xffffffff,0xffffffff)+extension+vals
        return struct.pack('<HHI',0x102,16,8+len(body))+body
    nodes=(element('manifest',[('package',package)])+
           element('provider',[('authorities',provider)])+
           element('permission',[('name',permission)])+
           element('activity',[('name','com.facebook.orca.threadview.ThreadViewActivity')]))
    return struct.pack('<HHI',3,8,8+len(pool)+len(nodes))+pool+nodes


class IsolatedPackageTests(unittest.TestCase):
    def test_package_rewrite(self):
        source=fixture(); fixed,summary=b.patch_manifest(source)
        self.assertEqual(len(fixed),len(source))
        self.assertTrue(summary['root_package_rewritten'])
        self.assertEqual(b.strings_and_elements(fixed)[2][0][1]['package'][1],b.PACKAGE_NEW)

    def test_authority_rewrite(self):
        fixed,summary=b.patch_manifest(fixture())
        self.assertEqual(summary['provider_authorities_rewritten'],1)
        self.assertTrue(b.strings_and_elements(fixed)[2][1][1]['authorities'][1].startswith('org.revibe.orca01.p'))

    def test_permission_rewrite(self):
        fixed,summary=b.patch_manifest(fixture())
        self.assertEqual(summary['custom_permissions_rewritten'],1)
        self.assertTrue(b.strings_and_elements(fixed)[2][2][1]['name'][1].startswith('org.revibe.orca01.m'))

    def test_app_class_names_unchanged(self):
        fixed,_=b.patch_manifest(fixture())
        self.assertEqual(b.strings_and_elements(fixed)[2][3][1]['name'][1],
                         'com.facebook.orca.threadview.ThreadViewActivity')

    def test_reject_wrong_original(self):
        with self.assertRaisesRegex(ValueError,'unexpected original package'):
            b.patch_manifest(fixture(package=b.PACKAGE_NEW))

    def test_reject_multi_authority(self):
        with self.assertRaisesRegex(ValueError,'multi-authority'):
            b.patch_manifest(fixture(provider='com.facebook.orca.foo;bar'))

    def test_reject_wrong_binary(self):
        with self.assertRaises(ValueError):
            b.patch_manifest(b'not an Android binary XML document')

    def test_generated_values_unique_and_equal_length(self):
        original='com.facebook.orca.messages'
        a=b.unique_fixed_length('org.revibe.orca01.p',original,1)
        c=b.unique_fixed_length('org.revibe.orca01.p',original,2)
        self.assertEqual(len(a),len(original))
        self.assertNotEqual(a,c)

    def test_refuse_too_short(self):
        with self.assertRaises(ValueError):
            b.unique_fixed_length('org.revibe.orca01.p','short',1)

    def test_never_overwrite_source(self):
        from unittest.mock import patch
        path=Path('/tmp/revibe-source.apk')
        with patch.object(b,'sha256',return_value=b.PINNED_SHA256):
            with self.assertRaisesRegex(ValueError,'never overwrite source'):
                b.run(path,path)


if __name__=='__main__':
    unittest.main()
