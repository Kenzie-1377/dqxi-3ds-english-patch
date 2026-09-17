import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from rebuild_rom import apply_ips


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
