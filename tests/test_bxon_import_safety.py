import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import dq11_bxon as bx


def marker_fixture(name="EnemyBaseParam"):
    blob = bytearray(80)
    blob[:4] = b"BXON"
    blob[12:12 + len(name)] = name.encode("ascii")
    blob.extend(b"&&&&" + "Original\0".encode("utf-16le") + b"\x9a\x7b")
    # Same marked-string arithmetic as a pointer, but the second field is data.
    struct.pack_into("<I", blob, 32, 84 - 32)
    struct.pack_into("<I", blob, 36, 84 - 36)
    return bytes(blob)


def text_fixture():
    blob = bytearray(96)
    blob[:4] = b"BXON"
    blob[12:22] = b"TextBlock\0"
    blob[40:44] = b"&&&&"
    struct.pack_into("<I", blob, 44, 1)
    blob[56:60] = b"&&&&"
    struct.pack_into("<I", blob, 72, 7)
    struct.pack_into("<I", blob, 80, 100 - 80)
    # Numeric marker collision at descriptor +4 must NOT be relocated.
    struct.pack_into("<I", blob, 68, 100 - 68)
    blob.extend(b"&&&&" + "Original\0".encode("utf-16le") + b"\x9a\x7b")
    return bytes(blob)


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.manifest, self.output = [self.root / n for n in ("input.bxon", "text.json", "output.bxon")]

    def fixture(self, character=False, typed=False):
        self.source.write_bytes(text_fixture() if typed else marker_fixture("CharacterIEData" if character else "EnemyBaseParam"))
        (bx.export_text_block if typed else bx.export_character_ie if character else bx.export_marker_bxon)(self.source, self.manifest)
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def save(self, payload):
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")

    def test_numeric_candidate_is_not_pointer_proof(self):
        blob = marker_fixture()
        self.assertEqual(bx.parse_marker_text(blob)[0].references, [32, 36])
        p = self.fixture()
        p["entries"][0]["translation"] = "Longer replacement that would relocate numeric data"
        self.save(p)
        with self.assertRaisesRegex(ValueError, "typed pointer schema required"):
            bx.import_marker_bxon(self.source, self.manifest, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), blob)

    def test_same_size_change_also_requires_schema(self):
        p = self.fixture()
        p["entries"][0]["translation"] = "Modified"
        self.save(p)
        with self.assertRaises(ValueError):
            bx.import_marker_bxon(self.source, self.manifest, self.output)

    def test_character_ie_cannot_use_second_unsafe_path(self):
        p = self.fixture(character=True)
        p["entries"][0]["translation"] = "Changed"
        self.save(p)
        with self.assertRaises(ValueError):
            bx.import_character_ie(self.source, self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_marker_noop_is_byte_exact(self):
        self.fixture()
        bx.import_marker_bxon(self.source, self.manifest, self.output)
        self.assertEqual(self.output.read_bytes(), self.source.read_bytes())

    def test_character_noop_is_byte_exact(self):
        self.fixture(character=True)
        bx.import_character_ie(self.source, self.manifest, self.output)
        self.assertEqual(self.output.read_bytes(), self.source.read_bytes())

    def test_stale_hash_rejected(self):
        p = self.fixture()
        p["source_sha256"] = "0" * 64
        self.save(p)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            bx.import_marker_bxon(self.source, self.manifest, self.output)

    def test_noop_does_not_overwrite_output(self):
        self.fixture()
        self.output.write_bytes(b"user file")
        with self.assertRaises(FileExistsError):
            bx.import_marker_bxon(self.source, self.manifest, self.output)
        self.assertEqual(self.output.read_bytes(), b"user file")

    def test_noop_cannot_overwrite_original(self):
        self.fixture()
        before = self.source.read_bytes()
        with self.assertRaises(ValueError):
            bx.import_marker_bxon(self.source, self.manifest, self.source)
        self.assertEqual(self.source.read_bytes(), before)

    def test_noop_cannot_overwrite_manifest(self):
        self.fixture()
        with self.assertRaises(ValueError):
            bx.import_marker_bxon(self.source, self.manifest, self.manifest)

    def test_falsey_nonstring_translation_rejected(self):
        p = self.fixture()
        p["entries"][0]["translation"] = 0
        self.save(p)
        with self.assertRaises(ValueError):
            bx.import_marker_bxon(self.source, self.manifest, self.output)

    def test_textblock_noop_retains_noncanonical_padding(self):
        self.fixture(typed=True)
        bx.import_text_block(self.source, self.manifest, self.output)
        self.assertEqual(self.output.read_bytes(), self.source.read_bytes())

    def test_typed_textblock_leaves_numeric_collision_untouched(self):
        p = self.fixture(typed=True)
        p["entries"][0]["translation"] = "Longer replacement"
        self.save(p)
        bx.import_text_block(self.source, self.manifest, self.output)
        before, after = self.source.read_bytes(), self.output.read_bytes()
        self.assertEqual(before[68:72], after[68:72])
        self.assertEqual(bx.parse_text_block(after)[0].text, "Longer replacement")

    def test_typed_textblock_rejects_stale_hash(self):
        p = self.fixture(typed=True)
        p["source_sha256"] = hashlib.sha256(b"wrong").hexdigest()
        self.save(p)
        with self.assertRaises(ValueError):
            bx.import_text_block(self.source, self.manifest, self.output)


if __name__ == "__main__":
    unittest.main()
