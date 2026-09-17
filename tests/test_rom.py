import sys
import unittest
import hashlib
import struct
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from rebuild_rom import apply_ips, normalize_private_header


class HeaderTests(unittest.TestCase):
    def fixture(self):
        data = bytearray(2048)
        data[256:260] = b'NCCH'
        struct.pack_into('<I', data, 0x180, 512)
        struct.pack_into('<III', data, 0x1a0, 2, 1, 1)
        struct.pack_into('<III', data, 0x1b0, 3, 1, 1)
        for start, target in [(512, 0x160), (1024, 0x1c0), (1536, 0x1e0)]:
            data[target:target+32] = hashlib.sha256(data[start:start+512]).digest()
        return data

    def test_stale_flag_changes_only_one_byte_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'private.bin'
            original = self.fixture()
            path.write_bytes(original)
            self.assertTrue(normalize_private_header(path))
            original[0x18f] |= 4
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(normalize_private_header(path))

    def test_rejects_non_plaintext_without_modification(self):
        for offset in [512, 1024, 1536]:
            with self.subTest(offset=offset), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/'private.bin'
                data = self.fixture()
                data[offset] ^= 1
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    normalize_private_header(path)
                self.assertEqual(path.read_bytes(), data)


class ExecutablePatchTests(unittest.TestCase):
    def test_literal_and_run(self):
        patch = b'PATCH'+b'\0\0\1\0\2AB'+b'\0\0\4\0\0\0\3Z'+b'EOF'
        self.assertEqual(apply_ips(b'01234567', patch), b'0AB3ZZZ7')

    def test_rejects_resize(self):
        with self.assertRaises(ValueError):
            apply_ips(b'123', b'PATCH\0\0\2\0\2ABEOF')

    def test_rejects_truncation(self):
        for patch in [b'', b'PATCH', b'PATCH\0\0\1\0\5A', b'PATCHEOF\0\0\1']:
            with self.assertRaises(ValueError):
                apply_ips(b'12345', patch)


if __name__ == '__main__':
    unittest.main()
