import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_bridge_diagnostics import PATCH_DIR, RELEASE_SHA256, VARIANTS
from delta import MAGIC, apply


class BridgeDiagnosticTests(unittest.TestCase):
    def test_patch_only_payloads_match_manifest_and_source(self):
        for label, patch_sha, target_sha, target_size in VARIANTS:
            with self.subTest(label=label):
                payload = (PATCH_DIR / f"{label}.dqdelta").read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), patch_sha)
                self.assertEqual(payload[:5], MAGIC)
                self.assertEqual(payload[5:37].hex(), RELEASE_SHA256)
                self.assertEqual(payload[37:69].hex(), target_sha)
                self.assertEqual(int.from_bytes(payload[69:77], "little"), target_size)
                with self.assertRaises(ValueError):
                    apply(b"not the verified 0.3.0 archive", payload)
