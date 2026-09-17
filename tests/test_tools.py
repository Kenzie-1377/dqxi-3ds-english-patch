import hashlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from text_patch import apply_patch, read_text, wrap_text
from dq11_pack import Archive, Entry, build_archive, read_archive
from dq11_blz import decompress


class TextTests(unittest.TestCase):
    def fixture(self):
        data = struct.pack('<I', 8) + b'&&&&' + 'Hello\0'.encode('utf-16le')
        manifest = {'format': 'reviewed-text-pointers-v1',
                    'input_sha256': hashlib.sha256(data).hexdigest(),
                    'edits': [{'pointer': 0, 'old': 'Hello', 'new': 'Welcome aboard!'}]}
        return data, manifest

    def test_append_preserves_nonpointer_bytes(self):
        data, manifest = self.fixture()
        result = apply_patch(data, manifest)
        self.assertEqual(read_text(result, 0), 'Welcome aboard!')
        self.assertEqual(data[4:], result[4:len(data)])

    def test_rejects_wrong_hash(self):
        data, manifest = self.fixture()
        with self.assertRaises(ValueError):
            apply_patch(data + b'x', manifest)

    def test_rejects_wrong_old_text(self):
        data, manifest = self.fixture()
        manifest['edits'][0]['old'] = 'Other'
        with self.assertRaises(ValueError):
            apply_patch(data, manifest)

    def test_rejects_changed_controls(self):
        data, manifest = self.fixture()
        manifest['edits'][0]['new'] = '\x04\x01'
        with self.assertRaises(ValueError):
            apply_patch(data, manifest)

    def test_wrap_names(self):
        result = wrap_text('Hello \x04\x01, welcome to the village.')
        self.assertIn('\x04\x01', result)
        self.assertTrue(all(len(line.replace('\x04\x01', 'PLAYER')) <= 24
                            for line in result.splitlines()))

    def test_tab_valued_token_is_not_whitespace(self):
        self.assertEqual(wrap_text('Obtained \x04\t coins!'), 'Obtained\n\x04\t\ncoins!')

    def test_oversize_word(self):
        with self.assertRaises(ValueError):
            wrap_text('x' * 25)

    def test_blank_paragraph(self):
        self.assertEqual(wrap_text('Hello\n\nWorld'), 'Hello\n\nWorld')

    def test_archive_round_trip(self):
        entry = Entry('sample.txt', 0, 40, 0, 5, 7, b'hello')
        archive = Archive('PACK', '<', 0, 0, 0, 0xfeff, 24, 0, 0, [entry])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.pack'
            path.write_bytes(build_archive(archive))
            loaded = read_archive(path)
            self.assertEqual(loaded.entries[0].data, b'hello')
            self.assertEqual(loaded.entries[0].table_value, 7)

    def test_invalid_compression(self):
        with self.assertRaises(ValueError):
            decompress(b'bad')


if __name__ == '__main__':
    unittest.main()
