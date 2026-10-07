# DQXI 3DS English Patch

An experimental, unofficial English translation for the Japanese Nintendo 3DS
edition of Dragon Quest XI. Maintained by **Kenzie-1377**.

## Project status

**This project is not complete. I will be updating it as I can.** There is no
fixed release schedule. Expect untranslated Japanese, rough translations, and
layout issues. Back up your saves before trying it.

The **0.5.3 experimental prerelease** adds recently reviewed dialogue and UI
repairs and an Octagonia rendering repair. It packages 733 targets, with 42
updated and 691 payloads unchanged from 0.5.2. The player reports that Octagonia
and Heliodor render correctly in Azahar with the repaired shared archive.
The Church crash fix has a separate user-reported hardware pass on **0.5.2**;
the new 0.5.3 archive has not been hardware tested. The full Octagonia dialogue
audit, whole-game stability and comprehensive rendered text fit remain unfinished.
See the [changelog](CHANGELOG.md) and [verification scope](docs/release-validation.md).

The earlier **0.5.0 experimental prerelease** substantially expands regional
dialogue and speaker-name coverage while retaining the player-confirmed
Veronica/Sylvando final-letter repair. It packages 733 patch targets: 111 updated
and 622 unchanged from 0.4.0. The regional translation pass converted 7,588
fields, with original-data, archive and conservative text-fit checks.
Japanese and ambiguous text remain, and image/executable text, rendered layouts
and real-hardware gameplay are not fully audited. This is neither fully
translated nor stable. The frozen candidate passed builder verification and the
player reported it was good to go after the requested limited spot check. See the
[changelog](CHANGELOG.md) and [scoped completion checklist](docs/completion-status.md)
for changes, completed audited scopes and work still to do.

**Historical 0.5.2 release-time status (later Church hardware pass noted above):** Compacts
the item-text storage in `syscmn.pack`, preserving the existing English item
names and descriptions, resource strings and original gameplay values. The
player reports that the compact variant renders Heliodor correctly in Azahar;
the previous translated item entry reproduced the problem in controlled tests.
The exact graphics failure mechanism is not diagnosed. **This version has not
been tested on real hardware.** The 0.5.1 bridge repair remains included, but its
earlier limited hardware pass does not validate 0.5.2. The Church exit crash,
other reported crashes and whole-game validation remain unresolved. Back up
saves and avoid mixing older external patch overrides with the new build.

**0.5.1 experimental hardware bridge-crash hotfix:** Four enemy-category values in
`gamecmn.pack` were accidentally relocated as if they were text pointers.
The fix restores those original numeric values, changing only eight bytes from
0.5.0 and retaining its English translation. The player reports the diagnostic
ROM passed the previously crashing real-hardware bridge/walking test.
This does not establish whole-game stability or fix the separate Church exit
report. The Heliodor rendering error may have returned: a hardware photo shows
similar corruption, but confirmation awaits a clean-install test without
leftover external patch files. A Windows-native C#/.NET Framework 4.8 builder
replaces the old Python engine, whose failure cause remains unknown. The exact
native candidate passed repeated complete builds and independent cartridge
verification. See the [0.5.1 changelog](CHANGELOG.md)
for scope and remaining limits.

**Historical New 3DS hardware reports through 0.5.0:** A hardware tester confirms
that **0.3.2 still crashes** in 3D mode when crossing the bridge toward
Heliodor, and also crashes when leaving the Church of Guidance. The tester
reports that the earlier Heliodor rendering error is no longer visible in
0.3.2; that improvement has not been broadly validated. Removing the
translated `romfs/gamecmn.pack` and using an original-data PACK control
allowed an earlier bridge/Heliodor test to pass. A compact translated variant
crossed the bridge in Azahar, but that did not predict hardware behavior.
**Do not treat 0.3.2 as a crash repair.**
**0.4.0 is also not a crash repair and has not been validated on real hardware.**
**0.5.0 likewise makes no hardware-crash repair claim.**
Back up your saves and mod files. See [issue #1](https://github.com/Kenzie-1377/dqxi-3ds-english-patch/issues/1)
and the [0.3.2 patch-only original-data control](diagnostics/bridge_0_3_2/README.md).
The older [0.3.0 diagnostics](diagnostics/bridge_0_3_0/README.md) reject a
0.3.2 input. Diagnostic files are not a release or a permanent workaround.

This repository now includes the **translation differences and tools needed to
build an installable mod from your own supported game files**. It contains no ROM,
complete extracted game archives, encryption keys, saves, or emulator.
The patch cannot be used by itself without matching original inputs.

## What you need

- Your own **decrypted Japanese game**, title ID `0004000000199200`.
- Windows x64 with .NET Framework 4.8. **The EXE does not require or bundle Python.**
- Allow at least 25 GB free for ROM rebuilding, or several GB for mod-folder output.
- An emulator with compatible LayeredFS and ExeFS IPS mod support.

The builder checks every required source file's SHA-256. A different revision,
an already-patched input, or an incompatible update will be rejected. Do not
bypass the checks. No ROM downloader, encryption keys, or decryption service is
included.

## Standalone Windows app — no Python required

Use `DQXI-English-Translation-Builder.exe` from the repository's release assets
from the **0.5.3** assets. It includes the interface and translation patches and
uses Windows' installed .NET Framework 4.8. Source ZIPs do not contain the EXE.
Clean-host and Windows 8 compatibility are unverified.

1. Open the EXE and choose your decrypted Japanese ROM.
2. Choose an output folder and select **Translated .3ds file** (default), or **Mod folders**.
3. Leave the verified extractor download enabled, or select your own CTRTool. ROM output also asks permission to download the pinned 3dstool rebuilder.
4. Click **Build translation** and watch the progress.
5. When verification succeeds, click **Open output folder**. For ROM output, open **DQXI-English.3ds** directly in your emulator. For mod folders, follow **Installation help**.

Single-ROM output requires a genuine decrypted `.3ds`/`.cci` cartridge image,
not a renamed `.app`/`.cxi`. The original cartridge's other partitions are
preserved and verified. The original ROM is never overwritten. Rebuilt ROMs are
decrypted/unsigned and require compatible emulators or custom-firmware workflows.
The 0.5.1 ROM matched the player's limited hardware bridge diagnostic byte for
byte, not a comprehensive hardware playthrough. Do not distribute rebuilt ROMs.
Older external LayeredFS/IPS overrides can change their behavior.

Decrypted cartridges with a stale encryption flag are handled automatically:
the builder verifies the plaintext hashes, then corrects only its private
working copy. It does not decrypt encrypted ROMs or change your original file.

The app supports safe cancellation and displays build errors in the window.
It creates a new mod subfolder; it does not replace your ROM or saves. Private
extracted files are kept under `.dqxi-private` beside the generated mod folders.
Do not share that private folder or the generated mod.

The executable is unsigned, so Windows may show an unrecognized-app warning.
Do not disable security software; use only the maintainer's trusted download.

## Run the native builder from source (Windows developers)

Run `Build-Windows-Exe.ps1` using PowerShell and the Windows .NET Framework 4.8
compiler, then open `Build-Translation.cmd`. The source is in `tools/native/`.
Source builds are not automatically certified as the separately verified release
asset. For native command-line builds, supply a fresh output directory:

```text
dist/DQXI-English-Translation-Builder.exe --rom "YOUR_GAME.cci" --download-tools --output "NEW_FOLDER"
dist/DQXI-English-Translation-Builder.exe --rom "YOUR_GAME.cci" --download-tools --output-format rom --output "NEW_FOLDER"
dist/DQXI-English-Translation-Builder.exe --extracted "YOUR_EXTRACTED_FOLDER" --output "NEW_FOLDER"
```

Use `--ctrtool PATH` instead of `--download-tools` for a local extractor;
`--rebuild-tool PATH` supplies the pinned local ROM rebuilder. The GUI defaults
to `.3ds` output; the command line defaults to mod folders.

## Historical Python developer tools (not the native release engine)

The following older tools remain for maintainer reference. They are not the
recommended builder; their execution-failure cause has not been diagnosed.
`Build-Translation.cmd` now launches the compiled native builder instead.

1. Download this repository using **Code → Download ZIP**, then extract it.
2. Install Python from [python.org](https://www.python.org/downloads/) if needed.
3. Run `python tools/build_gui.py` from the repository folder.
4. Select your decrypted `.3ds`, `.cci`, `.cxi`, or `.app` file.
5. Approve the download of the pinned official CTRTool extractor.
6. Wait for the successful verification message.

The builder creates a new folder under `output/` containing `romfs/` and
`exefs/code.ips`. It never rewrites your ROM or saves and does not automatically
overwrite an existing mod installation.

The source GUI now defaults to a single translated `.3ds`. Command-line builds
retain the original mod-folder default; add `--output-format rom` to rebuild a
cartridge. Temporary and generated game data remain private and Git-ignored.

**CIA input is not supported by this launcher.** Supply the decrypted game
application/content file or use the extracted-files option below.

### Command-line alternatives

From the repository root:

```sh
python tools/build_translation.py --rom "YOUR_GAME.cci" --download-ctrtool
```

To produce a translated cartridge file:

```sh
python tools/build_translation.py --rom "YOUR_GAME.cci" --download-ctrtool --output-format rom
```

The rebuilding helper is downloaded from the
[official 3dstool v1.2.6 release](https://github.com/dnasdw/3dstool/releases/tag/v1.2.6)
and verified against a pinned SHA-256. Only the executable is installed; optional
upstream key databases are not installed or used. `--rebuild-tool PATH` can supply
a local executable instead.

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
Hardware workflows vary; only the reported limited bridge diagnostic was tested,
not every installation method or hardware configuration.

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

## Current progress

The **0.5.0 experimental prerelease** contains 733 patch targets (730 PACK
deltas, two BCH deltas and one executable IPS), with 111 updated and 622 retained
from 0.4.0. It includes 7,588 newly converted regional Japanese fields
(6,302 dialogue and 1,286 speaker labels), including repeated fields rather
than unique conversations. Five English-only corrections are counted separately.
Earlier quest/journal, battle-message, tutorial, forge, speaker-name, item,
Tickington and screen-fit work is retained. See the
[changelog](CHANGELOG.md) for completed scopes and remaining work, and
[validation notes](docs/release-validation.md) for the checks performed.

This is not a complete translation. Broader character dialogue and some graphics
remain Japanese. The latest broad regional audit reports 356 Japanese candidates
across 26 packs, including unsupported fields, duplicates, potentially unused
text and numeric pointer lookalikes. This is not an active conversation count
or completion percentage; other audit scopes overlap and must not be added.
The Hotto title image and saved Tockle name behavior still need
in-game checks, and text readability is not yet finished on every screen.

## Development

Original Python source is included for archive handling, guarded text edits,
word wrapping, delta generation, and installation. Python's standard library is
sufficient; no machine-translation model is downloaded.

```sh
python -m unittest discover -s tests -v
```

To build the standalone Windows EXE yourself, install `pyinstaller==6.22.3` in
your Python environment and run `Build-Windows-Exe.ps1`. Alternatively, run the
**Build Windows app** workflow in GitHub Actions and download its artifact.
Maintainers can attach the EXE to a GitHub Release; it is not stored in Git.
The GUI and runtime are bundled with PyInstaller; see its
[packaging documentation](https://pyinstaller.org/en/stable/usage.html).
Third-party runtime notices are included under `licenses/`.

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
