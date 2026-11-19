"""Independent non-Meta fixture tests for the ARM64 research package/signing tools."""
import datetime as dt
import hashlib
import pathlib
import sys
import tempfile
import unittest
import zipfile

ENGINEERING=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ENGINEERING))
import apk_v2_sign as v2
import build_arm64_research as builder
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates
from cryptography.x509.oid import NameOID

class Stage7Tests(unittest.TestCase):
    def test_research_label_same_length(self):
        self.assertEqual(len(builder.OLD), len(builder.NEW))
        self.assertEqual(builder.OLD,b'Update Messenger')

    def test_sha_pin_and_distinct_output(self):
        self.assertEqual(len(builder.PIN_SHA256),64)
        self.assertNotEqual(builder.PIN_SHA256, hashlib.sha256(b'mock').hexdigest())

    def test_v2_signing_rejects_modified_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            td=pathlib.Path(td)
            inp=td/'fixture_unsigned.zip'; out=td/'signed.zip'; secret=td/'key.p12'
            with zipfile.ZipFile(inp,'w') as z:
                z.writestr('data.txt','Original test content (NOT a Meta APK)')
            private_key=rsa.generate_private_key(public_exponent=65537, key_size=2048)
            name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Unit Test Only')])
            now=dt.datetime.now(dt.timezone.utc)
            cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name)
                  .public_key(private_key.public_key()).serial_number(x509.random_serial_number())
                  .not_valid_before(now-dt.timedelta(days=1))
                  .not_valid_after(now+dt.timedelta(days=1))
                  .sign(private_key,hashes.SHA256()))
            secret.write_bytes(serialize_key_and_certificates(b'local-test',private_key,cert,None,serialization.BestAvailableEncryption(b'testing')))
            result=v2.sign_v2(inp,out,secret,b'testing')
            self.assertEqual(result['content_digest'],'passed')
            self.assertEqual(v2.verify_v2(out)['v2_signature'],'RSA-SHA256 verified')
            with zipfile.ZipFile(out) as z:
                self.assertEqual(z.read('data.txt'),b'Original test content (NOT a Meta APK)')
            tampered=bytearray(out.read_bytes()); tampered[40]^=1
            out.write_bytes(tampered)
            with self.assertRaises((ValueError,Exception)):
                v2.verify_v2(out)

if __name__=='__main__':unittest.main()
