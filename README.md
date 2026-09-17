# DQXI 3DS English Patch

An experimental, unofficial English translation for the Japanese Nintendo 3DS
edition of Dragon Quest XI. Maintained by **Kenzie-1377**.

## Project status

**This project is not complete. I will be updating it as I can.** There is no
fixed release schedule. Expect untranslated Japanese, rough translations, and
layout issues. Back up your saves before trying it.

This repository now includes the **translation differences and tools needed to
build an installable mod from your own supported game files**. It contains no ROM,
complete extracted game archives, encryption keys, saves, or emulator.
The patch cannot be used by itself without matching original inputs.

## What you need

- Your own **decrypted Japanese game**, title ID `0004000000199200`.
- Windows x64 and Python 3.10 or newer for the easy builder.
- Several GB of free disk space for private extraction.
- An emulator with compatible LayeredFS and ExeFS IPS mod support.

The builder checks every required source file's SHA-256. A different revision,
an already-patched input, or an incompatible update will be rejected. Do not
bypass the checks. No ROM downloader, encryption keys, or decryption service is
included.

## Build on Windows

1. Download this repository using **Code → Download ZIP**, then extract it.
2. Install Python from [python.org](https://www.python.org/downloads/) if needed.
3. Double-click **Build-Translation.cmd**.
4. Select your decrypted `.3ds`, `.cci`, `.cxi`, or `.app` file.
5. Approve the download of the pinned official CTRTool extractor.
6. Wait for the successful verification message.

The builder creates a new folder under `output/` containing `romfs/` and
`exefs/code.ips`. It never rewrites your ROM or saves and does not automatically
overwrite an existing mod installation.

**CIA input is not supported by this launcher.** Supply the decrypted game
application/content file or use the extracted-files option below.

### Command-line alternatives

From the repository root:

```sh
python tools/build_translation.py --rom "YOUR_GAME.cci" --download-ctrtool
```

To use your own CTRTool executable instead of downloading it:

```sh
python tools/build_translation.py --rom "YOUR_GAME.cci" --ctrtool "PATH_TO_CTRTOOL"
```

If you already have extracted originals, arrange them as
`YOUR_EXTRACTED_FOLDER/romfs/` and `YOUR_EXTRACTED_FOLDER/exefs/code.bin`:

```sh
python tools/build_translation.py --extracted "YOUR_EXTRACTED_FOLDER"
```

Use `--output "NEW_FOLDER"` for another build. Existing output directories are
refused to avoid accidental overwrites. The `.app` extraction path and extracted
inputs were tested locally; other accepted containers require matching extracted
hashes and have not all been tested.

## Install the generated mod

With the game closed, back up any existing mod and your saves. For the Azahar
mod-folder layout, put the generated `romfs` and `exefs` folders under:

```text
load/mods/0004000000199200/
  romfs/
  exefs/
    code.ips
```

Use the emulator's game-specific Mods Location menu to find the correct user
directory. Do not place the repository or the `release/` folder there.
Restart the emulator, then load a normal save rather than a save state.

See the [mod layout reference maintained by the Azahar team](https://citra.azahar-emu.org/help/feature/game-modding/).
This is an archived Citra reference; menu labels can vary by emulator version.
Real 3DS hardware installation has not been validated by this release.

## Known issues

- This is a partial translation, not the official English localization.
- Some names can remain cached in existing saves (for example Ruki/Sandy).
  These tools do not modify saves.
- Dialogue wrapping uses conservative limits, but long-message pagination still
  needs gameplay testing.
- Version hashes validate reconstruction, not the quality of every translation
  or the correctness of every game event.
- Do not combine with other mods touching the same files without reviewing them.

## Privacy and sharing

`release/` contains delta patches and a hash manifest, not ready-to-run game
archives. Only share the repository/patches, **not** generated `output/` or
extracted `private/` folders. Those local folders contain game-derived files.
They are ignored by Git. Original game files, working mods, and saves are not
deleted by these tools.

The extractor is fetched from the
[official CTRTool v1.3.0 release](https://github.com/3DSGuy/Project_CTR/releases/tag/ctrtool-v1.3.0)
and checked against a pinned SHA-256. Its upstream license and notices remain
with that tool; it is not relicensed by this repository.

## Development

Original Python source is included for archive handling, guarded text edits,
word wrapping, delta generation, and installation. Python's standard library is
sufficient; no machine-translation model is downloaded.

```sh
python -m unittest discover -s tests -v
```

Maintainers can regenerate a release from their own originals and reviewed mod:

```sh
python tools/make_release.py --base "ORIGINAL_FOLDER" --mod "MOD_FOLDER" --output "NEW_RELEASE_FOLDER"
```

The original folder must contain `romfs/` and `exefs/code.bin`. The generator
uses only the mod's active `romfs/` tree and `exefs/code.ips`, not backup trees.
Each delta is reconstructed and verified before the manifest is written.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [text patch notes](docs/patching.md).
Development has included AI assistance. Review and test contributions.

## License

Original code and documentation are MIT licensed; see [LICENSE](LICENSE).
That license does not grant rights to underlying game content, translations of
third-party material, trademarks, or assets. The patch data is provided separately
from the original code license. Dragon Quest XI and related names belong to their
respective owners. This is an unofficial project, not endorsed by its developers
or publishers.
