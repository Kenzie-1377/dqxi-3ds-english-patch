"""Build the translation from the user's own decrypted ROM or extracted files."""
import argparse
import hashlib
import json
import subprocess
import urllib.request
import zipfile
import sys
import threading
from pathlib import Path, PurePosixPath
from delta import apply, sha
from make_release import normalize

ROOT = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]
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


def fetch_ctrtool(folder=None):
    folder = folder or ROOT/'private/ctrtool-v1.3.0'
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


class BuildCancelled(Exception):
    pass


def build(args, notify=None, cancel=None, work_root=None):
    notify = notify or (lambda message, progress: print(message, flush=True))
    cancel = cancel or threading.Event()
    work_root = work_root or ROOT/'private'
    def check():
        if cancel.is_set():
            raise BuildCancelled('Build cancelled. Do not install partial output.')
    check()
    rom_output = getattr(args, 'output_format', 'mod') == 'rom'
    if rom_output:
        from rebuild_rom import partitions
        if not args.rom:
            raise ValueError('ROM rebuilding requires the original .3ds/.cci cartridge input')
        partitions(args.rom)
    notify('Checking translation package...', 0)
    manifest = json.loads((args.release/'manifest.json').read_text(encoding='utf8'))
    if manifest.get('format') != 'dqxi-translation-deltas-v1' or manifest.get('title_id') != '0004000000199200':
        raise ValueError('Unsupported release')
    if args.output.exists():
        raise ValueError('Output already exists; choose a new directory')
    if args.rom:
        if args.rom.suffix.lower() not in {'.3ds', '.cci', '.cxi', '.app'} or not args.rom.is_file():
            raise ValueError('Select a decrypted .3ds, .cci, .cxi, or .app file')
        notify('Downloading and verifying the official extractor...', 3)
        tool = fetch_ctrtool(work_root/'ctrtool-v1.3.0') if args.download_ctrtool else args.ctrtool
        check()
        if tool is None or not tool.is_file():
            raise ValueError('An extractor is required')
        import uuid
        extracted = work_root/('extract-'+uuid.uuid4().hex)
        extracted.mkdir(parents=True)
        notify('Extracting your game. This may take several minutes...', 8)
        with (extracted/'extractor.log').open('wb') as log:
            process = subprocess.Popen([str(tool.resolve()), '-p', '-n', '0',
                        '--romfsdir='+str(extracted/'romfs'), '--exefsdir='+str(extracted/'exefs'),
                        str(args.rom.resolve())], stdout=log, stderr=log,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            while process.poll() is None:
                if cancel.wait(0.2):
                    process.terminate()
                    process.wait()
                    check()
            if process.returncode:
                raise ValueError('Extraction failed. Confirm the ROM is decrypted. Details: '+str(extracted/'extractor.log'))
    else:
        extracted = args.extracted.resolve()
    paths = set()
    count = len(manifest['files'])
    for i, row in enumerate(manifest['files'], 1):
        check()
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
        if i % 10 == 0 or i == count:
            notify(f'Checking game version: {i}/{count} files', 15+int(30*i/count))
    check()
    args.output.mkdir(parents=True, exist_ok=False)
    for i, row in enumerate(manifest['files'], 1):
        check()
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
        if i % 10 == 0 or i == count:
            notify(f'Building and verifying: {i}/{count} files', 45+int((20 if rom_output else 55)*i/count))
    if rom_output:
        from rebuild_rom import rebuild
        result = rebuild(args.rom.resolve(), extracted.resolve(), args.output.resolve(), notify, cancel, getattr(args, 'rebuild_tool', None))
        notify('Complete. Your translated .3ds file is ready. Original ROM unchanged.', 100)
        return result
    notify('Complete. Your ROM and saves have not been changed.', 100)
    return args.output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--rom', type=Path, help='Decrypted .3ds/.cci/.cxi/.app file')
    source.add_argument('--extracted', type=Path, help='Folder containing romfs/ and exefs/code.bin')
    parser.add_argument('--ctrtool', type=Path)
    parser.add_argument('--output-format', choices=['mod', 'rom'], default='mod')
    parser.add_argument('--rebuild-tool', type=Path, help='Optional local 3dstool executable for ROM output')
    parser.add_argument('--download-ctrtool', action='store_true', help='Download the pinned official Windows x64 extractor')
    parser.add_argument('--release', type=Path, default=ROOT/'release')
    parser.add_argument('--output', type=Path, default=ROOT/'output/english-mod')
    args = parser.parse_args()
    result = build(args)
    print('Verified output created at:', result.resolve())

if __name__ == '__main__':
    main()
