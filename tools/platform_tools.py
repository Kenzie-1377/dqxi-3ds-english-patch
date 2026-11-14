"""Pinned official native tools for Windows x64 and Linux x86_64."""
import hashlib
import io
import os
import platform
import tarfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

TOOLS = {
 ('Windows','ctrtool'):('https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v1.3.0/ctrtool-v1.3.0-win_x64.zip','8031dff3be72d0adb250fae1f969f27627e12a89ebc6dd074a15a75f87ddc949','ctrtool.exe'),
 ('Linux','ctrtool'):('https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v1.3.0/ctrtool-v1.3.0-ubuntu_x86_64.zip','f553194b0ab2b539457160231cf5651c554e148f17ec960fae63424e82582aa8','ctrtool'),
 ('Windows','3dstool'):('https://github.com/dnasdw/3dstool/releases/download/v1.2.6/3dstool.zip','481e20f445eb2f0f506d0d88cd750385bc8377670d681d6f66f584a176027806','3dstool.exe'),
 ('Linux','3dstool'):('https://github.com/dnasdw/3dstool/releases/download/v1.2.6/3dstool_linux_x86_64.tar.gz','d42e3de7766ee552b3609ac5acb7ad3f07209dd91bc45a21d3fc2b049790ede2','3dstool'),
}
def specification(tool, system=None, machine=None):
    system=system or platform.system();machine=(machine or platform.machine()).lower()
    if machine not in ('amd64','x86_64')or(system,tool)not in TOOLS:
        raise ValueError('Automatic tool downloads support Windows x64 and Linux x86_64; provide compatible local tools for this platform')
    return TOOLS[system,tool]

def install_archive(data,folder,spec):
    url,expected,executable=spec
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Official tool archive checksum mismatch')
    if url.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(data))as archive:
            names=[x for x in archive.infolist()if not x.is_dir()and PurePosixPath(x.filename).name==executable]
            if len(names)!=1:raise ValueError('Unexpected official tool archive')
            payload=archive.read(names[0])
    else:
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz')as archive:
            names=[x for x in archive.getmembers()if x.isfile()and PurePosixPath(x.name).name==executable]
            if len(names)!=1:raise ValueError('Unexpected official tool archive')
            payload=archive.extractfile(names[0]).read()
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);dest=folder/executable
    if dest.is_symlink():raise ValueError('Refusing linked tool path')
    with dest.open('xb')as f:f.write(payload)
    if os.name!='nt':dest.chmod(0o755)
    return dest

def fetch(tool,folder):
    spec=specification(tool)
    with urllib.request.urlopen(spec[0],timeout=60)as response:data=response.read(32*1024*1024+1)
    if len(data)>32*1024*1024:raise ValueError('Tool archive exceeds size limit')
    return install_archive(data,folder,spec)
