"""Reconstruct five temporary Heliodor bridge diagnostic archives.

The input must be the exact gamecmn.pack built by release 0.3.0. This tool
never modifies the input, an installed mod, or saves.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import delta


RELEASE_SHA256 = "493b95fad71a6a06da99a7c70b589cf0169c93307624476b69c114773b31c79a"
RELEASE_SIZE = 2731112
VARIANTS = (
    (
        "original_pack_control",
        "3c2960d209fa14531d9798094acc8526c8aeb3fc0e316d005a4928c1f0aa2485",
        "26bf97310438c16e400b3bb36253c9f5c45eca787b216029bd65bf4f8e1b9ceb",
        2525032,
    ),
    (
        "story_a010_original",
        "22de14892bfc52b713aad2444254892ca2eb6704a41aec67ca7459e4cd773570",
        "f269740cfe5e87e837f63d9c7e4126d6bc31fb9f7183c1bda587629e418feb29",
        2723048,
    ),
    (
        "scenario_guide_original",
        "316a225191ff11b44b40f2b3298dbafe346187fbcf77c246265f07e2190c91ea",
        "1bbff5f6c67424655ddb1a1316efe7dbe9af8ab8645b0c96ace1ad773e56469d",
        2699752,
    ),
    (
        "group_a_only",
        "51b2a0881bb1ac330e482c133f6ae89c5d954cd54797c64a801d63b41bb3aafa",
        "2a6c044562ae8de9fdfb16447d905ec0a4d71b2914041fb7f8eeb20b7c51ec01",
        2628200,
    ),
    (
        "group_b_only",
        "033b00737e8ef8d71da15616a0de7ee9d4c65afb9d822c1f3290d0c0da2ee41d",
        "28193915d3e142cc3ed18ac69f82030da47e73e571e47fc3699a9dddc12f166f",
        2627816,
    ),
)
PATCH_DIR = Path(__file__).resolve().parents[1] / "diagnostics" / "bridge_0_3_0"


def checked_bytes(path: Path, expected_sha256: str, expected_size: int | None = None) -> bytes:
    data = path.read_bytes()
    if expected_size is not None and len(data) != expected_size:
        raise ValueError(f"{path}: unexpected size {len(data)}")
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError(f"{path}: SHA-256 does not match")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_gamecmn", type=Path, help="Exact 0.3.0 romfs/gamecmn.pack")
    parser.add_argument("--output", required=True, type=Path, help="New, nonexistent output folder")
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        parser.error(f"output already exists: {output}")

    reconstructed = []
    try:
        source = checked_bytes(args.release_gamecmn, RELEASE_SHA256, RELEASE_SIZE)
        for label, patch_sha256, target_sha256, target_size in VARIANTS:
            patch = checked_bytes(PATCH_DIR / f"{label}.dqdelta", patch_sha256)
            target = delta.apply(source, patch)
            if len(target) != target_size or hashlib.sha256(target).hexdigest() != target_sha256:
                raise ValueError(f"{label}: reconstructed archive does not match expected hash/size")
            reconstructed.append((label, target, target_sha256))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    output.mkdir(parents=True, exist_ok=False)
    for label, target, target_sha256 in reconstructed:
        folder = output / label
        folder.mkdir()
        destination = folder / "gamecmn.pack"
        with destination.open("xb") as stream:
            stream.write(target)
        checked_bytes(destination, target_sha256, len(target))
        print(f"{label}: {destination} (SHA-256 {target_sha256})")


if __name__ == "__main__":
    main()
