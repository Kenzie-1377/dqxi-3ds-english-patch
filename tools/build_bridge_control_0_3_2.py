"""Reconstruct the original-data gamecmn PACK from an exact 0.3.2 mod file.

This diagnostic does not install anything or touch saves. The repository only
contains patch data; the caller supplies their own matching 0.3.2 archive.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import delta


SOURCE_SHA256 = "eeb7dbd02c304c71c2b3b552fd4265c25f847220c63743f70050aad94bfb9ea1"
SOURCE_SIZE = 2589416
PATCH_SHA256 = "9a8cfe50b215b378fa3603f87c7822bece237648c4b704549815202a1785890a"
TARGET_SHA256 = "26bf97310438c16e400b3bb36253c9f5c45eca787b216029bd65bf4f8e1b9ceb"
TARGET_SIZE = 2525032
PATCH = Path(__file__).resolve().parents[1] / "diagnostics/bridge_0_3_2/original_pack_control.dqdelta"


def checked_bytes(path: Path, sha256: str, size: int | None = None) -> bytes:
    data = path.read_bytes()
    if (size is not None and len(data) != size) or hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError(f"{path}: unexpected size or SHA-256")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_gamecmn", type=Path, help="Exact 0.3.2 romfs/gamecmn.pack")
    parser.add_argument("--output", type=Path, required=True, help="New, nonexistent output folder")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")
    try:
        source = checked_bytes(args.release_gamecmn, SOURCE_SHA256, SOURCE_SIZE)
        patch = checked_bytes(PATCH, PATCH_SHA256)
        original = delta.apply(source, patch)
        if len(original) != TARGET_SIZE or hashlib.sha256(original).hexdigest() != TARGET_SHA256:
            raise ValueError("reconstructed original PACK failed verification")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    output.mkdir(parents=True, exist_ok=False)
    path = output / "gamecmn.pack"
    with path.open("xb") as stream:
        stream.write(original)
    checked_bytes(path, TARGET_SHA256, TARGET_SIZE)
    print(f"Original-data control: {path} (SHA-256 {TARGET_SHA256})")


if __name__ == "__main__":
    main()
