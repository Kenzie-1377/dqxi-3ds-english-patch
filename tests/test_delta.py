import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from delta import create, apply
from build_translation import safe


class DeltaTests(unittest.TestCase):
    def test_roundtrips(self):
        randomizer = random.Random(7)
        original = randomizer.randbytes(4096)
        for target in [original, b'', b'new', original[:91]+b'CHANGED'+original[122:], original+b'added', original[64:]+original[:64]]:
            self.assertEqual(apply(original, create(original, target)), target)

    def test_wrong_source(self):
        with self.assertRaises(ValueError):
            apply(b'wrong', create(b'right', b'target'))

    def test_invalid_patch(self):
        with self.assertRaises(ValueError):
            apply(b'', b'bad')

    def test_paths(self):
        for name in ['../escape', '/absolute', 'C:/drive', 'foo\\bar']:
            with self.assertRaises(ValueError):
                safe(Path.cwd(), name)


if __name__ == '__main__':
    unittest.main()
