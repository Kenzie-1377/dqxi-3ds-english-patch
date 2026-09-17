# DQXI 3DS English Patch — source tools

An experimental, unofficial English-translation tooling project for the Japanese
Nintendo 3DS edition of Dragon Quest XI. Maintained by **Kenzie-1377**.

**This initial public repository contains source tools, not a playable translation
release.** It does not yet reproduce the complete private development build.
No ROM, extracted game data, translated game script, executable, emulator, keys,
or save files are included. Bring your own local inputs; do not upload them here.

## Project status

This project is **not complete**. I will be updating it as I can. There is no
fixed release schedule, and translations, compatibility, and tooling may change.
Thank you for your patience while I work on it.

— Kenzie-1377

## Included

- PACK/PACA archive inspection and uncompressed rebuilding.
- Backward-LZ decompression for supported local PACA inputs.
- Guarded append-only UTF-16 text replacement with exact input-hash and old-text checks.
- Word wrapping that preserves dynamic text tokens, including player names.
- Synthetic tests that do not require game files.

The tools use Python 3.10 or newer and the standard library only.

## Quick start

Run from this repository's root:

```sh
python -m unittest discover -s tests -v
python tools/dq11_pack.py --help
python tools/dq11_blz.py --help
python tools/text_patch.py --help
```

For local, uncompressed archives:

```sh
python tools/dq11_pack.py list input/example.pack
python tools/dq11_pack.py extract input/example.pack output/extracted
python tools/dq11_pack.py rebuild input/example.pack output/rebuilt.pack --replacements output/replacements
```

For a supported compressed archive, first decompress to a separate output:

```sh
python tools/dq11_blz.py input/example.pack output/expanded.pack --pack-magic
```

Never overwrite your original input. Keep all extracted files and generated
archives under the ignored `input/`, `output/`, or `private/` directories.

## Text patch workflow

See [the format and safety notes](docs/patching.md). A patch manifest must identify
the exact input hash, verified text-pointer offsets, expected current strings,
and replacement strings. This release deliberately does **not** ship a complete
game-specific offset/translation manifest.

The private prototype used a 24-cell line limit with room for six-letter player
names. This is an empirical setting, not a guarantee for every screen or font.
Wrapping does not create new dialogue pages. Long-message continuation needs
in-game testing; never shorten text by blindly discarding overflow.

## Current limitations

- Work in progress; not a complete or professionally reviewed translation.
- No public full-build recipe or ready-to-install patch is included yet.
- BXON pointer offsets must be structurally verified. Searching every integer
  for apparent pointers can corrupt event flags and unrelated data.
- A name initialized in a save can remain unchanged after text assets change.
  These tools do not edit saves.
- Archive tools target known format variants, not arbitrary hostile inputs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Useful contributions include synthetic
format tests, verified structure documentation, and reproducible bug reports.

## License and attribution

Original source code and documentation in this repository are MIT licensed;
see [LICENSE](LICENSE). The license does not grant rights to third-party game
content, trademarks, or assets. Dragon Quest XI and its associated names belong
to their respective owners. This project is not affiliated with or endorsed by
the game's developers or publishers.

Development has included AI assistance. Review and test changes before using
them with personal game data.
