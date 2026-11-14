import json
import sys
import tempfile
import threading
import unittest
from unittest import mock
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import build_translation
from build_translation import build, BuildCancelled
from delta import create, sha
import make_release


def build_fixture(args,notify):
    # Synthetic fixtures retain a strict, fixture-specific manifest pin.
    raw=(args.release/'manifest.json').read_bytes()
    with mock.patch.object(build_translation,'RELEASE_MANIFEST_SHA',sha(raw)), mock.patch.object(build_translation,'RELEASE_TARGETS',len(json.loads(raw)['files'])):
        return build(args,notify)


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
            manifest = dict(format='dqxi-translation-deltas-v1', title_id='0004000000199200', version='1.0', files=[dict(path='romfs/test.pack', source='sample', kind='delta', payload='test.dqdelta', source_sha256=sha(original), payload_sha256=sha(delta), target_sha256=sha(target), target_size=len(target))])
            (release/'manifest.json').write_text(json.dumps(manifest))
            args = SimpleNamespace(rom=None, extracted=source, release=release, output=root/'output')
            progress = []
            build_fixture(args, lambda text, value:progress.append(value))
            self.assertEqual((args.output/'romfs/test.pack').read_bytes(), target)
            self.assertEqual(progress[-1], 100)
            with self.assertRaises(ValueError):
                build_fixture(args, lambda *_:None)
            args.output = root/'rejected'
            (source/'sample').write_bytes(b'wrong version')
            with self.assertRaises(ValueError):
                build_fixture(args, lambda *_:None)
            self.assertFalse(args.output.exists())

    def test_release_and_builder_include_standalone_bch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root/'original'
            mod = root/'mod'
            release = root/'release'
            rel = Path('romfs/ui/location/location_b021_001a.bch')
            (original/rel).parent.mkdir(parents=True)
            (mod/rel).parent.mkdir(parents=True)
            (original/rel).write_bytes(b'BCH\0original texture')
            (mod/rel).write_bytes(b'BCH\0English Hotto texture')
            font=Path('romfs/font/3D14.bffnt')
            (original/font).parent.mkdir(parents=True)
            (mod/font).parent.mkdir(parents=True)
            (original/font).write_bytes(b'original font')
            (mod/font).write_bytes(b'six pixel space font')
            old_argv = sys.argv
            try:
                sys.argv = ['make_release', '--base', str(original),
                            '--mod', str(mod), '--output', str(release)]
                make_release.main()
            finally:
                sys.argv = old_argv
            manifest = json.loads((release/'manifest.json').read_text(encoding='utf8'))
            self.assertEqual({row['path'] for row in manifest['files']}, {rel.as_posix(),font.as_posix()})
            args = SimpleNamespace(rom=None, extracted=original, release=release,
                                   output=root/'rebuilt')
            build_fixture(args, lambda *_: None)
            self.assertEqual((args.output/rel).read_bytes(), (mod/rel).read_bytes())
            self.assertEqual((args.output/font).read_bytes(),(mod/font).read_bytes())


if __name__ == '__main__':
    unittest.main()
