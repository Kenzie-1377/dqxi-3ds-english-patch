"""Standalone visual translation builder; no external interpreter when frozen."""
import json
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
from build_translation import ROOT, build, BuildCancelled
from delta import sha, create, apply


class Application:
    def __init__(self, root):
        self.root, self.busy, self.built = root, False, None
        self.events, self.cancel = queue.Queue(), threading.Event()
        root.title('DQXI 3DS — English Translation Builder')
        root.geometry('800x610')
        root.minsize(720, 590)
        style = ttk.Style(root)
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        style.configure('Title.TLabel', font=('Segoe UI', 21, 'bold'))
        panel = ttk.Frame(root, padding=24)
        panel.pack(fill='both', expand=True)
        panel.columnconfigure(0, weight=1)
        ttk.Label(panel, text='Build your English translation', style='Title.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(panel, text='DRAGON QUEST XI • Japanese Nintendo 3DS edition').grid(row=1, column=0, sticky='w', pady=(4, 14))
        ttk.Label(panel, text='Work in progress — incomplete translation, updated as the maintainer can.\nYour original ROM and saves are never modified.', wraplength=700).grid(row=2, column=0, sticky='w', pady=(0, 18))
        self.rom = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.home()/'DQXI Translation Builds'))
        self.extractor = tk.StringVar()
        self.download = tk.BooleanVar(value=True)
        self.controls = []
        self.path_row(panel, 3, '1. Your decrypted Japanese game (.3ds, .cci, .cxi, .app)', self.rom, self.pick_rom)
        self.path_row(panel, 5, '2. Output folder (a new mod subfolder will be created)', self.output, self.pick_output)
        check = ttk.Checkbutton(panel, text='Download the verified official extractor from GitHub (internet required)', variable=self.download)
        check.grid(row=7, column=0, sticky='w', pady=(14, 6))
        self.controls.append(check)
        self.path_row(panel, 8, 'Optional: use your own ctrtool.exe instead of downloading', self.extractor, self.pick_extractor)
        self.status = tk.StringVar(value='Ready. Select your game to begin.')
        ttk.Label(panel, textvariable=self.status, wraplength=700).grid(row=10, column=0, sticky='w', pady=(20, 8))
        self.progress = ttk.Progressbar(panel, maximum=100)
        self.progress.grid(row=11, column=0, sticky='ew')
        buttons = ttk.Frame(panel)
        buttons.grid(row=12, column=0, sticky='ew', pady=(18, 10))
        start = ttk.Button(buttons, text='Build translation', command=self.start)
        start.pack(side='left')
        self.controls.append(start)
        self.cancel_button = ttk.Button(buttons, text='Cancel', command=self.request_cancel, state='disabled')
        self.cancel_button.pack(side='left', padx=8)
        self.open_button = ttk.Button(buttons, text='Open built mod', command=self.open_output, state='disabled')
        self.open_button.pack(side='right')
        ttk.Button(buttons, text='Installation help', command=self.help).pack(side='right', padx=8)
        ttk.Label(panel, text='Requires your own supported, decrypted ROM. No ROMs or keys are downloaded.\nAllow several GB of disk space. CIA files are not supported.', wraplength=700).grid(row=13, column=0, sticky='w', pady=(10, 0))
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)

    def path_row(self, panel, row, label, variable, browse):
        ttk.Label(panel, text=label).grid(row=row, column=0, sticky='w', pady=(4, 5))
        frame = ttk.Frame(panel)
        frame.grid(row=row+1, column=0, sticky='ew')
        frame.columnconfigure(0, weight=1)
        field = ttk.Entry(frame, textvariable=variable)
        field.grid(row=0, column=0, sticky='ew')
        button = ttk.Button(frame, text='Browse…', command=browse)
        button.grid(row=0, column=1, padx=(8, 0))
        self.controls.extend([field, button])

    def pick_rom(self):
        path = filedialog.askopenfilename(filetypes=[('Decrypted 3DS game', '*.3ds *.cci *.cxi *.app')])
        if path:
            self.rom.set(path)

    def pick_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output.set(path)

    def pick_extractor(self):
        path = filedialog.askopenfilename(filetypes=[('CTRTool', '*.exe')])
        if path:
            self.extractor.set(path)
            self.download.set(False)

    def start(self):
        if not Path(self.rom.get()).is_file() or Path(self.rom.get()).suffix.lower() not in {'.3ds', '.cci', '.cxi', '.app'}:
            messagebox.showerror('Select a game', 'Choose your decrypted Japanese game file first.')
            return
        if not self.output.get().strip() or (not self.download.get() and not Path(self.extractor.get()).is_file()):
            messagebox.showerror('Missing input', 'Choose an output folder and an extractor, or enable the download.')
            return
        parent = Path(self.output.get()).resolve()
        output = parent/('English-mod-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        args = SimpleNamespace(rom=Path(self.rom.get()), extracted=None,
                               ctrtool=Path(self.extractor.get()) if self.extractor.get() else None,
                               download_ctrtool=self.download.get(), release=ROOT/'release', output=output)
        self.busy = True
        self.cancel.clear()
        self.progress['value'] = 0
        for item in self.controls:
            item.configure(state='disabled')
        self.open_button.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        def worker():
            try:
                built = build(args, lambda text, value:self.events.put(('progress', text, value)), self.cancel, parent/'.dqxi-private')
                self.events.put(('done', built))
            except BuildCancelled as error:
                self.events.put(('cancelled', str(error)))
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=False).start()

    def request_cancel(self):
        self.cancel.set()
        self.cancel_button.configure(state='disabled')
        self.status.set('Cancelling safely; waiting for the current operation…')

    def poll(self):
        while not self.events.empty():
            event = self.events.get()
            if event[0] == 'progress':
                if not self.cancel.is_set():
                    self.status.set(event[1])
                self.progress['value'] = event[2]
                continue
            self.busy = False
            for item in self.controls:
                item.configure(state='normal')
            self.cancel_button.configure(state='disabled')
            if event[0] == 'done':
                self.built = event[1]
                self.open_button.configure(state='normal')
                self.status.set('Success! Your verified mod is ready. Open it below, then follow Installation help.')
            elif event[0] == 'cancelled':
                self.status.set('Cancelled. Do not install partial output. Your ROM and saves are unchanged.')
            else:
                self.status.set('Build failed. Your ROM and saves are unchanged.')
                messagebox.showerror('Unable to build translation', event[1]+'\n\nDo not install partial output.')
        self.root.after(100, self.poll)

    def open_output(self):
        if self.built:
            os.startfile(self.built)

    def help(self):
        messagebox.showinfo('Installing your generated mod',
            '1. Close the game and back up existing mods and saves.\n\n'
            '2. Open the game’s Mods Location in your emulator.\n\n'
            '3. Copy the generated romfs and exefs folders into:\nload/mods/0004000000199200/\n\n'
            '4. Restart the emulator and load a normal save.\n\n'
            'Do not share the built mod or .dqxi-private folder: they contain game-derived data. '
            'Only share the builder and public patches. Hardware installation is untested.')

    def close(self):
        if self.busy:
            if messagebox.askyesno('Build in progress', 'Cancel the build? Wait for cancellation before closing.'):
                self.request_cancel()
            return
        self.root.destroy()


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--self-test':
        report = Path(sys.argv[2])
        manifest = json.loads((ROOT/'release/manifest.json').read_text(encoding='utf8'))
        for row in manifest['files']:
            if sha((ROOT/'release'/row['payload']).read_bytes()) != row['payload_sha256']:
                raise ValueError('Bundled payload mismatch')
        if apply(b'base', create(b'base', b'target')) != b'target':
            raise ValueError('Delta self-test failed')
        root = tk.Tk()
        root.withdraw()
        Application(root)
        root.update_idletasks()
        result = dict(frozen=bool(getattr(sys, 'frozen', False)), payloads=len(manifest['files']), gui_created=True)
        root.destroy()
        if len(sys.argv) == 5:
            args = SimpleNamespace(rom=None, extracted=Path(sys.argv[3]), output=Path(sys.argv[4]), release=ROOT/'release', ctrtool=None, download_ctrtool=False)
            build(args, lambda *_:None)
            result['mod_built'] = True
        elif len(sys.argv) == 7 and sys.argv[3] == '--rom':
            args = SimpleNamespace(rom=Path(sys.argv[4]), extracted=None, output=Path(sys.argv[5]), release=ROOT/'release', ctrtool=Path(sys.argv[6]), download_ctrtool=False)
            build(args, lambda *_:None, work_root=args.output.parent/'exe-test-private')
            result['rom_build'] = True
        report.write_text(json.dumps(result), encoding='utf8')
        return
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()
