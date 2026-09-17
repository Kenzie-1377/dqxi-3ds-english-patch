"""Windows-friendly file picker for the ROM-to-mod builder."""
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime


def main():
    root = tk.Tk()
    root.withdraw()
    rom = filedialog.askopenfilename(title='Select your decrypted Japanese DQXI game',
                                    filetypes=[('Decrypted 3DS game', '*.3ds *.cci *.cxi *.app')])
    if not rom:
        return
    if not messagebox.askyesno('Download extractor?', 'Download the pinned official CTRTool v1.3.0 from GitHub?\nYour ROM and saves will not be changed.'):
        return
    project = Path(__file__).resolve().parents[1]
    output = project/'output'/('english-mod-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    result = subprocess.run([sys.executable, str(project/'tools/build_translation.py'),
                             '--rom', rom, '--download-ctrtool', '--output', str(output)])
    if result.returncode:
        messagebox.showerror('Build failed', 'See the console for details. Do not install partial output. Your ROM and saves were not changed.')
        sys.exit(result.returncode)
    messagebox.showinfo('Translation built', 'Verified mod created at:\n'+str(output)+'\n\nSee README.md for installation instructions.')


if __name__ == '__main__':
    main()
