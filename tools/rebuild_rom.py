"""Rebuild a user's decrypted NCSD cartridge as a separate translated .3ds."""
import hashlib
import shutil
import struct
import subprocess
import urllib.request
import zipfile
import uuid
from pathlib import Path

TOOL_URL = 'https://github.com/dnasdw/3dstool/releases/download/v1.2.6/3dstool.zip'
TOOL_SHA = '481e20f445eb2f0f506d0d88cd750385bc8377670d681d6f66f584a176027806'


def fetch_tool(folder):
    folder.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(TOOL_URL, timeout=60) as response:
        data = response.read(32*1024*1024+1)
    if hashlib.sha256(data).hexdigest() != TOOL_SHA:
        raise ValueError('ROM rebuilding tool checksum mismatch')
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = [n for n in archive.namelist() if Path(n).name.lower() == '3dstool.exe']
        if len(names) != 1:
            raise ValueError('Unexpected rebuilding tool package')
        executable = folder/'3dstool.exe'
        executable.write_bytes(archive.read(names[0]))
    # Only the executable is installed, not optional upstream key databases.
    return executable


def apply_ips(data, patch):
    if patch[:5] != b'PATCH':
        raise ValueError('Invalid executable patch')
    out = bytearray(data)
    p = 5
    while p+3 <= len(patch):
        if patch[p:p+3] == b'EOF':
            if p+3 != len(patch):
                raise ValueError('Unexpected IPS footer or truncation')
            return bytes(out)
        if p+5 > len(patch):
            break
        offset = int.from_bytes(patch[p:p+3], 'big')
        size = int.from_bytes(patch[p+3:p+5], 'big')
        p += 5
        if size:
            payload = patch[p:p+size]
            if len(payload) != size:
                raise ValueError('Truncated IPS record')
            p += size
        else:
            if p+3 > len(patch):
                raise ValueError('Truncated IPS run')
            size = int.from_bytes(patch[p:p+2], 'big')
            payload = patch[p+2:p+3] * size
            p += 3
        if offset+size > len(out):
            raise ValueError('Code patch exceeds the original executable size')
        out[offset:offset+size] = payload
    raise ValueError('Missing IPS end marker')


def partitions(path):
    with path.open('rb') as stream:
        header = stream.read(512)
    if len(header) != 512 or header[256:260] != b'NCSD':
        raise ValueError('Single-ROM output requires a real .3ds/.cci cartridge image. For .app/.cxi, select mod folders.')
    rows = {}
    for i in range(8):
        offset, size = struct.unpack_from('<II', header, 0x120+i*8)
        if size:
            if not offset or (offset+size)*512 > path.stat().st_size:
                raise ValueError('Invalid cartridge partition bounds')
            rows[i] = (offset*512, size*512)
    if 0 not in rows:
        raise ValueError('Cartridge has no game partition')
    with path.open('rb') as stream:
        stream.seek(rows[0][0])
        ncch = stream.read(512)
    if ncch[256:260] != b'NCCH' or int.from_bytes(ncch[0x118:0x120], 'little') != 0x0004000000199200:
        raise ValueError('This is not the supported Japanese DQXI cartridge')
    return rows


def hash_range(path, offset, length):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        stream.seek(offset)
        while length:
            block = stream.read(min(length, 1024*1024))
            if not block:
                raise ValueError('Unexpected end of ROM')
            digest.update(block)
            length -= len(block)
    return digest.digest()


def verify_ncch(path):
    with path.open('rb') as stream:
        header = stream.read(512)
    if header[256:260] != b'NCCH' or not header[0x18f] & 4:
        raise ValueError('Rebuilt game is not a decrypted NCCH')
    exheader_size = struct.unpack_from('<I', header, 0x180)[0]
    if hash_range(path, 512, exheader_size) != header[0x160:0x180]:
        raise ValueError('Extended-header hash verification failed')
    for base, digest_offset in [(0x1a0, 0x1c0), (0x1b0, 0x1e0)]:
        offset, size, hash_size = struct.unpack_from('<III', header, base)
        if hash_size and hash_range(path, offset*512, hash_size*512) != header[digest_offset:digest_offset+32]:
            raise ValueError('Filesystem header hash verification failed')


def rebuild(rom, extracted, mod, notify, cancel, tool=None):
    from build_translation import BuildCancelled
    rows = partitions(rom)
    folder = extracted/('rebuild-'+uuid.uuid4().hex)
    folder.mkdir(exist_ok=False)
    def check():
        if cancel.is_set():
            raise BuildCancelled('ROM rebuild cancelled. Do not use partial output.')
    def run(arguments):
        check()
        with (folder/'rebuild.log').open('ab') as log:
            process = subprocess.Popen([str(tool.resolve()), *map(str, arguments)],
                                       cwd=folder, stdout=log, stderr=log,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            while process.poll() is None:
                if cancel.wait(0.2):
                    process.terminate()
                    process.wait()
                    check()
            if process.returncode:
                raise ValueError('ROM rebuilding failed. See '+str(folder/'rebuild.log'))
    notify('Preparing the ROM rebuilding tool...', 66)
    if tool is None:
        tool = fetch_tool(folder/'tool')
    parts = {i:folder/f'partition{i}.bin' for i in rows}
    arguments = ['-x', '-t', 'cci', '-f', rom, '--header', folder/'ncsd.bin']
    for i, path in parts.items():
        arguments += [f'--partition{i}', path]
    notify('Preserving the original cartridge partitions...', 69)
    run(arguments)
    run(['-x', '-t', 'cxi', '-f', parts[0], '--header', folder/'ncch.bin', '--exh', folder/'exheader.bin',
         '--logo', folder/'logo.bin', '--plain', folder/'plain.bin', '--exefs', folder/'original-exefs.bin'])
    run(['-x', '-t', 'exefs', '-f', folder/'original-exefs.bin', '--header', folder/'exefs-header.bin'])
    # These are private files freshly extracted by the builder, not user inputs.
    notify('Applying the translation and executable fixes...', 73)
    for replacement in (mod/'romfs').rglob('*'):
        if replacement.is_file():
            check()
            dest = extracted/'romfs'/replacement.relative_to(mod/'romfs')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(replacement, dest)
    code = extracted/'exefs/code.bin'
    patched_code = apply_ips(code.read_bytes(), (mod/'exefs/code.ips').read_bytes())
    code.write_bytes(patched_code)
    exheader = bytearray((folder/'exheader.bin').read_bytes())
    exheader[0x0d] &= ~1  # ExeFS .code is stored uncompressed in the new image.
    (folder/'exheader.bin').write_bytes(exheader)
    # CTRTool and 3dstool use different filenames for these same ExeFS entries.
    for source_name, target_name in [('banner.bin', 'banner.bnr'), ('icon.bin', 'icon.icn')]:
        source = extracted/'exefs'/source_name
        if source.exists():
            shutil.copyfile(source, extracted/'exefs'/target_name)
    run(['-c', '-t', 'exefs', '-f', folder/'new-exefs.bin', '--header', folder/'exefs-header.bin', '--exefs-dir', extracted/'exefs'])
    notify('Rebuilding the game filesystem. This can take several minutes...', 77)
    run(['-c', '-t', 'romfs', '-f', folder/'new-romfs.bin', '--romfs-dir', extracted/'romfs'])
    notify('Rebuilding the translated game partition...', 85)
    arguments = ['-c', '-t', 'cxi', '-f', folder/'translated.cxi', '--header', folder/'ncch.bin',
                 '--exh', folder/'exheader.bin', '--exefs', folder/'new-exefs.bin', '--romfs', folder/'new-romfs.bin', '--not-encrypt']
    for option, name in [('--logo', 'logo.bin'), ('--plain', 'plain.bin')]:
        path = folder/name
        if path.exists() and path.stat().st_size:
            arguments += [option, path]
    run(arguments)
    verify_ncch(folder/'translated.cxi')
    notify('Writing the translated .3ds file...', 91)
    partial = mod/'DQXI-English.3ds.partial'
    final = mod/'DQXI-English.3ds'
    parts[0] = folder/'translated.cxi'
    arguments = ['-c', '-t', 'cci', '-f', partial, '--header', folder/'ncsd.bin', '--not-pad']
    for i, path in parts.items():
        arguments += [f'--partition{i}', path]
    run(arguments)
    notify('Verifying the rebuilt cartridge and preserved partitions...', 96)
    rebuilt = partitions(partial)
    if rows.keys() != rebuilt.keys():
        raise ValueError('Cartridge partition set changed')
    for i, (offset, size) in rebuilt.items():
        check()
        expected = parts[i]
        if size != expected.stat().st_size or hash_range(partial, offset, size) != hash_range(expected, 0, size):
            raise ValueError('Cartridge partition verification failed')
        if i and hash_range(rom, *rows[i]) != hash_range(partial, offset, size):
            raise ValueError('An unrelated cartridge partition changed')
    partial.rename(final)
    return final
