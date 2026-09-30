"""Small local-only GUI for building the 0.3.0 bridge diagnostic variants.

It accepts an exact 0.3.0 gamecmn.pack and never edits that input, an
installed mod, or saves. Only patch data is embedded in the executable.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from build_bridge_diagnostics import RELEASE_SHA256, RELEASE_SIZE, VARIANTS
from delta import apply


def patch_folder() -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return root / "diagnostics" / "bridge_0_3_0"


def checked(path: Path, digest: str, size: int | None = None) -> bytes:
    data = path.read_bytes()
    if size is not None and len(data) != size:
        raise ValueError(f"Unexpected file size: {path.name}")
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"SHA-256 mismatch: {path.name}")
    return data


def build(source_path: Path, output_path: Path) -> list[Path]:
    if output_path.exists():
        raise ValueError("Output folder already exists; choose a fresh location.")
    source = checked(source_path, RELEASE_SHA256, RELEASE_SIZE)
    results = []
    for label, patch_hash, target_hash, target_size in VARIANTS:
        patch = checked(patch_folder() / f"{label}.dqdelta", patch_hash)
        target = apply(source, patch)
        if len(target) != target_size or hashlib.sha256(target).hexdigest() != target_hash:
            raise ValueError(f"Reconstruction check failed: {label}")
        results.append((label, target, target_hash))
    output_path.mkdir(parents=True, exist_ok=False)
    written = []
    for label, target, target_hash in results:
        folder = output_path / label
        folder.mkdir()
        destination = folder / "gamecmn.pack"
        with destination.open("xb") as stream:
            stream.write(target)
        checked(destination, target_hash, len(target))
        written.append(destination)
    return written


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == "--self-test":
        paths = build(Path(sys.argv[2]), Path(sys.argv[3]))
        Path(sys.argv[4]).write_text(json.dumps({
            "frozen": bool(getattr(sys, "frozen", False)),
            "variants": len(paths),
            "sha256": {path.parent.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        }), encoding="utf-8")
        return
    root = tk.Tk()
    root.title("DQXI bridge diagnostic builder (0.3.0 only)")
    root.geometry("610x255")
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Heliodor bridge diagnostic builder", font=("Segoe UI", 15, "bold")).pack(anchor="w")
    ttk.Label(
        frame,
        text="Select the exact 0.3.0 romfs/gamecmn.pack from your own mod. This creates three\n"
        "temporary test variants in a new folder. It does not install them or touch saves.",
        justify="left",
    ).pack(anchor="w", pady=(8, 8))
    ttk.Label(frame, text="Test original_pack_control first. Close the game before changing files.").pack(anchor="w")
    ttk.Label(frame, text="0.3.1 gamecmn.pack will be rejected; this tool is for 0.3.0 only.").pack(anchor="w", pady=(0, 12))

    def choose_and_build() -> None:
        selected = filedialog.askopenfilename(title="Select 0.3.0 gamecmn.pack", filetypes=[("PACK archive", "*.pack")])
        if not selected:
            return
        parent = filedialog.askdirectory(title="Choose a folder for the new bridge-tests-0.3.0 folder")
        if not parent:
            return
        try:
            output = Path(parent) / "bridge-tests-0.3.0"
            paths = build(Path(selected), output)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Diagnostic build failed", str(exc))
            return
        messagebox.showinfo("Diagnostic files ready", f"Built and verified {len(paths)} variants in:\n{output}\n\nTest original_pack_control first. Do not distribute the generated PACK files.")

    ttk.Button(frame, text="Choose 0.3.0 gamecmn.pack and build tests", command=choose_and_build).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    main()
