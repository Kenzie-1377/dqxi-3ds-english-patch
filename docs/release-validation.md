# Initial player-build validation

Validated September 16, 2026:

- 14 synthetic unit tests passed.
- The pinned Windows x64 CTRTool v1.3.0 download matched its recorded SHA-256.
- A decrypted game application (`.app`) was extracted through the player builder.
- All source-file checks passed against the release manifest.
- All 379 generated mod files matched the active development mod byte for byte.
- Release deltas and manifest total 955,089 bytes (about 0.96 MB).
- The release tree contains only deltas, a small executable patch payload, and
  a hash/path manifest. It does not contain a ROM, full game archive, or save.

These checks establish reproducibility of the current incomplete mod, not that
the game has been fully translated or every scene has been tested. The original
game and saved progress were not changed. The new builder's `.cci`, `.3ds`, and
`.cxi` container paths have not all received end-to-end tests. Their extracted
files must pass the same mandatory hash checks.

## Standalone Windows application

The Windows x64 windowed EXE bundles Python 3.13, Tcl/Tk, and the 379 patch
payloads. It does not require users to install Python. It downloads the pinned
extractor with consent, or accepts an existing extractor.

- 16 automated tests passed, including cancellation before I/O and rejection of
  incorrect inputs without creating output.
- The frozen executable successfully created its graphical interface and verified
  all embedded payload hashes in a hidden startup smoke test.
- The frozen executable completed both extracted-input and decrypted `.app`
  ROM-to-mod builds. The final ROM-to-mod build's 379 output hashes matched the
  release manifest.
- The bundled-file inventory contained no ROM, extracted PACK archive, or save.
- Runtime license notices are bundled. The executable is unsigned.

The UI was instantiated in the smoke test; interactive clicking and all Windows
display-scaling configurations have not been exhaustively tested. Automated tests
were run on a development machine; a separate clean Windows machine test remains
recommended before promoting the release as stable.
