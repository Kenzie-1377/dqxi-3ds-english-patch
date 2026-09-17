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
