"""Linux-only smoke check for the two pinned native helper executables."""
import platform
import subprocess
import tempfile
from pathlib import Path
from platform_tools import fetch

def main():
    if platform.system()!='Linux':raise SystemExit('Run this smoke check on Linux x86_64')
    with tempfile.TemporaryDirectory(prefix='dqxi-linux-tools-')as temp:
        for tool in('ctrtool','3dstool'):
            executable=fetch(tool,Path(temp)/tool)
            p=subprocess.run([str(executable),'--help'],capture_output=True,text=True,timeout=20)
            text=p.stdout+p.stderr
            if p.returncode not in(0,1)or tool.lower()not in text.lower():
                raise RuntimeError(tool+' failed its Linux execution check: '+text[-500:])
            print(tool+' Linux execution check passed')

if __name__=='__main__':main()
