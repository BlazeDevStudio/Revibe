#!/usr/bin/env python3
"""Small, audited-example APK Signature Scheme v2 signer/verifier for a local research file.

Not a substitute for Android SDK apksigner on production releases. This code uses
APK v2 format described by Android Open Source Project and independently validates
the resulting digest and cryptographic signature.
"""
import hashlib
import math
import struct
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_der_x509_certificate

MAGIC = b'APK Sig Block 42'
BLOCK_ID = 0x7109871a
SIG_ID = 0x0103  # RSA SHA256 PKCS1 v1.5
MB = 1 << 20
u32 = lambda n: struct.pack('<I', n)
u64 = lambda n: struct.pack('<Q', n)
lp = lambda b: u32(len(b)) + b


def get_layout(data):
    pos = data.rfind(b'PK\x05\x06', max(0, len(data) - 65557))
    if pos < 0 or pos + 22 > len(data):
        raise ValueError('No ZIP EOCD')
    if pos + 22 + struct.unpack_from('<H', data, pos + 20)[0] != len(data):
        raise ValueError('Invalid EOCD comment length')
    cd_size, cd_off = struct.unpack_from('<II', data, pos + 12)
    if cd_off == 0xffffffff or cd_size == 0xffffffff:
        raise ValueError('ZIP64 unsupported')
    if cd_off + cd_size != pos:
        raise ValueError('ZIP central directory not contiguous with EOCD')
    return cd_off, pos


def content_digest(section1, section3, section4):
    # Streaming-friendly top-level digest (in-memory bytes here for simplicity)
    n = sum((len(s) + MB - 1) // MB for s in (section1, section3, section4))
    h = hashlib.sha256()
    h.update(b'\x5a' + u32(n))
    for section in (section1, section3, section4):
        for i in range(0, len(section), MB):
            chunk = section[i:i + MB]
            h.update(hashlib.sha256(b'\xa5' + u32(len(chunk)) + chunk).digest())
    return h.digest()


def sign_v2(jar_signed_apk: Path, output_apk: Path, pkcs12_key: Path, password: bytes):
    from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
    key, cert, _ = load_key_and_certificates(pkcs12_key.read_bytes(), password)
    if not key or not cert:
        raise ValueError('Missing PKCS12 certificate/key')
    b = jar_signed_apk.read_bytes()
    cd_start, eocd = get_layout(b)
    digest = content_digest(b[:cd_start], b[cd_start:eocd], b[eocd:])
    signed = lp(lp(u32(SIG_ID) + lp(digest))) + lp(lp(cert.public_bytes(serialization.Encoding.DER))) + lp(b'')
    sig = key.sign(signed, padding.PKCS1v15(), hashes.SHA256())
    public_der = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    signer = lp(signed) + lp(lp(u32(SIG_ID) + lp(sig))) + lp(public_der)
    value = lp(lp(signer))
    pair = u64(len(value) + 4) + u32(BLOCK_ID) + value
    block_len = len(pair) + 24
    block = u64(block_len) + pair + u64(block_len) + MAGIC
    patched_eocd = bytearray(b[eocd:])
    struct.pack_into('<I', patched_eocd, 16, cd_start + len(block))
    output_apk.write_bytes(b[:cd_start] + block + b[cd_start:eocd] + patched_eocd)
    return verify_v2(output_apk)


def get_lp(b, pos):
    if pos + 4 > len(b):
        raise ValueError('truncated LP field')
    n = struct.unpack_from('<I', b, pos)[0]
    if pos + 4 + n > len(b):
        raise ValueError('invalid LP size')
    return b[pos + 4:pos + 4 + n], pos + 4 + n


def verify_v2(path: Path):
    b = path.read_bytes()
    cd_start, eocd = get_layout(b)
    if b[cd_start - 16:cd_start] != MAGIC:
        raise ValueError('missing APK Signing Block magic')
    size = struct.unpack_from('<Q', b, cd_start - 24)[0]
    block_start = cd_start - (size + 8)
    if block_start < 0 or struct.unpack_from('<Q', b, block_start)[0] != size:
        raise ValueError('signing block length mismatch')
    pairs = b[block_start + 8:cd_start - 24]
    p = 0
    values = []
    while p < len(pairs):
        if p + 8 > len(pairs):
            raise ValueError('incomplete signing pair')
        n = struct.unpack_from('<Q', pairs, p)[0]
        if n < 4 or p + 8 + n > len(pairs):
            raise ValueError('malformed signing pair')
        ident = struct.unpack_from('<I', pairs, p + 8)[0]
        if ident == BLOCK_ID:
            values.append(pairs[p + 12:p + 8 + n])
        p += 8 + n
    if len(values) != 1:
        raise ValueError('expected one v2 signature pair')
    signers, _ = get_lp(values[0], 0)
    signer, _ = get_lp(signers, 0)
    signed, offset = get_lp(signer, 0)
    signatures, offset = get_lp(signer, offset)
    spki, offset = get_lp(signer, offset)
    signature_record, _ = get_lp(signatures, 0)
    alg = struct.unpack_from('<I', signature_record, 0)[0]
    signature, _ = get_lp(signature_record, 4)
    if alg != SIG_ID:
        raise ValueError('unsupported signature algorithm')
    public_key = serialization.load_der_public_key(spki)
    public_key.verify(signature, signed, padding.PKCS1v15(), hashes.SHA256())
    digests, position = get_lp(signed, 0)
    certs, position = get_lp(signed, position)
    attrs, position = get_lp(signed, position)
    dig_rec, _ = get_lp(digests, 0)
    digest_alg = struct.unpack_from('<I', dig_rec, 0)[0]
    digest, _ = get_lp(dig_rec, 4)
    der_cert, _ = get_lp(certs, 0)
    cert = load_der_x509_certificate(der_cert)
    if cert.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo) != spki:
        raise ValueError('certificate public key mismatch')
    if digest_alg != SIG_ID or len(digest) != 32:
        raise ValueError('bad digest record')
    original_eocd = bytearray(b[eocd:])
    struct.pack_into('<I', original_eocd, 16, block_start)
    expected = content_digest(b[:block_start], b[cd_start:eocd], bytes(original_eocd))
    if expected != digest:
        raise ValueError('signed APK content digest mismatch')
    return {'v2_signature': 'RSA-SHA256 verified', 'content_digest': 'passed', 'signing_certificate_sha256': cert.fingerprint(hashes.SHA256()).hex()}
