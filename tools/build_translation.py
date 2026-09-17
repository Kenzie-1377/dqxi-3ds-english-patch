"""Build the translation from the user's own decrypted ROM or extracted files."""
import argparse
import hashlib
import json
import subprocess
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from delta import apply, sha
from make_release import normalize

ROOT = Path(__file__).resolve().parents[1]
CTR_URL = 'https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v1.3.0/ctrtool-v1.3.0-win_x64.zip'
CTR_SHA = '8031dff3be72d0adb250fae1f969f27627e12a89ebc6dd074a15a75f87ddc949'


def safe(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} for p in path.parts) or '\\' in name or ':' in name:
        raise ValueError('Unsafe manifest path')
    result = root.joinpath(*path.parts).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Path escapes root')
    return result


def fetch_ctrtool():
    folder = ROOT/'private/ctrtool-v1.3.0'
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder/'download.zip'
    with urllib.request.urlopen(CTR_URL, timeout=60) as response:
        data = response.read(32*1024*1024+1)
    if hashlib.sha256(data).hexdigest() != CTR_SHA:
        raise ValueError('CTRTool download hash mismatch')
    archive.write_bytes(data)
    with zipfile.ZipFile(archive) as package:
        for item in package.infolist():
            if item.is_dir():
                continue
            dest = safe(folder, item.filename)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(package.read(item))
    matches = list(folder.rglob('ctrtool.exe'))
    if len(matches) != 1:
        raise ValueError('Unexpected CTRTool package')
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--rom', type=Path, help='Decrypted .3ds/.cci/.cxi/.app file')
    source.add_argument('--extracted', type=Path, help='Folder containing romfs/ and exefs/code.bin')
    parser.add_argument('--ctrtool', type=Path)
    parser.add_argument('--download-ctrtool', action='store_true', help='Download the pinned official Windows x64 extractor')
    parser.add_argument('--release', type=Path, default=ROOT/'release')
    parser.add_argument('--output', type=Path, default=ROOT/'output/english-mod')
    args = parser.parse_args()
    manifest = json.loads((args.release/'manifest.json').read_text(encoding='utf8'))
    if manifest.get('format') != 'dqxi-translation-deltas-v1' or manifest.get('title_id') != '0004000000199200':
        parser.error('Unsupported release')
    if args.output.exists():
        parser.error('Output already exists; choose a new directory to avoid overwriting files')
    if args.rom:
        if args.rom.suffix.lower() not in {'.3ds', '.cci', '.cxi', '.app'}:
            parser.error('Use a decrypted .3ds, .cci, .cxi, or .app file; CIA is not supported by this launcher')
        tool = fetch_ctrtool() if args.download_ctrtool else args.ctrtool
        if tool is None or not tool.is_file():
            parser.error('Specify --ctrtool or --download-ctrtool')
        import uuid
        extracted = ROOT/'private'/('extract-'+uuid.uuid4().hex)
        extracted.mkdir(parents=True)
        subprocess.run([str(tool.resolve()), '-p', '-n', '0',
                        '--romfsdir='+str(extracted/'romfs'), '--exefsdir='+str(extracted/'exefs'),
                        str(args.rom.resolve())], check=True, stdout=subprocess.DEVNULL)
    else:
        extracted = args.extracted.resolve()
    # Preflight every input and payload before creating any output.
    paths = set()
    for row in manifest['files']:
        dest = safe(args.output, row['path'])
        if dest in paths:
            raise ValueError('Duplicate output path')
        paths.add(dest)
        data = safe(extracted, row['source']).read_bytes()
        if row['kind'] == 'delta':
            data = normalize(data)
        elif row['kind'] != 'ips' or row['path'] != 'exefs/code.ips':
            raise ValueError('Unknown patch type')
        if sha(data) != row['source_sha256']:
            raise ValueError('Game version/input mismatch: '+row['source'])
        if sha(safe(args.release, row['payload']).read_bytes()) != row['payload_sha256']:
            raise ValueError('Damaged release payload')
    args.output.mkdir(parents=True, exist_ok=False)
    for i, row in enumerate(manifest['files'], 1):
        patch = safe(args.release, row['payload']).read_bytes()
        if row['kind'] == 'delta':
            result = apply(normalize(safe(extracted, row['source']).read_bytes()), patch)
        else:
            result = patch
            if not result.startswith(b'PATCH'):
                raise ValueError('Invalid IPS payload')
        if sha(result) != row['target_sha256'] or len(result) != row['target_size']:
            raise ValueError('Output verification failed')
        dest = safe(args.output, row['path'])
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as stream:
            stream.write(result)
        if i % 100 == 0:
            print('Built', i, 'files', flush=True)
    print('Verified mod created at:', args.output.resolve())
    print('ROM and saves unchanged. Private extracted files remain under private/; do not share them.')


if __name__ == '__main__':
    main()
