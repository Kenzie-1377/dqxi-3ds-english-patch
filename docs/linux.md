# DQXI English Translation Builder 1.0 — Linux

This package is a Python 3 command-line builder. It does not need Wine or the
Windows executable. Use Python 3.10 or newer and your own supported decrypted
Japanese Dragon Quest XI game (title `0004000000199200`).

Extract the tar.gz package, open a terminal in its folder, and run:

```sh
./build-translation.sh --rom "/path/to/game.3ds" --output-format rom --download-ctrtool --output "/path/to/new-output"
./build-translation.sh --rom "/path/to/game.cia" --output-format cia --download-ctrtool --output "/path/to/new-output"
```

Use a different new output folder for each build. For mod folders, use
`--output-format mod`. With already extracted originals:

```sh
./build-translation.sh --extracted "/path/to/originals" --output-format mod --output "/path/to/new-output"
```

Originals must contain romfs/ and exefs/code.bin. Inputs and existing saves are
not overwritten. CIA output requires CIA input and retains its ticket,
certificate chain, metadata and unrelated contents. The modified CIA needs a
compatible custom-firmware console or emulator; no encryption keys are included.
Encrypted or mismatched game data are rejected.

Automatic tool downloads support Linux x86_64 and verify pinned official
CTRTool 1.3.0 and 3dstool 1.2.6 archives. To use local compatible tools, replace
`--download-ctrtool` with `--ctrtool /path/to/ctrtool` and, for rebuilt ROM/CIA
output, add `--rebuild-tool /path/to/3dstool`. The official Ubuntu x86_64 tool
may require your distribution's C++ runtime libraries.

The shared Python engine is tested against all 1,256 original inputs and output
hashes. Native Linux execution and real-console CIA installation are separate
validation steps and are not certified by Windows-hosted tests.

Report crashes, progression blockers and broken quests at:
https://github.com/Kenzie-1377/dqxi-3ds-english-patch/issues

Do not share generated ROMs, CIAs, mod folders or extracted originals. Share
this patch package instead. See LICENSE for original-code licensing; game
content and third-party tools retain their own rights and notices.
