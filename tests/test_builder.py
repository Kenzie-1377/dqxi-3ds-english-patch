import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from build_translation import build, BuildCancelled
from delta import create, sha


class BuilderTests(unittest.TestCase):
    def test_cancel_before_io(self):
        event = threading.Event()
        event.set()
        with self.assertRaises(BuildCancelled):
            build(None, cancel=event)

    def test_verified_build_and_wrong_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = root/'release'
            release.mkdir()
            source = root/'original'
            source.mkdir()
            original, target = b'original bytes', b'translated bytes'
            (source/'sample').write_bytes(original)
            delta = create(original, target)
            (release/'test.dqdelta').write_bytes(delta)
            manifest = dict(format='dqxi-translation-deltas-v1', title_id='0004000000199200', files=[dict(path='romfs/test.pack', source='sample', kind='delta', payload='test.dqdelta', source_sha256=sha(original), payload_sha256=sha(delta), target_sha256=sha(target), target_size=len(target))])
            (release/'manifest.json').write_text(json.dumps(manifest))
            args = SimpleNamespace(rom=None, extracted=source, release=release, output=root/'output')
            progress = []
            build(args, lambda text, value:progress.append(value))
            self.assertEqual((args.output/'romfs/test.pack').read_bytes(), target)
            self.assertEqual(progress[-1], 100)
            with self.assertRaises(ValueError):
                build(args, lambda *_:None)
            args.output = root/'rejected'
            (source/'sample').write_bytes(b'wrong version')
            with self.assertRaises(ValueError):
                build(args, lambda *_:None)
            self.assertFalse(args.output.exists())


if __name__ == '__main__':
    unittest.main()
