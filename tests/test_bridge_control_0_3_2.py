import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_bridge_control_0_3_2 import PATCH, PATCH_SHA256, SOURCE_SHA256, TARGET_SHA256, TARGET_SIZE
from delta import MAGIC, apply


class BridgeControl032Tests(unittest.TestCase):
    def test_patch_is_guarded_and_matches_manifest(self):
        payload = PATCH.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), PATCH_SHA256)
        self.assertEqual(payload[:5], MAGIC)
        self.assertEqual(payload[5:37].hex(), SOURCE_SHA256)
        self.assertEqual(payload[37:69].hex(), TARGET_SHA256)
        self.assertEqual(int.from_bytes(payload[69:77], "little"), TARGET_SIZE)
        with self.assertRaises(ValueError):
            apply(b"wrong game version", payload)
