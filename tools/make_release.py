"""Maintainer: create delta-only release data from original files and a mod."""
import argparse
import json
from pathlib import Path
from delta import create, apply, sha
from dq11_blz import decompress


def normalize(data):
    if data[:4] == b'PACA':
        data = b'PACK' + decompress(data)[4:]
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True, help='Folder containing original romfs/ and exefs/code.bin')
    parser.add_argument('--mod', type=Path, required=True, help='Existing mod folder containing romfs/ and exefs/')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    mod_files = [args.mod/'exefs/code.ips', *sorted((args.mod/'romfs').rglob('*.pack'))]
    for mod in mod_files:
        if not mod.is_file():
            continue
        rel = mod.relative_to(args.mod).as_posix()
        target = mod.read_bytes()
        if rel == 'exefs/code.ips':
            source = (args.base/'exefs/code.bin').read_bytes()
            payload = target
            kind = 'ips'
            name = 'code.patchdata'
            source_rel = 'exefs/code.bin'
        elif rel.startswith('romfs/') and rel.endswith('.pack'):
            source_rel = rel
            source = normalize((args.base/rel).read_bytes())
            if source == target:
                continue
            payload = create(source, target)
            if apply(source, payload) != target:
                raise ValueError('Delta verification failed')
            kind = 'delta'
            name = f'{len(rows):04d}.dqdelta'
        else:
            raise ValueError('Unexpected mod file: '+rel)
        (args.output/name).write_bytes(payload)
        rows.append(dict(path=rel, source=source_rel, kind=kind, payload=name,
                         source_sha256=sha(source), target_sha256=sha(target),
                         payload_sha256=sha(payload), target_size=len(target)))
        if len(rows) % 100 == 0:
            print('Verified', len(rows), 'files', flush=True)
    manifest = dict(format='dqxi-translation-deltas-v1', title_id='0004000000199200',
                    status='Incomplete; updated as the maintainer can.', files=rows)
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf8')
    print('Release verified:', len(rows), 'files;', sum(p.stat().st_size for p in args.output.iterdir()), 'bytes')


if __name__ == '__main__':
    main()
