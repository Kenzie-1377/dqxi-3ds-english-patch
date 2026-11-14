import hashlib
import importlib.util
import io
import struct
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import cia_container as cia
import platform_tools

def ncch(fill=0,size=1024):
    d=bytearray([fill]*size);d[256:260]=b'NCCH';struct.pack_into('<Q',d,0x118,cia.TITLE);return bytes(d)

def fixture(path,game=None):
    game=game or ncch();extra=b'preserve unrelated content'+bytes(17);contents=[game,extra];t=bytearray(0xb04+96)
    struct.pack_into('>I',t,0,0x10004);t[0x180]=1;struct.pack_into('>Q',t,0x18c,cia.TITLE);struct.pack_into('>HH',t,0x1de,2,0)
    for i,d in enumerate(contents):
        p=0xb04+i*48;struct.pack_into('>IHHQ',t,p,0x20+i,i,0,len(d));t[p+16:p+48]=hashlib.sha256(d).digest()
    struct.pack_into('>HH',t,0x204,0,2);t[0x208:0x228]=hashlib.sha256(t[0xb04:]).digest();t[0x1e4:0x204]=hashlib.sha256(t[0x204:0xb04]).digest()
    h=bytearray(0x2020);cert=b'certificate sentinel';ticket=b'ticket sentinel';meta=b'metadata sentinel';struct.pack_into('<IHHIIIIQ',h,0,0x2020,0,0,len(cert),len(ticket),len(t),len(meta),sum(cia.align(len(d),16)for d in contents));h[0x20]=0xc0
    with Path(path).open('xb')as f:
        for d in(h,cert,ticket,t):f.write(d);f.write(bytes(cia.align(f.tell())-f.tell()))
        for d in contents:f.write(d);f.write(bytes(cia.align(f.tell(),16)-f.tell()))
        f.write(bytes(cia.align(f.tell())-f.tell()));f.write(meta)
    return Path(path)

class CiaTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.source=fixture(self.root/'original.cia')
    def tearDown(self):self.temp.cleanup()
    def test_rebuild_preserves_unrelated_contents_and_metadata(self):
        original=self.source.read_bytes();game=self.root/'game.cxi';game.write_bytes(ncch(5,1536));out=self.root/'patched.cia';cia.write_replacement(self.source,game,out);before=cia.read(self.source);after=cia.read(out)
        self.assertEqual(self.source.read_bytes(),original)
        for k in('cert','ticket','meta'):self.assertEqual(before[k],after[k])
        self.assertEqual(after['game']['size'],1536);self.assertEqual(cia.digest_range(out,after['game']['offset'],1536),hashlib.sha256(game.read_bytes()).digest())
    def test_output_cannot_overwrite_input_or_existing_file(self):
        game=self.root/'game.cxi';game.write_bytes(ncch(3));original=self.source.read_bytes()
        with self.assertRaises(FileExistsError):cia.write_replacement(self.source,game,self.source)
        self.assertEqual(self.source.read_bytes(),original)
    def test_damaged_game_rejected(self):
        j=cia.read(self.source);d=bytearray(self.source.read_bytes());d[j['game']['offset']+600]^=1;self.source.write_bytes(d)
        with self.assertRaisesRegex(ValueError,'hash mismatch'):cia.read(self.source)
    def test_invalid_tmd_hash_rejected(self):
        d=bytearray(self.source.read_bytes());d[cia.align(cia.align(cia.align(0x2020)+len(b'certificate sentinel'))+len(b'ticket sentinel'))+0x208]^=1;self.source.write_bytes(d)
        with self.assertRaises(ValueError):cia.read(self.source)
    def test_truncated_cia_rejected(self):
        self.source.write_bytes(self.source.read_bytes()[:-10])
        with self.assertRaises(ValueError):cia.read(self.source)
    def test_platform_selection_and_rejection(self):
        self.assertTrue(platform_tools.specification('ctrtool','Linux','x86_64')[0].endswith('ubuntu_x86_64.zip'))
        self.assertTrue(platform_tools.specification('3dstool','Windows','AMD64')[2].endswith('.exe'))
        with self.assertRaises(ValueError):platform_tools.specification('ctrtool','Linux','aarch64')
    def test_modified_download_rejected_before_writing(self):
        with self.assertRaises(ValueError):platform_tools.install_archive(b'bad',self.root/'tool',platform_tools.specification('ctrtool','Linux','x86_64'))
        self.assertFalse((self.root/'tool').exists())

if __name__=='__main__':unittest.main()
